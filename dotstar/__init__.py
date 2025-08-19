"""
Viewer Dot Star - Scientific Data File Viewer
Multi-format data file browsing and analysis tool designed for researchers
"""

__version__ = "0.1.0"
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
