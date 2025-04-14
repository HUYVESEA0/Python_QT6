import sys
import os
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from views.login_view import LoginDialog
from utils.logger import Logger
from DB.db_manager import DatabaseManager
from controllers.user_controller import UserController

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
    
    # Khởi tạo database manager
    db_manager = DatabaseManager()
    
    # Khởi tạo user controller
    user_controller = UserController(db_manager)
    
    # Hiển thị màn hình đăng nhập
    login_dialog = LoginDialog(user_controller)
    
    # Biến lưu thông tin người dùng đăng nhập
    current_user = None
    
    def on_login_successful(user):
        nonlocal current_user
        current_user = user
    
    # Kết nối signal khi đăng nhập thành công
    login_dialog.loginSuccessful.connect(on_login_successful)
    
    # Nếu đăng nhập thành công, hiển thị cửa sổ chính
    if login_dialog.exec():
        # Khởi tạo cửa sổ chính với thông tin người dùng
        window = MainWindow(current_user)
        window.show()
        
        # Chạy ứng dụng
        sys.exit(app.exec())
    else:
        # Người dùng đã hủy đăng nhập
        db_manager.close()
        sys.exit(0)

if __name__ == "__main__":
    main()