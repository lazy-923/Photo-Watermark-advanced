"""
水印编辑器面板
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QSpinBox, QPushButton, QColorDialog,
                           QSlider, QComboBox, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase

class WatermarkEditor(QWidget):
    """水印编辑器面板"""
    
    # 定义信号
    watermarkChanged = pyqtSignal()  # 水印设置改变时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.position = (0, 0)  # (x, y) for 3x3 grid, default top-left
        self._init_ui()
        
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 文本水印设置组
        text_group = QGroupBox("文本水印设置")
        text_layout = QVBoxLayout(text_group)
        
        # 文本输入
        text_input_layout = QHBoxLayout()
        text_label = QLabel("水印文本:")
        self.text_input = QLineEdit()
        self.text_input.textChanged.connect(self._on_settings_changed)
        text_input_layout.addWidget(text_label)
        text_input_layout.addWidget(self.text_input)
        text_layout.addLayout(text_input_layout)
        
        # 字体设置
        font_layout = QHBoxLayout()
        font_label = QLabel("字体:")
        self.font_combo = QComboBox()
        # 添加一些常用字体
        self.font_combo.addItems([
            "Arial", "Times New Roman", "Courier New", 
            "SimSun", "SimHei", "Microsoft YaHei"
        ])
        self.font_combo.currentTextChanged.connect(self._on_settings_changed)
        
        size_label = QLabel("字号:")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(36)
        self.size_spin.valueChanged.connect(self._on_settings_changed)
        
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        font_layout.addWidget(size_label)
        font_layout.addWidget(self.size_spin)
        text_layout.addLayout(font_layout)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        color_label = QLabel("颜色:")
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.color_button.setStyleSheet("background-color: black;")
        self.color_button.clicked.connect(self._choose_color)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        text_layout.addLayout(color_layout)
        
        layout.addWidget(text_group)
        
        # 图片水印设置组
        image_group = QGroupBox("图片水印设置")
        image_layout = QVBoxLayout(image_group)
        
        # 图片选择
        image_btn_layout = QHBoxLayout()
        self.image_path_label = QLabel("未选择图片")
        self.select_image_btn = QPushButton("选择图片")
        self.select_image_btn.clicked.connect(self._choose_image)
        image_btn_layout.addWidget(self.image_path_label)
        image_btn_layout.addWidget(self.select_image_btn)
        image_layout.addLayout(image_btn_layout)
        
        # 缩放设置
        scale_layout = QHBoxLayout()
        scale_label = QLabel("缩放:")
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(1, 200)
        self.scale_spin.setValue(100)
        self.scale_spin.setSuffix("%")
        self.scale_spin.valueChanged.connect(self._on_settings_changed)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_spin)
        image_layout.addLayout(scale_layout)
        
        layout.addWidget(image_group)
        
        # 通用设置组
        common_group = QGroupBox("通用设置")
        common_layout = QVBoxLayout(common_group)
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self._on_settings_changed)
        opacity_value = QLabel("255")
        self.opacity_slider.valueChanged.connect(
            lambda v: opacity_value.setText(str(v)))
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(opacity_value)
        common_layout.addLayout(opacity_layout)
        
        # 旋转设置
        rotation_layout = QHBoxLayout()
        rotation_label = QLabel("旋转角度:")
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.setValue(0)
        self.rotation_spin.valueChanged.connect(self._on_settings_changed)
        rotation_layout.addWidget(rotation_label)
        rotation_layout.addWidget(self.rotation_spin)
        common_layout.addLayout(rotation_layout)
        
        layout.addWidget(common_group)
        layout.addStretch()
        
        # 九宫格位置选择
        position_group = QGroupBox("位置设置")
        position_layout = QVBoxLayout(position_group)
        
        # 创建3x3的按钮网格
        for i in range(3):
            row_layout = QHBoxLayout()
            for j in range(3):
                btn = QPushButton()
                btn.setFixedSize(40, 40)
                btn.clicked.connect(lambda checked, x=j, y=i: 
                                 self._on_position_selected(x, y))
                row_layout.addWidget(btn)
            position_layout.addLayout(row_layout)
            
        layout.addWidget(position_group)
        
    def _choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet(
                f"background-color: {color.name()};")
            self._on_settings_changed()
            
    def _choose_image(self):
        """选择水印图片"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择水印图片",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_name:
            self.image_path_label.setText(file_name)
            self._on_settings_changed()
            
    def _on_position_selected(self, x: int, y: int):
        """九宫格位置选择
        
        Args:
            x: 横向位置(0-2)
            y: 纵向位置(0-2)
        """
        self.position = (x, y)
        self._on_settings_changed()
        
    def _on_settings_changed(self):
        """水印设置改变时的处理"""
        self.watermarkChanged.emit()
        
    def get_settings(self):
        """获取当前水印设置
        
        Returns:
            dict: 水印设置字典
        """
        return {
            'text': self.text_input.text(),
            'font_name': self.font_combo.currentText(),
            'font_size': self.size_spin.value(),
            'color': self.color_button.palette().button().color().getRgb()[:3],
            'opacity': self.opacity_slider.value(),
            'rotation': self.rotation_spin.value(),
            'scale': self.scale_spin.value() / 100.0,
            'image_path': self.image_path_label.text() 
                         if self.image_path_label.text() != "未选择图片" else None,
            'position': self.position
        }