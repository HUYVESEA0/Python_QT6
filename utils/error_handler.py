import sys
import traceback
import logging
import sqlite3  # Thêm dòng này
from enum import Enum, auto
from PyQt6.QtWidgets import QMessageBox
from utils.logger import Logger


class ErrorSeverity(Enum):
    """Mức độ nghiêm trọng của lỗi"""
    INFO = auto()        # Thông tin, không phải lỗi nghiêm trọng
    WARNING = auto()      # Cảnh báo, có thể tiếp tục nhưng có thể gặp vấn đề
    ERROR = auto()        # Lỗi, không thể tiếp tục thao tác hiện tại
    CRITICAL = auto()     # Lỗi nghiêm trọng, cần đóng ứng dụng


class AppException(Exception):
    """Lớp cơ sở cho tất cả các ngoại lệ trong ứng dụng"""
    
    def __init__(self, message, severity=ErrorSeverity.ERROR, cause=None):
        """
        Khởi tạo ngoại lệ
        
        Args:
            message (str): Thông báo lỗi
            severity (ErrorSeverity): Mức độ nghiêm trọng của lỗi
            cause (Exception, optional): Ngoại lệ gốc gây ra lỗi này
        """
        self.message = message
        self.severity = severity
        self.cause = cause
        super().__init__(message)


class DatabaseException(AppException):
    """Ngoại lệ liên quan đến cơ sở dữ liệu"""
    pass


class ConfigException(AppException):
    """Ngoại lệ liên quan đến cấu hình"""
    pass


class NetworkException(AppException):
    """Ngoại lệ liên quan đến mạng"""
    pass


class FileException(AppException):
    """Ngoại lệ liên quan đến file"""
    pass


class ValidationException(AppException):
    """Ngoại lệ liên quan đến kiểm tra dữ liệu"""
    def __init__(self, message, field=None, severity=ErrorSeverity.WARNING, cause=None):
        self.field = field
        super().__init__(message, severity, cause)


class ValidationError(Exception):
    """Exception raised for validation errors in input data."""
    pass


