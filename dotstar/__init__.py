"""
DotStarViewer - 科研数据文件查看器
专为科研人员设计的多格式数据文件浏览和分析工具
"""

__version__ = "1.0.0"
__author__ = "DotStar Team"
__description__ = "Scientific Data File Viewer"

from .core.main_window import MainWindow
from .core.file_loader import FileLoader
from .core.data_inspector import DataInspector

__all__ = [
    "MainWindow",
    "FileLoader", 
    "DataInspector"
]
