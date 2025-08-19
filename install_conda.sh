#!/bin/bash

# DotStarViewer Conda环境安装脚本
# 支持Linux/macOS系统

set -e

echo "🌟 DotStar科研数据查看器 - Conda安装脚本"
echo "============================================="

# 检查conda是否安装
echo "📋 检查Conda环境..."
if ! command -v conda &> /dev/null; then
    echo "❌ 未找到Conda，请先安装Anaconda或Miniconda"
    echo "📥 下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

CONDA_VERSION=$(conda --version)
echo "✅ 找到Conda: $CONDA_VERSION"

# 检查environment.yml文件
if [ ! -f "environment.yml" ]; then
    echo "❌ 未找到environment.yml文件"
    exit 1
fi

echo "📦 environment.yml文件内容："
cat environment.yml

# 询问环境名称
read -p "🔧 请输入环境名称 [默认: dotstar-viewer]: " env_name
env_name=${env_name:-dotstar-viewer}

# 检查环境是否已存在
if conda env list | grep -q "^$env_name "; then
    echo "⚠️  环境 '$env_name' 已存在"
    read -p "是否删除并重新创建? [y/N]: " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        echo "🗑️  删除现有环境..."
        conda env remove -n $env_name -y
    else
        echo "❌ 安装取消"
        exit 1
    fi
fi

# 创建conda环境
echo "🐍 创建Conda环境: $env_name"
conda env create -n $env_name -f environment.yml

# 激活环境
echo "🔄 激活环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $env_name

# 验证安装
echo "🧪 验证安装..."
python -c "
import sys
print(f'Python版本: {sys.version}')

# 检查核心依赖
try:
    import PyQt5
    print('✅ PyQt5 安装成功')
except ImportError as e:
    print(f'❌ PyQt5 导入失败: {e}')
    sys.exit(1)

try:
    import numpy as np
    import pandas as pd
    import yaml
    print('✅ 基础科学计算包安装成功')
except ImportError as e:
    print(f'❌ 基础包导入失败: {e}')
    sys.exit(1)

# 检查可选依赖
optional_packages = {
    'scipy': '科学计算',
    'h5py': 'HDF5支持',
    'torch': 'PyTorch',
    'matplotlib': '可视化'
}

for package, desc in optional_packages.items():
    try:
        __import__(package)
        print(f'✅ {desc} ({package}) 安装成功')
    except ImportError:
        print(f'⚠️  {desc} ({package}) 未安装')

print('🎉 环境验证完成！')
"

if [ $? -eq 0 ]; then
    # 创建激活脚本
    echo "📝 创建启动脚本..."
    
    # Linux/macOS启动脚本
    cat > start_dotstar.sh << EOF
#!/bin/bash
# DotStar数据查看器启动脚本

# 获取conda路径
CONDA_BASE=\$(conda info --base)
source \$CONDA_BASE/etc/profile.d/conda.sh

# 激活环境
conda activate $env_name

# 启动应用
python main.py

# 可选：退出时停用环境
# conda deactivate
EOF
    chmod +x start_dotstar.sh
    
    # Windows批处理文件（如果需要）
    cat > start_dotstar.bat << 'EOF'
@echo off
call conda activate %env_name%
python main.py
pause
EOF
    
    # 创建环境信息文件
    cat > conda_env_info.txt << EOF
DotStar数据查看器 - Conda环境信息
================================

环境名称: $env_name
创建时间: $(date)
Python版本: $(python --version)

激活命令:
  conda activate $env_name

启动应用:
  方式1: ./start_dotstar.sh
  方式2: conda activate $env_name && python main.py

环境管理:
  查看环境: conda env list
  删除环境: conda env remove -n $env_name
  导出环境: conda env export -n $env_name > environment_backup.yml
  更新环境: conda env update -n $env_name -f environment.yml

EOF
    
    # 创建示例数据
    echo "📁 生成示例数据..."
    python create_sample_data.py
    
    echo ""
    echo "🎉 安装完成！"
    echo ""
    echo "🚀 启动方式："
    echo "   方式1: ./start_dotstar.sh"
    echo "   方式2: conda activate $env_name && python main.py"
    echo ""
    echo "📖 环境信息: conda_env_info.txt"
    echo "📁 示例数据: sample_data/"
    echo "📚 使用文档: README.md"
    echo ""
    echo "🔧 环境管理："
    echo "   激活: conda activate $env_name"
    echo "   停用: conda deactivate"
    echo "   删除: conda env remove -n $env_name"
    echo ""
    
else
    echo "❌ 安装验证失败，请检查错误信息"
    exit 1
fi
