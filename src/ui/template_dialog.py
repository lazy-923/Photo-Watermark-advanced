"""
模板管理对话框
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QListWidget, QListWidgetItem,
                           QInputDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from core.template_manager import TemplateManager

class TemplateDialog(QDialog):
    """模板管理对话框"""
    
    # 定义信号
    templateSelected = pyqtSignal(dict)  # 当选择模板时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self._init_ui()
        
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("水印模板管理")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self._load_template)
        layout.addWidget(self.template_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 保存当前设置为模板
        save_btn = QPushButton("保存当前设置为模板")
        save_btn.clicked.connect(self._save_current_settings)
        button_layout.addWidget(save_btn)
        
        # 删除模板
        delete_btn = QPushButton("删除模板")
        delete_btn.clicked.connect(self._delete_template)
        button_layout.addWidget(delete_btn)
        
        # 加载模板
        load_btn = QPushButton("加载模板")
        load_btn.clicked.connect(self._load_template)
        button_layout.addWidget(load_btn)
        
        layout.addLayout(button_layout)
        
        # 更新模板列表
        self._update_template_list()
        
    def _update_template_list(self):
        """更新模板列表"""
        self.template_list.clear()
        for name in self.template_manager.get_template_names():
            self.template_list.addItem(name)
            
    def _save_current_settings(self):
        """保存当前设置为新模板"""
        # 获取当前水印设置
        current_settings = self.parent().watermark_editor.get_settings() \
            if self.parent() else {}
            
        # 获取模板名称
        name, ok = QInputDialog.getText(
            self,
            "保存模板",
            "请输入模板名称:"
        )
        
        if ok and name:
            if self.template_manager.add_template(name, current_settings):
                self._update_template_list()
                QMessageBox.information(self, "成功", "模板保存成功！")
            else:
                QMessageBox.warning(self, "错误", "模板名称已存在！")
                
    def _delete_template(self):
        """删除选中的模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的模板！")
            return
            
        name = current_item.text()
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除模板 '{name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.template_manager.delete_template(name):
                self._update_template_list()
                QMessageBox.information(self, "成功", "模板删除成功！")
            else:
                QMessageBox.warning(self, "错误", "删除模板失败！")
                
    def _load_template(self):
        """加载选中的模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要加载的模板！")
            return
            
        name = current_item.text()
        settings = self.template_manager.get_template(name)
        
        if settings:
            self.templateSelected.emit(settings)
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "加载模板失败！")