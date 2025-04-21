from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
import os
import logging

class ThemeManager(QObject):
    """
    Quản lý theme cho ứng dụng
    Hỗ trợ chuyển đổi giữa light theme và dark theme
    """
    theme_changed = pyqtSignal(str)  # Signal phát ra khi theme thay đổi
    
    def __init__(self, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.current_theme = "light"  # Default theme
        self.themes = {
            "light": "resources/styles/light_theme.qss",
            "dark": "resources/styles/dark_theme.qss"
        }
        
        # Nếu có config manager, lấy theme từ config
        if self.config_manager:
            try:
                self.current_theme = self.config_manager.get('ui', 'theme', 'light')
            except:
                logging.warning("Không thể đọc theme từ config, sử dụng light theme mặc định")
                self.current_theme = "light"
    
    def apply_theme(self, theme_name=None):
        """
        Áp dụng theme cho ứng dụng
        
        Args:
            theme_name (str, optional): Tên của theme cần áp dụng. 
                                       Nếu không chỉ định, sẽ dùng theme hiện tại
        """
        if theme_name:
            self.current_theme = theme_name
        
        theme_path = self.themes.get(self.current_theme)
        
        if not theme_path or not os.path.exists(theme_path):
            logging.warning(f"Không tìm thấy file theme: {theme_path}, dùng stylesheet mặc định")
            # Load và áp dụng stylesheet mặc định
            default_style_path = "resources/styles/styles.qss"
            if os.path.exists(default_style_path):
                self._apply_stylesheet(default_style_path)
            return
        
        # Load và áp dụng stylesheet
        self._apply_stylesheet(theme_path)
        
        # Lưu theme vào config nếu có config manager
        if self.config_manager:
            try:
                self.config_manager.set('ui', 'theme', self.current_theme)
                self.config_manager.save_config()  # Changed from save() to save_config()
            except:
                logging.warning("Không thể lưu theme vào config")
        
        # Phát signal theme đã thay đổi
        self.theme_changed.emit(self.current_theme)
    
    def toggle_theme(self):
        """
        Chuyển đổi giữa light theme và dark theme
        """
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)
        return new_theme
    
    def get_current_theme(self):
        """
        Trả về theme hiện tại
        
        Returns:
            str: Tên của theme hiện tại
        """
        return self.current_theme
    
    def _apply_stylesheet(self, style_path):
        """
        Đọc và áp dụng stylesheet từ file
        
        Args:
            style_path (str): Đường dẫn đến file stylesheet
        """
        try:
            with open(style_path, "r", encoding="utf-8") as file:
                style = file.read()
                QApplication.instance().setStyleSheet(style)
        except Exception as e:
            logging.error(f"Lỗi khi đọc file stylesheet: {e}")
