from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QRect, QEasingCurve, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QFont
from enum import Enum
import logging

class NotificationType(Enum):
    """Loại thông báo"""
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4

class NotificationWidget(QWidget):
    """Widget hiển thị thông báo"""
    
    def __init__(self, message, notification_type=NotificationType.INFO, parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.parent_widget = parent
        self.opacity = 1.0
        self.animation_duration = 300  # Thời gian hiệu ứng (ms)
        
        # Thiết lập giao diện
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Thiết lập giao diện và hiệu ứng
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Thiết lập giao diện thông báo"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Xác định màu sắc dựa trên loại thông báo
        if self.notification_type == NotificationType.SUCCESS:
            self.bg_color = QColor(39, 174, 96, 230)
            icon_text = "✅"
        elif self.notification_type == NotificationType.WARNING:
            self.bg_color = QColor(241, 196, 15, 230)
            icon_text = "⚠️"
        elif self.notification_type == NotificationType.ERROR:
            self.bg_color = QColor(231, 76, 60, 230)
            icon_text = "❌"
        else:  # INFO
            self.bg_color = QColor(41, 128, 185, 230)
            icon_text = "ℹ️"
        
        # Icon
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("", 14))
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setStyleSheet("color: white; font-size: 12px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: white;
                background: transparent;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30%);
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(self.close_animation)
        layout.addWidget(close_btn)
        
        # Thiết lập kích thước
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
    
    def setup_animations(self):
        """Thiết lập các animation"""
        # Animation xuất hiện
        self.show_animation = QPropertyAnimation(self, b"geometry")
        self.show_animation.setDuration(self.animation_duration)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animation biến mất
        self.hide_animation = QPropertyAnimation(self, b"geometry")
        self.hide_animation.setDuration(self.animation_duration)
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.hide_animation.finished.connect(self.on_hide_finished)
    
    def showEvent(self, event):
        """Xử lý khi widget được hiển thị"""
        super().showEvent(event)
        
        if self.parent_widget:
            # Tính vị trí hiển thị (góc trên phải)
            parent_rect = self.parent_widget.geometry()
            start_x = parent_rect.right() - self.width() - 20
            start_y = parent_rect.top() + 50
            
            # Vị trí bắt đầu (ẩn)
            start_rect = QRect(parent_rect.right() + 20, start_y, self.width(), self.height())
            self.setGeometry(start_rect)
            
            # Vị trí kết thúc (hiển thị)
            end_rect = QRect(start_x, start_y, self.width(), self.height())
            
            # Thiết lập và bắt đầu animation
            self.show_animation.setStartValue(start_rect)
            self.show_animation.setEndValue(end_rect)
            self.show_animation.start()
    
    def close_animation(self):
        """Bắt đầu animation đóng thông báo"""
        current_rect = self.geometry()
        end_rect = QRect(
            self.parent_widget.geometry().right() + 20,
            current_rect.y(),
            current_rect.width(),
            current_rect.height()
        )
        
        # Thiết lập và bắt đầu animation đóng
        self.hide_animation.setStartValue(current_rect)
        self.hide_animation.setEndValue(end_rect)
        self.hide_animation.start()
    
    def on_hide_finished(self):
        """Xử lý khi animation ẩn kết thúc"""
        self.close()
        self.deleteLater()
    
    def paintEvent(self, event):
        """Vẽ widget thông báo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Vẽ bóng đổ
        shadow_color = QColor(0, 0, 0, 50)
        for i in range(5):
            painter.setPen(QPen(QColor(0, 0, 0, 0), 1))
            painter.setBrush(QBrush(QColor(shadow_color)))
            painter.drawRoundedRect(i, i, self.width() - 2*i, self.height() - 2*i, 10, 10)
        
        # Vẽ nền
        path = QPainterPath()
        path.addRoundedRect(5, 5, self.width() - 10, self.height() - 10, 8, 8)
        painter.setPen(QPen(QColor(0, 0, 0, 0)))
        painter.setBrush(QBrush(self.bg_color))
        painter.drawPath(path)

class NotificationManager:
    """
    Quản lý hiển thị thông báo trong ứng dụng
    """
    
    def __init__(self):
        self.parent = None
        self.active_notifications = []
        self.default_timeout = 3000  # 3 giây
        self.notification_spacing = 10  # Khoảng cách giữa các thông báo
        self.theme_manager = None
    
    def set_parent(self, parent):
        """Thiết lập parent widget cho thông báo"""
        self.parent = parent
    
    def set_theme_manager(self, theme_manager):
        """Thiết lập theme manager"""
        self.theme_manager = theme_manager
    
    def show_notification(self, message, notification_type, timeout=None):
        """
        Hiển thị thông báo
        
        Args:
            message (str): Nội dung thông báo
            notification_type (NotificationType): Loại thông báo
            timeout (int, optional): Thời gian hiển thị (ms)
        """
        if not self.parent:
            logging.warning("NotificationManager: Parent chưa được thiết lập")
            return
        
        try:
            # Tạo widget thông báo mới
            notification = NotificationWidget(message, notification_type, self.parent)
            
            # Điều chỉnh vị trí nếu đã có các thông báo khác
            self.adjust_positions(notification)
            
            # Thêm vào danh sách thông báo đang hiển thị
            self.active_notifications.append(notification)
            
            # Hiển thị thông báo
            notification.show()
            
            # Thiết lập timer để tự động đóng thông báo
            timeout = timeout if timeout is not None else self.default_timeout
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._close_notification(notification))
            timer.start(timeout)
            
            # Lưu timer trong notification để tránh bị thu hồi bởi garbage collector
            notification.timer = timer
            
            # Ghi log
            log_level = {
                NotificationType.INFO: logging.INFO,
                NotificationType.SUCCESS: logging.INFO,
                NotificationType.WARNING: logging.WARNING,
                NotificationType.ERROR: logging.ERROR
            }.get(notification_type, logging.INFO)
            
            logging.log(log_level, f"Notification: {message}")
            
        except Exception as e:
            logging.error(f"Lỗi hiển thị thông báo: {str(e)}")
    
    def adjust_positions(self, new_notification):
        """Điều chỉnh vị trí các thông báo để không bị chồng lên nhau"""
        offset = 0
        for notification in self.active_notifications:
            offset += notification.height() + self.notification_spacing
        
        # Điều chỉnh vị trí ban đầu của thông báo mới
        if offset > 0:
            current_pos = new_notification.pos()
            new_notification.move(current_pos.x(), current_pos.y() + offset)
    
    def _close_notification(self, notification):
        """
        Đóng thông báo
        
        Args:
            notification (NotificationWidget): Widget thông báo cần đóng
        """
        if notification in self.active_notifications:
            notification.close_animation()
            self.active_notifications.remove(notification)
    
    def show_info(self, message, timeout=None):
        """Hiển thị thông báo thông tin"""
        self.show_notification(message, NotificationType.INFO, timeout)
    
    def show_success(self, message, timeout=None):
        """Hiển thị thông báo thành công"""
        self.show_notification(message, NotificationType.SUCCESS, timeout)
    
    def show_warning(self, message, timeout=None):
        """Hiển thị thông báo cảnh báo"""
        self.show_notification(message, NotificationType.WARNING, timeout)
    
    def show_error(self, message, timeout=None):
        """Hiển thị thông báo lỗi"""
        self.show_notification(message, NotificationType.ERROR, timeout)
    
    def close_all(self):
        """Đóng tất cả các thông báo đang hiển thị"""
        for notification in self.active_notifications[:]:
            self._close_notification(notification)
    
    def show_confirmation(self, message, callback_yes=None, callback_no=None, parent=None):
        """
        Hiển thị hộp thoại xác nhận với nút Yes/No
        
        Args:
            message (str): Nội dung xác nhận
            callback_yes (callable): Hàm callback khi người dùng chọn Yes
            callback_no (callable): Hàm callback khi người dùng chọn No
            parent (QWidget): Widget cha để hiển thị dialog
        """
        parent = parent or self.parent
        if not parent:
            logging.warning("NotificationManager: Parent chưa được thiết lập")
            return False
        
        reply = QMessageBox.question(
            parent,
            "Xác nhận",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if callback_yes:
                callback_yes()
            return True
        else:
            if callback_no:
                callback_no()
            return False
