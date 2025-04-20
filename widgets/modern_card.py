from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                            QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
import os

class ModernCard(QFrame):
    """
    Card hiện đại với hiệu ứng hover và animation
    """
    def __init__(self, title="", value="", description="", icon_path=None, color="#2979ff", parent=None):
        """
        Khởi tạo card hiện đại
        
        Args:
            title (str): Tiêu đề card
            value (str): Giá trị chính hiển thị
            description (str): Mô tả bổ sung
            icon_path (str): Đường dẫn đến icon
            color (str): Màu sắc chính (hex color)
            parent (QWidget): Widget cha
        """
        super().__init__(parent)
        
        self.title = title
        self.value = value
        self.description = description
        self.icon_path = icon_path
        self.color = color
        self.is_hovered = False
        
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """Thiết lập giao diện cho card"""
        self.setObjectName("modernCard")
        self.setProperty("color", self.color)
        
        # Thiết lập độ cao và độ rộng tối thiểu
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Tạo shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # Layout chính
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon (nếu có)
        if self.icon_path and os.path.exists(self.icon_path):
            icon_container = QWidget()
            icon_container.setFixedWidth(50)
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_label = QLabel()
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            
            icon_layout.addWidget(icon_label)
            main_layout.addWidget(icon_container)
        
        # Nội dung
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
        # Tiêu đề
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("cardTitle")
        content_layout.addWidget(self.title_label)
        
        # Giá trị
        self.value_label = QLabel(self.value)
        self.value_label.setObjectName("cardValue")
        content_layout.addWidget(self.value_label)
        
        # Mô tả (nếu có)
        if self.description:
            self.description_label = QLabel(self.description)
            self.description_label.setObjectName("cardDescription")
            content_layout.addWidget(self.description_label)
        
        main_layout.addWidget(content_container, 1)  # Stretch factor 1
        
        # Thiết lập khả năng theo dõi hover
        self.setMouseTracking(True)
    
    def setup_animations(self):
        """Thiết lập các animation cho card"""
        # Animation cho shadow khi hover
        self.shadow_effect = self.graphicsEffect()
    
    def update_value(self, value, animate=True):
        """
        Cập nhật giá trị hiển thị với animation
        
        Args:
            value (str): Giá trị mới
            animate (bool): Có áp dụng animation hay không
        """
        if animate:
            # Tạo hiệu ứng "flash" khi giá trị thay đổi
            current_style = self.value_label.styleSheet()
            
            # Lưu giá trị hiện tại
            old_value = self.value_label.text()
            
            if old_value != str(value):
                # Áp dụng highlight color
                highlight_style = f"{current_style}; color: #FF6D00;"
                self.value_label.setStyleSheet(highlight_style)
                
                # Cập nhật giá trị
                self.value_label.setText(str(value))
                
                # Thiết lập QTimer để khôi phục style sau 500ms
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, lambda: self.value_label.setStyleSheet(current_style))
        else:
            # Cập nhật giá trị không có animation
            self.value_label.setText(str(value))
    
    def enterEvent(self, event):
        """Xử lý khi chuột vào card"""
        self.is_hovered = True
        
        # Thay đổi shadow
        shadow = self.shadow_effect
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 6)
        
        # Thêm style hover
        self.setStyleSheet("""
            #modernCard {
                background-color: #f9f9f9;
                transform: translateY(-2px);
            }
        """)
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Xử lý khi chuột rời khỏi card"""
        self.is_hovered = False
        
        # Khôi phục shadow
        shadow = self.shadow_effect
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        
        # Xóa style hover
        self.setStyleSheet("")
        
        super().leaveEvent(event)
