from PyQt6.QtCore import QSettings, QCoreApplication
import os
import logging

class ThemeManager:
    """Quản lý theme của ứng dụng"""
    
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    
    def __init__(self):
        """Khởi tạo theme manager"""
        # Khởi tạo settings
        QCoreApplication.setOrganizationName("MyOrg")
        QCoreApplication.setApplicationName("StudentManagement")
        self.settings = QSettings()
        
        # Đọc theme từ settings
        self.current_theme = self.settings.value("theme", self.THEME_LIGHT)
        
        # Đường dẫn đến các file stylesheet
        self.theme_paths = {
            self.THEME_LIGHT: "resources/styles/light_theme.qss",
            self.THEME_DARK: "resources/styles/dark_theme.qss"
        }
        
        # Custom stylesheet (luôn được áp dụng)
        self.custom_style_path = "resources/styles/custom_styles.qss"
        
        # Callbacks khi theme thay đổi
        self.theme_changed_callbacks = []
    
    def get_current_theme(self):
        """
        Lấy theme hiện tại
        
        Returns:
            str: Tên của theme hiện tại
        """
        return self.current_theme
    
    def set_theme(self, theme):
        """
        Thiết lập theme cho ứng dụng
        
        Args:
            theme (str): Tên của theme (light, dark)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        if theme not in self.theme_paths:
            logging.warning(f"Theme không hợp lệ: {theme}")
            return False
        
        # Cập nhật theme hiện tại
        self.current_theme = theme
        
        # Lưu vào settings
        self.settings.setValue("theme", theme)
        
        # Áp dụng theme
        self.apply_current_theme()
        
        # Gọi các callback nếu có
        for callback in self.theme_changed_callbacks:
            try:
                callback(theme)
            except Exception as e:
                logging.error(f"Lỗi khi gọi theme callback: {str(e)}")
        
        return True
    
    def toggle_theme(self):
        """
        Chuyển đổi giữa theme sáng và tối
        
        Returns:
            str: Tên của theme mới
        """
        new_theme = self.THEME_DARK if self.current_theme == self.THEME_LIGHT else self.THEME_LIGHT
        self.set_theme(new_theme)
        return new_theme
    
    def apply_current_theme(self):
        """
        Áp dụng theme hiện tại cho ứng dụng
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        from PyQt6.QtWidgets import QApplication
        
        # Kiểm tra xem theme có tồn tại không
        theme_path = self.theme_paths.get(self.current_theme)
        if not theme_path or not os.path.exists(theme_path):
            logging.warning(f"File theme không tồn tại: {theme_path}")
            return False
        
        try:
            # Đọc nội dung file stylesheet
            with open(theme_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
            
            # Thêm custom stylesheet nếu tồn tại
            if os.path.exists(self.custom_style_path):
                with open(self.custom_style_path, "r", encoding="utf-8") as f:
                    stylesheet += "\n" + f.read()
            
            # Áp dụng stylesheet
            QApplication.instance().setStyleSheet(stylesheet)
            
            logging.info(f"Đã áp dụng theme: {self.current_theme}")
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi áp dụng theme: {str(e)}")
            return False
    
    def add_theme_changed_callback(self, callback):
        """
        Thêm callback được gọi khi theme thay đổi
        
        Args:
            callback (callable): Hàm callback nhận theme_name làm tham số
        """
        if callable(callback) and callback not in self.theme_changed_callbacks:
            self.theme_changed_callbacks.append(callback)
    
    def get_theme_color(self, color_name):
        """
        Lấy màu sắc theo theme
        
        Args:
            color_name (str): Tên màu cần lấy
            
        Returns:
            str: Mã màu theo theme hiện tại
        """
        # Định nghĩa các màu theo theme
        colors = {
            self.THEME_LIGHT: {
                "primary": "#007BFF",
                "success": "#28A745",
                "warning": "#FFC107",
                "danger": "#DC3545",
                "info": "#17A2B8",
                "text": "#212529",
                "background": "#FFFFFF",
                "border": "#DEE2E6"
            },
            self.THEME_DARK: {
                "primary": "#0063B1",
                "success": "#13A10E",
                "warning": "#C19C00",
                "danger": "#C42B1C",
                "info": "#0078D4",
                "text": "#FFFFFF",
                "background": "#1E1E1E",
                "border": "#3F3F46"
            }
        }
        
        # Lấy màu theo theme hiện tại
        return colors.get(self.current_theme, {}).get(color_name, "#000000")
