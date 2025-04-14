import os
import sys
import platform
import logging

class PathHelper:
    """
    Lớp tiện ích xử lý đường dẫn trong ứng dụng giúp tránh các lỗi về đường dẫn
    trên các hệ điều hành khác nhau
    """
    
    @staticmethod
    def get_app_root():
        """
        Lấy đường dẫn thư mục gốc của ứng dụng
        
        Returns:
            str: Đường dẫn thư mục gốc
        """
        if getattr(sys, 'frozen', False):
            # Nếu ứng dụng được đóng gói với PyInstaller
            return os.path.dirname(sys.executable)
        else:
            # Nếu đang chạy từ mã nguồn
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    @staticmethod
    def get_resource_path(relative_path):
        """
        Lấy đường dẫn đầy đủ đến tài nguyên
        
        Args:
            relative_path (str): Đường dẫn tương đối từ thư mục gốc ứng dụng
            
        Returns:
            str: Đường dẫn đầy đủ tới tài nguyên
        """
        # Chuẩn hóa đường dẫn cho phù hợp với hệ điều hành
        relative_path = os.path.normpath(relative_path)
        
        # Tạo đường dẫn đầy đủ
        full_path = os.path.join(PathHelper.get_app_root(), relative_path)
        
        return full_path
        
    @staticmethod
    def ensure_dir(path):
        """
        Đảm bảo thư mục tồn tại, tạo nếu chưa có
        
        Args:
            path (str): Đường dẫn thư mục cần kiểm tra/tạo
            
        Returns:
            bool: True nếu thư mục đã tồn tại hoặc được tạo thành công
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            return True
        except Exception as e:
            logging.error(f"Lỗi khi tạo thư mục {path}: {e}")
            return False
    
    @staticmethod
    def normalize_path(path):
        """
        Chuẩn hóa đường dẫn cho phù hợp với hệ điều hành hiện tại
        
        Args:
            path (str): Đường dẫn cần chuẩn hóa
            
        Returns:
            str: Đường dẫn đã chuẩn hóa
        """
        return os.path.normpath(path)