class ErrorHandler:
    """
    Lớp xử lý lỗi tập trung cho ứng dụng.
    Cung cấp các phương thức để xử lý ngoại lệ một cách nhất quán.
    """
    
    @staticmethod
    def setup_exception_handling():
        """Thiết lập xử lý ngoại lệ toàn cục"""
        sys.excepthook = ErrorHandler.global_exception_handler
    
    @staticmethod
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """
        Xử lý ngoại lệ không bắt được ở mức toàn cục
        
        Args:
            exc_type: Loại ngoại lệ
            exc_value: Giá trị ngoại lệ
            exc_traceback: Traceback
        """
        # Bỏ qua KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        # Ghi log chi tiết
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
    
    @staticmethod
    def handle_exception(exception, show_dialog=True, parent=None):
        """
        Xử lý ngoại lệ theo mức độ nghiêm trọng
        
        Args:
            exception (Exception): Ngoại lệ cần xử lý
            show_dialog (bool): Có hiển thị dialog không
            parent (QWidget): Widget cha cho dialog
            
        Returns:
            bool: True nếu ngoại lệ đã được xử lý, False nếu nên dừng thao tác
        """
        # Chuyển đổi ngoại lệ thành AppException nếu cần
        if not isinstance(exception, AppException):
            app_ex = ErrorHandler.convert_exception(exception)
        else:
            app_ex = exception
            
        # Log theo mức độ nghiêm trọng
        message = f"{app_ex.message}"
        if app_ex.cause:
            message += f" Nguyên nhân: {str(app_ex.cause)}"
            
        if app_ex.severity == ErrorSeverity.INFO:
            logging.info(message)
        elif app_ex.severity == ErrorSeverity.WARNING:
            logging.warning(message)
        elif app_ex.severity == ErrorSeverity.ERROR:
            logging.error(message)
        elif app_ex.severity == ErrorSeverity.CRITICAL:
            logging.critical(message)
            
        # Hiển thị dialog nếu cần
        if show_dialog:
            ErrorHandler.show_error_dialog(app_ex, parent)
            
        # Trả về False nếu là lỗi nghiêm trọng để caller có thể dừng thao tác
        return app_ex.severity in (ErrorSeverity.INFO, ErrorSeverity.WARNING)
    
    @staticmethod
    def convert_exception(exception):
        """
        Chuyển đổi ngoại lệ thành AppException
        
        Args:
            exception (Exception): Ngoại lệ cần chuyển đổi
            
        Returns:
            AppException: Ngoại lệ đã chuyển đổi
        """
        message = str(exception)
        severity = ErrorSeverity.ERROR
        
        # Phân loại theo loại exception
        if isinstance(exception, (ValueError, TypeError, ValidationError)):
            return ValidationException(message, severity=severity, cause=exception)
        elif isinstance(exception, (FileNotFoundError, PermissionError, OSError)):
            return FileException(message, severity=severity, cause=exception)
        elif isinstance(exception, (ConnectionError, TimeoutError)):
            return NetworkException(message, severity=severity, cause=exception)
        elif isinstance(exception, (sqlite3.Error, 
                                   sqlite3.IntegrityError, 
                                   sqlite3.OperationalError)):
            return DatabaseException(message, severity=severity, cause=exception)
        else:
            return AppException(message, severity=severity, cause=exception)
    
    @staticmethod
    def show_error_dialog(app_exception, parent=None):
        """
        Hiển thị dialog lỗi phù hợp với loại lỗi
        
        Args:
            app_exception (AppException): Ngoại lệ cần hiển thị
            parent (QWidget): Widget cha cho dialog
        """
        dialog = QMessageBox(parent)
        
        # Thiết lập icon theo mức độ nghiêm trọng
        if app_exception.severity == ErrorSeverity.INFO:
            dialog.setIcon(QMessageBox.Icon.Information)
            dialog.setWindowTitle("Thông tin")
        elif app_exception.severity == ErrorSeverity.WARNING:
            dialog.setIcon(QMessageBox.Icon.Warning)
            dialog.setWindowTitle("Cảnh báo")
        elif app_exception.severity == ErrorSeverity.ERROR:
            dialog.setIcon(QMessageBox.Icon.Critical)
            dialog.setWindowTitle("Lỗi")
        elif app_exception.severity == ErrorSeverity.CRITICAL:
            dialog.setIcon(QMessageBox.Icon.Critical)
            dialog.setWindowTitle("Lỗi nghiêm trọng")
            
        # Thiết lập nội dung
        dialog.setText(app_exception.message)
        
        # Hiển thị thông tin về nguyên nhân nếu có
        if app_exception.cause:
            cause_details = str(app_exception.cause)
            dialog.setInformativeText(f"Chi tiết: {cause_details}")
            
            # Thêm traceback nếu có
            try:
                if hasattr(app_exception.cause, '__traceback__') and app_exception.cause.__traceback__:
                    tb_str = "".join(traceback.format_tb(app_exception.cause.__traceback__))
                    dialog.setDetailedText(tb_str)
            except:
                pass
                
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    @staticmethod
    def safe_call(func, *args, error_message="Đã xảy ra lỗi khi thực hiện thao tác", 
                 show_dialog=True, parent=None, **kwargs):
        """
        Gọi hàm an toàn với xử lý ngoại lệ
        
        Args:
            func (callable): Hàm cần gọi
            error_message (str): Thông báo lỗi khi có ngoại lệ
            show_dialog (bool): Có hiển thị dialog không
            parent (QWidget): Widget cha cho dialog
            *args, **kwargs: Tham số cho hàm
            
        Returns:
            tuple: (result, success) - Kết quả trả về và trạng thái thành công
        """
        try:
            result = func(*args, **kwargs)
            return result, True
        except Exception as e:
            app_ex = ErrorHandler.convert_exception(e)
            app_ex.message = f"{error_message}. {app_ex.message}"
            ErrorHandler.handle_exception(app_ex, show_dialog, parent)
            return None, False
