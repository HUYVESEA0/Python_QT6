import sys
import os
import traceback
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

from utils.logger import Logger
from utils.path_helper import PathHelper
from utils.config_manager import ConfigManager
from utils.cleanup import cleanup_temp_files
from views.main_window import MainWindow
from views.login_dialog import LoginDialog
from controllers.user_controller import UserController
from utils.initialize_data import initialize_all_data

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

def close_database(db_manager):
    """Đóng kết nối cơ sở dữ liệu an toàn"""
    try:
        if db_manager and hasattr(db_manager, 'close'):
            db_manager.close()
            logging.info("Đã đóng kết nối cơ sở dữ liệu")
    except Exception as e:
        logging.error(f"Lỗi khi đóng kết nối cơ sở dữ liệu: {str(e)}")

def main():
    """Hàm chính khởi động ứng dụng với giao diện mới."""
    db_manager = None
    app = None
    
    try:
        # Thiết lập xử lý ngoại lệ toàn cục
        sys.excepthook = exception_hook
        
        # Tạo ConfigManager để quản lý cấu hình và kiểm tra phụ thuộc
        config_manager = ConfigManager()
        
        # Ensure the config_manager has loaded properly
        logging.info("ConfigManager initialized")
        
        # Check if database path exists
        db_path = config_manager.get_db_path()
        logging.info(f"Database path: {db_path}")
        
        if not db_path:
            raise ValueError("Không thể xác định đường dẫn đến cơ sở dữ liệu")
        
        # Kiểm tra phụ thuộc
        if not config_manager.check_all_required_dependencies():
            # Lấy danh sách các gói bị thiếu
            missing_packages = []
            for module_name, pip_package in config_manager.required_packages.items():
                if not config_manager.check_dependency(module_name):
                    missing_packages.append(pip_package)
                    
            # Hiển thị thông báo lỗi
            error_msg = "Thiếu các thư viện bắt buộc: " + ", ".join(missing_packages)
            QMessageBox.critical(None, "Lỗi phụ thuộc", 
                                f"{error_msg}\n\nVui lòng cài đặt các thư viện trên bằng lệnh:\npip install {' '.join(missing_packages)}")
            return
            
        # Tạo ứng dụng
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Thiết lập kiểu giao diện
        
        # Dọn dẹp file tạm từ phiên trước (nếu có)
        cleanup_temp_files()
        
        # Khởi tạo quản lý cơ sở dữ liệu
        try:
            from DB.db_manager import DatabaseManager
            db_path = config_manager.get_db_path()
            if not db_path:
                raise ValueError("Không thể xác định đường dẫn đến cơ sở dữ liệu")
                
            db_manager = DatabaseManager(db_path)
            # Kiểm tra kết nối đến cơ sở dữ liệu
            if not db_manager.check_database_integrity():
                raise ConnectionError("Kiểm tra tính toàn vẹn cơ sở dữ liệu thất bại")
            
            # Initialize application data
            initialize_all_data(db_path)
                
            user_controller = UserController(db_manager)
        except Exception as e:
            logging.critical(f"Lỗi khởi tạo cơ sở dữ liệu: {str(e)}")
            QMessageBox.critical(None, "Lỗi cơ sở dữ liệu", 
                               f"Không thể kết nối đến cơ sở dữ liệu: {str(e)}")
            return
        
        # Hiển thị dialog đăng nhập
        login_dialog = LoginDialog(user_controller)
        login_result = login_dialog.exec()
        
        if login_result == QDialog.DialogCode.Accepted:
            try:
                current_user = login_dialog.get_user()
                if not current_user:
                    raise ValueError("Không thể lấy thông tin người dùng sau khi đăng nhập")
                
                # Khởi tạo và hiển thị cửa sổ chính
                window = MainWindow(current_user)
                
                # Kết nối sự kiện đóng ứng dụng với việc đóng cơ sở dữ liệu
                app.aboutToQuit.connect(lambda: close_database(db_manager))
                
                window.show()
                
                # Chạy vòng lặp sự kiện
                return app.exec()
            except Exception as e:
                logging.critical(f"Lỗi khởi tạo cửa sổ chính: {str(e)}")
                QMessageBox.critical(None, "Lỗi ứng dụng", 
                                   f"Không thể khởi tạo cửa sổ chính: {str(e)}")
                # Đảm bảo cơ sở dữ liệu được đóng
                close_database(db_manager)
                return 1
        else:
            logging.info("Người dùng đã hủy đăng nhập")
            close_database(db_manager)
            return 0
            
    except Exception as e:
        logging.critical(f"Lỗi không xử lý được: {str(e)}")
        QMessageBox.critical(None, "Lỗi không xử lý được", str(e))
        # Đảm bảo cơ sở dữ liệu được đóng
        close_database(db_manager)
        return 1
    finally:
        # Đảm bảo dọn dẹp tài nguyên ngay cả khi có lỗi
        cleanup_temp_files()

if __name__ == "__main__":
    sys.exit(main())