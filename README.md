# Viewer Dot Star (Viewer.*)

A multi-format data file browser tool designed for researchers.

## Features

- **File Format Support**: JSON, Pickle, NumPy, MATLAB, HDF5, NetCDF, CSV, YAML, TOML, PLY, OBJ, STL, PyTorch, SafeTensors, TIFF, FITS
- **Data Inspection**: Tree view, multiple display modes, statistical analysis
- **User Interface**: Drag & drop, recent files, multi-language support

## Installation

### Requirements
- Python
- PyQt5
- NumPy
- toml

### Install
```bash
git clone https://github.com/dotstar/dataviewer.git
cd DotStarViewer
pip install -r requirements.txt
python main.py
```

### Optional Dependencies
```bash
# For additional format support
pip install scipy h5py netCDF4 pyarrow open3d torch safetensors astropy
```

## Usage

1. Launch: `python main.py`
2. Load files: Drag & drop or File -> Open
3. Explore data in tree view and detail panels

## License

MIT License
