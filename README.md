# DotStar 科研数据查看器

一个专为科研人员设计的多格式数据文件浏览和分析工具。

## 🌟 特性

### 📁 广泛的文件格式支持
- **通用格式**: JSON, Pickle
- **科学计算**: NumPy (npy, npz), MATLAB (mat), HDF5 (h5, hdf5), NetCDF (nc)
- **表格数据**: CSV, TSV, Parquet
- **配置文件**: YAML, TOML
- **3D数据**: PLY, OBJ, STL, OFF, XYZ点云
- **深度学习**: PyTorch (pt, pth), SafeTensors
- **图像**: TIFF, FITS天文图像

### 🔍 强大的数据检查功能
- **层次化结构显示**: 树形视图展示复杂数据结构
- **多视图模式**: 文本视图、表格视图、原始数据视图
- **详细统计分析**: 自动计算数值统计信息
- **智能数据预览**: 大文件自动截断和优化显示

### 🎨 用户友好的界面
- **拖拽加载**: 支持文件拖拽操作
- **最近文件**: 快速访问最近打开的文件
- **实时进度**: 大文件加载进度显示
- **多语言支持**: 中文界面和文档

## 📦 安装

### 环境要求
- Python 3.7+
- Conda (推荐) 或 Python pip

### 🐍 Conda安装 (推荐)

1. **下载项目**
```bash
git clone https://github.com/dotstar/dataviewer.git
cd DotStarViewer
```

2. **一键安装**
```bash
chmod +x install_conda.sh
./install_conda.sh
```

3. **启动应用**
```bash
./start_dotstar.sh
# 或者
conda activate dotstar-viewer
python main.py
```

### 🐍 手动Conda安装

```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate dotstar-viewer

# 启动应用
python main.py
```

### 📦 Pip安装 (备选方案)

1. **克隆仓库**
```bash
git clone https://github.com/dotstar/dataviewer.git
cd dataviewer
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行程序**
```bash
python main.py
```

### 可选依赖安装

**Conda方式：**
```bash
conda activate dotstar-viewer
conda install -c conda-forge open3d astropy
pip install safetensors
```

**Pip方式：**
```bash
# 科学计算格式
pip install scipy h5py netCDF4

# 3D数据支持
pip install open3d

# 深度学习格式
pip install torch safetensors

# 天文图像
pip install astropy

# 表格数据
pip install pyarrow
```

## 🚀 快速开始

### 1. 安装和启动

**Conda用户 (推荐):**
```bash
# 一键安装
./install_conda.sh

# 启动应用
./start_dotstar.sh
```

**手动启动:**
```bash
conda activate dotstar-viewer
python main.py
```

### 2. 加载数据文件

**方法一：拖拽操作**
- 直接将数据文件拖拽到应用程序窗口

**方法二：文件浏览**
- 点击"浏览文件"按钮选择文件
- 或使用菜单 `文件 -> 打开文件` (Ctrl+O)

### 3. 探索数据

- **左侧面板**: 查看文件信息和最近文件
- **数据结构树**: 展开查看数据的层次结构
- **详细面板**: 
  - *概览标签*: 文件和数据总体信息
  - *数据标签*: 多种格式查看数据内容
  - *统计标签*: 数值数据的统计分析
  - *可视化标签*: 数据可视化选项

## 📊 支持的数据类型示例

### JSON科研数据
```json
{
  "experiment": {
    "name": "蛋白质结构分析",
    "samples": [
      {"id": "S001", "concentration": 10.5},
      {"id": "S002", "concentration": 8.3}
    ]
  }
}
```

### NumPy数组
```python
import numpy as np
# 支持1D, 2D, 3D及更高维度数组
data = np.random.randn(1000, 100)
np.save('experiment_data.npy', data)
```

### YAML配置
```yaml
实验配置:
  名称: "深度学习模型训练"
  参数:
    学习率: 0.001
    批量大小: 32
```

## 🛠️ 开发

### 项目结构
```
DotStarViewer/
├── main.py                 # 程序入口
├── requirements.txt        # pip依赖列表
├── environment.yml         # conda环境配置
├── install_conda.sh        # conda自动安装脚本
├── start_dotstar.sh        # 启动脚本
├── dotstar/               # 主要源码
│   ├── __init__.py
│   └── core/              # 核心模块
│       ├── main_window.py      # 主窗口
│       ├── file_loader.py      # 文件加载器
│       └── data_inspector.py   # 数据检查器
├── sample_data/           # 示例数据
├── create_sample_data.py  # 示例数据生成脚本
└── README.md
```

### 添加新的文件格式支持

1. 在 `file_loader.py` 中的 `SUPPORTED_FORMATS` 添加格式
2. 实现对应的 `_load_xxx()` 方法
3. 更新文件过滤器

### 自定义数据显示

在 `data_inspector.py` 中扩展显示组件：
- 修改 `DataTreeWidget` 自定义树形显示
- 扩展 `DetailPanel` 添加新的标签页
- 在 `VisualizationTab` 中添加可视化类型

## 🔧 高级用法

### 批量处理
```python
from dotstar.core.file_loader import FileLoader

loader = FileLoader()
for file_path in file_list:
    data, metadata = loader.load_file(file_path)
    # 处理数据...
```

### 编程接口
```python
from dotstar import MainWindow, FileLoader, DataInspector
from PyQt5.QtWidgets import QApplication

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
```

## 🧪 测试数据

**方式1: 自动生成 (推荐)**
```bash
# 如果使用conda
conda activate dotstar-viewer
python create_sample_data.py

# 如果使用pip
python create_sample_data.py
```

**方式2: 手动创建**
```bash
# 创建示例数据目录
mkdir sample_data

# 然后运行上述命令
```

这将在 `sample_data/` 目录中创建各种格式的测试文件：
- `experiment.json` - JSON实验数据
- `lab_results.csv` - CSV实验结果  
- `ml_config.yaml` - YAML配置文件
- `time_series.npy` - NumPy时间序列数据
- `molecular_dynamics.npz` - 多数组NPZ文件
- `experiment_results.pkl` - Pickle复杂对象
- 以及更多格式的示例文件

## 🐛 故障排除

### 常见问题

**Q: conda环境创建失败**
A: 检查网络连接，尝试更换conda源：
```bash
conda config --add channels conda-forge
conda config --add channels pytorch
```

**Q: 提示"Import could not be resolved"**
A: 这是IDE的提示，确保激活了正确的conda环境

**Q: 某些文件格式无法加载**
A: 检查是否安装了对应的可选依赖包，使用以下命令检查：
```bash
conda activate dotstar-viewer
conda list
```

**Q: 大文件加载很慢**
A: 程序会显示进度条，大文件会自动优化显示

**Q: 中文显示乱码**
A: 确保文件编码为UTF-8

**Q: 如何更新环境**
A: 
```bash
conda env update -n dotstar-viewer -f environment.yml
```

**Q: 如何完全重装**
A:
```bash
conda env remove -n dotstar-viewer
./install_conda.sh
```

### 日志和调试

程序运行时会在控制台输出详细信息，如遇问题请查看错误信息。

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献指南
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [PyQt5](https://riverbankcomputing.com/software/pyqt/) - GUI框架
- [NumPy](https://numpy.org/) - 数值计算
- [Pandas](https://pandas.pydata.org/) - 数据分析
- [Open3D](http://www.open3d.org/) - 3D数据处理

## 📧 联系

- 项目主页: https://github.com/dotstar/dataviewer
- 邮箱: support@dotstar.dev

---

**DotStar科研数据查看器** - 让数据探索更简单 🌟
