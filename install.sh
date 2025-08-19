#!/bin/bash

# DotStarViewer 自动安装脚本
# 适用于 Ubuntu/Debian 系统

set -e

echo "🌟 DotStar科研数据查看器 - 自动安装脚本"
echo "============================================="

# 检查Python版本
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ 找到Python版本: $PYTHON_VERSION"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "📦 安装pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# 更新系统包
echo "🔄 更新系统包..."
sudo apt update

# 安装系统依赖
echo "📦 安装系统依赖..."
sudo apt install -y \
    python3-dev \
    python3-pyqt5 \
    python3-pyqt5.qtcore \
    python3-pyqt5.qtgui \
    python3-pyqt5.qtwidgets \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0

# 创建虚拟环境（可选）
read -p "🤔 是否创建Python虚拟环境？(推荐) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv dotstar_env
    source dotstar_env/bin/activate
    echo "✅ 虚拟环境已激活"
    
    # 创建激活脚本
    cat > activate_dotstar.sh << 'EOF'
#!/bin/bash
source dotstar_env/bin/activate
python main.py
EOF
    chmod +x activate_dotstar.sh
    echo "📝 已创建启动脚本: activate_dotstar.sh"
fi

# 升级pip
echo "⬆️ 升级pip..."
pip3 install --upgrade pip

# 安装基础依赖
echo "📦 安装基础Python包..."
pip3 install \
    PyQt5>=5.15.0 \
    numpy>=1.21.0 \
    pandas>=1.3.0 \
    PyYAML>=5.4.0 \
    toml>=0.10.0 \
    Pillow>=8.3.0

# 询问是否安装可选依赖
echo ""
echo "🔧 可选依赖安装："

read -p "🧪 安装科学计算支持 (scipy, h5py, netCDF4)? [y/N]: " install_science
if [[ $install_science =~ ^[Yy]$ ]]; then
    echo "📊 安装科学计算包..."
    pip3 install scipy>=1.7.0 h5py>=3.1.0 netCDF4>=1.5.0
fi

read -p "🤖 安装深度学习支持 (torch, safetensors)? [y/N]: " install_ml
if [[ $install_ml =~ ^[Yy]$ ]]; then
    echo "🧠 安装深度学习包..."
    pip3 install torch>=1.9.0 safetensors>=0.2.0
fi

read -p "🌌 安装天文图像支持 (astropy)? [y/N]: " install_astro
if [[ $install_astro =~ ^[Yy]$ ]]; then
    echo "🔭 安装天文学包..."
    pip3 install astropy>=4.3.0
fi

read -p "📊 安装表格数据支持 (pyarrow)? [y/N]: " install_tables
if [[ $install_tables =~ ^[Yy]$ ]]; then
    echo "📈 安装表格数据包..."
    pip3 install pyarrow>=5.0.0
fi

read -p "🎯 安装3D数据支持 (open3d)? [y/N]: " install_3d
if [[ $install_3d =~ ^[Yy]$ ]]; then
    echo "🎨 安装3D数据包..."
    pip3 install open3d>=0.13.0
fi

read -p "📊 安装可视化支持 (matplotlib)? [y/N]: " install_viz
if [[ $install_viz =~ ^[Yy]$ ]]; then
    echo "📊 安装可视化包..."
    pip3 install matplotlib>=3.4.0
fi

# 创建示例数据
echo ""
echo "📁 创建示例数据文件..."
python3 create_sample_data.py

# 创建桌面启动器（可选）
read -p "🖥️ 是否创建桌面启动器？ [y/N]: " create_desktop
if [[ $create_desktop =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    DESKTOP_FILE="$HOME/.local/share/applications/dotstar-viewer.desktop"
    
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=DotStar数据查看器
Comment=科研数据文件查看和分析工具
Exec=bash -c "cd '$CURRENT_DIR' && python3 main.py"
Icon=$CURRENT_DIR/dotstar-icon.png
Terminal=false
Categories=Science;Development;
StartupWMClass=DotStarViewer
EOF
    
    echo "🚀 桌面启动器已创建: $DESKTOP_FILE"
fi

# 测试安装
echo ""
echo "🧪 测试安装..."
python3 -c "
import sys
try:
    from dotstar.core.file_loader import FileLoader
    from dotstar.core.main_window import MainWindow
    print('✅ DotStarViewer核心模块导入成功')
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)

try:
    from PyQt5.QtWidgets import QApplication
    print('✅ PyQt5导入成功')
except ImportError as e:
    print(f'❌ PyQt5导入失败: {e}')
    sys.exit(1)

print('🎉 安装测试通过！')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 安装完成！"
    echo ""
    echo "🚀 启动方式："
    if [[ $create_venv =~ ^[Yy]$ ]]; then
        echo "   方式1: ./activate_dotstar.sh"
        echo "   方式2: source dotstar_env/bin/activate && python main.py"
    else
        echo "   python3 main.py"
    fi
    echo ""
    echo "📖 使用说明："
    echo "   - 拖拽数据文件到应用程序窗口"
    echo "   - 或点击'浏览文件'按钮选择文件"
    echo "   - 支持格式: JSON, CSV, NumPy, MATLAB, HDF5等"
    echo ""
    echo "📁 示例数据位置: sample_data/"
    echo "📚 帮助文档: README.md"
    echo ""
else
    echo "❌ 安装测试失败，请检查错误信息"
    exit 1
fi
