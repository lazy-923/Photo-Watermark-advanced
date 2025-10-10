"""
核心图片处理模块
"""
from typing import Optional, Tuple, Union, List
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
import os

class ImageProcessor:
    """图像处理类"""
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    
    def __init__(self):
        self._image = None
        self._original_image = None
        self._watermark_settings = {}
        self._watermark_image = None  # 用于存储水印图片
        self._current_watermark_layer = None # 用于存储当前水印图层
        self._watermark_bbox = None # (x, y, width, height)
        self.reset_watermark_settings()

    def reset_watermark_settings(self):
        """重置水印设置"""
        self._watermark_settings = {
            'text': '',
            'font_name': 'arial.ttf',
            'font_size': 36,
            'color': (0, 0, 0),
            'opacity': 255,
            'rotation': 0,
            'scale': 1.0,
            'position': (0.05, 0.05),  # 使用相对位置 (0.0-1.0)
        }
        self._watermark_image = None # 重置时也清除水印图片
        self._current_watermark_layer = None
        self._watermark_bbox = None

    def load_image(self, image_path: str) -> bool:
        """加载图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            self._image = Image.open(image_path)
            self._original_image = self._image.copy()  # 保存原始图片
            
            # 确保图片是RGB或RGBA模式
            if self._image.mode not in ('RGB', 'RGBA'):
                self._image = self._image.convert('RGBA')
                self._original_image = self._original_image.convert('RGBA')
            
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
            
    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """检查文件是否为支持的格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ImageProcessor.SUPPORTED_FORMATS
        
    def get_image_size(self) -> Tuple[int, int]:
        """获取图片尺寸
        
        Returns:
            Tuple[int, int]: (宽, 高)
        """
        if self._image:
            return self._image.size
        return (0, 0)
            
    def get_watermark_bounding_box(self) -> Optional[Tuple[int, int, int, int]]:
        """获取当前水印的边界框 (x, y, width, height)"""
        return self._watermark_bbox

    def set_watermark_text(self, text: str) -> None:
        """设置水印文本
        
        Args:
            text: 水印文本
        """
        self._watermark_settings['text'] = text
        
    def set_watermark_font(self, font_name: str, size: int) -> None:
        """设置水印字体
        
        Args:
            font_name: 字体名称
            size: 字体大小
        """
        self._watermark_settings['font_name'] = font_name
        self._watermark_settings['font_size'] = size if size > 0 else 36
        
    def set_watermark_color(self, color: Tuple[int, int, int]) -> None:
        """设置水印颜色
        
        Args:
            color: RGB颜色值
        """
        self._watermark_settings['color'] = color
        
    def set_watermark_opacity(self, opacity: int) -> None:
        """设置水印不透明度
        
        Args:
            opacity: 不透明度 (0-255)
        """
        self._watermark_settings['opacity'] = max(0, min(255, opacity))
        
    def set_watermark_position(self, position: Tuple[float, float]) -> None:
        """设置水印相对位置
        
        Args:
            position: (x, y) 相对位置 (0.0-1.0)
        """
        self._watermark_settings['position'] = position
        
    def set_watermark_rotation(self, angle: float) -> None:
        """设置水印旋转角度
        
        Args:
            angle: 旋转角度
        """
        self._watermark_settings['rotation'] = angle
        
    def set_watermark_scale(self, scale: float) -> None:
        """设置图片水印缩放比例
        
        Args:
            scale: 缩放比例 (e.g., 1.0 for 100%)
        """
        self._watermark_settings['scale'] = scale
        
    def add_text_watermark(self) -> bool:
        """添加文本水印
        
        Returns:
            bool: 是否成功添加水印
        """
        if self._image is None or not self._watermark_settings['text']:
            self._watermark_bbox = None
            self._current_watermark_layer = None
            if self._original_image:
                self._image = self._original_image.copy()
            return False
            
        try:
            # 恢复原始图片
            self._image = self._original_image.copy()
            
            # 创建水印图层
            watermark = Image.new('RGBA', self._image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 设置字体
            try:
                font = ImageFont.truetype(
                    self._watermark_settings['font_name'],
                    self._watermark_settings['font_size']
                ) if self._watermark_settings['font_name'] else ImageFont.load_default(size=self._watermark_settings['font_size'])
            except Exception:
                font = ImageFont.load_default(size=self._watermark_settings['font_size'])
            
            # 获取文本大小
            text_bbox = draw.textbbox(
                (0, 0),
                self._watermark_settings['text'],
                font=font,
                anchor='lt'
            )
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # 创建一个单独的文本图层以便旋转
            text_layer = Image.new('RGBA', (text_width + 20, text_height + 20), (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_layer)
            
            # 绘制文本
            text_draw.text(
                (10, 10),
                self._watermark_settings['text'],
                font=font,
                fill=(*self._watermark_settings['color'], self._watermark_settings['opacity']),
                anchor='lt'
            )
            
            # 旋转文本
            if self._watermark_settings['rotation']:
                text_layer = text_layer.rotate(
                    self._watermark_settings['rotation'],
                    expand=True,
                    fillcolor=(255, 255, 255, 0)
                )

            self._current_watermark_layer = text_layer
            
            # 计算像素位置
            img_width, img_height = self.get_image_size()
            wm_width, wm_height = text_layer.size
            rel_x, rel_y = self._watermark_settings['position']
            
            pixel_x = int(rel_x * (img_width - wm_width))
            pixel_y = int(rel_y * (img_height - wm_height))
            
            pixel_x = max(0, min(pixel_x, img_width - wm_width))
            pixel_y = max(0, min(pixel_y, img_height - wm_height))

            self._watermark_bbox = (pixel_x, pixel_y, wm_width, wm_height)

            # 粘贴到水印图层
            watermark.paste(
                text_layer,
                (pixel_x, pixel_y),
                text_layer
            )
            
            # 合并水印层
            if self._image.mode != 'RGBA':
                self._image = self._image.convert('RGBA')
            
            self._image = Image.alpha_composite(self._image, watermark)
            return True
            
        except Exception as e:
            print(f"Error adding text watermark: {e}")
            self._watermark_bbox = None
            self._current_watermark_layer = None
            return False
    
    def add_image_watermark(self, image_path: str) -> bool:
        """添加图片水印
        
        Args:
            image_path: 水印图片路径
            
        Returns:
            bool: 是否成功添加水印
        """
        if self._image is None or not image_path:
            self._watermark_bbox = None
            self._current_watermark_layer = None
            if self._original_image:
                self._image = self._original_image.copy()
            return False
            
        try:
            # 恢复原始图片
            self._image = self._original_image.copy()

            # 加载水印图片
            watermark_img = Image.open(image_path)
            
            # 确保水印图片是RGBA模式
            if watermark_img.mode != 'RGBA':
                watermark_img = watermark_img.convert('RGBA')
            
            # 调整水印图片大小
            if self._watermark_settings['scale'] != 1.0:
                new_size = tuple(int(dim * self._watermark_settings['scale']) for dim in watermark_img.size)
                watermark_img = watermark_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 旋转水印
            if self._watermark_settings['rotation']:
                watermark_img = watermark_img.rotate(
                    self._watermark_settings['rotation'],
                    expand=True,
                    fillcolor=(255, 255, 255, 0)
                )
            
            # 调整不透明度
            if self._watermark_settings['opacity'] != 255:
                alpha = watermark_img.getchannel('A')
                alpha = ImageEnhance.Brightness(alpha).enhance(self._watermark_settings['opacity'] / 255.0)
                watermark_img.putalpha(alpha)

            self._current_watermark_layer = watermark_img

            # 计算像素位置
            img_width, img_height = self.get_image_size()
            wm_width, wm_height = watermark_img.size
            rel_x, rel_y = self._watermark_settings['position']

            pixel_x = int(rel_x * (img_width - wm_width))
            pixel_y = int(rel_y * (img_height - wm_height))

            pixel_x = max(0, min(pixel_x, img_width - wm_width))
            pixel_y = max(0, min(pixel_y, img_height - wm_height))

            self._watermark_bbox = (pixel_x, pixel_y, wm_width, wm_height)
            
            # 创建一个新的RGBA图层
            watermark_layer = Image.new('RGBA', self._image.size, (255, 255, 255, 0))
            
            # 粘贴水印图片
            watermark_layer.paste(
                watermark_img,
                (pixel_x, pixel_y),
                watermark_img
            )
            
            # 合并水印层
            if self._image.mode != 'RGBA':
                self._image = self._image.convert('RGBA')
            
            self._image = Image.alpha_composite(self._image, watermark_layer)
            return True
            
        except Exception as e:
            print(f"Error adding image watermark: {e}")
            self._watermark_bbox = None
            self._current_watermark_layer = None
            return False
            
    def resize_image(self, width: Optional[int] = None, height: Optional[int] = None,
                    scale: Optional[float] = None) -> bool:
        """调整图片大小
        
        Args:
            width: 目标宽度
            height: 目标高度
            scale: 缩放比例
            
        Returns:
            bool: 是否成功调整
        """
        if self._image is None:
            return False
            
        try:
            if scale:
                new_size = tuple(int(dim * scale) for dim in self._image.size)
            elif width and height:
                new_size = (width, height)
            elif width:
                ratio = width / self._image.size[0]
                new_size = (width, int(self._image.size[1] * ratio))
            elif height:
                ratio = height / self._image.size[1]
                new_size = (int(self._image.size[0] * ratio), height)
            else:
                return False
                
            self._image = self._image.resize(new_size, Image.Resampling.LANCZOS)
            return True
            
        except Exception as e:
            print(f"Error resizing image: {e}")
            return False
            
    def save_image(self, output_path: str, quality: int = 95, format: Optional[str] = None) -> bool:
        """保存图片
        
        Args:
            output_path: 输出路径
            quality: 图片质量 (1-100)
            format: 输出格式，如 'JPEG', 'PNG' 等
            
        Returns:
            bool: 是否成功保存
        """
        if self._image is None:
            return False
            
        try:
            # 确定输出格式
            if not format:
                format = os.path.splitext(output_path)[1][1:].upper()
                if format in ('JPG', 'JPEG'):
                    format = 'JPEG'
                elif format == 'PNG':
                    format = 'PNG'
            
            # 转换图片模式
            if format == 'JPEG':
                if self._image.mode == 'RGBA':
                    # 创建白色背景
                    background = Image.new('RGB', self._image.size, (255, 255, 255))
                    background.paste(self._image, mask=self._image.getchannel('A'))
                    background.save(output_path, format=format, quality=quality)
                else:
                    self._image.convert('RGB').save(output_path, format=format, quality=quality)
            else:
                self._image.save(output_path, format=format)
            
            return True
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return False