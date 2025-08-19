#!/usr/bin/env python3
"""
创建示例数据文件的脚本
用于测试DotStarViewer的各种数据格式支持
"""

import numpy as np
import json
import pickle
import os
from pathlib import Path

def create_sample_data():
    """创建各种格式的示例数据文件"""
    
    # 确保sample_data目录存在
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # 1. 创建NumPy数组文件
    print("创建NumPy数组文件...")
    
    # 一维数组 - 时间序列数据
    time_series = np.sin(np.linspace(0, 4*np.pi, 1000)) + 0.1 * np.random.randn(1000)
    np.save(sample_dir / "time_series.npy", time_series)
    
    # 二维数组 - 图像数据
    image_data = np.random.randint(0, 256, size=(256, 256, 3), dtype=np.uint8)
    np.save(sample_dir / "synthetic_image.npy", image_data)
    
    # 三维数组 - 体积数据
    volume_data = np.random.randn(64, 64, 64).astype(np.float32)
    np.save(sample_dir / "volume_data.npy", volume_data)
    
    # NPZ文件 - 多个数组
    experiment_data = {
        'positions': np.random.randn(1000, 3),
        'velocities': np.random.randn(1000, 3), 
        'forces': np.random.randn(1000, 3),
        'energies': np.random.randn(1000),
        'timestamps': np.linspace(0, 10, 1000)
    }
    np.savez(sample_dir / "molecular_dynamics.npz", **experiment_data)
    
    # 2. 创建复杂的Python对象 (Pickle)
    print("创建Pickle文件...")
    
    class ExperimentResult:
        def __init__(self):
            self.metadata = {
                'experiment_id': 'EXP-2024-001',
                'researcher': '李四',
                'institution': '清华大学',
                'date': '2024-01-15'
            }
            self.measurements = np.random.randn(500, 10)
            self.parameters = {
                'temperature': np.linspace(20, 80, 50),
                'pressure': np.linspace(1, 10, 50),
                'concentration': [0.1, 0.5, 1.0, 2.0, 5.0]
            }
            self.results = {
                'mean_response': np.mean(self.measurements, axis=0),
                'std_response': np.std(self.measurements, axis=0),
                'correlation_matrix': np.corrcoef(self.measurements.T)
            }
    
    experiment = ExperimentResult()
    with open(sample_dir / "experiment_results.pkl", 'wb') as f:
        pickle.dump(experiment, f)
    
    # 3. 创建嵌套的JSON数据
    print("创建复杂JSON文件...")
    
    complex_data = {
        "研究项目": {
            "项目名称": "新材料性能测试",
            "负责人": "王五",
            "团队成员": ["张三", "李四", "赵六"],
            "开始日期": "2024-01-01",
            "预计结束": "2024-12-31"
        },
        "实验设计": {
            "变量": {
                "温度": {"范围": [20, 100], "单位": "°C", "步长": 5},
                "压力": {"范围": [1, 50], "单位": "MPa", "步长": 2},
                "时间": {"范围": [0, 3600], "单位": "秒", "步长": 60}
            },
            "测量指标": [
                {"名称": "弹性模量", "单位": "GPa", "精度": 0.1},
                {"名称": "屈服强度", "单位": "MPa", "精度": 1.0},
                {"名称": "断裂韧性", "单位": "MPa·m^0.5", "精度": 0.01}
            ]
        },
        "数据": {
            "实验组1": {
                "条件": {"温度": 25, "压力": 10},
                "测量值": [45.2, 78.9, 234.5, 56.7, 89.1],
                "重复次数": 5,
                "标准差": 12.3
            },
            "实验组2": {
                "条件": {"温度": 50, "压力": 20},
                "测量值": [48.7, 82.1, 241.8, 59.2, 91.6],
                "重复次数": 5,
                "标准差": 14.1
            },
            "对照组": {
                "条件": {"温度": 25, "压力": 1},
                "测量值": [42.1, 75.3, 228.9, 54.2, 86.7],
                "重复次数": 5,
                "标准差": 11.8
            }
        },
        "统计分析": {
            "ANOVA": {
                "F统计量": 23.45,
                "p值": 0.001,
                "自由度": [2, 12]
            },
            "相关性分析": {
                "温度-强度": 0.87,
                "压力-模量": 0.76,
                "时间-韧性": -0.23
            }
        },
        "结论": [
            "温度升高显著提高材料强度",
            "压力对弹性模量有正向影响",
            "长时间暴露会降低断裂韧性"
        ]
    }
    
    with open(sample_dir / "complex_experiment.json", 'w', encoding='utf-8') as f:
        json.dump(complex_data, f, ensure_ascii=False, indent=2)
    
    # 4. 创建带有中文的配置文件
    print("创建YAML配置文件...")
    
    yaml_content = """
# 深度学习实验配置文件
实验配置:
  名称: "图像分类模型优化"
  版本: "v2.1"
  描述: "使用迁移学习优化图像分类性能"

数据集:
  训练集:
    路径: "/data/train"
    样本数: 10000
    类别数: 100
  验证集:
    路径: "/data/val" 
    样本数: 2000
  测试集:
    路径: "/data/test"
    样本数: 3000

模型架构:
  基础模型: "ResNet50"
  预训练: true
  冻结层数: 10
  分类器:
    - 层类型: "全连接"
      神经元数: 512
      激活函数: "ReLU"
      Dropout: 0.5
    - 层类型: "全连接"
      神经元数: 100
      激活函数: "Softmax"

训练参数:
  优化器: "Adam"
  学习率: 0.001
  批量大小: 32
  训练轮数: 50
  学习率调度:
    类型: "StepLR"
    步长: 10
    衰减因子: 0.1

数据增强:
  - 随机旋转: [-15, 15]
  - 随机缩放: [0.8, 1.2]
  - 随机翻转: "水平"
  - 颜色抖动: 0.2

评估指标:
  - "准确率"
  - "精确率"
  - "召回率"
  - "F1分数"
  - "混淆矩阵"
"""
    
    with open(sample_dir / "deep_learning_config.yaml", 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"示例数据文件已创建在 {sample_dir} 目录中:")
    for file in sample_dir.glob("*"):
        print(f"  - {file.name}")

if __name__ == "__main__":
    create_sample_data()
