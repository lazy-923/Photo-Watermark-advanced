"""
主窗口模块
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QFileDialog, QListWidget,
                           QMessageBox, QSpinBox, QDialog, QLineEdit,
                           QDialogButtonBox, QFormLayout, QComboBox,
                           QListWidgetItem)
from .template_dialog import TemplateDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
import os
from core.image_processor import ImageProcessor
from .watermark_editor import WatermarkEditor
from .preview_panel import PreviewPanel

class ExportDialog(QDialog):
    """导出设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导出设置")
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QFormLayout(self)
        
        # 输出目录选择
        self.output_dir = QLineEdit()
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output_dir)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.output_dir)
        dir_layout.addWidget(browse_btn)
        layout.addRow("输出目录:", dir_layout)
        
        # 文件名设置
        self.prefix = QLineEdit()
        layout.addRow("文件名前缀:", self.prefix)
        
        self.suffix = QLineEdit()
        self.suffix.setText("_watermarked")
        layout.addRow("文件名后缀:", self.suffix)
        
        # 格式选择
        self.format = QComboBox()
        self.format.addItems(["JPEG", "PNG"])
        layout.addRow("输出格式:", self.format)
        
        # 质量设置
        self.quality = QSpinBox()
        self.quality.setRange(1, 100)
        self.quality.setValue(95)
        layout.addRow("图片质量:", self.quality)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def browse_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir.setText(dir_path)
            
class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('图片水印工具')
        self.setGeometry(100, 100, 960, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板（图片列表和水印设置）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 图片列表组
        image_list_group = QVBoxLayout()
        
        # 添加图片按钮
        add_image_btn = QPushButton('添加图片')
        add_image_btn.clicked.connect(self.add_images)
        image_list_group.addWidget(add_image_btn)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(60, 60))
        self.image_list.currentItemChanged.connect(self.on_image_selected)
        image_list_group.addWidget(self.image_list)
        
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
        
        image_list_group.addLayout(tool_btn_layout)
        
        left_layout.addLayout(image_list_group)
        
        # 水印编辑器
        self.watermark_editor = WatermarkEditor()
        self.watermark_editor.watermarkChanged.connect(self.update_preview)
        left_layout.addWidget(self.watermark_editor)
        
        # 右侧预览面板
        self.preview_panel = PreviewPanel()
        
        # 添加到主布局
        main_layout.addWidget(left_panel, 1)  # 1:2 比例
        main_layout.addWidget(self.preview_panel, 2)
        
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
            
            # ��果是第一张图片，则选中
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
                
    def on_image_selected(self, current, previous):
        """图片选择改变时的处理"""
        if current:
            image_path = current.data(Qt.ItemDataRole.UserRole)
            self.current_image_path = image_path
            self.preview_panel.load_image(image_path)
            self.update_preview()
            
    def update_preview(self):
        """更新预览"""
        if self.current_image_path:
            settings = self.watermark_editor.get_settings()
            self.preview_panel.update_watermark(settings)
            
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
        self.update_preview()
        
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