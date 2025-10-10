"""
主窗口模块
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QFileDialog, QListWidget,
                           QMessageBox, QSpinBox, QDialog, QLineEdit,
                           QDialogButtonBox, QFormLayout, QComboBox,
                           QListWidgetItem)
from .template_dialog import TemplateDialog
from .export_dialog import ExportDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
import os
from ..core.image_processor import ImageProcessor
from .watermark_editor import WatermarkEditor
from .preview_panel import PreviewPanel


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self._current_file = None
        self.image_settings = {}  # 用于存储每个图片的设置
        self._init_ui()

    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('图片水印工具')
        self.setGeometry(100, 100, 900, 500)  # 稍微增大了窗口尺寸
        
        # 允许拖放
        self.setAcceptDrops(True)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # --- 左侧面板 (图片列表) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 添加图片按钮
        add_image_btn = QPushButton('添加图片')
        add_image_btn.clicked.connect(self.add_images)
        left_layout.addWidget(add_image_btn)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80)) # 增大了缩略图尺寸
        left_layout.addWidget(self.image_list)
        
        # 工具按钮布局
        tool_btn_layout = QHBoxLayout()
        
        # 模板管理按钮
        template_btn = QPushButton('模板管理')
        template_btn.clicked.connect(self.show_template_dialog)
        tool_btn_layout.addWidget(template_btn)
        
        # 批量处理按钮
        export_btn = QPushButton('导出处理')
        export_btn.clicked.connect(self.export_images)
        tool_btn_layout.addWidget(export_btn)
        
        left_layout.addLayout(tool_btn_layout)
        
        # --- 中间面板 (预览) ---
        self.preview_panel = PreviewPanel()
        
        # --- 右侧面板 (水印编辑器) ---
        self.watermark_editor = WatermarkEditor()
        
        # 添加到主布局
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.preview_panel, 4)
        main_layout.addWidget(self.watermark_editor, 2)
        
        # 连接信号和槽
        self.image_list.itemSelectionChanged.connect(self._on_file_selected)
        self.watermark_editor.watermarkChanged.connect(self._on_watermark_changed)
        
        # 拖拽结束后，使用最终位置更新编辑器
        self.preview_panel.watermarkDragFinished.connect(self.watermark_editor.update_position)
        
        # 如果需要实时显示坐标，可以连接watermarkMoved信号到一个专门的槽
        # self.preview_panel.watermarkMoved.connect(self.update_coords_display) 

        # self.action_open.triggered.connect(self._open_files)
        # self.action_save_as.triggered.connect(self._save_file_as)
        # self.action_exit.triggered.connect(self.close)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖动进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and ImageProcessor.is_supported_format(file_path):
                self.add_image_from_path(file_path)

    def add_image_from_path(self, file_path: str):
        """从路径添加图片"""
        try:
            # 创建缩略图
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "警告", f"无法加载图片: {file_path}")
                return
                
            icon = QIcon(pixmap.scaled(
                60, 60,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            
            # 添加到列表
            item = QListWidgetItem(
                icon,
                os.path.basename(file_path)
            )
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.image_list.addItem(item)
            
            # 果是第一张图片，则选中
            if self.image_list.count() == 1:
                self.image_list.setCurrentRow(0)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加图片时出错：\\n{str(e)}")

    def add_images(self):
        """添加图片"""
        try:
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
            file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
            
            if file_dialog.exec():
                filenames = file_dialog.selectedFiles()
                for filename in filenames:
                    self.add_image_from_path(filename)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加图片时出错：\\n{str(e)}")
                
    def show_template_dialog(self):
        """显示模板管理对话框"""
        dialog = TemplateDialog(self)
        dialog.templateSelected.connect(self.load_template)
        dialog.exec()
        
    def load_template(self, settings: dict):
        """加载水印模板
        
        Args:
            settings: 模板设置
        """
        # 更新水印编辑器的设置
        if settings.get('text'):
            self.watermark_editor.text_input.setText(settings['text'])
        if settings.get('font_name'):
            index = self.watermark_editor.font_combo.findText(settings['font_name'])
            if index >= 0:
                self.watermark_editor.font_combo.setCurrentIndex(index)
        if settings.get('font_size'):
            self.watermark_editor.size_spin.setValue(settings['font_size'])
        if settings.get('color'):
            color = settings['color']
            self.watermark_editor.color_button.setStyleSheet(
                f"background-color: rgb({color[0]},{color[1]},{color[2]});"
            )
        if settings.get('opacity') is not None:
            self.watermark_editor.opacity_slider.setValue(settings['opacity'])
        if settings.get('rotation') is not None:
            self.watermark_editor.rotation_spin.setValue(settings['rotation'])
        if settings.get('scale') is not None:
            self.watermark_editor.scale_spin.setValue(int(settings['scale'] * 100))
        if settings.get('position') is not None:
            self.watermark_editor.position = settings['position']
        
        # 更新预览
        self._on_watermark_changed(self.watermark_editor.get_settings())
        
    def export_images(self):
        """导出处理图片"""
        if self.image_list.count() == 0:
            QMessageBox.warning(self, "警告", "请先添加需要处理的图片！")
            return
            
        # 显示导出设置对话框
        dialog = ExportDialog(self)
        if dialog.exec():
            output_dir = dialog.output_dir.text()
            prefix = dialog.prefix.text()
            suffix = dialog.suffix.text()
            format = dialog.format.currentText()
            quality = dialog.quality.value()
            
            if not output_dir:
                QMessageBox.warning(self, "警告", "请选择输出目录！")
                return
                
            # 处理所有图片
            processor = ImageProcessor()
            settings = self.watermark_editor.get_settings()
            
            # 应用所有设置到处理器
            processor.set_watermark_position(settings.get('position', (0, 0)))
            processor.set_watermark_opacity(settings.get('opacity', 255))
            processor.set_watermark_rotation(settings.get('rotation', 0))
            processor.set_watermark_scale(settings.get('scale', 1.0))

            if settings.get('text'):
                processor.set_watermark_text(settings['text'])
                if settings.get('font_name'):
                    processor.set_watermark_font(
                        settings['font_name'],
                        settings['font_size']
                    )
                processor.set_watermark_color(settings['color'])
            
            for i in range(self.image_list.count()):
                item = self.image_list.item(i)
                input_path = item.data(Qt.ItemDataRole.UserRole)
                
                # 生成输出文件名
                filename = os.path.basename(input_path)
                name, ext = os.path.splitext(filename)
                output_filename = f"{prefix}{name}{suffix}.{format.lower()}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 处理图片
                processor.load_image(input_path)
                
                if settings.get('text'):  # 文本水印
                    processor.add_text_watermark()
                elif settings.get('image_path'):  # 图片水印
                    processor.add_image_watermark(settings['image_path'])
                    
                processor.save_image(output_path, quality=quality, format=format)
                
            QMessageBox.information(self, "完成", "图片处理完成！")

    def _on_file_selected(self):
        """当文件列表中的选择项改变时调用"""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            self._current_file = None
            return

        # 1. 保存当前图片的设置（如果存在）
        if self._current_file:
            current_settings = self.watermark_editor.get_settings()
            self.image_settings[self._current_file] = current_settings

        # 2. 加载新图片
        new_file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self._current_file = new_file_path
        self.preview_panel.load_image(new_file_path)

        # 3. 加载新图片的设置
        if new_file_path in self.image_settings:
            settings = self.image_settings[new_file_path]
            self.watermark_editor.set_settings(settings)
        else:
            # 如果没有，则重置为默认设置
            default_settings = {
                'text': '', 'font_name': 'Arial', 'font_size': 36,
                'color': (0, 0, 0), 'opacity': 255, 'rotation': 0,
                'scale': 1.0, 'image_path': None, 'position': (0.05, 0.05)
            }
            self.image_settings[new_file_path] = default_settings
            self.watermark_editor.set_settings(default_settings)
            
        # 4. 更新预览（set_settings会触发watermarkChanged，所以这里可能重复，但为了确保逻辑清晰）
        self._on_watermark_changed(self.watermark_editor.get_settings())


    def _on_watermark_changed(self, settings: dict):
        """当水印设置改变时调用"""
        if self._current_file:
            # 更新预览
            self.preview_panel.update_watermark(settings)
            # 保存当前设置
            self.image_settings[self._current_file] = settings

    def _open_files(self):
        """打开一个或多个图片文件"""
        # This method is not fully implemented or connected
        self.add_images()