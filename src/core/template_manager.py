"""
水印模板管理模块
"""
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class WatermarkTemplate:
    """水印模板类"""
    def __init__(self, name: str, settings: Dict):
        self.name = name
        self.settings = settings
        self.created_at = datetime.now().isoformat()
        self.last_used = self.created_at
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'name': self.name,
            'settings': self.settings,
            'created_at': self.created_at,
            'last_used': self.last_used
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'WatermarkTemplate':
        """从字典创建模板"""
        template = cls(data['name'], data['settings'])
        template.created_at = data['created_at']
        template.last_used = data['last_used']
        return template

class TemplateManager:
    """模板管理类"""
    
    def __init__(self, templates_file: str = 'templates.json'):
        self.templates_file = templates_file
        self.templates: List[WatermarkTemplate] = []
        self.load_templates()
        
    def load_templates(self) -> None:
        """加载模板"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = [
                        WatermarkTemplate.from_dict(template_data)
                        for template_data in data
                    ]
            except Exception as e:
                print(f"Error loading templates: {e}")
                self.templates = []
                
    def save_templates(self) -> bool:
        """保存模板"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [template.to_dict() for template in self.templates],
                    f,
                    indent=4,
                    ensure_ascii=False
                )
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            return False
            
    def add_template(self, name: str, settings: Dict) -> bool:
        """添加模板
        
        Args:
            name: 模板名称
            settings: 水印设置
            
        Returns:
            bool: 是否成功添加
        """
        # 检查是否存在同名模板
        if any(t.name == name for t in self.templates):
            return False
            
        template = WatermarkTemplate(name, settings)
        self.templates.append(template)
        return self.save_templates()
        
    def update_template(self, name: str, settings: Dict) -> bool:
        """更新模板
        
        Args:
            name: 模板名称
            settings: 新的水印设置
            
        Returns:
            bool: 是否成功更新
        """
        for template in self.templates:
            if template.name == name:
                template.settings = settings
                template.last_used = datetime.now().isoformat()
                return self.save_templates()
        return False
        
    def delete_template(self, name: str) -> bool:
        """删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 是否成功删除
        """
        initial_length = len(self.templates)
        self.templates = [t for t in self.templates if t.name != name]
        if len(self.templates) != initial_length:
            return self.save_templates()
        return False
        
    def get_template(self, name: str) -> Optional[Dict]:
        """获取模板设置
        
        Args:
            name: 模板名称
            
        Returns:
            Optional[Dict]: 模板设置，如果不存在返回None
        """
        for template in self.templates:
            if template.name == name:
                template.last_used = datetime.now().isoformat()
                self.save_templates()
                return template.settings
        return None
        
    def get_template_names(self) -> List[str]:
        """获取所有模板名称
        
        Returns:
            List[str]: 模板名称列表
        """
        return [template.name for template in self.templates]
        
    def get_recent_templates(self, limit: int = 5) -> List[Dict]:
        """获取最近使用的模板
        
        Args:
            limit: 返回的模板数量
            
        Returns:
            List[Dict]: 模板列表
        """
        sorted_templates = sorted(
            self.templates,
            key=lambda t: t.last_used,
            reverse=True
        )
        return [
            {'name': t.name, 'settings': t.settings}
            for t in sorted_templates[:limit]
        ]