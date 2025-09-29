"""
图片水印应用的主入口
"""
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

def exception_hook(exctype, value, tb):
    """全局异常处理器"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(error_msg)  # 打印到控制台
    QMessageBox.critical(None, "错误", f"程序发生错误：\n{str(value)}")
    
def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        # 设置全局异常处理器
        sys.excepthook = exception_hook
        
        return app.exec()
    except Exception as e:
        QMessageBox.critical(None, "错误", f"启动失败：{str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())