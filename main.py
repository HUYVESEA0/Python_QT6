import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from views.main_window import MainWindow
from views.login_dialog import LoginDialog
from utils.logger import Logger
from utils.path_helper import PathHelper
from DB.db_manager import DatabaseManager
from controllers.user_controller import UserController

def exception_hook(exc_type, exc_value, exc_traceback):
    """Xử lý ngoại lệ không bắt được"""
    # Ghi log chi tiết cho exception
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    Logger.log_exception(error_msg)
    
    # Hiển thị hộp thoại lỗi thân thiện
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setWindowTitle("Lỗi ứng dụng")
    error_dialog.setText("Đã xảy ra lỗi không xử lý được:")
    error_dialog.setInformativeText(str(exc_value))
    error_dialog.setDetailedText(error_msg)
    error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_dialog.exec()

def main():
    """Hàm chính khởi động ứng dụng."""
    try:
        # Thiết lập exception hook
        sys.excepthook = exception_hook
        
        # Thiết lập logging
        Logger.setup(log_file="logs/student_management.log")
        
        # Tạo thư mục data nếu chưa tồn tại
        PathHelper.ensure_dir("data")
        
        # Khởi tạo ứng dụng
        app = QApplication(sys.argv)
        app.setApplicationName("Hệ thống Quản lý Sinh viên")
        app.setOrganizationName("MyOrg")
        
        # Hiển thị splash screen
        splash_path = PathHelper.get_resource_path("resources/images/splash.png")
        if os.path.exists(splash_path):
            splash_pixmap = QPixmap(splash_path)
            splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
            splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
            splash.show()
            app.processEvents()
        else:
            splash = None
        
        # Tùy chỉnh kiểu dáng nếu có file CSS
        style_path = PathHelper.get_resource_path("resources/styles/styles.qss")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
            except Exception as e:
                Logger.log_exception(e)
        
        # Khởi tạo database manager
        db_manager = DatabaseManager()
        
        # Khởi tạo user controller
        user_controller = UserController(db_manager)
        
        # Biến lưu thông tin người dùng đăng nhập
        current_user = None
        
        def on_login_successful(user):
            nonlocal current_user
            current_user = user
        
        # Đợi một chút (để hiển thị splash đủ lâu)
        if splash:
            QTimer.singleShot(1500, lambda: splash.finish(None))
        
        # Hiển thị màn hình đăng nhập
        login_dialog = LoginDialog(user_controller)
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
            
    except Exception as e:
        Logger.log_exception(f"Lỗi khởi động ứng dụng: {e}")
        
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Lỗi khởi động")
        error_dialog.setText("Không thể khởi động ứng dụng")
        error_dialog.setInformativeText(str(e))
        error_dialog.setDetailedText(traceback.format_exc())
        error_dialog.exec()
        sys.exit(1)

if __name__ == "__main__":
    main()