"""
Data Inspector Module
Provides data structure analysis, hierarchical display and detailed information viewing functions
"""

from typing import Any, Dict, List, Tuple, Optional, Union
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QTextEdit, QSplitter, QTabWidget,
                            QTableWidget, QTableWidgetItem, QLabel, QGroupBox,
                            QScrollArea, QPushButton, QComboBox, QSpinBox,
                            QCheckBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from .translator import Translator

class DataInspector(QWidget):
    """Data Inspector Main Interface"""
    
    dataChanged = pyqtSignal(object, dict)  # Data change signal
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.current_data = None
        self.current_metadata = {}
        self.translator = translator or Translator()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up user interface"""
        layout = QVBoxLayout(self)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left side: hierarchy structure tree
        self.tree_widget = DataTreeWidget(translator=self.translator)
        tree_group = QGroupBox(self.translator.tr("data_structure"))
        tree_layout = QVBoxLayout(tree_group)
        tree_layout.addWidget(self.tree_widget)
        main_splitter.addWidget(tree_group)
        
        # Right side: detailed information panel
        self.detail_panel = DetailPanel(translator=self.translator)
        main_splitter.addWidget(self.detail_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([700, 300])
        
        # Connect signals
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
    def update_language(self, translator):
        """Update interface language"""
        self.translator = translator
        # Update translator for all components
        self.tree_widget.translator = translator
        self.detail_panel.translator = translator
        self.detail_panel.overview_tab.translator = translator
        self.detail_panel.data_tab.translator = translator
        self.detail_panel.stats_tab.translator = translator
        
        # Reset UI text
        self.tree_widget.setup_tree()
        # Reset tab titles
        self.detail_panel.setTabText(0, self.translator.tr("overview"))
        self.detail_panel.setTabText(1, self.translator.tr("data"))
        self.detail_panel.setTabText(2, self.translator.tr("statistics"))
        
    def set_data(self, data: Any, metadata: Dict[str, Any]):
        """Set data to inspect"""
        self.current_data = data
        self.current_metadata = metadata
        
        # Update tree structure
        self.tree_widget.set_data(data, metadata)
        
        # Update detailed information panel
        self.detail_panel.show_overview(data, metadata)
        
        # Emit signal
        self.dataChanged.emit(data, metadata)
        
    def on_selection_changed(self):
        """Handle selection change"""
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            data_path = self.tree_widget.get_item_path(item)
            selected_data = self.tree_widget.get_data_at_path(data_path)
            self.detail_panel.show_data_detail(selected_data, data_path)

class DataTreeWidget(QTreeWidget):
    """Data structure tree display component"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.data = None
        self.metadata = {}
        self.translator = translator or Translator()
        self.setup_tree()
        
    def setup_tree(self):
        """Set up tree component"""
        self.setHeaderLabels([
            self.translator.tr("name"), 
            self.translator.tr("type"), 
            self.translator.tr("size shape"), 
            self.translator.tr("data description")
        ])
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 120)
        
        # Set font
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(9)
        self.setFont(font)
        
    def set_data(self, data: Any, metadata: Dict[str, Any]):
        """Set data and build tree structure"""
        self.data = data
        self.metadata = metadata
        self.clear()
        
        # Create root node
        root_item = QTreeWidgetItem(['Data Root Node', 
                                   type(data).__name__,
                                   self._get_size_description(data),
                                   metadata.get('file_format', '')])
        self.addTopLevelItem(root_item)
        
        # Recursively build tree
        self._build_tree_recursive(root_item, data, '')
        
        # Expand first level
        root_item.setExpanded(True)
        
    def _build_tree_recursive(self, parent_item: QTreeWidgetItem, data: Any, path: str, max_depth: int = 5):
        """Recursively build tree structure"""
        if max_depth <= 0:
            return
            
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                item = QTreeWidgetItem([
                    str(key),
                    type(value).__name__,
                    self._get_size_description(value),
                    self._get_description(value)
                ])
                item.setData(0, Qt.UserRole, current_path)
                parent_item.addChild(item)
                
                # Recursively handle child items
                if isinstance(value, (dict, list, tuple)) and len(str(value)) < 10000:
                    self._build_tree_recursive(item, value, current_path, max_depth - 1)
                    
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data[:10]):  # Limit display to first 10 elements
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                item = QTreeWidgetItem([
                    f"[{i}]",
                    type(value).__name__,
                    self._get_size_description(value),
                    self._get_description(value)
                ])
                item.setData(0, Qt.UserRole, current_path)
                parent_item.addChild(item)
                
                # Recursively handle child items
                if isinstance(value, (dict, list, tuple)) and len(str(value)) < 10000:
                    self._build_tree_recursive(item, value, current_path, max_depth - 1)
                    
            # If list is too long, add ellipsis
            if len(data) > 10:
                item = QTreeWidgetItem([f"... ({len(data) - 10} more items)", "", "", ""])
                parent_item.addChild(item)
                
        elif hasattr(data, '__dict__'):
            # Handle object attributes
            for attr_name in dir(data):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(data, attr_name)
                        if not callable(attr_value):
                            current_path = f"{path}.{attr_name}" if path else attr_name
                            item = QTreeWidgetItem([
                                attr_name,
                                type(attr_value).__name__,
                                self._get_size_description(attr_value),
                                self._get_description(attr_value)
                            ])
                            item.setData(0, Qt.UserRole, current_path)
                            parent_item.addChild(item)
                    except:
                        continue
                        
    def _get_size_description(self, data: Any) -> str:
        """Get data size description"""
        if hasattr(data, 'shape'):
            return str(data.shape)
        elif hasattr(data, '__len__'):
            try:
                length = len(data)
                return f"Length: {length}"
            except:
                pass
        elif hasattr(data, 'size'):
            return f"Size: {data.size}"
        
        return ""
    
    def _get_description(self, data: Any) -> str:
        """Get data description"""
        if hasattr(data, 'dtype'):
            return str(data.dtype)
        elif isinstance(data, (int, float)):
            return str(data)[:50]
        elif isinstance(data, str):
            return f'"{data[:30]}..."' if len(data) > 30 else f'"{data}"'
        elif isinstance(data, (list, tuple)):
            return f"{len(data)} items"
        elif isinstance(data, dict):
            return f"{len(data)} keys"
        
        return ""
    
    def get_item_path(self, item: QTreeWidgetItem) -> str:
        """Get item path"""
        path = item.data(0, Qt.UserRole)
        return path if path else ""
    
    def get_data_at_path(self, path: str) -> Any:
        """Get data at specified path"""
        if not path or self.data is None:
            return self.data
            
        try:
            # Parse path and get data
            result = self.data
            parts = path.split('.')
            
            for part in parts:
                if '[' in part and ']' in part:
                    # Handle array index
                    key = part.split('[')[0]
                    index_str = part.split('[')[1].split(']')[0]
                    index = int(index_str)
                    
                    if key:
                        result = result[key]
                    result = result[index]
                else:
                    # Handle dictionary keys or attributes
                    if isinstance(result, dict):
                        result = result[part]
                    else:
                        result = getattr(result, part)
                        
            return result
        except:
            return None

