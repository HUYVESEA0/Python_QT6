from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QPushButton,
                            QDialogButtonBox, QMessageBox, QCheckBox,
                            QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QSettings, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont
import os
import logging

class LoginDialog(QDialog):
    """
    Dialog hiển thị giao diện đăng nhập.
    """
    # Add loginSuccessful signal
    loginSuccessful = pyqtSignal(object)
    
    def __init__(self, user_controller, theme_manager=None):
        super().__init__()
        self.setObjectName("loginDialog")
        self.user_controller = user_controller
        self.theme_manager = theme_manager
        self.user = None
        self.settings = QSettings("XYZ University", "StudentManagementSystem")
        self.init_ui()
        
        # Apply current theme if theme manager was provided
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def on_theme_changed(self, theme_name):
        """Handle theme changes."""
        # Update specific UI elements for the login dialog that need theme-specific styling
        if theme_name == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Apply dark theme specific styles."""
        # These are additional styles specific to the login dialog
        # The main theme stylesheet is already applied to the application
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D30;
            }
            QLabel[heading="true"] {
                color: #E1E1E1;
            }
            QLabel {
                color: #E1E1E1;
            }
            QCheckBox {
                color: #E1E1E1;
            }
        """)
    
    def apply_light_theme(self):
        """Apply light theme specific styles."""
        # Reset to default which inherits from QApplication stylesheet
        self.setStyleSheet("")
    
    def init_ui(self):
        """Thiết lập giao diện đăng nhập."""
        self.setWindowTitle("Đăng nhập")
        self.setWindowIcon(QIcon("resources/icons/login.png") if os.path.exists("resources/icons/login.png") else QIcon())
        self.setMinimumSize(400, 350)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        
        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo và tiêu đề
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        if os.path.exists("resources/logo.png"):
            logo_label = QLabel()
            pixmap = QPixmap("resources/logo.png")
            scaled_pixmap = pixmap.scaled(QSize(80, 80), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(logo_label)
        
        # Tiêu đề
        title_label = QLabel("Hệ thống Quản lý Sinh viên")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Tiêu đề phụ
        subtitle_label = QLabel("Đăng nhập để tiếp tục")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        
        # Form đăng nhập
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(15)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        form_layout.addRow("Tên đăng nhập:", self.username_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        form_layout.addRow("Mật khẩu:", self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # Remember me
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        remember_layout.addWidget(self.remember_checkbox)
        
        # Nút quên mật khẩu
        self.forgot_button = QPushButton("Quên mật khẩu?")
        self.forgot_button.setFlat(True)
        self.forgot_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot_button.clicked.connect(self.forgot_password)
        remember_layout.addStretch()
        remember_layout.addWidget(self.forgot_button)
        
        main_layout.addLayout(remember_layout)
        main_layout.addSpacing(10)
        
        # Login button
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)
        
        # Version info
        version_label = QLabel("Phiên bản 2.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(version_label)
        
        self.setLayout(main_layout)
        
        # Load saved credentials if exists
        self.load_saved_credentials()
        
        # Connect Enter key to login function
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
        
        # Check current theme and apply specific styles if needed
        if self.theme_manager and self.theme_manager.get_current_theme() == "dark":
            self.apply_dark_theme()
    
    def load_saved_credentials(self):
        """Tải thông tin đăng nhập đã lưu."""
        if self.settings.contains("login/remember") and self.settings.value("login/remember") == "true":
            username = self.settings.value("login/username", "")
            self.username_input.setText(username)
            self.remember_checkbox.setChecked(True)
            
            # Focus to password field if username is filled
            if username:
                self.password_input.setFocus()
        else:
            self.username_input.setFocus()
    
    def save_credentials(self, username):
        """Lưu thông tin đăng nhập."""
        if self.remember_checkbox.isChecked():
            self.settings.setValue("login/remember", "true")
            self.settings.setValue("login/username", username)
        else:
            self.settings.setValue("login/remember", "false")
            self.settings.remove("login/username")
    
    def login(self):
        """Xử lý đăng nhập."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Lỗi đăng nhập", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return
        
        # Hiển thị thông báo đang đăng nhập
        self.login_button.setEnabled(False)
        self.login_button.setText("Đang đăng nhập...")
        
        # Thực hiện đăng nhập
        self.user = self.user_controller.authenticate(username, password)
        
        if self.user:
            # Lưu thông tin đăng nhập nếu được chọn
            self.save_credentials(username)
            logging.info(f"Đăng nhập thành công: {username}")
            # Emit loginSuccessful signal with the user object
            self.loginSuccessful.emit(self.user)
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi đăng nhập", 
                               "Tên đăng nhập hoặc mật khẩu không chính xác!")
            self.password_input.clear()
            self.password_input.setFocus()
            logging.warning(f"Đăng nhập thất bại: {username}")
            
            # Reset login button
            self.login_button.setEnabled(True)
            self.login_button.setText("Đăng nhập")
    
    def forgot_password(self):
        """Xử lý khi người dùng quên mật khẩu."""
        QMessageBox.information(self, "Quên mật khẩu", 
                             "Vui lòng liên hệ với quản trị viên để lấy lại mật khẩu.\n"
                             "Email: admin@xyz.edu.vn\n"
                             "Hotline: 1900 xxxx")
    
    def get_user(self):
        """Trả về người dùng đã đăng nhập."""
        return self.user
