import os
import logging
from PyQt6.QtGui import QIcon, QPixmap
from utils.path_helper import PathHelper

class ResourceManager:
    """
    Lớp quản lý tài nguyên ứng dụng như icons, images, styles
    """
    
    @staticmethod
    def get_icon(icon_name, fallback=None):
        """
        Lấy QIcon từ tên icon
        
        Args:
            icon_name (str): Tên file icon (không cần phần mở rộng)
            fallback (QIcon, optional): Icon thay thế nếu không tìm thấy
            
        Returns:
            QIcon: Đối tượng QIcon
        """
        icon_path = PathHelper.get_icon_path(icon_name)
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            logging.warning(f"Không tìm thấy icon: {icon_path}")
            return fallback if fallback is not None else QIcon()
    
    @staticmethod
    def get_pixmap(image_name, fallback=None):
        """
        Lấy QPixmap từ tên file ảnh
        
        Args:
            image_name (str): Tên file ảnh
            fallback (QPixmap, optional): Pixmap thay thế nếu không tìm thấy
            
        Returns:
            QPixmap: Đối tượng QPixmap
        """
        image_path = PathHelper.get_resource_path(os.path.join(PathHelper.RESOURCES_DIR, image_name))
        
        if os.path.exists(image_path):
            return QPixmap(image_path)
        else:
            logging.warning(f"Không tìm thấy ảnh: {image_path}")
            return fallback if fallback is not None else QPixmap()
    
    @staticmethod
    def get_stylesheet(style_name, default_content=""):
        """
        Lấy nội dung stylesheet từ tên file
        
        Args:
            style_name (str): Tên file stylesheet
            default_content (str, optional): Nội dung mặc định nếu không tìm thấy file
            
        Returns:
            str: Nội dung stylesheet
        """
        style_path = PathHelper.get_style_path(style_name)
        
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as file:
                    return file.read()
            except Exception as e:
                logging.error(f"Lỗi khi đọc stylesheet {style_path}: {e}")
                return default_content
        else:
            logging.warning(f"Không tìm thấy stylesheet: {style_path}")
            return default_content
