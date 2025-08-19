"""
数据加载器模块
处理不同格式的科研数据文件加载
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
import warnings

class FileLoader:
    """文件加载器类"""
    
    # 支持的文件格式
    SUPPORTED_FORMATS = {
        # General formats
        '.json': 'JSON format',
        '.pkl': 'Pickle format', 
        '.pickle': 'Pickle format',
        
        # Scientific computing
        '.npy': 'NumPy array',
        '.npz': 'NumPy compressed array',
        '.mat': 'MATLAB data',
        '.h5': 'HDF5 format',
        '.hdf5': 'HDF5 format',
        '.nc': 'NetCDF format',
        
        # Tabular data
        '.csv': 'CSV table',
        '.tsv': 'TSV table',
        '.parquet': 'Parquet format',
        
        # Configuration files
        '.yaml': 'YAML format',
        '.yml': 'YAML format',
        '.toml': 'TOML format',
        
        # 3D data
        '.ply': 'PLY point cloud',
        '.obj': 'OBJ model',
        '.stl': 'STL model',
        '.off': 'OFF model',
        '.xyz': 'XYZ point cloud',
        
        # Deep learning
        '.pt': 'PyTorch model',
        '.pth': 'PyTorch checkpoint',
        '.safetensors': 'SafeTensors format',
        
        # Images
        '.tiff': 'TIFF image',
        '.tif': 'TIFF image', 
        '.fits': 'FITS astronomical image'
    }
    
    def __init__(self):
        self.cached_data = {}
        self.file_metadata = {}
    
    def is_supported(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def get_format_description(self, file_path: str) -> str:
        """Get file format description"""
        ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_FORMATS.get(ext, 'Unknown format')
    
    def load_file(self, file_path: str) -> Tuple[Any, Dict[str, Any]]:
        """
        加载文件数据
        返回: (数据, 元数据)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported(file_path):
            raise ValueError(f"Unsupported file format: {file_path}")
        
        ext = Path(file_path).suffix.lower()
        file_size = os.path.getsize(file_path)
        
        try:
            # 根据文件扩展名选择加载方法
            if ext == '.json':
                data, metadata = self._load_json(file_path)
            elif ext in ['.pkl', '.pickle']:
                data, metadata = self._load_pickle(file_path)
            elif ext == '.npy':
                data, metadata = self._load_npy(file_path)
            elif ext == '.npz':
                data, metadata = self._load_npz(file_path)
            elif ext == '.mat':
                data, metadata = self._load_mat(file_path)
            elif ext in ['.h5', '.hdf5']:
                data, metadata = self._load_hdf5(file_path)
            elif ext == '.nc':
                data, metadata = self._load_netcdf(file_path)
            elif ext == '.csv':
                data, metadata = self._load_csv(file_path)
            elif ext == '.tsv':
                data, metadata = self._load_tsv(file_path)
            elif ext == '.parquet':
                data, metadata = self._load_parquet(file_path)
            elif ext in ['.yaml', '.yml']:
                data, metadata = self._load_yaml(file_path)
            elif ext == '.toml':
                data, metadata = self._load_toml(file_path)
            elif ext in ['.pt', '.pth']:
                data, metadata = self._load_pytorch(file_path)
            elif ext == '.safetensors':
                data, metadata = self._load_safetensors(file_path)
            elif ext in ['.ply', '.obj', '.stl', '.off', '.xyz']:
                data, metadata = self._load_3d_data(file_path)
            elif ext in ['.tiff', '.tif']:
                data, metadata = self._load_tiff(file_path)
            elif ext == '.fits':
                data, metadata = self._load_fits(file_path)
            else:
                raise ValueError(f"Unimplemented format: {ext}")
            
            # Add common metadata
            metadata.update({
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': file_size,
                'file_format': self.get_format_description(file_path),
                'file_extension': ext
            })
            
            return data, metadata
            
        except Exception as e:
            raise RuntimeError(f"Failed to load file {file_path}: {str(e)}")
    
    def _load_json(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = {
            'type': 'json',
            'encoding': 'utf-8'
        }
        
        if isinstance(data, dict):
            metadata['keys_count'] = len(data)
            metadata['top_level_keys'] = list(data.keys())[:10]  # First 10 keys
        elif isinstance(data, list):
            metadata['items_count'] = len(data)
            metadata['first_item_type'] = type(data[0]).__name__ if data else 'empty'
        
        return data, metadata
    
    def _load_pickle(self, file_path: str) -> Tuple[Any, Dict]:
        """加载Pickle文件"""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        metadata = {
            'type': 'pickle',
            'data_type': type(data).__name__
        }
        
        if hasattr(data, 'shape'):
            metadata['shape'] = data.shape
        if hasattr(data, 'dtype'):
            metadata['dtype'] = str(data.dtype)
        
        return data, metadata
    
    def _load_npy(self, file_path: str) -> Tuple[np.ndarray, Dict]:
        """加载NumPy数组文件"""
        data = np.load(file_path)
        
        metadata = {
            'type': 'numpy_array',
            'shape': data.shape,
            'dtype': str(data.dtype),
            'size': data.size,
            'ndim': data.ndim
        }
        
        if data.size > 0:
            metadata.update({
                'min_value': float(np.min(data)) if np.isreal(data).all() else 'complex',
                'max_value': float(np.max(data)) if np.isreal(data).all() else 'complex',
                'mean_value': float(np.mean(data)) if np.isreal(data).all() else 'complex'
            })
        
        return data, metadata
    
    def _load_npz(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载NumPy压缩文件"""
        try:
            # First try without allowing pickle
            npz_file = np.load(file_path, allow_pickle=False)
        except ValueError:
            # If it fails, allow pickle but issue a warning
            try:
                npz_file = np.load(file_path, allow_pickle=True)
                print("Warning: NPZ file contains pickled objects, loading with allow_pickle=True")
            except Exception as e:
                raise RuntimeError(f"Failed to load NPZ file: {str(e)}")
        
        data = {key: npz_file[key] for key in npz_file.files}
        
        metadata = {
            'type': 'numpy_archive',
            'arrays_count': len(data),
            'array_names': list(data.keys())
        }
        
        # Add detailed information for each array
        for key, arr in data.items():
            if hasattr(arr, 'shape'):
                metadata[f'{key}_shape'] = arr.shape
                metadata[f'{key}_dtype'] = str(arr.dtype)
        
        return data, metadata
    
    def _load_mat(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载MATLAB文件"""
        try:
            from scipy.io import loadmat
            data = loadmat(file_path)
            
            # Filter out MATLAB internal variables
            filtered_data = {k: v for k, v in data.items() 
                           if not k.startswith('__')}
            
            metadata = {
                'type': 'matlab',
                'variables_count': len(filtered_data),
                'variable_names': list(filtered_data.keys())
            }
            
            return filtered_data, metadata
            
        except ImportError:
            raise RuntimeError("scipy needs to be installed to read MATLAB files")
    
    def _load_hdf5(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载HDF5文件"""
        try:
            import h5py
            
            def read_hdf5_recursive(group):
                """Recursively read HDF5 groups"""
                result = {}
                for key in group.keys():
                    item = group[key]
                    if isinstance(item, h5py.Dataset):
                        result[key] = item[()]
                    elif isinstance(item, h5py.Group):
                        result[key] = read_hdf5_recursive(item)
                return result
            
            with h5py.File(file_path, 'r') as f:
                data = read_hdf5_recursive(f)
                
                metadata = {
                    'type': 'hdf5',
                    'top_level_keys': list(f.keys()),
                    'keys_count': len(f.keys())
                }
            
            return data, metadata
            
        except ImportError:
            raise RuntimeError("h5py needs to be installed to read HDF5 files")
    
    def _load_netcdf(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载NetCDF文件"""
        try:
            import netCDF4 as nc
            
            dataset = nc.Dataset(file_path, 'r')
            data = {}
            
            # Read variables
            for var_name in dataset.variables:
                var = dataset.variables[var_name]
                data[var_name] = var[:]
            
            # Read attributes
            attrs = {attr: getattr(dataset, attr) for attr in dataset.ncattrs()}
            
            metadata = {
                'type': 'netcdf',
                'variables': list(dataset.variables.keys()),
                'dimensions': dict(dataset.dimensions),
                'attributes': attrs
            }
            
            dataset.close()
            return data, metadata
            
        except ImportError:
            raise RuntimeError("netCDF4 needs to be installed to read NetCDF files")
    
    def _load_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """加载CSV文件"""
        data = pd.read_csv(file_path)
        
        metadata = {
            'type': 'csv',
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()}
        }
        
        return data, metadata
    
    def _load_tsv(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """加载TSV文件"""
        data = pd.read_csv(file_path, sep='\t')
        
        metadata = {
            'type': 'tsv',
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()}
        }
        
        return data, metadata
    
    def _load_parquet(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """加载Parquet文件"""
        data = pd.read_parquet(file_path)
        
        metadata = {
            'type': 'parquet',
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()}
        }
        
        return data, metadata
    
    def _load_yaml(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载YAML文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        metadata = {
            'type': 'yaml',
            'encoding': 'utf-8'
        }
        
        if isinstance(data, dict):
            metadata['keys_count'] = len(data)
            metadata['top_level_keys'] = list(data.keys())[:10]
        
        return data, metadata
    
    def _load_toml(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载TOML文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        metadata = {
            'type': 'toml',
            'encoding': 'utf-8',
            'sections': list(data.keys()) if isinstance(data, dict) else []
        }
        
        return data, metadata
    
    def _load_pytorch(self, file_path: str) -> Tuple[Any, Dict]:
        """加载PyTorch文件"""
        try:
            import torch
            
            data = torch.load(file_path, map_location='cpu')
            
            metadata = {
                'type': 'pytorch',
                'data_type': type(data).__name__
            }
            
            if isinstance(data, dict):
                metadata['keys'] = list(data.keys())
                metadata['keys_count'] = len(data)
            elif hasattr(data, 'state_dict'):
                metadata['has_state_dict'] = True
            
            return data, metadata
            
        except ImportError:
            raise RuntimeError("PyTorch needs to be installed to read .pt/.pth files")
    
    def _load_safetensors(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载SafeTensors文件"""
        try:
            from safetensors import safe_open
            
            tensors = {}
            with safe_open(file_path, framework="numpy") as f:
                for key in f.keys():
                    tensors[key] = f.get_tensor(key)
            
            metadata = {
                'type': 'safetensors',
                'tensors_count': len(tensors),
                'tensor_names': list(tensors.keys())
            }
            
            return tensors, metadata
            
        except ImportError:
            raise RuntimeError("safetensors needs to be installed to read SafeTensors files")
    
    def _load_3d_data(self, file_path: str) -> Tuple[Dict, Dict]:
        """加载3D数据文件"""
        try:
            import open3d as o3d
            
            ext = Path(file_path).suffix.lower()
            
            if ext == '.ply':
                mesh = o3d.io.read_triangle_mesh(file_path)
                point_cloud = o3d.io.read_point_cloud(file_path)
            elif ext == '.obj':
                mesh = o3d.io.read_triangle_mesh(file_path)
                point_cloud = None
            elif ext == '.stl':
                mesh = o3d.io.read_triangle_mesh(file_path)
                point_cloud = None
            elif ext == '.xyz':
                point_cloud = o3d.io.read_point_cloud(file_path)
                mesh = None
            else:
                mesh = o3d.io.read_triangle_mesh(file_path)
                point_cloud = o3d.io.read_point_cloud(file_path)
            
            data = {}
            metadata = {'type': '3d_data', 'format': ext}
            
            if mesh and len(mesh.vertices) > 0:
                data['mesh'] = {
                    'vertices': np.asarray(mesh.vertices),
                    'faces': np.asarray(mesh.triangles) if len(mesh.triangles) > 0 else None,
                    'vertex_colors': np.asarray(mesh.vertex_colors) if len(mesh.vertex_colors) > 0 else None,
                    'vertex_normals': np.asarray(mesh.vertex_normals) if len(mesh.vertex_normals) > 0 else None
                }
                metadata['vertices_count'] = len(mesh.vertices)
                metadata['faces_count'] = len(mesh.triangles)
            
            if point_cloud and len(point_cloud.points) > 0:
                data['point_cloud'] = {
                    'points': np.asarray(point_cloud.points),
                    'colors': np.asarray(point_cloud.colors) if len(point_cloud.colors) > 0 else None,
                    'normals': np.asarray(point_cloud.normals) if len(point_cloud.normals) > 0 else None
                }
                metadata['points_count'] = len(point_cloud.points)
            
            return data, metadata
            
        except ImportError:
            raise RuntimeError("Open3D needs to be installed to read 3D files")
    
    def _load_tiff(self, file_path: str) -> Tuple[np.ndarray, Dict]:
        """加载TIFF图像"""
        try:
            from PIL import Image
            
            img = Image.open(file_path)
            data = np.array(img)
            
            metadata = {
                'type': 'tiff_image',
                'shape': data.shape,
                'dtype': str(data.dtype),
                'mode': img.mode,
                'size': img.size
            }
            
            return data, metadata
            
        except ImportError:
            raise RuntimeError("Pillow needs to be installed to read TIFF files")
    
    def _load_fits(self, file_path: str) -> Tuple[Any, Dict]:
        """加载FITS天文图像"""
        try:
            from astropy.io import fits
            
            with fits.open(file_path) as hdul:
                data = hdul[0].data
                header = dict(hdul[0].header)
                
                metadata = {
                    'type': 'fits_image',
                    'shape': data.shape if data is not None else None,
                    'dtype': str(data.dtype) if data is not None else None,
                    'header_keys': list(header.keys())[:20],  # First 20 header entries
                    'header': header
                }
            
            return data, metadata
            
        except ImportError:
            raise RuntimeError("astropy needs to be installed to read FITS files")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return list(self.SUPPORTED_FORMATS.keys())
    
    def get_file_filter(self) -> str:
        """Get file dialog filter string"""
        filters = ["All supported formats (*" + " *".join(self.SUPPORTED_FORMATS.keys()) + ")"]
        
        # Group by category
        format_groups = {
            "General formats": ['.json', '.pkl', '.pickle'],
            "Scientific computing": ['.npy', '.npz', '.mat', '.h5', '.hdf5', '.nc'],
            "Tabular data": ['.csv', '.tsv', '.parquet'],
            "Configuration files": ['.yaml', '.yml', '.toml'],
            "3D data": ['.ply', '.obj', '.stl', '.off', '.xyz'],
            "Deep learning": ['.pt', '.pth', '.safetensors'],
            "Images": ['.tiff', '.tif', '.fits']
        }
        
        for group_name, extensions in format_groups.items():
            filter_str = f"{group_name} (*" + " *".join(extensions) + ")"
            filters.append(filter_str)
        
        filters.append("All files (*.*)")
        
        return ";;".join(filters)
