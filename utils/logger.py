import logging
import os
from datetime import datetime
import sys

class Logger:
    """
    Lớp quản lý logging cho ứng dụng.
    """
    
    @staticmethod
    def setup(log_level=logging.INFO, log_file=None, console=True):
        """
        Thiết lập logging cho ứng dụng.
        
        Args:
            log_level: Mức độ log (mặc định: INFO)
            log_file: Tên file log (mặc định: student_management_{ngày}.log)
            console: Có hiển thị log ra console không (mặc định: True)
        """
        # Tạo thư mục logs nếu chưa tồn tại
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Nếu không có tên file được chỉ định, tạo tên file mặc định
        if log_file is None:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"student_management_{today}.log")
        
        # Thiết lập định dạng log
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        # Thiết lập root logger
        logger = logging.getLogger()
        logger.setLevel(log_level)
        
        # Xóa tất cả handlers hiện có để tránh ghi log trùng lặp
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        # Thêm file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
        
        # Thêm console handler nếu yêu cầu
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(log_format, date_format))
            logger.addHandler(console_handler)
        
        logging.info("Hệ thống logging đã được thiết lập")
        return logger

    @staticmethod
    def get_logger(name):
        """
        Lấy logger có tên cụ thể.
        
        Args:
            name: Tên của logger
        
        Returns:
            Logger: Đối tượng logger
        """
        return logging.getLogger(name)
    
    @staticmethod
    def log_exception(exception):
        """
        Ghi log exception.
        
        Args:
            exception: Exception cần ghi log
        """
        logging.exception(f"Exception phát sinh: {exception}")
