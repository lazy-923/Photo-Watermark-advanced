"""
预览面板模块
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QMouseEvent
from PIL.ImageQt import ImageQt
from ..core.image_processor import ImageProcessor

class PreviewPanel(QWidget):
    """预览面板类"""
    
    # 当水印被拖拽移动时发出信号，传递新的相对位置 (x, y)
    watermarkMoved = pyqtSignal(tuple)
    # 当拖拽操作完成时发出信号
    watermarkDragFinished = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._image_processor = ImageProcessor()
        self._is_dragging = False
        self._drag_start_pos = QPoint()
        self._watermark_start_pos_rel = (0, 0)
        self._current_settings = {} # 缓存当前水印设置

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
            
    def update_watermark(self, settings: dict, from_drag: bool = False):
        """更新水印设置
        
        Args:
            settings: 水印设置字典
            from_drag: 是否由内部拖拽调用
        """
        if not from_drag:
            self._current_settings = settings.copy()

        if not self._image_processor._image:
            return
            
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

    def _get_image_rect_in_label(self):
        """计算缩放后的图片在Label中实际占据的矩形区域"""
        pixmap = self.preview_label.pixmap()
        if not pixmap or pixmap.isNull():
            return None

        label_size = self.preview_label.size()
        pixmap_size = pixmap.size()

        x = (label_size.width() - pixmap_size.width()) // 2
        y = (label_size.height() - pixmap_size.height()) // 2
        
        return x, y, pixmap_size.width(), pixmap_size.height()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件，用于开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            img_rect = self._get_image_rect_in_label()
            if not img_rect: return

            x_offset, y_offset, scaled_w, scaled_h = img_rect
            
            # 将label坐标转换为缩放后图片的坐标
            pos_in_pixmap = event.pos() - QPoint(x_offset, y_offset)

            # 检查点击是否在图片区域内
            if not (0 <= pos_in_pixmap.x() < scaled_w and 0 <= pos_in_pixmap.y() < scaled_h):
                return

            # 获取水印边界框
            wm_bbox = self._image_processor.get_watermark_bounding_box()
            if not wm_bbox: return
            
            original_w, original_h = self._image_processor.get_image_size()
            
            # 将缩放后图片的坐标转换为原始图片坐标
            original_x = (pos_in_pixmap.x() / scaled_w) * original_w
            original_y = (pos_in_pixmap.y() / scaled_h) * original_h

            # 检查点击是否在水印边界框内
            wm_x, wm_y, wm_w, wm_h = wm_bbox
            if wm_x <= original_x < wm_x + wm_w and wm_y <= original_y < wm_y + wm_h:
                self._is_dragging = True
                self._drag_start_pos = event.pos()
                # 使用缓存的设置来获取起始位置
                self._watermark_start_pos_rel = self._current_settings.get('position', (0.05, 0.05))
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件，用于处理拖拽"""
        if self._is_dragging and self._current_settings:
            img_rect = self._get_image_rect_in_label()
            if not img_rect: return
            
            _, _, scaled_w, scaled_h = img_rect
            original_w, original_h = self._image_processor.get_image_size()
            
            # 从 image_processor 获取水印的实际尺寸
            wm_bbox = self._image_processor.get_watermark_bounding_box()
            if not wm_bbox: 
                # 如果没有 bbox，可能是因为水印还没有被渲染，我们可以尝试从当前图层获取
                if self._image_processor._current_watermark_layer:
                    wm_w, wm_h = self._image_processor._current_watermark_layer.size
                else:
                    return # 如果完全没有水印信息，则无法继续
            else:
                _, _, wm_w, wm_h = wm_bbox

            # 计算鼠标在label中的位移
            delta = event.pos() - self._drag_start_pos
            
            # 将label位移转换为原始图片的像素位移
            delta_x_original = (delta.x() / scaled_w) * original_w
            delta_y_original = (delta.y() / scaled_h) * original_h

            # 计算新的水印左上角像素位置
            start_pos_x_px = self._watermark_start_pos_rel[0] * (original_w - wm_w) if original_w > wm_w else 0
            start_pos_y_px = self._watermark_start_pos_rel[1] * (original_h - wm_h) if original_h > wm_h else 0
            
            new_pos_x_px = start_pos_x_px + delta_x_original
            new_pos_y_px = start_pos_y_px + delta_y_original

            # 将新的像素位置转换为相对位置
            new_rel_x = new_pos_x_px / (original_w - wm_w) if original_w > wm_w else 0
            new_rel_y = new_pos_y_px / (original_h - wm_h) if original_h > wm_h else 0
            
            # 限制在 0.0 - 1.0 之间
            new_rel_x = max(0.0, min(1.0, new_rel_x))
            new_rel_y = max(0.0, min(1.0, new_rel_y))
            
            new_pos = (new_rel_x, new_rel_y)

            # 创建一个临时设置副本并更新位置
            temp_settings = self._current_settings.copy()
            temp_settings['position'] = new_pos
            
            # 直接更新预览，标记为来自拖拽
            self.update_watermark(temp_settings, from_drag=True)
            
            # 发出信号，以便其他UI（如位置输入框）可以实时更新
            self.watermarkMoved.emit(new_pos)


    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件，用于结束拖拽"""
        if event.button() == Qt.MouseButton.LeftButton and self._is_dragging:
            self._is_dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # 计算最终位置
            img_rect = self._get_image_rect_in_label()
            if not img_rect: return
            
            _, _, scaled_w, scaled_h = img_rect
            original_w, original_h = self._image_processor.get_image_size()
            wm_bbox = self._image_processor.get_watermark_bounding_box()
            if not wm_bbox: return

            _, _, wm_w, wm_h = wm_bbox

            delta = event.pos() - self._drag_start_pos
            delta_x_original = (delta.x() / scaled_w) * original_w
            delta_y_original = (delta.y() / scaled_h) * original_h

            start_pos_x_px = self._watermark_start_pos_rel[0] * (original_w - wm_w) if original_w > wm_w else 0
            start_pos_y_px = self._watermark_start_pos_rel[1] * (original_h - wm_h) if original_h > wm_h else 0
            
            new_pos_x_px = start_pos_x_px + delta_x_original
            new_pos_y_px = start_pos_y_px + delta_y_original

            new_rel_x = new_pos_x_px / (original_w - wm_w) if original_w > wm_w else 0
            new_rel_y = new_pos_y_px / (original_h - wm_h) if original_h > wm_h else 0
            
            new_rel_x = max(0.0, min(1.0, new_rel_x))
            new_rel_y = max(0.0, min(1.0, new_rel_y))

            # 发出拖拽完成信号，将最终位置传递给编辑器
            self.watermarkDragFinished.emit((new_rel_x, new_rel_y))
        
    def resizeEvent(self, event):
        """窗口大小改变事件处理"""
        super().resizeEvent(event)
        self._update_preview()