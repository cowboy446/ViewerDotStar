"""
Main Window Module
DotStarViewer's main user interface
"""

import os
import sys
from typing import Optional, Any, Dict
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QMenuBar, QMenu, QAction, QToolBar,
                            QStatusBar, QFileDialog, QMessageBox, QLabel,
                            QPushButton, QFrame, QTextEdit, QProgressBar,
                            QGroupBox, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap, QDragEnterEvent, QDropEvent

from .file_loader import FileLoader
from .data_inspector import DataInspector
from .translator import translator

class FileLoadThread(QThread):
    """File loading thread"""
    
    dataLoaded = pyqtSignal(object, dict)  # Data loading completed signal
    errorOccurred = pyqtSignal(str)  # Error signal
    progressChanged = pyqtSignal(int)  # Progress signal
    
    def __init__(self, file_path: str, loader: FileLoader):
        super().__init__()
        self.file_path = file_path
        self.loader = loader
        
    def run(self):
        """Run file loading"""
        try:
            self.progressChanged.emit(30)
            data, metadata = self.loader.load_file(self.file_path)
            self.progressChanged.emit(100)
            self.dataLoaded.emit(data, metadata)
        except Exception as e:
            self.errorOccurred.emit(str(e))

class DropArea(QFrame):
    """Drag and drop area component"""
    
    fileDropped = pyqtSignal(str)  # File drop signal
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up interface"""
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            DropArea:hover {
                border-color: #007acc;
                background-color: #e6f3ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon label
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; color: #666;")
        layout.addWidget(icon_label)
        
        # Hint text
        text_label = QLabel(translator.tr('drag_drop_hint'))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        layout.addWidget(text_label)
        
        # Browse button
        browse_btn = QPushButton(translator.tr('browse_files'))
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """Drop event"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.fileDropped.emit(file_path)
            
    def browse_file(self):
        """Browse file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translator.tr('select_data_file'),
            "",
            translator.tr('all_supported') + " (*.json *.pkl *.npy *.npz *.mat *.h5 *.hdf5 *.csv *.yaml *.yml *.toml *.pt *.pth *.ply *.obj);;" + translator.tr('all_files') + " (*.*)"
        )
        if file_path:
            self.fileDropped.emit(file_path)

class MainWindow(QMainWindow):
    """Main window class"""
    
    def __init__(self):
        super().__init__()
        self.file_loader = FileLoader()
        self.current_data = None
        self.current_metadata = {}
        self.recent_files = []
        self.settings = QSettings("DotStar", "DataViewer")
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
        self.load_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(translator.tr('main_window_title'))
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 左侧面板（文件区域）
        self.left_panel = self.create_left_panel()
        self.main_splitter.addWidget(self.left_panel)
        
        # 右侧面板（数据检查器）
        self.data_inspector = DataInspector()
        self.main_splitter.addWidget(self.data_inspector)
        
        # 设置分割器比例
        self.main_splitter.setSizes([300, 900])
        
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 文件拖放区域
        file_group = QGroupBox(translator.tr('file_loading'))
        file_layout = QVBoxLayout(file_group)
        
        self.drop_area = DropArea()
        self.drop_area.fileDropped.connect(self.load_file)
        file_layout.addWidget(self.drop_area)
        
        layout.addWidget(file_group)
        
        # 文件信息区域
        info_group = QGroupBox(translator.tr('file_info'))
        info_layout = QVBoxLayout(info_group)
        
        self.file_info_label = QLabel(translator.tr('no_file_loaded'))
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        info_layout.addWidget(self.file_info_label)
        
        layout.addWidget(info_group)
        
        # 最近文件区域
        recent_group = QGroupBox(translator.tr('recent_files_panel'))
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_files_widget = QTextEdit()
        self.recent_files_widget.setMaximumHeight(150)
        self.recent_files_widget.setReadOnly(True)
        recent_layout.addWidget(self.recent_files_widget)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        
        return panel
        
    def setup_menus(self):
        """设置菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu(translator.tr('file_menu'))
        
        open_action = QAction(translator.tr('open_file'), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 最近文件子菜单
        self.recent_menu = file_menu.addMenu(translator.tr('recent_files'))
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction(translator.tr('exit'), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu(translator.tr('view_menu'))
        
        toggle_left_action = QAction(translator.tr('toggle_left_panel'), self)
        toggle_left_action.setCheckable(True)
        toggle_left_action.setChecked(True)
        toggle_left_action.triggered.connect(self.toggle_left_panel)
        view_menu.addAction(toggle_left_action)
        
        view_menu.addSeparator()
        
        # 语言子菜单
        language_menu = view_menu.addMenu(translator.tr('language'))
        
        # 英文选项
        en_action = QAction(translator.tr('english'), self)
        en_action.setCheckable(True)
        en_action.setChecked(translator.get_language() == 'en')
        en_action.triggered.connect(lambda: self.change_language('en'))
        language_menu.addAction(en_action)
        
        # 中文选项  
        zh_action = QAction(translator.tr('chinese'), self)
        zh_action.setCheckable(True)
        zh_action.setChecked(translator.get_language() == 'zh')
        zh_action.triggered.connect(lambda: self.change_language('zh'))
        language_menu.addAction(zh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu(translator.tr('help_menu'))
        
        about_action = QAction(translator.tr('about'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = self.addToolBar(translator.tr('main_toolbar'))
        toolbar.setMovable(False)
        
        # 打开文件按钮
        open_action = QAction(translator.tr('open'), self)
        open_action.setToolTip(translator.tr('open_tooltip'))
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # 支持格式按钮
        formats_action = QAction(translator.tr('supported_formats'), self)
        formats_action.setToolTip(translator.tr('formats_tooltip'))
        formats_action.triggered.connect(self.show_supported_formats)
        toolbar.addAction(formats_action)
        
    def setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # 状态标签
        self.status_label = QLabel(translator.tr('ready'))
        self.statusbar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
        
        # 文件格式标签
        self.format_label = QLabel("")
        self.statusbar.addPermanentWidget(self.format_label)
        
    def open_file(self):
        """打开文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translator.tr('select_data_file'),
            "",
            self.file_loader.get_file_filter()
        )
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path: str):
        """加载文件"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, translator.tr('error'), translator.tr('file_not_found', file_path))
            return
            
        if not self.file_loader.is_supported(file_path):
            QMessageBox.warning(self, translator.tr('error'), translator.tr('unsupported_format', file_path))
            return
            
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(translator.tr('loading'))
        
        # 在线程中加载文件
        self.load_thread = FileLoadThread(file_path, self.file_loader)
        self.load_thread.dataLoaded.connect(self.on_data_loaded)
        self.load_thread.errorOccurred.connect(self.on_load_error)
        self.load_thread.progressChanged.connect(self.progress_bar.setValue)
        self.load_thread.start()
        
    def on_data_loaded(self, data: Any, metadata: Dict[str, Any]):
        """数据加载完成"""
        self.current_data = data
        self.current_metadata = metadata
        
        # 更新界面
        self.data_inspector.set_data(data, metadata)
        self.update_file_info(metadata)
        self.add_to_recent_files(metadata['file_path'])
        
        # 更新状态栏
        self.progress_bar.setVisible(False)
        self.status_label.setText(translator.tr('loaded', metadata['file_name']))
        self.format_label.setText(metadata['file_format'])
        
    def on_load_error(self, error_message: str):
        """加载错误"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(translator.tr('load_failed'))
        QMessageBox.critical(self, translator.tr('load_error'), translator.tr('load_error_msg', error_message))
        
    def update_file_info(self, metadata: Dict[str, Any]):
        """更新文件信息显示"""
        info_text = f"""
        <b>{translator.tr('file_name')}:</b> {metadata.get('file_name', 'N/A')}<br>
        <b>{translator.tr('format')}:</b> {metadata.get('file_format', 'N/A')}<br>
        <b>{translator.tr('size')}:</b> {self._format_file_size(metadata.get('file_size', 0))}<br>
        <b>{translator.tr('type')}:</b> {metadata.get('type', 'N/A')}
        """
        self.file_info_label.setText(info_text)
        
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
    def add_to_recent_files(self, file_path: str):
        """添加到最近文件列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        
        # 限制最近文件数量
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
            
        self.update_recent_files_display()
        self.update_recent_menu()
        self.save_settings()
        
    def update_recent_files_display(self):
        """更新最近文件显示"""
        if not self.recent_files:
            self.recent_files_widget.setText(translator.tr('no_recent_files'))
            return
            
        text_lines = []
        for i, file_path in enumerate(self.recent_files, 1):
            file_name = os.path.basename(file_path)
            text_lines.append(f"{i}. {file_name}")
            
        self.recent_files_widget.setText("\n".join(text_lines))
        
    def update_recent_menu(self):
        """更新最近文件菜单"""
        self.recent_menu.clear()
        
        for file_path in self.recent_files:
            file_name = os.path.basename(file_path)
            action = QAction(file_name, self)
            action.setData(file_path)
            action.triggered.connect(lambda checked, path=file_path: self.load_file(path))
            self.recent_menu.addAction(action)
            
        if not self.recent_files:
            no_files_action = QAction(translator.tr('no_recent_files'), self)
            no_files_action.setEnabled(False)
            self.recent_menu.addAction(no_files_action)
            
    def toggle_left_panel(self, checked: bool):
        """切换左侧面板显示"""
        self.left_panel.setVisible(checked)
        
    def show_supported_formats(self):
        """显示支持的文件格式"""
        formats_text = translator.tr('formats_text', "")
        for ext, desc in self.file_loader.SUPPORTED_FORMATS.items():
            formats_text += f"{ext}: {desc}\n"
            
        QMessageBox.information(self, translator.tr('supported_formats_title'), formats_text)
        
    def change_language(self, language_code: str):
        """切换语言"""
        translator.set_language(language_code)
        message = translator.tr('language_changed')
        QMessageBox.information(self, translator.tr('information'), message)
        
    def show_about(self):
        """显示关于对话框"""
        about_text = translator.tr('about_text')
        QMessageBox.about(self, translator.tr('about_title'), about_text)
        
    def load_settings(self):
        """加载设置"""
        # 恢复窗口几何
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # 恢复最近文件
        recent = self.settings.value("recent_files", [])
        if isinstance(recent, list):
            self.recent_files = recent
            self.update_recent_files_display()
            self.update_recent_menu()
            
    def save_settings(self):
        """保存设置"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("recent_files", self.recent_files)
        
    def closeEvent(self, event):
        """关闭事件"""
        self.save_settings()
        event.accept()
