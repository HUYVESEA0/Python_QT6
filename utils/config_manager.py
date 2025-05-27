"""
Module quản lý cấu hình tổng hợp cho ứng dụng
"""
import os
import logging
import configparser
from pathlib import Path
from dotenv import load_dotenv
from utils.path_helper import PathHelper
import importlib

class ConfigManager:
    """Quản lý cấu hình ứng dụng"""
    
    def __init__(self, config_file_path=None):
        # Nếu có đường dẫn được cung cấp, sử dụng nó; nếu không, sử dụng đường dẫn mặc định
        if config_file_path:
            self.config_file = config_file_path
        else:
            self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        
        # Thư viện bắt buộc
        self.required_packages = {
            "PyQt6": "PyQt6",
            "dotenv": "python-dotenv"
            # Thêm các thư viện khác khi cần
        }
        
        # Tải cấu hình từ .env
        load_dotenv()
        
        # Thư mục gốc
        self.root_dir = Path(__file__).parent.parent.absolute()
        
        # Create configparser object for config access
        self.config = configparser.ConfigParser()
        
        # Cấu hình phân cấp
        self._config = {}
        
        # Tải cấu hình từ file nếu có
        self._load_config()
    
    def get(self, section, key=None, default=None):
        """
        Get configuration values.
        
        Args:
            section: Config section
            key: Optional key within section
            default: Default value if section/key not found
            
        Returns:
            Either entire section dict or specific key value
        """
        try:
            if key is None:
                # Return the entire section
                if section in self._config:
                    return self._config.get(section, {})
                return default
            else:
                # Return specific key from section with optional default
                section_data = self._config.get(section, {})
                return section_data.get(key, default)
        except Exception as e:
            logging.error(f"Error in ConfigManager.get(): {e}")
            return default
    
    def set(self, section, key, value):
        """Thiết lập giá trị cấu hình"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def get_config(self, section, key, default=None):
        """Lấy giá trị cấu hình phân cấp"""
        if section not in self._config:
            return default
        return self._config[section].get(key, default)
    
    def save_config(self):
        """Lưu cấu hình vào file"""
        config_path = os.path.join(self.root_dir, 'config', 'app_config.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(self._config, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Lỗi khi lưu cấu hình: {str(e)}")
            return False
    
    def _load_config(self):
        """Load configuration from files and environment variables"""
        # Create a DEFAULT section if it doesn't exist
        if 'DEFAULT' not in self._config:
            self._config['DEFAULT'] = {}
            
        # Add DEFAULT section to configparser
        self.config['DEFAULT'] = {}
        
        # Load environment variables into DEFAULT section
        for key, value in os.environ.items():
            if key.startswith('APP_'):
                self._config['DEFAULT'][key] = value
                self.config['DEFAULT'][key] = value
    
    def get_db_path(self):
        """
        Get database path from config file with fallback to default
        """
        try:
            # Try to get from the config file
            return self.config.get("database", "path")
        except (configparser.NoSectionError, configparser.NoOptionError):
            # If not found, use default path and ensure directory exists
            default_path = "data/app.db"
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            
            # Create the missing section
            if not self.config.has_section("database"):
                self.config.add_section("database")
            self.config.set("database", "path", default_path)
            
            # Save the updated config
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    self.config.write(f)
            except Exception as e:
                logging.warning(f"Could not save default database configuration: {str(e)}")
            return default_path
    
    def check_dependency(self, module_name):
        """Kiểm tra xem một thư viện đã được cài đặt chưa"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False

    def check_all_required_dependencies(self):
        """Kiểm tra tất cả các thư viện bắt buộc"""
        for module_name in self.required_packages:
            if not self.check_dependency(module_name):
                return False
        return True
