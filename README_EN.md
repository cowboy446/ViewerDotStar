# DotStar Scientific Data Viewer

A multi-format data file browser and analysis tool designed for researchers.

## 🌟 Features

### 📁 Extensive File Format Support
- **Common Formats**: JSON, Pickle
- **Scientific Computing**: NumPy (npy, npz), MATLAB (mat), HDF5 (h5, hdf5), NetCDF (nc)
- **Tabular Data**: CSV, TSV, Parquet
- **Configuration Files**: YAML, TOML
- **3D Data**: PLY, OBJ, STL, OFF, XYZ point clouds
- **Deep Learning**: PyTorch (pt, pth), SafeTensors
- **Images**: TIFF, FITS astronomical images

### 🔍 Powerful Data Inspection
- **Hierarchical Structure Display**: Tree view for complex data structures
- **Multiple View Modes**: Text view, table view, raw data view
- **Detailed Statistical Analysis**: Automatic numerical statistics calculation
- **Smart Data Preview**: Large file auto-truncation and optimized display

### 🎨 User-Friendly Interface
- **Drag & Drop Loading**: Support for file drag and drop operations
- **Recent Files**: Quick access to recently opened files
- **Real-time Progress**: Loading progress display for large files
- **Multi-language Support**: English and Chinese interface

## 📦 Installation

### System Requirements
- Python 3.7+
- Conda (recommended) or Python pip

### 🐍 Conda Installation (Recommended)

1. **Download Project**
```bash
git clone https://github.com/dotstar/dataviewer.git
cd DotStarViewer
```

2. **One-Click Installation**
```bash
chmod +x install_conda.sh
./install_conda.sh
```

3. **Launch Application**
```bash
./start_dotstar.sh
# or
conda activate dotstar-viewer
python main.py
```

### 🐍 Manual Conda Installation

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate dotstar-viewer

# Launch application
python main.py
```

### 📦 Pip Installation (Alternative)

1. **Clone Repository**
```bash
git clone https://github.com/dotstar/dataviewer.git
cd dataviewer
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Program**
```bash
python main.py
```

### Optional Dependencies

**Conda Method:**
```bash
conda activate dotstar-viewer
conda install -c conda-forge open3d astropy
pip install safetensors
```

**Pip Method:**
```bash
# Scientific computing formats
pip install scipy h5py netCDF4

# 3D data support
pip install open3d

# Deep learning formats
pip install torch safetensors

# Astronomical images
pip install astropy

# Tabular data
pip install pyarrow
```

## 🚀 Quick Start

### 1. Installation and Launch

**Conda Users (Recommended):**
```bash
# One-click installation
./install_conda.sh

# Launch application
./start_dotstar.sh
```

**Manual Launch:**
```bash
conda activate dotstar-viewer
python main.py
```

### 2. Load Data Files

**Method 1: Drag & Drop**
- Directly drag data files to the application window

**Method 2: File Browser**
- Click "Browse Files" button to select files
- Or use menu `File -> Open File` (Ctrl+O)

### 3. Explore Data

- **Left Panel**: View file information and recent files
- **Data Structure Tree**: Expand to view hierarchical data structure
- **Detail Panel**: 
  - *Overview Tab*: File and data overview information
  - *Data Tab*: View data content in multiple formats
  - *Statistics Tab*: Numerical data statistical analysis
  - *Visualization Tab*: Data visualization options

## 📊 Supported Data Type Examples

### JSON Research Data
```json
{
  "experiment": {
    "name": "Protein Structure Analysis",
    "samples": [
      {"id": "S001", "concentration": 10.5},
      {"id": "S002", "concentration": 8.3}
    ]
  }
}
```

### NumPy Arrays
```python
import numpy as np
# Supports 1D, 2D, 3D and higher dimensional arrays
data = np.random.randn(1000, 100)
np.save('experiment_data.npy', data)
```

### YAML Configuration
```yaml
experiment_config:
  name: "Deep Learning Model Training"
  parameters:
    learning_rate: 0.001
    batch_size: 32
```

## 🛠️ Development

### Project Structure
```
DotStarViewer/
├── main.py                 # Program entry point
├── requirements.txt        # pip dependency list
├── environment.yml         # conda environment configuration
├── install_conda.sh        # conda auto-installation script
├── start_dotstar.sh        # launch script
├── dotstar/               # main source code
│   ├── __init__.py
│   └── core/              # core modules
│       ├── main_window.py      # main window
│       ├── file_loader.py      # file loader
│       ├── data_inspector.py   # data inspector
│       └── translator.py       # internationalization
├── sample_data/           # sample data
├── create_sample_data.py  # sample data generation script
└── README.md
```

### Adding New File Format Support

1. Add format to `SUPPORTED_FORMATS` in `file_loader.py`
2. Implement corresponding `_load_xxx()` method
3. Update file filter

### Custom Data Display

Extend display components in `data_inspector.py`:
- Modify `DataTreeWidget` for custom tree display
- Extend `DetailPanel` to add new tabs
- Add visualization types in `VisualizationTab`

## 🔧 Advanced Usage

### Batch Processing
```python
from dotstar.core.file_loader import FileLoader

loader = FileLoader()
for file_path in file_list:
    data, metadata = loader.load_file(file_path)
    # Process data...
```

### Programming Interface
```python
from dotstar import MainWindow, FileLoader, DataInspector
from PyQt5.QtWidgets import QApplication

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
```

## 🧪 Test Data

**Method 1: Auto-generate (Recommended)**
```bash
# If using conda
conda activate dotstar-viewer
python create_sample_data.py

# If using pip
python create_sample_data.py
```

**Method 2: Manual Creation**
```bash
# Create sample data directory
mkdir sample_data

# Then run the above command
```

This will create various format test files in the `sample_data/` directory:
- `experiment.json` - JSON experimental data
- `lab_results.csv` - CSV experimental results  
- `ml_config.yaml` - YAML configuration file
- `time_series.npy` - NumPy time series data
- `molecular_dynamics.npz` - Multi-array NPZ file
- `experiment_results.pkl` - Pickle complex object
- And more format sample files

## 🐛 Troubleshooting

### Common Issues

**Q: conda environment creation failed**
A: Check network connection, try changing conda sources:
```bash
conda config --add channels conda-forge
conda config --add channels pytorch
```

**Q: "Import could not be resolved" prompt**
A: This is an IDE prompt, ensure the correct conda environment is activated

**Q: Some file formats cannot be loaded**
A: Check if corresponding optional dependency packages are installed, use the following command to check:
```bash
conda activate dotstar-viewer
conda list
```

**Q: Large files load slowly**
A: The program will show a progress bar, large files will be automatically optimized for display

**Q: Chinese characters display as garbled text**
A: Ensure file encoding is UTF-8

**Q: How to update environment**
A: 
```bash
conda env update -n dotstar-viewer -f environment.yml
```

**Q: How to completely reinstall**
A:
```bash
conda env remove -n dotstar-viewer
./install_conda.sh
```

### Logging and Debugging

The program will output detailed information to the console during runtime. Please check error messages if you encounter issues.

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

### Contribution Guidelines
1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [PyQt5](https://riverbankcomputing.com/software/pyqt/) - GUI framework
- [NumPy](https://numpy.org/) - Numerical computing
- [Pandas](https://pandas.pydata.org/) - Data analysis
- [Open3D](http://www.open3d.org/) - 3D data processing

## 📧 Contact

- Project Homepage: https://github.com/dotstar/dataviewer
- Email: support@dotstar.dev

---

**DotStar Scientific Data Viewer** - Making data exploration easier 🌟
