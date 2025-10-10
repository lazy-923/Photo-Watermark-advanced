import sys
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow

def main():
    """应用程序主入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setOrganizationName("YourCompany")
    app.setApplicationName("Photo Watermark Advanced")
    
    # 加载和应用样式表
    try:
        with open("styles/style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: stylesheet 'styles/style.qss' not found.")

    main_win = MainWindow()
    main_win.show()
    
    return app.exec()

if __name__ == '__main__':
    # 为了让这个脚本也能被直接运行（主要用于开发），
    # 我们需要临时将项目根目录添加到 sys.path
    import os
    # 将当前文件路径的上两级目录（即项目根目录）添加到 sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # 现在，我们可以像从外部调用一样，使用绝对路径导入
    from src.ui.main_window import MainWindow
    
    sys.exit(main())