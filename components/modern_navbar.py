from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QToolButton, QMenu, 
                            QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QPainter, QPen, QBrush, QPainterPath, QAction
import os

class NavButton(QToolButton):
    """Button tùy chỉnh cho thanh điều hướng"""
    
    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(parent)
        
        # Thiết lập nội dung
        self.setText(text)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        
        # Thiết lập kiểu dáng
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setIconSize(QSize(20, 20))
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setAutoRaise(True)
        
        # Kiểu dáng
        self.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 8px 16px;
                background: transparent;
                color: #333333;
                font-size: 13px;
                border-radius: 4px;
                min-width: 40px;
            }
            
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            
            QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            QToolButton::menu-indicator { 
                image: none;
            }
        """)

class ModernNavbar(QFrame):
    """Thanh điều hướng hiện đại kết hợp menu và toolbar"""
    
    # Signal để thông báo khi tab được chọn
    tabSelected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tab_index = 0
        
        # Thiết lập giao diện
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện navbar"""
        # Thiết lập frame
        self.setObjectName("modernNavbar")
        self.setStyleSheet("""
            #modernNavbar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
            
            QLabel#appTitle {
                color: #2979ff;
                font-size: 16px;
                font-weight: bold;
                padding-left: 10px;
            }
            
            QPushButton#themeButton {
                border: none;
                background-color: transparent;
                padding: 8px;
                border-radius: 4px;
            }
            
            QPushButton#themeButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        
        # Layout chính - renamed from layout to main_layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(5)
        
        # Tiêu đề ứng dụng
        self.title_label = QLabel("Quản Lý Sinh Viên")
        self.title_label.setObjectName("appTitle")
        self.main_layout.addWidget(self.title_label)
        
        # Thêm khoảng cách
        self.main_layout.addSpacing(20)
        
        # Dictionary để lưu trữ các button và menu
        self.nav_buttons = {}
        self.tab_buttons = []
        
    def add_tab_button(self, text, icon_path, tab_index, tooltip=""):
        """Thêm nút chuyển tab trực tiếp"""
        button = NavButton(text, icon_path, self)
        button.setToolTip(tooltip)
        button.clicked.connect(lambda: self.tabSelected.emit(tab_index))
        self.main_layout.addWidget(button)
        self.tab_buttons.append(button)
        return button
    
    def add_menu_button(self, title, icon_path=None):
        """Thêm nút menu với dropdown"""
        button = NavButton(title, icon_path, self)
        menu = QMenu(button)
        button.setMenu(menu)
        self.main_layout.addWidget(button)
        self.nav_buttons[title] = (button, menu)
        return button, menu
    
    def add_action_to_menu(self, menu_title, action_text, callback, icon_path=None, shortcut=None):
        """Thêm action vào menu đã tồn tại"""
        if menu_title in self.nav_buttons:
            _, menu = self.nav_buttons[menu_title]
            action = QAction(action_text, self)
            
            if icon_path and os.path.exists(icon_path):
                action.setIcon(QIcon(icon_path))
                
            if shortcut:
                action.setShortcut(shortcut)
                
            action.triggered.connect(callback)
            menu.addAction(action)
            return action
        return None
    
    def add_separator_to_menu(self, menu_title):
        """Thêm dấu ngăn cách vào menu"""
        if menu_title in self.nav_buttons:
            _, menu = self.nav_buttons[menu_title]
            menu.addSeparator()
    
    def add_right_aligned_widget(self, widget):
        """Thêm widget căn phải"""
        self.main_layout.addStretch(1)  # Đẩy tất cả sang bên phải
        self.main_layout.addWidget(widget)
    
    def set_active_tab(self, index):
        """Đánh dấu tab đang active"""
        self.current_tab_index = index
        
        # Cập nhật kiểu dáng cho các tab button
        for i, button in enumerate(self.tab_buttons):
            if i == index:
                button.setStyleSheet("""
                    QToolButton {
                        border: none;
                        padding: 8px 16px;
                        background-color: rgba(41, 121, 255, 0.1);
                        color: #2979ff;
                        font-size: 13px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    
                    QToolButton:hover {
                        background-color: rgba(41, 121, 255, 0.15);
                    }
                """)
            else:
                button.setStyleSheet("""
                    QToolButton {
                        border: none;
                        padding: 8px 16px;
                        background: transparent;
                        color: #333333;
                        font-size: 13px;
                        border-radius: 4px;
                    }
                    
                    QToolButton:hover {
                        background-color: rgba(0, 0, 0, 0.05);
                    }
                """)
    
    def set_compact_mode(self, compact=False):
        """Chuyển đổi giữa chế độ đầy đủ và thu gọn"""
        self.compact_mode = compact
        
        # Điều chỉnh hiển thị các nút
        for button in self.tab_buttons:
            if compact:
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                if hasattr(button, 'original_text'):
                    button.original_text = button.text()
                    button.setText("")
                button.setToolTip(button.original_text)
            else:
                # Khôi phục text nếu có
                if hasattr(button, 'original_text') and button.original_text:
                    button.setText(button.original_text)
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
