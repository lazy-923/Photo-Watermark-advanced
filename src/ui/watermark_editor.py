"""
水印编辑器模块
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QGridLayout,
                             QPushButton, QSlider, QLabel, QLineEdit,
                             QColorDialog, QFontDialog, QComboBox, QHBoxLayout, QSpinBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from typing import Tuple

class WatermarkEditor(QWidget):
    """水印编辑器类"""
    watermarkChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_position_relative = (0.05, 0.05)
        self._color = QColor("black")  # 存储当前颜色
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

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
        self.font_combo.addItems(["Arial", "Times New Roman", "Courier New", "SimSun", "SimHei", "Microsoft YaHei"])
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
        self.color_button.setStyleSheet(f"background-color: {self._color.name()};")
        self.color_button.clicked.connect(self._choose_color)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        text_layout.addLayout(color_layout)
        
        layout.addWidget(text_group)

        # 图片水印设置
        image_group = QGroupBox("图片水印设置")
        image_layout = QVBoxLayout(image_group)
        self.select_image_btn = QPushButton("选择图片")
        self.select_image_btn.clicked.connect(self._choose_image)
        self.image_path_label = QLabel("未选择图片")
        image_layout.addWidget(self.select_image_btn)
        image_layout.addWidget(self.image_path_label)
        layout.addWidget(image_group)

        # 通用设置
        common_group = QGroupBox("通用设置")
        common_layout = QVBoxLayout(common_group)
        
        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self._on_settings_changed)
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        common_layout.addLayout(opacity_layout)

        # 旋转
        rotation_layout = QHBoxLayout()
        rotation_label = QLabel("旋转:")
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setRange(0, 360)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self._on_settings_changed)
        rotation_layout.addWidget(rotation_label)
        rotation_layout.addWidget(self.rotation_slider)
        common_layout.addLayout(rotation_layout)

        # 缩放
        scale_layout = QHBoxLayout()
        scale_label = QLabel("缩放:")
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 200) # 10% to 200%
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self._on_settings_changed)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_slider)
        common_layout.addLayout(scale_layout)

        layout.addWidget(common_group)

        # 位置设置
        position_group = QGroupBox("位置")
        position_grid = QGridLayout(position_group)
        self.position_buttons = []
        positions = [(y, x) for y in range(3) for x in range(3)]
        for i, (y, x) in enumerate(positions):
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, pos=(x, y): self._on_position_selected(pos))
            position_grid.addWidget(btn, y, x)
            self.position_buttons.append(btn)
        layout.addWidget(position_group)

        layout.addStretch()
        self._update_position_buttons()

    def _on_settings_changed(self):
        self.watermarkChanged.emit(self.get_settings())

    def _choose_color(self):
        color = QColorDialog.getColor(self._color)
        if color.isValid():
            self._color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")
            self._on_settings_changed()

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path_label.setText(path)
            self._on_settings_changed()

    def _on_position_selected(self, grid_pos: Tuple[int, int]):
        """九宫格按钮点击槽函数"""
        x, y = grid_pos
        # 将九宫格索引转换为相对坐标
        rel_x = 0.05 if x == 0 else 0.5 if x == 1 else 0.95
        rel_y = 0.05 if y == 0 else 0.5 if y == 1 else 0.95
        self._current_position_relative = (rel_x, rel_y)
        self._update_position_buttons()
        self._on_settings_changed()

    def update_position(self, position: Tuple[float, float]):
        """更新位置，由外部调用（如拖拽结束）"""
        self._current_position_relative = position
        self._update_position_buttons()
        # 拖拽结束后，我们仍然需要发出信号，以确保所有状态同步
        self._on_settings_changed()

    def _update_position_buttons(self):
        """根据当前相对位置更新九宫格按钮的选中状态"""
        # 取消所有按钮的选中状态
        for btn in self.position_buttons:
            btn.setChecked(False)

        # 试图找到匹配的九宫格按钮并选中它
        x_rel, y_rel = self._current_position_relative
        x_grid, y_grid = -1, -1

        if abs(x_rel - 0.05) < 0.01: x_grid = 0
        elif abs(x_rel - 0.5) < 0.01: x_grid = 1
        elif abs(x_rel - 0.95) < 0.01: x_grid = 2

        if abs(y_rel - 0.05) < 0.01: y_grid = 0
        elif abs(y_rel - 0.5) < 0.01: y_grid = 1
        elif abs(y_rel - 0.95) < 0.01: y_grid = 2

        if x_grid != -1 and y_grid != -1:
            index = y_grid * 3 + x_grid
            if 0 <= index < len(self.position_buttons):
                self.position_buttons[index].setChecked(True)

    def get_settings(self) -> dict:
        """获取所有水印设置"""
        return {
            "text": self.text_input.text(),
            "font_name": self.font_combo.currentText(),
            "font_size": self.size_spin.value(),
            "color": (self._color.red(), self._color.green(), self._color.blue()),
            "opacity": self.opacity_slider.value(),
            "rotation": self.rotation_slider.value(),
            "scale": self.scale_slider.value() / 100.0,
            "position": self._current_position_relative,
            "image_path": self.image_path_label.text() if self.image_path_label.text() != "未选择图片" else None,
        }

    def set_settings(self, settings: dict):
        """根据传入的设置字典更新UI"""
        self.text_input.setText(settings.get('text', ''))
        self.font_combo.setCurrentText(settings.get('font_name', 'Arial'))
        self.size_spin.setValue(settings.get('font_size', 36))
        
        color_tuple = settings.get('color', (0, 0, 0))
        self._color = QColor(*color_tuple)
        self.color_button.setStyleSheet(f"background-color: {self._color.name()};")
        
        self.opacity_slider.setValue(settings.get('opacity', 255))
        self.rotation_slider.setValue(settings.get('rotation', 0))
        self.scale_slider.setValue(int(settings.get('scale', 1.0) * 100))
        
        image_path = settings.get('image_path')
        if image_path:
            self.image_path_label.setText(image_path)
        else:
            self.image_path_label.setText("未选择图片")
            
        self._current_position_relative = settings.get('position', (0.05, 0.05))
        self._update_position_buttons()
        
        # 更新设置后，发出信号以刷新预览
        self._on_settings_changed()