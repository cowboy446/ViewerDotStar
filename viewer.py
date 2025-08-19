#!/usr/bin/env python3
"""
Viewer Dot Star Main Program Entry Point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotstar.core.main_window import MainWindow

def main():
    """Main function"""
    # Set high DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Viewer Dot Star")
    app.setApplicationDisplayName("Viewer.*")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("DotStar")

    # Create main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
