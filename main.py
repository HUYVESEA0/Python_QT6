import sys
import os
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from utils.logger import Logger

def main():
    """Hàm chính khởi động ứng dụng."""
    # Thiết lập logging
    Logger.setup(log_file="logs/student_management.log")
    
    # Khởi tạo ứng dụng
    app = QApplication(sys.argv)
    
    # Tùy chỉnh kiểu dáng nếu có file CSS
    style_path = "resources/styles/styles.qss"
    if os.path.exists(style_path):
        try:
            with open(style_path, "r") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            Logger.log_exception(e)
    else:
        Logger.get_logger(__name__).warning(f"Không tìm thấy file styles: {style_path}")
        
    # Khởi tạo cửa sổ chính
    window = MainWindow()
    window.show()
    
    # Chạy ứng dụng
    sys.exit(app.exec())

if __name__ == "__main__":
    main()