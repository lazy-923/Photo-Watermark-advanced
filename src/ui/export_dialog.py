from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout,
    QComboBox, QSpinBox, QDialogButtonBox, QFileDialog
)

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
