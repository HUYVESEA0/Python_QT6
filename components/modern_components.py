"""
Module chứa các thành phần giao diện hiện đại cho ứng dụng
"""

import os
from PyQt6.QtWidgets import (QWidget, QFrame, QLabel, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QIcon, QColor
from PyQt6.QtCore import Qt, QSize

class CardWidget(QFrame):
    """Widget hiển thị thông tin dạng card với drop shadow"""
    
    def __init__(self, title="", value="", icon_path=None, color="#2979ff", parent=None):
        """
        Khởi tạo CardWidget
        
        Args:
            title (str): Tiêu đề của card
            value (str): Giá trị hiển thị chính
            icon_path (str): Đường dẫn đến icon (nếu có)
            color (str): Màu sắc chủ đạo của card (hex color)
            parent (QWidget): Widget cha
        """
        super(CardWidget, self).__init__(parent)
        
        # Thiết lập style cơ bản
        self.setObjectName("modernCard")
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background-color: white;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        # Tạo drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Tạo layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Thêm icon nếu có
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                layout.addWidget(icon_label)
        
        # Phần thông tin
        info_layout = QVBoxLayout()
        
        # Tiêu đề
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"font-size: 12px; color: #666; font-weight: bold;")
        info_layout.addWidget(self.title_label)
        
        # Giá trị
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        info_layout.addWidget(self.value_label)
        
        layout.addLayout(info_layout)
        layout.setStretch(1, 1)  # Cho phần thông tin mở rộng
    
    def set_value(self, value):
        """Cập nhật giá trị hiển thị"""
        self.value_label.setText(str(value))
    
    def set_title(self, title):
        """Cập nhật tiêu đề"""
        self.title_label.setText(title)

class ActionButton(QPushButton):
    """Button với icon và kiểu hiện đại"""
    
    def __init__(self, text="", icon_path=None, color="#2979ff", parent=None):
        """
        Khởi tạo ActionButton
        
        Args:
            text (str): Text hiển thị trên button
            icon_path (str): Đường dẫn đến icon
            color (str): Màu sắc của button (hex color)
            parent (QWidget): Widget cha
        """
        super(ActionButton, self).__init__(text, parent)
        
        # Thiết lập icon nếu có
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))
        
        # Thiết lập style
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {self._lighten_color(color, 0.1)};
            }}
            
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.1)};
            }}
        """)
    
    def _lighten_color(self, color, factor=0.1):
        """Làm sáng màu lên một chút"""
        if color.startswith('#'):
            color = color[1:]
        
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor=0.1):
        """Làm tối màu đi một chút"""
        if color.startswith('#'):
            color = color[1:]
        
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

class HeaderBar(QWidget):
    """Thanh tiêu đề với các nút thao tác"""
    
    def __init__(self, title="", parent=None):
        """
        Khởi tạo HeaderBar
        
        Args:
            title (str): Tiêu đề hiển thị
            parent (QWidget): Widget cha
        """
        super(HeaderBar, self).__init__(parent)
        
        # Layout chính
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Tiêu đề
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2979ff;")
        layout.addWidget(title_label)
        
        # Thêm khoảng trống đẩy các nút về bên phải
        layout.addStretch()
        
        # Container cho các nút
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(8)
        
        layout.addWidget(self.button_container)
    
    def add_button(self, text, callback=None, icon_path=None, color="#2979ff"):
        """
        Thêm nút vào thanh tiêu đề
        
        Args:
            text (str): Text hiển thị trên nút
            callback (function): Hàm callback khi nút được nhấn
            icon_path (str): Đường dẫn đến icon
            color (str): Màu sắc của nút (hex color)
        
        Returns:
            QPushButton: Nút đã được thêm
        """
        button = ActionButton(text, icon_path, color)
        if callback:
            button.clicked.connect(callback)
        self.button_layout.addWidget(button)
        return button
