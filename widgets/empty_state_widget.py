from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import os

class EmptyStateWidget(QWidget):
    """
    Widget hiển thị trạng thái không có dữ liệu với hướng dẫn và nút hành động
    """
    actionTriggered = pyqtSignal()
    
    def __init__(self, 
                 message="Không có dữ liệu", 
                 action_text="Thêm mới", 
                 icon_path=None, 
                 parent=None):
        super().__init__(parent)
        self.setObjectName("emptyStateWidget")
        self.message = message
        self.action_text = action_text
        self.icon_path = icon_path
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện cho widget trạng thái trống"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon (nếu có)
        if self.icon_path and os.path.exists(self.icon_path):
            icon_label = QLabel()
            pixmap = QIcon(self.icon_path).pixmap(64, 64)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)
        
        # Thông báo
        message_label = QLabel(self.message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; color: #757575; margin: 10px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Nút hành động
        if self.action_text:
            action_button = QPushButton(self.action_text)
            action_button.setCursor(Qt.CursorShape.PointingHandCursor)
            action_button.setMaximumWidth(200)
            action_button.setStyleSheet("""
                QPushButton {
                    background-color: #2979ff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #448aff;
                }
                QPushButton:pressed {
                    background-color: #0d47a1;
                }
            """)
            action_button.clicked.connect(lambda: self.actionTriggered.emit())
            layout.addWidget(action_button, 0, Qt.AlignmentFlag.AlignCenter)
