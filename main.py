import sys
import logging
from PyQt6.QtWidgets import QApplication, QDialog  # pylint: disable=no-name-in-module
from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.cleanup import cleanup_temp_files
from utils.error_handler import ErrorHandler, DatabaseException, ConfigException, ErrorSeverity
from utils.initialize_data import initialize_all_data
from utils.theme_manager import ThemeManager

# Other application imports
from views.main_window import MainWindow
from views.login_dialog import LoginDialog
from controllers.user_controller import UserController

def close_database(db_manager):
    """Đóng kết nối cơ sở dữ liệu an toàn"""
    try:
        if db_manager and hasattr(db_manager, 'close'):
            db_manager.close()
            logging.info("Đã đóng kết nối cơ sở dữ liệu")
    except (AttributeError, RuntimeError, OSError) as e:
        logging.error("Lỗi khi đóng kết nối cơ sở dữ liệu: %s", str(e))

def main():
    """Hàm chính khởi động ứng dụng với giao diện mới."""
    db_manager = None
    app = None
    
    try:
        # Thiết lập xử lý ngoại lệ toàn cục
        ErrorHandler.setup_exception_handling()
        
        # Thiết lập logger
        Logger.setup()
        logging.info("Đang khởi động ứng dụng...")
        
        # Tạo ConfigManager để quản lý cấu hình và kiểm tra phụ thuộc
        config_manager = ConfigManager()
        logging.info("ConfigManager đã khởi tạo")
        
        # Kiểm tra đường dẫn cơ sở dữ liệu
        db_path = config_manager.get_db_path()
        logging.info("Đường dẫn cơ sở dữ liệu: %s", db_path)
        
        if not db_path:
            raise ConfigException(
                "Không thể xác định đường dẫn đến cơ sở dữ liệu", 
                ErrorSeverity.CRITICAL
            )
        
        # Kiểm tra các thư viện phụ thuộc
        if not config_manager.check_all_required_dependencies():
            # Lấy danh sách các gói bị thiếu
            missing_packages = []
            for module_name, pip_package in config_manager.required_packages.items():
                if not config_manager.check_dependency(module_name):
                    missing_packages.append(pip_package)
                    
            # Tạo và hiển thị thông báo lỗi
            error_msg = "Thiếu các thư viện bắt buộc: " + ", ".join(missing_packages)
            install_cmd = f"pip install {' '.join(missing_packages)}"
            raise ConfigException(
                f"{error_msg}\n\nVui lòng cài đặt các thư viện trên bằng lệnh:\n{install_cmd}",
                ErrorSeverity.CRITICAL
            )
            
        # Tạo ứng dụng
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Thiết lập kiểu giao diện
        
        # Dọn dẹp file tạm từ phiên trước (nếu có)
        cleanup_temp_files()
        
        # Initialize theme manager early
        theme_manager = ThemeManager(config_manager)
        
        # Khởi tạo quản lý cơ sở dữ liệu
        try:
            from DB.db_manager import DatabaseManager
            db_path = config_manager.get_db_path()
            if not db_path:
                raise ConfigException(
                    "Không thể xác định đường dẫn đến cơ sở dữ liệu", 
                    ErrorSeverity.CRITICAL
                )
                
            db_manager = DatabaseManager(db_path)
            # Kiểm tra kết nối đến cơ sở dữ liệu
            if not db_manager.check_database_integrity():
                raise DatabaseException(
                    "Kiểm tra tính toàn vẹn cơ sở dữ liệu thất bại", 
                    ErrorSeverity.CRITICAL
                )
            
            # Initialize application data
            initialize_all_data(db_path)
                
            user_controller = UserController(db_manager)
        except ImportError as e:
            raise ConfigException(
                f'Không thể import module DB.db_manager: {str(e)}',  
                ErrorSeverity.CRITICAL, 
                cause=e
            ) from e
        except Exception as e:
            raise DatabaseException(
                f'Không thể kết nối đến cơ sở dữ liệu: {str(e)}', 
                ErrorSeverity.CRITICAL, 
                cause=e
            ) from e
        
        # Apply theme before creating the login dialog
        theme_manager.apply_theme()
        
        # Hiển thị dialog đăng nhập
        login_dialog = LoginDialog(user_controller, theme_manager)
        login_result = login_dialog.exec()
        
        if login_result == QDialog.DialogCode.Accepted:
            # Người dùng đã đăng nhập thành công
            current_user = login_dialog.get_user()
            if not current_user:
                raise DatabaseException(
                    "Không thể lấy thông tin người dùng sau khi đăng nhập", 
                    ErrorSeverity.ERROR
                )
            
            # Khởi tạo và hiển thị cửa sổ chính
            window = MainWindow(current_user)
            
            # Kết nối sự kiện đóng ứng dụng với việc đóng cơ sở dữ liệu
            app.aboutToQuit.connect(lambda: close_database(db_manager))
            
            window.show()
            
            # Chạy vòng lặp sự kiện
            return app.exec()
        else:
            # Người dùng hủy đăng nhập
            logging.info("Người dùng đã hủy đăng nhập")
            close_database(db_manager)
            return 0
            
    except (ConfigException, DatabaseException) as e:
        # These are already properly handled custom exceptions
        ErrorHandler.handle_exception(e, True)
        close_database(db_manager)
        return 1
    except (ImportError, ModuleNotFoundError) as e:
        # Handle missing modules specifically
        error = ConfigException(f"Missing required module: {str(e)}", ErrorSeverity.CRITICAL, cause=e)
        ErrorHandler.handle_exception(error, True)
        close_database(db_manager)
        return 1
    except (OSError, IOError) as e:
        # Handle file system and I/O errors
        error = ConfigException(f"File system error: {str(e)}", ErrorSeverity.CRITICAL, cause=e)
        ErrorHandler.handle_exception(error, True)
        close_database(db_manager)
        return 1
    except Exception as e:  # pylint: disable=broad-exception-caught

        logging.critical("Unexpected error occurred - this should be investigated: %s", str(e), exc_info=True)
        ErrorHandler.handle_exception(e, True)
        close_database(db_manager)
        return 1
    finally:
        # Đảm bảo dọn dẹp tài nguyên ngay cả khi có lỗi
        cleanup_temp_files()

if __name__ == "__main__":
    sys.exit(main())