from PyQt6.QtWidgets import QWidget6 import uic
from PyQt6 import uic
import os

class StatisticCard(QWidget):from PyQt6 import uic    """
    """
    Widget hiển thị một thẻ thống kê trên dashboard.tatisticCard(QWidget):
    """rent=None):
    def __init__(self, title, value, icon_path=None, bg_color="#ffffff", text_color="#2f3640", parent=None):get hiển thị một thẻ thống kê trên dashboard. super().__init__(parent)
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "statistic_card.ui")lue, icon_path=None, bg_color="#ffffff", text_color="#2f3640", parent=None):
        uic.loadUi(ui_path, self)arent)con_path
        join(os.path.dirname(__file__), "statistic_card.ui")_color
        self.title = titler
        self.value = value
        self.icon_path = icon_path
        self.bg_color = bg_coloralue
        self.text_color = text_color        self.icon_path = icon_path        """Thiết lập giao diện cho thẻ"""
        = bg_colorth/to/your/statistic_card.ui", self)  # Đường dẫn tới file .ui của bạn
        # Thiết lập giao diện cho thẻ
        self.setObjectName("statistic-card")
        self.setStyleSheet(f"""
            #statistic-card {{
                background-color: {self.bg_color};
                border-radius: 8px;ic-card")
                min-height: 120px;
                max-height: 120px;
            }}  background-color: {self.bg_color};
            #card-title {{ius: 8px;
                color: {self.text_color};
                opacity: 0.8;20px;
            }}
            #card-value {{
                color: {self.text_color};
                font-weight: bold;
            }}
        """)#card-value {{
                color: {self.text_color};
        # Icon (nếu có): bold;
        if self.icon_path and os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)self.setSizePolicy(
                self.icon_label.setPixmap(pixmap)y.Policy.Expanding, , value):
                self.icon_label.setFixedSize(32, 32)edhị"""
        
        # Tiêu đềself.value_label.setText(str(value))
        self.title_label.setText(self.title)       layout = QHBoxLayout(self)        layout.setContentsMargins(15, 15, 15, 15)                # Icon (nếu có)        if self.icon_path and os.path.exists(self.icon_path):            icon_layout = QVBoxLayout()            icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)                        icon_label = QLabel()            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)            pixmap = QPixmap(self.icon_path)            if not pixmap.isNull():                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)                icon_label.setPixmap(pixmap)                icon_label.setFixedSize(32, 32)                icon_layout.addWidget(icon_label)                        layout.addLayout(icon_layout)                # Nội dung (title và value)        content_layout = QVBoxLayout()                # Tiêu đề        self.title_label = QLabel(self.title)        self.title_label.setObjectName("card-title")        title_font = QFont()        title_font.setPointSize(10)        self.title_label.setFont(title_font)        content_layout.addWidget(self.title_label)                # Giá trị        self.value_label = QLabel(self.value)        self.value_label.setObjectName("card-value")        value_font = QFont()        value_font.setPointSize(18)        value_font.setBold(True)        self.value_label.setFont(value_font)        content_layout.addWidget(self.value_label)                layout.addLayout(content_layout, 1)    def set_value(self, value):
        title_font = QFont()
        title_font.setPointSize(10)
        self.title_label.setFont(title_font)
                # Giá trị        self.value_label.setText(self.value)        value_font = QFont()        value_font.setPointSize(18)        value_font.setBold(True)        self.value_label.setFont(value_font)    def set_value(self, value):        """Cập nhật giá trị hiển thị"""        self.value = value        self.value_label.setText(str(value))