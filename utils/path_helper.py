import os
import sys
import logging

class PathHelper:
    """
    Lớp tiện ích xử lý đường dẫn trong ứng dụng giúp tránh các lỗi về đường dẫn
    trên các hệ điều hành khác nhau
    """
    # Các hằng số đường dẫn thông dụng
    RESOURCES_DIR = "resources"
    ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
    STYLES_DIR = os.path.join(RESOURCES_DIR, "styles")
    DATA_DIR = "data"
    TEMP_DIR = "temp"
    LOGS_DIR = "logs"
    BACKUPS_DIR = os.path.join(DATA_DIR, "backups")
    
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
    def get_icon_path(icon_name):
        """
        Lấy đường dẫn đến file icon
        
        Args:
            icon_name (str): Tên file icon (với hoặc không có phần mở rộng)
            
        Returns:
            str: Đường dẫn đầy đủ đến file icon
        """
        # Thêm phần mở rộng .png nếu chưa có
        if not icon_name.lower().endswith(('.png', '.jpg', '.jpeg', '.ico')):
            icon_name = f"{icon_name}.png"
            
        icon_path = os.path.join(PathHelper.ICONS_DIR, icon_name)
        return PathHelper.get_resource_path(icon_path)
    
    @staticmethod
    def get_style_path(style_name):
        """
        Lấy đường dẫn đến file stylesheet
        
        Args:
            style_name (str): Tên file stylesheet (với hoặc không có phần mở rộng)
            
        Returns:
            str: Đường dẫn đầy đủ đến file stylesheet
        """
        # Thêm phần mở rộng .qss nếu chưa có
        if not style_name.lower().endswith('.qss'):
            style_name = f"{style_name}.qss"
            
        style_path = os.path.join(PathHelper.STYLES_DIR, style_name)
        return PathHelper.get_resource_path(style_path)
    
    @staticmethod
    def get_data_path(filename=None):
        """
        Lấy đường dẫn đến thư mục hoặc file dữ liệu
        
        Args:
            filename (str, optional): Tên file dữ liệu nếu cần
            
        Returns:
            str: Đường dẫn đầy đủ đến thư mục hoặc file dữ liệu
        """
        data_dir = PathHelper.get_resource_path(PathHelper.DATA_DIR)
        if filename:
            return os.path.join(data_dir, filename)
        return data_dir
    
    @staticmethod
    def get_temp_path(filename=None):
        """
        Lấy đường dẫn đến thư mục hoặc file tạm
        
        Args:
            filename (str, optional): Tên file tạm nếu cần
            
        Returns:
            str: Đường dẫn đầy đủ đến thư mục hoặc file tạm
        """
        temp_dir = PathHelper.get_resource_path(PathHelper.TEMP_DIR)
        # Đảm bảo thư mục tồn tại
        PathHelper.ensure_dir(temp_dir)
        
        if filename:
            return os.path.join(temp_dir, filename)
        return temp_dir
    
    @staticmethod
    def get_backup_path(filename=None):
        """
        Lấy đường dẫn đến thư mục hoặc file backup
        
        Args:
            filename (str, optional): Tên file backup nếu cần
            
        Returns:
            str: Đường dẫn đầy đủ đến thư mục hoặc file backup
        """
        backup_dir = PathHelper.get_resource_path(PathHelper.BACKUPS_DIR)
        # Đảm bảo thư mục tồn tại
        PathHelper.ensure_dir(backup_dir)
        
        if filename:
            return os.path.join(backup_dir, filename)
        return backup_dir
        
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
        except (FileNotFoundError, PermissionError, OSError) as e:
            logging.error("Lỗi khi tạo thư mục %s: %s", path, str(e))
    
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

    @staticmethod
    def is_file_exists(file_path):
        """
        Kiểm tra xem file có tồn tại hay không
        
        Args:
            file_path (str): Đường dẫn file cần kiểm tra
            
        Returns:
            bool: True nếu file tồn tại, False nếu không
        """
        return os.path.isfile(file_path)
    
    @staticmethod
    def is_dir_exists(dir_path):
        """
        Kiểm tra xem thư mục có tồn tại hay không
        
        Args:
            dir_path (str): Đường dẫn thư mục cần kiểm tra
            
        Returns:
            bool: True nếu thư mục tồn tại, False nếu không
        """
        return os.path.isdir(dir_path)
    
    @staticmethod
    def get_extension(file_path):
        """
        Lấy phần mở rộng của file
        
        Args:
            file_path (str): Đường dẫn file
            
        Returns:
            str: Phần mở rộng của file
        """
        return os.path.splitext(file_path)[1]
    
    @staticmethod
    def get_filename(file_path):
        """
        Lấy tên file từ đường dẫn
        
        Args:
            file_path (str): Đường dẫn file
            
        Returns:
            str: Tên file (bao gồm phần mở rộng)
        """
        return os.path.basename(file_path)
    
    @staticmethod
    def get_filename_without_extension(file_path):
        """
        Lấy tên file từ đường dẫn, không bao gồm phần mở rộng
        
        Args:
            file_path (str): Đường dẫn file
            
        Returns:
            str: Tên file (không bao gồm phần mở rộng)
        """
        return os.path.splitext(os.path.basename(file_path))[0]
