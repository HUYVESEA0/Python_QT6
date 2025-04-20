import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

class StatisticCard(QWidget):
    """
    Widget hiển thị một thẻ thống kê trên dashboard.
    """
    def __init__(self, title, value, icon_path=None, bg_color="#ffffff", text_color="#2f3640", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_path = icon_path
        self.bg_color = bg_color
        self.text_color = text_color
        self.init_ui()

    def init_ui(self):
        """Thiết lập giao diện cho thẻ"""
        self.setObjectName("statistic-card")
        self.setStyleSheet(f"""
            #statistic-card {{
                background-color: {self.bg_color};
                border-radius: 8px;
                min-height: 120px;
                max-height: 120px;
            }}
            #card-title {{
                color: {self.text_color};
                opacity: 0.8;
            }}
            #card-value {{
                color: {self.text_color};
                font-weight: bold;
            }}
        """)
        
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Fixed
        )
        
        # Layout chính
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon (nếu có)
        if self.icon_path and os.path.exists(self.icon_path):
            icon_layout = QVBoxLayout()
            icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                icon_label.setFixedSize(32, 32)
                icon_layout.addWidget(icon_label)
            
            layout.addLayout(icon_layout)
        
        # Nội dung (title và value)
        content_layout = QVBoxLayout()
        
        # Tiêu đề
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("card-title")
        title_font = QFont()
        title_font.setPointSize(10)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)
        
        # Giá trị
        self.value_label = QLabel(self.value)
        self.value_label.setObjectName("card-value")
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        content_layout.addWidget(self.value_label)
        
        layout.addLayout(content_layout, 1)

    def set_value(self, value):
        """Cập nhật giá trị hiển thị"""
        self.value = value
        self.value_label.setText(str(value))
