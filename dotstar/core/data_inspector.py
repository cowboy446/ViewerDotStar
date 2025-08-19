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
from PyQt5.QtCore import Qt, pyqtSignal
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
        self.detail_panel.viz_tab.translator = translator
        
        # Reset UI text
        self.tree_widget.setup_tree()
        # Reset tab titles
        self.detail_panel.setTabText(0, self.translator.tr("overview"))
        self.detail_panel.setTabText(1, self.translator.tr("data"))
        self.detail_panel.setTabText(2, self.translator.tr("statistics"))
        self.detail_panel.setTabText(3, self.translator.tr("visualization"))
        
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
            self.translator.tr("size_shape"), 
            self.translator.tr("description")
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
        """设置数据并构建树形结构"""
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
        """递归构建树形结构"""
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
            for i, value in enumerate(data[:100]):  # Limit display to first 100 elements
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
            if len(data) > 100:
                item = QTreeWidgetItem([f"... ({len(data) - 100} more items)", "", "", ""])
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
        """获取数据大小描述"""
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
        """获取数据描述"""
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
        """获取项目的路径"""
        path = item.data(0, Qt.UserRole)
        return path if path else ""
    
    def get_data_at_path(self, path: str) -> Any:
        """根据路径获取数据"""
        if not path or self.data is None:
            return self.data
            
        try:
            # 解析路径并获取数据
            result = self.data
            parts = path.split('.')
            
            for part in parts:
                if '[' in part and ']' in part:
                    # 处理数组索引
                    key = part.split('[')[0]
                    index_str = part.split('[')[1].split(']')[0]
                    index = int(index_str)
                    
                    if key:
                        result = result[key]
                    result = result[index]
                else:
                    # 处理字典键或属性
                    if isinstance(result, dict):
                        result = result[part]
                    else:
                        result = getattr(result, part)
                        
            return result
        except:
            return None

class DetailPanel(QTabWidget):
    """详细信息面板"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_tabs()
        
    def setup_tabs(self):
        """设置标签页"""
        # 概览标签
        self.overview_tab = OverviewTab(translator=self.translator)
        self.addTab(self.overview_tab, self.translator.tr("overview"))
        
        # 数据标签
        self.data_tab = DataTab(translator=self.translator)
        self.addTab(self.data_tab, self.translator.tr("data"))
        
        # 统计标签
        self.stats_tab = StatisticsTab(translator=self.translator)
        self.addTab(self.stats_tab, self.translator.tr("statistics"))
        
        # 可视化标签
        self.viz_tab = VisualizationTab(translator=self.translator)
        self.addTab(self.viz_tab, self.translator.tr("visualization"))
        
    def show_overview(self, data: Any, metadata: Dict[str, Any]):
        """显示数据概览"""
        self.overview_tab.set_data(data, metadata)
        self.setCurrentIndex(0)  # 切换到概览标签
        
    def show_data_detail(self, data: Any, path: str):
        """显示数据详情"""
        self.data_tab.set_data(data, path)
        self.stats_tab.set_data(data, path)
        self.viz_tab.set_data(data, path)

class OverviewTab(QWidget):
    """概览标签页"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 文件信息区域
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
        """设置数据"""
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
        """格式化文件大小"""
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
            if len(data) <= 10:
                lines.append(f"Keys: {list(data.keys())}")
            else:
                lines.append(f"First 10 Keys: {list(data.keys())[:10]}")
                
        elif isinstance(data, (list, tuple)):
            lines.append(f"Element Count: {len(data)}")
            if len(data) > 0:
                first_type = type(data[0]).__name__
                lines.append(f"First Element Type: {first_type}")
                
        return "\n".join(lines)
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """格式化元数据"""
        lines = []
        for key, value in metadata.items():
            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                lines.append(f"{key}: {type(value).__name__} (Too long, omitted)")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

