from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QRect, QEasingCurve, QSize, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QFont, QFontDatabase
from enum import Enum
import logging

class NotificationType(Enum):
    """Loại thông báo"""
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4


class NotificationWidget(QWidget):
    """Widget hiển thị thông báo với thiết kế hiện đại"""
    
    def __init__(self, message, notification_type=NotificationType.INFO, parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.parent_widget = parent
        self.opacity = 1.0
        self.animation_duration = 350  # Thời gian hiệu ứng (ms)
        
        # Thiết lập giao diện
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Thiết lập giao diện và hiệu ứng
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Thiết lập giao diện thông báo với thiết kế hiện đại"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        # Xác định màu sắc và nội dung dựa trên loại thông báo
        if self.notification_type == NotificationType.SUCCESS:
            self.bg_color = QColor(46, 204, 113, 245)
            self.border_color = QColor(39, 174, 96)
            icon_text = "✓"
            style_class = "success"
        elif self.notification_type == NotificationType.WARNING:
            self.bg_color = QColor(241, 196, 15, 245)
            self.border_color = QColor(243, 156, 18)
            icon_text = "!"
            style_class = "warning"
        elif self.notification_type == NotificationType.ERROR:
            self.bg_color = QColor(231, 76, 60, 245)
            self.border_color = QColor(192, 57, 43)
            icon_text = "×"
            style_class = "error"
        else:  # INFO
            self.bg_color = QColor(52, 152, 219, 245)
            self.border_color = QColor(41, 128, 185)
            icon_text = "i"
            style_class = "info"
        
        # Icon container với nền tròn
        icon_container = QWidget()
        icon_container.setFixedSize(28, 28)
        icon_container.setStyleSheet(f"""
            background-color: white;
            border-radius: 14px;
            color: {self.border_color.name()};
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon
        icon_label = QLabel(icon_text)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            color: {self.border_color.name()};
            font-size: 16px;
            font-weight: bold;
        """)
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_container)
        
        # Message và nội dung
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        
        # Tiêu đề thông báo
        title_label = QLabel(self.get_title_for_type())
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        content_layout.addWidget(title_label)
        
        # Nội dung thông báo
        message_label = QLabel(self.message)
        message_label.setStyleSheet("color: rgba(255, 255, 255, 220); font-size: 12px;")
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)
        
        layout.addLayout(content_layout, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: rgba(255, 255, 255, 200);
                background: transparent;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: white;
                background-color: rgba(255, 255, 255, 20%);
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(self.close_animation)
        layout.addWidget(close_btn)
        
        # Thiết lập kích thước
        self.setMinimumWidth(320)
        self.setMaximumWidth(400)
    
    def get_title_for_type(self):
        """Trả về tiêu đề dựa trên loại thông báo"""
        if self.notification_type == NotificationType.SUCCESS:
            return "Thành công"
        elif self.notification_type == NotificationType.WARNING:
            return "Cảnh báo"
        elif self.notification_type == NotificationType.ERROR:
            return "Lỗi"
        else:
            return "Thông tin"
    
    def setup_animations(self):
        """Thiết lập các animation phức tạp hơn"""
        # Hiệu ứng opacity
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Animation xuất hiện - kết hợp vị trí và độ trong suốt
        self.entrance_animation_group = QParallelAnimationGroup(self)
        
        # Animation độ trong suốt
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(self.animation_duration)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animation vị trí sẽ được thiết lập trong showEvent
        self.move_in = QPropertyAnimation(self, b"geometry")
        self.move_in.setDuration(self.animation_duration)
        self.move_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.entrance_animation_group.addAnimation(self.fade_in)
        self.entrance_animation_group.addAnimation(self.move_in)
        
        # Animation biến mất - kết hợp vị trí và độ trong suốt
        self.exit_animation_group = QParallelAnimationGroup(self)
        self.exit_animation_group.finished.connect(self.on_hide_finished)
        
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(self.animation_duration)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.move_out = QPropertyAnimation(self, b"geometry")
        self.move_out.setDuration(self.animation_duration)
        self.move_out.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.exit_animation_group.addAnimation(self.fade_out)
        self.exit_animation_group.addAnimation(self.move_out)
    
    def showEvent(self, event):
        """Xử lý khi widget được hiển thị với hiệu ứng mượt mà hơn"""
        super().showEvent(event)
        
        if self.parent_widget:
            # Tính vị trí hiển thị (góc trên phải)
            parent_rect = self.parent_widget.geometry()
            
            # Điều chỉnh vị trí để hiển thị ở góc phải
            end_x = parent_rect.right() - self.width() - 20
            end_y = parent_rect.top() + 70
            
            # Vị trí bắt đầu (ẩn)
            start_rect = QRect(parent_rect.right(), end_y, self.width(), self.height())
            self.setGeometry(start_rect)
            
            # Vị trí kết thúc (hiển thị)
            end_rect = QRect(end_x, end_y, self.width(), self.height())
            
            # Thiết lập và bắt đầu animation
            self.move_in.setStartValue(start_rect)
            self.move_in.setEndValue(end_rect)
            self.entrance_animation_group.start()
    
    def close_animation(self):
        """Bắt đầu animation đóng thông báo mượt mà hơn"""
        current_rect = self.geometry()
        
        if self.parent_widget:
            # Vị trí kết thúc (ẩn ra bên phải)
            end_rect = QRect(
                self.parent_widget.geometry().right() + 20,
                current_rect.y(),
                current_rect.width(),
                current_rect.height()
            )
            
            # Thiết lập và bắt đầu animation
            self.move_out.setStartValue(current_rect)
            self.move_out.setEndValue(end_rect)
            self.exit_animation_group.start()
    
    def on_hide_finished(self):
        """Xử lý khi animation ẩn kết thúc"""
        self.close()
        self.deleteLater()
    
    def paintEvent(self, event):
        """Vẽ widget thông báo với thiết kế hiện đại"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Vẽ bóng đổ mượt mà hơn
        shadow_color = QColor(0, 0, 0, 60)
        for i in range(8):
            painter.setPen(QPen(QColor(0, 0, 0, 0), 1))
            shadow_opacity = 60 - i * 8
            if shadow_opacity > 0:
                shadow_color.setAlpha(shadow_opacity)
                painter.setBrush(QBrush(shadow_color))
                painter.drawRoundedRect(i, i, self.width() - 2*i, self.height() - 2*i, 8, 8)
        
        # Vẽ nền chính
        path = QPainterPath()
        path.addRoundedRect(4, 4, self.width() - 8, self.height() - 8, 8, 8)
        painter.setPen(QPen(self.border_color, 2))
        painter.setBrush(QBrush(self.bg_color))
        painter.drawPath(path)

class NotificationManager:
    """
    Quản lý hiển thị thông báo trong ứng dụng với thiết kế hiện đại
    """
    
    def __init__(self):
        self.parent = None
        self.active_notifications = []
        self.default_timeout = 4000  # 4 giây
        self.notification_spacing = 12  # Khoảng cách giữa các thông báo
        self.theme_manager = None
        self.max_notifications = 5  # Số lượng thông báo tối đa hiển thị cùng lúc
        self._widgets_refs = []  # Keep strong references to widgets to prevent deletion
    
    def set_parent(self, parent):
        """Thiết lập parent widget cho thông báo"""
        self.parent = parent
    
    def set_theme_manager(self, theme_manager):
        """Thiết lập theme manager"""
        self.theme_manager = theme_manager
    
    def show_notification(self, message, notification_type, timeout=None):
        """
        Hiển thị thông báo với thiết kế mới
        
        Args:
            message (str): Nội dung thông báo
            notification_type (NotificationType): Loại thông báo
            timeout (int, optional): Thời gian hiển thị (ms)
        """
        if not self.parent:
            logging.warning("NotificationManager: Parent chưa được thiết lập")
            return
        
        try:
            # Kiểm tra số lượng thông báo đang hiển thị 
            # Nếu quá nhiều, đóng thông báo cũ nhất
            if len(self.active_notifications) >= self.max_notifications:
                oldest_notification = self.active_notifications[0]
                self._close_notification(oldest_notification)
            
            # Tạo widget thông báo mới
            notification = NotificationWidget(message, notification_type, self.parent)
            
            # Store a reference to the notification in the timer to prevent premature garbage collection
            timeout = timeout if timeout is not None else self.default_timeout
            timer = QTimer(notification)  # Set the parent of the timer to the notification
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._close_notification(notification) 
                                 if notification in self.active_notifications else None)
            
            # Điều chỉnh vị trí nếu đã có các thông báo khác
            self.adjust_positions(notification)
            
            # Thêm vào danh sách thông báo đang hiển thị
            self.active_notifications.append(notification)
            
            # Keep a strong reference to prevent the widget from being deleted
            self._widgets_refs.append(notification)
            
            # Hiển thị thông báo
            notification.show()
            
            # Start timer
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
        """
        Điều chỉnh vị trí các thông báo để tạo hiệu ứng xếp chồng đẹp mắt
        
        Args:
            new_notification (NotificationWidget): Thông báo mới được thêm vào
        """
        offset = 0
        
        # Áp dụng offset cho thông báo mới dựa trên số lượng thông báo đã hiển thị
        for notification in self.active_notifications:
            offset += notification.height() + self.notification_spacing
        
        # Điều chỉnh vị trí ban đầu của thông báo mới
        if offset > 0:
            current_pos = new_notification.pos()
            new_notification.move(current_pos.x(), current_pos.y() + offset)
    
    def _close_notification(self, notification):
        """
        Đóng thông báo với animation
        
        Args:
            notification (NotificationWidget): Widget thông báo cần đóng
        """
        try:
            # Check if notification is in the list of active notifications and is valid
            if notification in self.active_notifications and notification.isVisible():
                notification.close_animation()
                self.active_notifications.remove(notification)
                
                # Điều chỉnh lại vị trí các thông báo còn lại
                self._reposition_notifications()
                
                # Remove from strong references list after animation completes
                def cleanup():
                    if notification in self._widgets_refs:
                        self._widgets_refs.remove(notification)
                
                # Connect cleanup to the finished signal
                notification.exit_animation_group.finished.connect(cleanup)
                
        except RuntimeError:
            # Handle case where the C++ object has been deleted
            if notification in self.active_notifications:
                self.active_notifications.remove(notification)
                
            if notification in self._widgets_refs:
                self._widgets_refs.remove(notification)
                
            # Điều chỉnh lại vị trí các thông báo còn lại
            self._reposition_notifications()
        except Exception as e:
            logging.error(f"Error closing notification: {str(e)}")
    
    def _reposition_notifications(self):
        """Điều chỉnh lại vị trí của các thông báo sau khi đóng một thông báo"""
        if not self.parent or not self.active_notifications:
            return
            
        parent_rect = self.parent.geometry()
        base_y = parent_rect.top() + 70
        
        for i, notification in enumerate(self.active_notifications):
            # Tính toán vị trí mới
            target_y = base_y + i * (notification.height() + self.notification_spacing)
            current_rect = notification.geometry()
            
            # Chỉ tạo animation nếu vị trí thực sự thay đổi
            if current_rect.y() != target_y:
                animation = QPropertyAnimation(notification, b"geometry")
                animation.setDuration(300)
                animation.setStartValue(current_rect)
                animation.setEndValue(QRect(current_rect.x(), target_y, 
                                           current_rect.width(), current_rect.height()))
                animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation.start()
    
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
        # Make a copy of the list to safely iterate while removing items
        notifications_to_close = self.active_notifications.copy()
        for notification in notifications_to_close:
            self._close_notification(notification)
        
        # Clear all references
        self._widgets_refs.clear()
    
    def show_confirmation(self, message, callback_yes=None, callback_no=None, parent=None):
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
