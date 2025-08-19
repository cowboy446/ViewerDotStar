"""
Internationalization Support Module
Provides Chinese and English language switching functionality
"""

import os
import json
from typing import Dict, Any
from PyQt5.QtCore import QSettings

class Translator:
    """Translator Class"""
    
    def __init__(self):
        self.current_language = 'en'  # Default English
        self.translations = {}
        self.settings = QSettings("DotStar", "DataViewer")
        self.load_translations()
        self.load_saved_language()
    
    def load_translations(self):
        """Load translation files"""
        # English translations
        self.translations['en'] = {
            # 主窗口
            'main_window_title': 'DotStar Scientific Data Viewer',
            'file_menu': '&File',
            'view_menu': '&View', 
            'help_menu': '&Help',
            'open_file': '&Open File',
            'recent_files': '&Recent Files',
            'exit': 'E&xit',
            'toggle_left_panel': 'Show/Hide Left Panel',
            'about': '&About',
            'main_toolbar': 'Main Toolbar',
            'open': '📁 Open',
            'open_tooltip': 'Open data file',
            'supported_formats': '📋 Supported Formats',
            'formats_tooltip': 'View supported file formats',
            'ready': 'Ready',
            'loading': 'Loading file...',
            'load_failed': 'Load failed',
            'loaded': 'Loaded: {}',
            
            # 文件相关
            'file_loading': 'File Loading',
            'file_info': 'File Information',
            'recent_files_panel': 'Recent Files',
            'no_recent_files': 'No recent files',
            'drag_drop_hint': 'Drag and drop files here\nor click browse',
            'browse_files': 'Browse Files',
            'select_data_file': 'Select Data File',
            'all_supported': 'All Supported Formats',
            'all_files': 'All Files (*.*)',
            'file_not_found': 'File not found: {}',
            'unsupported_format': 'Unsupported file format: {}',
            'load_error': 'Load Error',
            'load_error_msg': 'Failed to load file:\n{}',
            'no_file_loaded': 'No file loaded',
            
            # 数据检查器
            'data_structure': 'Data Structure',
            'overview': 'Overview',
            'data': 'Data',
            'statistics': 'Statistics', 
            'visualization': 'Visualization',
            'file_name': 'File Name',
            'format': 'Format',
            'size': 'Size',
            'path': 'Path',
            'type': 'Type',
            'data_root': 'Data Root',
            'name': 'Name',
            'shape_size': 'Size/Shape',
            'description': 'Description',
            'length': 'Length: {}',
            'items': '{} items',
            'keys': '{} keys',
            
            # 数据视图
            'view_mode': 'View Mode',
            'text_view': 'Text View',
            'table_view': 'Table View', 
            'raw_data': 'Raw Data',
            'text': 'Text',
            'table': 'Table',
            'raw': 'Raw',
            'not_suitable_table': 'This data is not suitable for table display',
            'data_too_long': '... (Data too long, truncated)',
            'more_items': '... ({} more items)',
            'value': 'Value',
            
            # 统计信息
            'data_type': 'Data Type',
            'shape': 'Shape',
            'dimensions': 'Dimensions',
            'total_elements': 'Total Elements',
            'dtype': 'Data Type',
            'numerical_stats': 'Numerical Statistics',
            'min_value': 'Minimum',
            'max_value': 'Maximum', 
            'mean_value': 'Mean',
            'std_dev': 'Standard Deviation',
            'variance': 'Variance',
            'percentile_25': '25th Percentile',
            'percentile_50': '50th Percentile (Median)',
            'percentile_75': '75th Percentile',
            'num_keys': 'Number of Keys',
            'keys': 'Keys',
            'first_10_keys': 'First 10 Keys',
            'num_elements': 'Number of Elements',
            'first_element_type': 'First Element Type',
            'string_length': 'String Length',
            'content_preview': 'Content Preview',
            'stats_error': 'Statistics calculation error: {}',
            
            # 可视化
            'viz_type': 'Visualization Type',
            'auto_select': 'Auto Select',
            'histogram': 'Histogram',
            'scatter_plot': 'Scatter Plot',
            'line_plot': 'Line Plot',
            'heatmap': 'Heatmap',
            'generate_chart': 'Generate Chart',
            'select_data_generate': 'Select data and click generate chart',
            'no_data_viz': 'No data to visualize',
            'viz_failed': 'Visualization generation failed: {}',
            '1d_data_viz': '1D data, can draw histogram or line plot\nData shape: {}',
            '2d_data_viz': '2D data, can draw heatmap or scatter plot\nData shape: {}',
            'nd_data_viz': 'Multi-dimensional data, needs dimensionality reduction for visualization\nData shape: {}',
            'unsupported_viz': 'Data type {} does not support direct visualization',
            
            # 关于对话框
            'about_title': 'About',
            'about_text': '''
            <h2>DotStar Scientific Data Viewer</h2>
            <p>Version: 0.1.0</p>
            <p>A multi-format data file browser and analysis tool designed for researchers</p>
            <p>Supports JSON, Pickle, NumPy, MATLAB, HDF5, CSV, YAML and many other formats</p>
            <p><b>Development Team:</b> DotStar</p>
            ''',
            
            # 支持格式
            'supported_formats_title': 'Supported File Formats',
            'formats_text': 'Supported file formats:\n\n{}',
            
            # 错误消息
            'error': 'Error',
            'warning': 'Warning',
            'information': 'Information',
            
            # 语言设置
            'language': 'Language',
            'english': 'English',
            'chinese': '中文',
            'language_changed': 'Language changed to English\nRestart application to take effect',
        }
        
        # 中文翻译
        self.translations['zh'] = {
            # 主窗口
            'main_window_title': 'DotStar 科研数据查看器',
            'file_menu': '文件(&F)',
            'view_menu': '视图(&V)',
            'help_menu': '帮助(&H)',
            'open_file': '打开文件(&O)',
            'recent_files': '最近文件(&R)',
            'exit': '退出(&X)',
            'toggle_left_panel': '显示/隐藏左侧面板',
            'about': '关于(&A)',
            'main_toolbar': '主工具栏',
            'open': '📁 打开',
            'open_tooltip': '打开数据文件',
            'supported_formats': '📋 支持格式',
            'formats_tooltip': '查看支持的文件格式',
            'ready': '就绪',
            'loading': '正在加载文件...',
            'load_failed': '加载失败',
            'loaded': '已加载: {}',
            
            # 文件相关
            'file_loading': '文件加载',
            'file_info': '文件信息',
            'recent_files_panel': '最近文件',
            'no_recent_files': '无最近文件',
            'drag_drop_hint': '拖放文件到这里\n或点击浏览文件',
            'browse_files': '浏览文件',
            'select_data_file': '选择数据文件',
            'all_supported': '所有支持的格式',
            'all_files': '所有文件 (*.*)',
            'file_not_found': '文件不存在: {}',
            'unsupported_format': '不支持的文件格式: {}',
            'load_error': '加载错误',
            'load_error_msg': '文件加载失败:\n{}',
            'no_file_loaded': '未加载文件',
            
            # 数据检查器
            'data_structure': '数据结构',
            'overview': '概览',
            'data': '数据',
            'statistics': '统计',
            'visualization': '可视化',
            'file_name': '文件名',
            'format': '格式',
            'size': '大小',
            'path': '路径',
            'type': '类型',
            'data_root': '数据根节点',
            'name': '名称',
            'shape_size': '大小/形状',
            'description': '描述',
            'length': '长度: {}',
            'items': '{} 项',
            'keys': '{} 个键',
            
            # 数据视图
            'view_mode': '显示模式',
            'text_view': '文本视图',
            'table_view': '表格视图',
            'raw_data': '原始数据',
            'text': '文本',
            'table': '表格',
            'raw': '原始',
            'not_suitable_table': '此数据不适合表格显示',
            'data_too_long': '... (数据太长，已截断)',
            'more_items': '... (还有 {} 项)',
            'value': '值',
            
            # 统计信息
            'data_type': '数据类型',
            'shape': '形状',
            'dimensions': '维度',
            'total_elements': '元素总数',
            'dtype': '数据类型',
            'numerical_stats': '数值统计',
            'min_value': '最小值',
            'max_value': '最大值',
            'mean_value': '平均值',
            'std_dev': '标准差',
            'variance': '方差',
            'percentile_25': '25%分位数',
            'percentile_50': '50%分位数(中位数)',
            'percentile_75': '75%分位数',
            'num_keys': '键的数量',
            'keys': '键',
            'first_10_keys': '前10个键',
            'num_elements': '元素数量',
            'first_element_type': '第一个元素类型',
            'string_length': '字符串长度',
            'content_preview': '内容预览',
            'stats_error': '统计计算错误: {}',
            
            # 可视化
            'viz_type': '可视化类型',
            'auto_select': '自动选择',
            'histogram': '直方图',
            'scatter_plot': '散点图',
            'line_plot': '折线图',
            'heatmap': '热力图',
            'generate_chart': '生成图表',
            'select_data_generate': '选择数据并点击生成图表',
            'no_data_viz': '没有数据可视化',
            'viz_failed': '可视化生成失败: {}',
            '1d_data_viz': '一维数据，可以绘制直方图或折线图\n数据形状: {}',
            '2d_data_viz': '二维数据，可以绘制热力图或散点图\n数据形状: {}',
            'nd_data_viz': '多维数据，需要降维后可视化\n数据形状: {}',
            'unsupported_viz': '数据类型 {} 不支持直接可视化',
            
            # 关于对话框
            'about_title': '关于',
            'about_text': '''
            <h2>DotStar 科研数据查看器</h2>
            <p>版本: 0.1.0</p>
            <p>专为科研人员设计的多格式数据文件浏览和分析工具</p>
            <p>支持JSON、Pickle、NumPy、MATLAB、HDF5、CSV、YAML等多种格式</p>
            <p><b>开发团队:</b> DotStar</p>
            ''',
            
            # 支持格式
            'supported_formats_title': '支持的文件格式',
            'formats_text': '支持的文件格式:\n\n{}',
            
            # 错误消息
            'error': '错误',
            'warning': '警告',
            'information': '信息',
            
            # 语言设置
            'language': '语言',
            'english': 'English',
            'chinese': '中文',
            'language_changed': '语言已切换为中文\n请重启应用程序使更改生效',
        }
    
    def load_saved_language(self):
        """Load saved language settings"""
        saved_lang = self.settings.value("language", "en")
        if saved_lang in self.translations:
            self.current_language = saved_lang
    
    def set_language(self, language_code: str):
        """Set language"""
        if language_code in self.translations:
            self.current_language = language_code
            self.settings.setValue("language", language_code)
    
    def get_language(self) -> str:
        """Get current language"""
        return self.current_language
    
    def tr(self, key: str, *args) -> str:
        """Translate text"""
        text = self.translations.get(self.current_language, {}).get(key, key)
        if args:
            try:
                return text.format(*args)
            except:
                return text
        return text
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages list"""
        return {
            'en': self.tr('english'),
            'zh': self.tr('chinese')
        }

# Global translator instance
translator = Translator()
