# Photo-Watermark-advanced

一个功能强大的桌面端图片批量加水印工具，使用 Python 和 PyQt6 构建。

## ✨ 功能特性

- **多种水印类型**: 支持添加文本水印和图片水印。
- **高度自定义**:
  - **文本水印**: 自定义文本内容、字体、大小、颜色、不透明度和旋转角度。
  - **图片水印**: 自定义水印图片、缩放比例、不透明度和旋转角度。
- **精确定位**: 提供九宫格定位选项，可以快速将水印放置在图片的九个标准位置。
- **实时预览**: 在添加和调整水印时，可以实时看到最终效果。
- **批量处理**: 支持一次性导入多张图片，并应用相同的水印设置进行批量处理。
- **模板管理**:
  - **保存模板**: 将当前的水印设置（如字体、颜色、位置等）保存为模板。
  - **加载模板**: 快速加载之前保存的模板，方便重复使用。
- **灵活的导出选项**:
  - 自定义输出目录。
  - 自定义文件名前缀和后缀。
  - 支持导出为 `JPEG` 和 `PNG` 格式。
  - 可为 `JPEG` 格式设置图片质量。
- **易于使用**:
  - 直观的图形用户界面。
  - 支持拖拽方式快速导入图片。

## 🚀 安装与运行

### 运行环境

- Python 3.x
- PyQt6
- Pillow (PIL Fork)
- numpy

### 从源码运行

1.  **克隆仓库**
    ```bash
    git clone <your-repository-url>
    cd Photo-Watermark-advanced
    ```

2.  **安装依赖**
    ```bash
    pip install PyQt6 Pillow numpy
    ```

3.  **运行应用**
    ```bash
    python src/main.py
    ```

## 📦 构建可执行文件

您可以使用 `PyInstaller` 将本应用打包成一个独立的 `.exe` 可执行文件。

1.  **安装 PyInstaller**
    ```bash
    pip install pyinstaller
    ```

2.  **执行打包命令**

    在项目根目录下运行以下命令：
    ```bash
    pyinstaller --onefile --windowed --name Photo-Watermark-advanced --paths src src/main.py
    ```
    - `--onefile`: 将所有依赖打包成单个 `.exe` 文件。
    - `--windowed`: 运行时不显示命令行窗口。
    - `--paths src`: 将 `src` 目录添加为模块搜索路径，防止出现 `ModuleNotFoundError`。

3.  **找到可执行文件**

    打包成功后，您可以在项目根目录下找到 `Photo-Watermark-advanced.exe`。