class DataTab(QWidget):
    """数据标签页"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.current_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 控制面板
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems([
            self.translator.tr("text_view"), 
            self.translator.tr("table_view"), 
            self.translator.tr("raw_data")
        ])
        self.view_mode_combo.currentTextChanged.connect(self.update_view)
        control_layout.addWidget(QLabel(self.translator.tr("view_mode") + ":"))
        control_layout.addWidget(self.view_mode_combo)
        
        control_layout.addStretch()
        layout.addWidget(control_frame)
        
        # 数据显示区域
        self.data_display = QTabWidget()
        layout.addWidget(self.data_display)
        
    def set_data(self, data: Any, path: str):
        """设置数据"""
        self.current_data = data
        self.update_view()
        
    def update_view(self):
        """更新视图"""
        if self.current_data is None:
            return
            
        # 清除现有标签
        self.data_display.clear()
        
        mode = self.view_mode_combo.currentText()
        
        if mode == self.translator.tr("text_view"):
            self._show_text_view()
        elif mode == self.translator.tr("table_view"):
            self._show_table_view()
        elif mode == self.translator.tr("raw_data"):
            self._show_raw_view()
            
    def _show_text_view(self):
        """显示文本视图"""
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setFont(QFont("Consolas", 9))
        
        # Format data as text
        text_content = self._format_data_as_text(self.current_data)
        text_widget.setText(text_content)
        
        self.data_display.addTab(text_widget, self.translator.tr("text"))
        
    def _show_table_view(self):
        """显示表格视图"""
        if hasattr(self.current_data, 'shape') and len(self.current_data.shape) <= 2:
            # Display as table
            table = QTableWidget()
            self._populate_table(table, self.current_data)
            self.data_display.addTab(table, self.translator.tr("table"))
        else:
            # Not suitable for table display
            label = QLabel("This data is not suitable for table display")
            label.setAlignment(Qt.AlignCenter)
            self.data_display.addTab(label, self.translator.tr("table"))
            
    def _show_raw_view(self):
        """显示原始数据视图"""
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setFont(QFont("Consolas", 8))
        
        # Display raw data
        raw_text = repr(self.current_data)
        if len(raw_text) > 50000:
            raw_text = raw_text[:50000] + "\n... (Data too long, truncated)"
        text_widget.setText(raw_text)
        
        self.data_display.addTab(text_widget, self.translator.tr("raw"))
    
    def _format_data_as_text(self, data: Any) -> str:
        """将数据格式化为文本"""
        if hasattr(data, 'shape'):
            # NumPy array or similar objects
            if len(data.shape) == 1:
                return str(data)
            elif len(data.shape) == 2:
                return str(data)
            else:
                return f"Multi-dimensional array {data.shape}:\n{str(data)[:1000]}..."
        elif isinstance(data, dict):
            lines = []
            for key, value in data.items():
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                lines.append(f"{key}: {value_str}")
            return "\n".join(lines)
        elif isinstance(data, (list, tuple)):
            if len(data) <= 100:
                return str(data)
            else:
                return str(data[:100]) + f"\n... ({len(data) - 100} more items)"
        else:
            return str(data)
    
    def _populate_table(self, table: QTableWidget, data: Any):
        """填充表格数据"""
        if hasattr(data, 'shape'):
            if len(data.shape) == 1:
                # One-dimensional array
                table.setRowCount(len(data))
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(["Value"])
                
                for i, value in enumerate(data):
                    item = QTableWidgetItem(str(value))
                    table.setItem(i, 0, item)
                    
            elif len(data.shape) == 2:
                # Two-dimensional array
                rows, cols = data.shape
                table.setRowCount(min(rows, 1000))  # Limit display rows
                table.setColumnCount(min(cols, 100))  # Limit display columns
                
                for i in range(min(rows, 1000)):
                    for j in range(min(cols, 100)):
                        item = QTableWidgetItem(str(data[i, j]))
                        table.setItem(i, j, item)

class StatisticsTab(QWidget):
    """统计标签页"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
    def set_data(self, data: Any, path: str):
        """设置数据并计算统计信息"""
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
                lines.append(f"Keys: {list(data.keys())[:10]}")
                
            elif isinstance(data, (list, tuple)):
                lines.append(f"Element Count: {len(data)}")
                if data:
                    element_types = set(type(x).__name__ for x in data[:100])
                    lines.append(f"Element Types: {', '.join(element_types)}")
                    
            elif isinstance(data, str):
                lines.append(f"String Length: {len(data)}")
                lines.append(f"Content Preview: {data[:100]}...")
                
        except Exception as e:
            lines.append(f"Statistics Calculation Error: {str(e)}")
            
        return "\n".join(lines)

class VisualizationTab(QWidget):
    """可视化标签页"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 控制面板
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        self.viz_type_combo = QComboBox()
        self.viz_type_combo.addItems([
            self.translator.tr("auto_select"),
            self.translator.tr("histogram"),
            self.translator.tr("scatter_plot"),
            self.translator.tr("line_plot"),
            self.translator.tr("heatmap")
        ])
        control_layout.addWidget(QLabel(self.translator.tr("visualization_type") + ":"))
        control_layout.addWidget(self.viz_type_combo)
        
        self.generate_btn = QPushButton(self.translator.tr("generate_chart"))
        self.generate_btn.clicked.connect(self.generate_visualization)
        control_layout.addWidget(self.generate_btn)
        
        control_layout.addStretch()
        layout.addWidget(control_frame)
        
        # Visualization display area
        self.viz_label = QLabel("Select data and click generate chart")
        self.viz_label.setAlignment(Qt.AlignCenter)
        self.viz_label.setMinimumHeight(400)
        self.viz_label.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(self.viz_label)
        
        self.current_data = None
        
    def set_data(self, data: Any, path: str):
        """设置数据"""
        self.current_data = data
        
    def generate_visualization(self):
        """Generate visualization"""
        if self.current_data is None:
            self.viz_label.setText("No data to visualize")
            return
            
        try:
            # matplotlib should be used here to generate charts
            # For simplicity, display text information for now
            viz_info = self._analyze_visualization_potential(self.current_data)
            self.viz_label.setText(viz_info)
        except Exception as e:
            self.viz_label.setText(f"Visualization generation failed: {str(e)}")
            
    def _analyze_visualization_potential(self, data: Any) -> str:
        """Analyze visualization potential"""
        if hasattr(data, 'shape'):
            if len(data.shape) == 1:
                return f"One-dimensional data, can draw histogram or line plot\nData shape: {data.shape}"
            elif len(data.shape) == 2:
                return f"Two-dimensional data, can draw heatmap or scatter plot\nData shape: {data.shape}"
            else:
                return f"Multi-dimensional data, needs dimensionality reduction for visualization\nData shape: {data.shape}"
        else:
            return f"Data type {type(data).__name__} does not support direct visualization"