class DetailPanel(QTabWidget):
    """Detail information panel"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_tabs()
        
    def setup_tabs(self):
        """Setup tab pages"""
        # Overview tab
        self.overview_tab = OverviewTab(translator=self.translator)
        self.addTab(self.overview_tab, self.translator.tr("overview"))
        
        # Data tab
        self.data_tab = DataTab(translator=self.translator)
        self.addTab(self.data_tab, self.translator.tr("data"))
        
        # Statistics tab
        self.stats_tab = StatisticsTab(translator=self.translator)
        self.addTab(self.stats_tab, self.translator.tr("statistics"))
        
    def show_overview(self, data: Any, metadata: Dict[str, Any]):
        """Show data overview"""
        self.overview_tab.set_data(data, metadata)
        self.setCurrentIndex(0)  # Switch to overview tab
        
    def show_data_detail(self, data: Any, path: str):
        """Show data details"""
        self.data_tab.set_data(data, path)
        self.stats_tab.set_data(data, path)

class OverviewTab(QWidget):
    """Overview tab page"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup interface"""
        layout = QVBoxLayout(self)
        
        # File information area
        file_group = QGroupBox(self.translator.tr("file_information"))
        file_layout = QVBoxLayout(file_group)
        self.file_info_label = QLabel()
        self.file_info_label.setWordWrap(True)
        file_layout.addWidget(self.file_info_label)
        layout.addWidget(file_group)
        
        # Data structure area
        structure_group = QGroupBox("Data Structure")
        structure_layout = QVBoxLayout(structure_group)
        self.structure_text = QTextEdit()
        self.structure_text.setReadOnly(True)
        self.structure_text.setMaximumHeight(200)
        structure_layout.addWidget(self.structure_text)
        layout.addWidget(structure_group)
        
        # Metadata area
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QVBoxLayout(metadata_group)
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        metadata_layout.addWidget(self.metadata_text)
        layout.addWidget(metadata_group)
        
    def set_data(self, data: Any, metadata: Dict[str, Any]):
        """Set data"""
        # Display file information
        file_info = f"""
        <b>File Name:</b> {metadata.get('file_name', 'N/A')}<br>
        <b>Format:</b> {metadata.get('file_format', 'N/A')}<br>
        <b>Size:</b> {self._format_file_size(metadata.get('file_size', 0))}<br>
        <b>Path:</b> {metadata.get('file_path', 'N/A')}
        """
        self.file_info_label.setText(file_info)
        
        # Display data structure
        structure_info = self._analyze_structure(data)
        self.structure_text.setText(structure_info)
        
        # Display metadata
        metadata_text = self._format_metadata(metadata)
        self.metadata_text.setText(metadata_text)
        
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _analyze_structure(self, data: Any) -> str:
        """Analyze data structure"""
        lines = []
        lines.append(f"Data Type: {type(data).__name__}")
        
        if hasattr(data, 'shape'):
            lines.append(f"Shape: {data.shape}")
        if hasattr(data, 'dtype'):
            lines.append(f"Data Type: {data.dtype}")
        if hasattr(data, 'size'):
            lines.append(f"Element Count: {data.size}")
        if hasattr(data, '__len__'):
            try:
                lines.append(f"Length: {len(data)}")
            except:
                pass
                
        if isinstance(data, dict):
            lines.append(f"Key Count: {len(data)}")
            lines.append(f"Keys: {list(data.keys())}")
                
        elif isinstance(data, (list, tuple)):
            lines.append(f"Element Count: {len(data)}")
            if len(data) > 0:
                first_type = type(data[0]).__name__
                lines.append(f"First Element Type: {first_type}")
                
        return "\n".join(lines)
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata"""
        lines = []
        for key, value in metadata.items():
            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                lines.append(f"{key}: {type(value).__name__} (Too long, omitted)")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

class DataTab(QWidget):
    """Data tab page"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.current_data = None
        self.current_path = ""
        self.data_stack = []  # Data navigation stack
        self.display_cache = {}  # Add display cache
        self.click_timer = QTimer()  # Double click timer
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._handle_single_click)
        self.last_clicked_item = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup interface"""
        layout = QVBoxLayout(self)
        
        # Navigation bar
        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        self.path_label = QLabel("Root")
        self.path_label.setStyleSheet("color: #888888;")  # Change to gray
        nav_layout.addWidget(self.path_label)
        
        nav_layout.addStretch()
        layout.addWidget(nav_frame)
        
        # Data display area - show tabs directly
        self.data_display = QTabWidget()
        layout.addWidget(self.data_display)
        
    def set_data(self, data: Any, path: str):
        """Set data"""
        self.current_data = data
        self.current_path = path
        # Clear cache
        self.display_cache.clear()
        self.update_view()
        
    def go_back(self):
        """Go back to previous level data"""
        if self.data_stack:
            data, path = self.data_stack.pop()
            self.current_data = data
            self.current_path = path
            self.display_cache.clear()
            self.update_view()
            
            if not self.data_stack:
                self.back_btn.setEnabled(False)
                
    def push_data(self, data: Any, path: str):
        """Push new data to stack"""
        self.data_stack.append((self.current_data, self.current_path))
        self.current_data = data
        self.current_path = path
        self.display_cache.clear()
        self.update_view()
        self.back_btn.setEnabled(True)
        
    def update_view(self):
        """Update view"""
        if self.current_data is None:
            return
            
        # Update path display
        display_path = self.current_path if self.current_path else "Root"
        self.path_label.setText(display_path)
            
        # Clear existing tabs
        self.data_display.clear()
        
        # Show all three views as tabs
        self._show_raw_view()
        self._show_text_view()
        self._show_table_view()
            
    def _show_text_view(self):
        """Show text view - use cache and limits"""
        # 检查缓存
        if 'text_view' in self.display_cache:
            text_widget = QTextEdit()
            text_widget.setReadOnly(True)
            text_widget.setFont(QFont("Consolas", 9))
            text_widget.setText(self.display_cache['text_view'])
            self.data_display.addTab(text_widget, "Text View")
            return
            
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setFont(QFont("Consolas", 9))
        
        # Limit processing data size
        text_content = self._format_data_as_text_safe(self.current_data)
        self.display_cache['text_view'] = text_content
        text_widget.setText(text_content)
        
        self.data_display.addTab(text_widget, "Text View")
        
    def _show_table_view(self):
        """Show table view - support recursive expansion and double-click navigation"""
        if hasattr(self.current_data, 'shape'):
            # Display as table with navigation support
            table = QTableWidget()
            self._populate_table_recursive(table, self.current_data, self.current_path)
            table.itemClicked.connect(self._on_table_item_clicked)
            table.itemDoubleClicked.connect(self._on_table_item_double_clicked)
            self.data_display.addTab(table, "Table View")
        elif isinstance(self.current_data, dict):
            # Display dictionary as table
            table = QTableWidget()
            self._populate_dict_table(table, self.current_data, self.current_path)
            table.itemClicked.connect(self._on_table_item_clicked)
            table.itemDoubleClicked.connect(self._on_table_item_double_clicked)
            self.data_display.addTab(table, "Table View")
        elif isinstance(self.current_data, (list, tuple)):
            # Display list/tuple as table
            table = QTableWidget()
            self._populate_list_table(table, self.current_data, self.current_path)
            table.itemClicked.connect(self._on_table_item_clicked)
            table.itemDoubleClicked.connect(self._on_table_item_double_clicked)
            self.data_display.addTab(table, "Table View")
        else:
            # Not suitable for table display
            label = QLabel("This data is not suitable for table display")
            label.setAlignment(Qt.AlignCenter)
            self.data_display.addTab(label, "Table View")
            
    def _show_raw_view(self):
        """Show raw data view - use cache and truncation"""
        # 检查缓存
        if 'raw_view' in self.display_cache:
            text_widget = QTextEdit()
            text_widget.setReadOnly(True)
            text_widget.setFont(QFont("Consolas", 8))
            text_widget.setText(self.display_cache['raw_view'])
            self.data_display.addTab(text_widget, "Raw Data")
            return
            
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setFont(QFont("Consolas", 8))
        
        # 智能截断大数据
        raw_text = self._get_raw_text_safe(self.current_data)
        self.display_cache['raw_view'] = raw_text
        text_widget.setText(raw_text)
        
        self.data_display.addTab(text_widget, "Raw Data")
    
    def _get_raw_text_safe(self, data: Any, max_chars: int = 10000) -> str:
        """Safely get raw text, avoid freezing with large data"""
        try:
            # 检查是否是数组且元素数量大于100
            if hasattr(data, 'shape'):
                try:
                    # 安全获取size属性 - 支持PyTorch张量和NumPy数组
                    if hasattr(data, 'numel'):  # PyTorch tensors
                        size = data.numel()
                    elif hasattr(data, 'size'):
                        size = data.size() if callable(data.size) else data.size
                    else:
                        # 根据shape计算元素数量
                        size = np.prod(data.shape)
                        
                    if size > 100:
                        # 大数组只显示形状和部分数据
                        try:
                            if hasattr(data, 'flat'):
                                preview = data.flat[:10]
                            elif hasattr(data, 'flatten'):
                                preview = data.flatten()[:10]
                            else:
                                # 对于PyTorch张量或其他类型
                                if len(data.shape) == 1:
                                    preview = data[:10]
                                else:
                                    preview = data.view(-1)[:10]  # PyTorch style flatten
                            
                            # 转换为字符串
                            if hasattr(preview, 'numpy'):
                                preview_str = str(preview.numpy())
                            else:
                                preview_str = str(preview)
                                
                            return f"Large array {data.shape}:\nFirst 10 elements: {preview_str}\n... (truncated for performance)"
                        except:
                            # 如果无法获取预览，尝试其他方法
                            try:
                                # 尝试简单的切片访问
                                if len(data.shape) == 1:
                                    preview = data[:10]
                                elif len(data.shape) == 2:
                                    preview = data[:5, :5]  # 显示5x5的小块
                                else:
                                    # 多维数组，尝试获取一个小的切片
                                    slices = [slice(0, min(3, s)) for s in data.shape[:3]]
                                    preview = data[tuple(slices)]
                                
                                # 转换为字符串
                                if hasattr(preview, 'numpy'):
                                    preview_str = str(preview.numpy())
                                elif hasattr(preview, 'tolist'):
                                    preview_str = str(preview.tolist())
                                else:
                                    preview_str = str(preview)
                                    
                                return f"Large array {data.shape}:\nSample data: {preview_str}\n... (truncated for performance)"
                            except:
                                return f"Large array {data.shape}:\nData type: {type(data)}\nToo large to preview safely"
                except Exception as e:
                    return f"Array shape {data.shape}:\nError getting size: {str(e)}"
            
            # 小数据直接转换
            raw_text = repr(data)
            if len(raw_text) > max_chars:
                return raw_text[:max_chars] + "\n... (truncated for performance)"
            return raw_text
        except Exception as e:
            return f"Unable to display raw data: {str(e)}\nData type: {type(data)}"
    
    def _format_data_as_text_safe(self, data: Any, max_elements: int = 100) -> str:
        """Safely format data as text"""
        try:
            if hasattr(data, 'shape'):
                # NumPy array or PyTorch tensor or similar objects
                try:
                    # 获取元素总数 - 支持不同类型的size属性
                    if hasattr(data, 'numel'):  # PyTorch tensors
                        size = data.numel()
                    elif hasattr(data, 'size'):
                        size = data.size() if callable(data.size) else data.size
                    else:
                        # 根据shape计算元素数量
                        size = np.prod(data.shape)
                        
                    if size > max_elements:
                        if len(data.shape) == 1:
                            # 一维数据，显示前10个元素
                            try:
                                preview = data[:10]
                                # 转换为字符串，处理PyTorch张量
                                if hasattr(preview, 'numpy'):
                                    preview_str = str(preview.numpy())
                                else:
                                    preview_str = str(preview)
                                return f"Array shape {data.shape}:\n{preview_str}\n... (showing first 10 of {size} elements)"
                            except:
                                return f"1D Array shape {data.shape}:\nFirst 10 elements: [data access error]\n... (showing first 10 of {size} elements)"
                        elif len(data.shape) == 2:
                            # 二维数据，显示前10x10
                            try:
                                rows, cols = min(10, data.shape[0]), min(10, data.shape[1])
                                preview = data[:rows, :cols]
                                if hasattr(preview, 'numpy'):
                                    preview_str = str(preview.numpy())
                                else:
                                    preview_str = str(preview)
                                return f"Array shape {data.shape}:\n{preview_str}\n... (showing first {rows}x{cols} of {data.shape[0]}x{data.shape[1]} elements)"
                            except:
                                return f"2D Array shape {data.shape}:\nFirst 10x10 elements: [data access error]\n... (showing partial data)"
                        else:
                            return f"Multi-dimensional array {data.shape}:\nToo large to display, use Raw Data tab for details"
                    else:
                        # 小数据，直接显示
                        try:
                            if hasattr(data, 'numpy'):
                                return str(data.numpy())
                            else:
                                return str(data)
                        except:
                            return f"Array shape {data.shape}:\n[Unable to convert to string safely]"
                except Exception as e:
                    # 如果出错，返回基本信息和错误详情
                    return f"Array shape {data.shape}:\nError processing data: {str(e)}\nData type: {type(data)}"
            elif isinstance(data, dict):
                lines = []
                for key, value in data.items():
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    lines.append(f"{key}: {value_str}")
                return "\n".join(lines)
            elif isinstance(data, (list, tuple)):
                if len(data) > max_elements:
                    preview = data[:10]
                    return f"{str(preview)}\n... (showing first 10 of {len(data)} items)"
                else:
                    return str(data)
            else:
                text = str(data)
                if len(text) > 10000:
                    return text[:10000] + "\n... (truncated for performance)"
                return text
        except Exception as e:
            return f"Unable to format data: {str(e)}\nData type: {type(data)}"
    
    def _populate_table_recursive(self, table: QTableWidget, data: Any, path: str):
        """Recursively populate table data, support full expansion of multi-dimensional arrays"""
        if hasattr(data, 'shape'):
            if len(data.shape) == 1:
                # 一维数组 - 横向展示，每个格子一个值
                cols = min(len(data), 100)  # 限制最大列数防止卡顿
                table.setRowCount(1)
                table.setColumnCount(cols)
                
                # 设置列标题
                col_headers = [f"[{i}]" for i in range(cols)]
                table.setHorizontalHeaderLabels(col_headers)
                
                for i in range(cols):
                    try:
                        value = data[i]
                        if hasattr(value, 'shape') and len(value.shape) > 0:
                            # 如果元素本身是数组，显示形状和类型
                            item_text = f"Array{value.shape}"
                            item = QTableWidgetItem(item_text)
                            item.setData(Qt.UserRole, ('navigate', value, f"{path}[{i}]"))
                            item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
                        else:
                            # 标量值 - 直接显示数值
                            item = QTableWidgetItem(str(value))
                            item.setData(Qt.UserRole, ('value', value, f"{path}[{i}]"))
                        table.setItem(0, i, item)
                    except Exception as e:
                        item = QTableWidgetItem(f"Error: {str(e)}")
                        table.setItem(0, i, item)
                
                if len(data) > 100:
                    # 添加省略信息到最后一列
                    table.setColumnCount(cols + 1)
                    item = QTableWidgetItem(f"...({len(data) - 100} more)")
                    table.setItem(0, cols, item)
                    
            elif len(data.shape) == 2:
                # 二维数组
                max_rows = min(data.shape[0], 500)
                max_cols = min(data.shape[1], 50)
                table.setRowCount(max_rows)
                table.setColumnCount(max_cols)
                
                # 设置列标题
                col_headers = [f"Col_{i}" for i in range(max_cols)]
                table.setHorizontalHeaderLabels(col_headers)
                
                for i in range(max_rows):
                    for j in range(max_cols):
                        try:
                            value = data[i, j]
                            if hasattr(value, 'shape') and len(value.shape) > 0:
                                # 元素是数组
                                item_text = f"Array {value.shape}"
                                item = QTableWidgetItem(item_text)
                                item.setData(Qt.UserRole, ('navigate', value, f"{path}[{i},{j}]"))
                                item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
                            else:
                                # 标量值
                                item = QTableWidgetItem(str(value))
                                item.setData(Qt.UserRole, ('value', value, f"{path}[{i},{j}]"))
                            table.setItem(i, j, item)
                        except Exception as e:
                            item = QTableWidgetItem("Error")
                            table.setItem(i, j, item)
                
                if data.shape[0] > 500 or data.shape[1] > 50:
                    table.setWindowTitle(f"Showing {max_rows}×{max_cols} of {data.shape[0]}×{data.shape[1]}")
                    
            else:
                # 高维数组，展示为可导航的层次结构
                if len(data.shape) > 2:
                    rows = min(data.shape[0], 100)
                    table.setRowCount(rows)
                    table.setColumnCount(1)
                    table.setHorizontalHeaderLabels([f"Dimension 0 (of {data.shape})"])
                    
                    for i in range(rows):
                        try:
                            sub_data = data[i]
                            item_text = f"[{i}] → Array {sub_data.shape} ({type(sub_data).__name__})"
                            item = QTableWidgetItem(item_text)
                            item.setData(Qt.UserRole, ('navigate', sub_data, f"{path}[{i}]"))
                            item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
                            table.setItem(i, 0, item)
                        except Exception as e:
                            item = QTableWidgetItem(f"Error: {str(e)}")
                            table.setItem(i, 0, item)
                            
                    if data.shape[0] > 100:
                        table.setRowCount(rows + 1)
                        item = QTableWidgetItem(f"... ({data.shape[0] - 100} more items hidden)")
                        table.setItem(rows, 0, item)

    def _populate_dict_table(self, table: QTableWidget, data: dict, path: str):
        """Populate dictionary data as table"""
        table.setRowCount(len(data))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Key", "Value"])
        
        for i, (key, value) in enumerate(data.items()):
            # 键列
            key_item = QTableWidgetItem(str(key))
            table.setItem(i, 0, key_item)
            
            # 值列
            if hasattr(value, 'shape') and len(value.shape) > 0:
                # 数组值
                value_text = f"Array {value.shape} ({type(value).__name__})"
                value_item = QTableWidgetItem(value_text)
                value_item.setData(Qt.UserRole, ('navigate', value, f"{path}.{key}"))
                value_item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
            elif isinstance(value, (dict, list, tuple)) and len(str(value)) > 100:
                # 复杂结构
                value_text = f"{type(value).__name__} (len={len(value)})"
                value_item = QTableWidgetItem(value_text)
                value_item.setData(Qt.UserRole, ('navigate', value, f"{path}.{key}"))
                value_item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
            else:
                # 简单值
                value_text = str(value)
                if len(value_text) > 100:
                    value_text = value_text[:100] + "..."
                value_item = QTableWidgetItem(value_text)
                value_item.setData(Qt.UserRole, ('value', value, f"{path}.{key}"))
            
            table.setItem(i, 1, value_item)

    def _populate_list_table(self, table: QTableWidget, data: list, path: str):
        """Populate list data as table"""
        max_items = min(len(data), 1000)
        table.setRowCount(max_items)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Index", "Value"])
        
        for i in range(max_items):
            # 索引列
            index_item = QTableWidgetItem(str(i))
            table.setItem(i, 0, index_item)
            
            # 值列
            value = data[i]
            if hasattr(value, 'shape') and len(value.shape) > 0:
                # 数组值
                value_text = f"Array {value.shape} ({type(value).__name__})"
                value_item = QTableWidgetItem(value_text)
                value_item.setData(Qt.UserRole, ('navigate', value, f"{path}[{i}]"))
                value_item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
            elif isinstance(value, (dict, list, tuple)) and len(str(value)) > 100:
                # 复杂结构
                value_text = f"{type(value).__name__} (len={len(value)})"
                value_item = QTableWidgetItem(value_text)
                value_item.setData(Qt.UserRole, ('navigate', value, f"{path}[{i}]"))
                value_item.setBackground(QColor(200, 200, 200))  # 改为灰色背景
            else:
                # 简单值
                value_text = str(value)
                if len(value_text) > 100:
                    value_text = value_text[:100] + "..."
                value_item = QTableWidgetItem(value_text)
                value_item.setData(Qt.UserRole, ('value', value, f"{path}[{i}]"))
            
            table.setItem(i, 1, value_item)
            
        if len(data) > 1000:
            table.setRowCount(max_items + 1)
            item = QTableWidgetItem(f"... ({len(data) - 1000} more items hidden)")
            table.setItem(max_items, 1, item)

    def _on_table_item_clicked(self, item: QTableWidgetItem):
        """Handle table cell click event - delayed processing to distinguish single and double clicks"""
        self.last_clicked_item = item
        self.click_timer.start(300)  # 300ms delay
        
    def _handle_single_click(self):
        """Handle single click event - only show information, no navigation"""
        if self.last_clicked_item:
            user_data = self.last_clicked_item.data(Qt.UserRole)
            if user_data and len(user_data) == 3:
                action, value, new_path = user_data
                if action == 'navigate':
                    # 单击可导航项目时显示提示
                    print(f"Double-click to navigate to: {new_path}")
                elif action == 'value':
                    # 显示值详情
                    print(f"Value at {new_path}: {value}")

    def _on_table_item_double_clicked(self, item: QTableWidgetItem):
        """Handle table cell double click event - execute navigation"""
        # Stop single click timer
        self.click_timer.stop()
        
        user_data = item.data(Qt.UserRole)
        if user_data and len(user_data) == 3:
            action, value, new_path = user_data
            if action == 'navigate':
                # Navigate to sub data
                self.push_data(value, new_path)
            elif action == 'value':
                # Show detailed information when double-clicking value item
                print(f"Detailed view of value at {new_path}: {value}")

    def _populate_table_safe(self, table: QTableWidget, data: Any):
        """Safely populate table data with size limits (keep original method for compatibility)"""
        if hasattr(data, 'shape'):
            if len(data.shape) == 1:
                # One-dimensional array - limit to 10 rows
                max_rows = min(len(data), 10)
                table.setRowCount(max_rows)
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(["Value"])
                
                for i in range(max_rows):
                    item = QTableWidgetItem(str(data[i]))
                    table.setItem(i, 0, item)
                
                if len(data) > 10:
                    # Add info about truncation
                    table.setRowCount(max_rows + 1)
                    item = QTableWidgetItem(f"... ({len(data) - 10} more rows truncated)")
                    table.setItem(max_rows, 0, item)
                    
            elif len(data.shape) == 2:
                # Two-dimensional array - limit to 10x10
                max_rows = min(data.shape[0], 10)
                max_cols = min(data.shape[1], 10)
                table.setRowCount(max_rows)
                table.setColumnCount(max_cols)
                
                for i in range(max_rows):
                    for j in range(max_cols):
                        try:
                            item = QTableWidgetItem(str(data[i, j]))
                            table.setItem(i, j, item)
                        except:
                            item = QTableWidgetItem("Error")
                            table.setItem(i, j, item)
                
                # Add truncation info if needed
                if data.shape[0] > 10 or data.shape[1] > 10:
                    truncated_info = f"Showing {max_rows}x{max_cols} of {data.shape[0]}x{data.shape[1]}"
                    table.setHorizontalHeaderLabels([f"Col {i}" for i in range(max_cols)] + [truncated_info] if max_cols < data.shape[1] else [f"Col {i}" for i in range(max_cols)])

class StatisticsTab(QWidget):
    """Statistics tab page"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup interface"""
        layout = QVBoxLayout(self)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
    def set_data(self, data: Any, path: str):
        """Set data and calculate statistics"""
        stats_text = self._calculate_statistics(data)
        self.stats_text.setText(stats_text)
        
    def _calculate_statistics(self, data: Any) -> str:
        """Calculate statistics"""
        lines = []
        lines.append(f"Data Type: {type(data).__name__}")
        
        try:
            if hasattr(data, 'shape'):
                lines.append(f"Shape: {data.shape}")
                lines.append(f"Dimensions: {len(data.shape)}")
                lines.append(f"Total Elements: {data.size}")
                
                if hasattr(data, 'dtype'):
                    lines.append(f"Data Type: {data.dtype}")
                
                # Numerical statistics
                if np.issubdtype(data.dtype, np.number):
                    lines.append("\nNumerical Statistics:")
                    lines.append(f"Minimum: {np.min(data)}")
                    lines.append(f"Maximum: {np.max(data)}")
                    lines.append(f"Mean: {np.mean(data)}")
                    lines.append(f"Standard Deviation: {np.std(data)}")
                    lines.append(f"Variance: {np.var(data)}")
                    
                    # Percentiles
                    lines.append(f"25% Percentile: {np.percentile(data, 25)}")
                    lines.append(f"50% Percentile (Median): {np.percentile(data, 50)}")
                    lines.append(f"75% Percentile: {np.percentile(data, 75)}")
                    
            elif isinstance(data, dict):
                lines.append(f"Key Count: {len(data)}")
                lines.append(f"Keys: {list(data.keys())}")
                
            elif isinstance(data, (list, tuple)):
                lines.append(f"Element Count: {len(data)}")
                if data:
                    element_types = set(type(x).__name__ for x in data[:10])
                    lines.append(f"Element Types: {', '.join(element_types)}")
                    
            elif isinstance(data, str):
                lines.append(f"String Length: {len(data)}")
                lines.append(f"Content Preview: {data[:100]}...")
                
        except Exception as e:
            lines.append(f"Statistics Calculation Error: {str(e)}")
            
        return "\n".join(lines)


