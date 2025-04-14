import os
import json
import logging
from PyQt6.QtCore import QSettings, QCoreApplication

class ConfigManager:
    """
    Quản lý cấu hình và cài đặt của ứng dụng
    """
    
    def __init__(self, config_file="config.json"):
        # Đảm bảo thư mục data tồn tại
        os.makedirs("data", exist_ok=True)
        
        # Đường dẫn đến file cấu hình
        self.config_file = os.path.join("data", config_file)
        
        # Cấu hình mặc định
        self.default_config = {
            "app": {
                "name": "Hệ thống Quản lý Sinh viên",
                "version": "2.0.0",
                "language": "vi_VN",
                "max_log_files": 10,
                "max_backup_files": 5,
                "auto_backup": True,
                "backup_interval_days": 7
            },
            "database": {
                "name": "student_management.db",
                "backup_on_exit": True
            },
            "ui": {
                "theme": "light",
                "font_size": 10,
                "show_welcome": True,
                "table_rows_per_page": 50,
                "notification_duration": 3000
            },
            "export": {
                "default_format": "excel",
                "default_directory": "exports",
                "include_headers": True
            }
        }
        
        # Cấu hình hiện tại
        self.config = self.load_config()
        
        # Khởi tạo QSettings
        QCoreApplication.setOrganizationName("MyOrg")
        QCoreApplication.setApplicationName("StudentManagement")
        self.settings = QSettings()
    
    def load_config(self):
        """
        Tải cấu hình từ file, hoặc tạo mới nếu không tồn tại
        
        Returns:
            dict: Cấu hình đã tải
        """
        try:
            if not os.path.exists(self.config_file):
                return self.create_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Đảm bảo tất cả các khóa mặc định có trong cấu hình
            self._ensure_default_keys(config)
                
            return config
                
        except Exception as e:
            logging.error(f"Lỗi khi tải file cấu hình: {e}")
            return self.create_default_config()
    
    def _ensure_default_keys(self, config):
        """
        Đảm bảo tất cả các khóa mặc định có trong cấu hình
        
        Args:
            config (dict): Cấu hình cần kiểm tra và cập nhật
        """
        for section, settings in self.default_config.items():
            if section not in config:
                config[section] = {}
                
            for key, value in settings.items():
                if key not in config[section]:
                    config[section][key] = value
    
    def create_default_config(self):
        """
        Tạo và lưu cấu hình mặc định
        
        Returns:
            dict: Cấu hình mặc định
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, ensure_ascii=False, indent=4)
                
            return self.default_config
                
        except Exception as e:
            logging.error(f"Lỗi khi tạo file cấu hình mặc định: {e}")
            return dict(self.default_config)  # Trả về bản sao của cấu hình mặc định
    
    def save_config(self):
        """
        Lưu cấu hình hiện tại vào file
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
                
            return True
                
        except Exception as e:
            logging.error(f"Lỗi khi lưu file cấu hình: {e}")
            return False
    
    def get(self, section, key, default=None):
        """
        Lấy giá trị cấu hình
        
        Args:
            section (str): Phần cấu hình
            key (str): Khóa cấu hình
            default: Giá trị mặc định nếu không tìm thấy
            
        Returns:
            Giá trị cấu hình hoặc giá trị mặc định
        """
        try:
            return self.config[section][key]
        except KeyError:
            if default is not None:
                return default
            
            # Thử lấy từ cấu hình mặc định
            try:
                return self.default_config[section][key]
            except KeyError:
                return None
    
    def set(self, section, key, value):
        """
        Thiết lập giá trị cấu hình
        
        Args:
            section (str): Phần cấu hình
            key (str): Khóa cấu hình
            value: Giá trị cấu hình mới
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            if section not in self.config:
                self.config[section] = {}
                
            self.config[section][key] = value
            return self.save_config()
                
        except Exception as e:
            logging.error(f"Lỗi khi thiết lập giá trị cấu hình: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """
        Lấy giá trị từ QSettings
        
        Args:
            key (str): Khóa cài đặt
            default: Giá trị mặc định
            
        Returns:
            Giá trị cài đặt hoặc giá trị mặc định
        """
        return self.settings.value(key, default)
    
    def set_setting(self, key, value):
        """
        Thiết lập giá trị cho QSettings
        
        Args:
            key (str): Khóa cài đặt
            value: Giá trị cần thiết lập
        """
        self.settings.setValue(key, value)
