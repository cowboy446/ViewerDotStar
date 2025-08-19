# DotStarViewer 可执行文件打包指南

本指南详细说明如何将DotStarViewer打包成独立的可执行文件。

## 方法一：使用提供的脚本（推荐）

### Linux/macOS用户

1. 赋予脚本执行权限：
```bash
chmod +x build_executable.sh
```

2. 运行打包脚本：
```bash
./build_executable.sh
```

### Windows用户

直接双击运行：
```
build_executable.bat
```

或在命令提示符中运行：
```cmd
build_executable.bat
```

### Python脚本方式

如果你更喜欢使用Python脚本：
```bash
python3 build_executable.py
```

## 方法二：手动使用PyInstaller

### 1. 安装PyInstaller

```bash
pip install pyinstaller
```

### 2. 基本打包命令

```bash
pyinstaller --name="DotStarViewer" \
            --windowed \
            --onefile \
            --icon="favicon.png" \
            --add-data="favicon.png:." \
            --add-data="dotstar:dotstar" \
            main.py
```

### 3. 完整打包命令（包含所有依赖）

```bash
pyinstaller --name="DotStarViewer" \
            --windowed \
            --onefile \
            --icon="favicon.png" \
            --add-data="favicon.png:." \
            --add-data="dotstar:dotstar" \
            --hidden-import="PyQt5.QtCore" \
            --hidden-import="PyQt5.QtGui" \
            --hidden-import="PyQt5.QtWidgets" \
            --hidden-import="numpy" \
            --hidden-import="torch" \
            --hidden-import="scipy" \
            --hidden-import="h5py" \
            --hidden-import="pandas" \
            --hidden-import="yaml" \
            --hidden-import="toml" \
            --hidden-import="PIL" \
            --hidden-import="matplotlib" \
            --hidden-import="open3d" \
            --hidden-import="pyarrow" \
            --hidden-import="safetensors" \
            --hidden-import="astropy" \
            --hidden-import="netCDF4" \
            --clean \
            main.py
```

**Windows用户注意**: 将 `:` 改为 `;`：
```cmd
--add-data="favicon.png;."
--add-data="dotstar;dotstar"
```

## 方法三：使用规格文件

1. 生成规格文件：
```bash
pyinstaller --name="DotStarViewer" main.py
```

2. 编辑生成的 `DotStarViewer.spec` 文件，根据需要修改配置

3. 使用规格文件构建：
```bash
pyinstaller DotStarViewer.spec
```

## 打包选项说明

- `--name="DotStarViewer"`: 设置可执行文件名称
- `--windowed`: 不显示控制台窗口（适用于GUI应用）
- `--onefile`: 将所有内容打包到单个可执行文件中
- `--icon="favicon.png"`: 设置可执行文件图标
- `--add-data`: 添加数据文件到打包中
- `--hidden-import`: 强制包含可能被遗漏的模块
- `--clean`: 清理之前的构建缓存

## 输出文件

打包成功后，可执行文件将位于：
- Linux/macOS: `dist/DotStarViewer`
- Windows: `dist/DotStarViewer.exe`

## 常见问题和解决方案

### 1. 模块导入错误

如果运行时出现模块导入错误，在打包命令中添加相应的 `--hidden-import` 选项。

### 2. 文件大小过大

- 使用 `--exclude-module` 排除不需要的模块
- 考虑使用 `--onedir` 而不是 `--onefile`

### 3. 启动时间过长

- 使用 `--onedir` 模式而不是 `--onefile`
- 优化代码，减少启动时的导入

### 4. 图标不显示

确保 `favicon.png` 文件存在且格式正确。

## 分发注意事项

1. **依赖检查**: 在目标系统上测试可执行文件
2. **权限设置**: Linux/macOS可能需要设置执行权限
3. **杀毒软件**: 某些杀毒软件可能误报，需要添加白名单
4. **系统兼容性**: 确保目标系统架构兼容

## 优化建议

1. **减小文件大小**:
   ```bash
   pyinstaller --onefile --strip --upx-dir=/path/to/upx main.py
   ```

2. **加速启动**:
   ```bash
   pyinstaller --onedir main.py
   ```

3. **调试模式**:
   ```bash
   pyinstaller --debug main.py
   ```

## 支持的平台

- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+, CentOS 7+)

## 许可证

打包后的可执行文件遵循原项目的许可证条款。
