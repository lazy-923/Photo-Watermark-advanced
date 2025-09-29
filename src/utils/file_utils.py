"""
工具函数模块
"""
import os
from typing import List, Tuple

def get_supported_formats() -> List[str]:
    """获取支持的图片格式列表
    
    Returns:
        List[str]: 支持的文件扩展名列表
    """
    return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

def is_image_file(filename: str) -> bool:
    """检查文件是否为支持的图片格式
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为支持的图片文件
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in get_supported_formats()

def generate_output_filename(input_path: str, prefix: str = '', 
                           suffix: str = '_watermarked',
                           output_dir: str = None) -> str:
    """生成输出文件名
    
    Args:
        input_path: 输入文件路径
        prefix: 文件名前缀
        suffix: 文件名后缀
        output_dir: 输出目录
        
    Returns:
        str: 输出文件路径
    """
    dirname, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    new_name = f"{prefix}{name}{suffix}{ext}"
    
    if output_dir:
        return os.path.join(output_dir, new_name)
    return os.path.join(dirname, new_name)