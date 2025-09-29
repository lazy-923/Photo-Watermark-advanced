"""
预览面板模块
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QMouseEvent
from PIL.ImageQt import ImageQt
from core.image_processor import ImageProcessor

class PreviewPanel(QWidget):
    """预览面板类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._image_processor = ImageProcessor()
        
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        layout.addWidget(self.preview_label)
        
    def load_image(self, image_path: str):
        """加载图片
        
        Args:
            image_path: 图片路径
        """
        if self._image_processor.load_image(image_path):
            self._update_preview()
            
    def update_watermark(self, settings: dict):
        """更新水印设置
        
        Args:
            settings: 水印设置字典
        """
        if not self._image_processor._image:
            return
            
        # 更新水印设置
        # self._image_processor.reset_watermark_settings() # 不再完全重置，而是逐个更新
        
        # 应用所有设置
        self._image_processor.set_watermark_position(settings.get('position', (0, 0)))
        self._image_processor.set_watermark_opacity(settings.get('opacity', 255))
        self._image_processor.set_watermark_rotation(settings.get('rotation', 0))
        self._image_processor.set_watermark_scale(settings.get('scale', 1.0))

        if settings.get('text'):  # 文本水印
            self._image_processor.set_watermark_text(settings['text'])
            if settings.get('font_name'):
                self._image_processor.set_watermark_font(
                    settings['font_name'],
                    settings['font_size']
                )
            self._image_processor.set_watermark_color(settings['color'])
            self._image_processor.add_text_watermark()
        elif settings.get('image_path'):  # 图片水印
            # image_path 会被传递给 add_image_watermark，由它来决定是否需要重新加载图片
            self._image_processor.add_image_watermark(settings['image_path'])
        else:
            # 如果没有水印，恢复到原始图片
            if self._image_processor._original_image:
                self._image_processor._image = self._image_processor._original_image.copy()

        # 更新预览
        self._update_preview()
        
    def _update_preview(self):
        """更新预览显示"""
        if not self._image_processor._image:
            return
            
        # 转换PIL图片为QPixmap
        qim = ImageQt(self._image_processor._image)
        pixmap = QPixmap.fromImage(qim)
        
        # 缩放图片以适应预览区域
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
        
    def resizeEvent(self, event):
        """窗口大小改变事件处理"""
        super().resizeEvent(event)
        self._update_preview()