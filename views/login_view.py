from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QMessageBox, QGridLayout,
                           QFormLayout, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

class LoginDialog(QDialog):
    """
    Dialog đăng nhập vào hệ thống.
    """
    # Signal phát ra khi đăng nhập thành công
    loginSuccessful = pyqtSignal(object)  # Truyền đối tượng User
    
    def __init__(self, user_controller):
        """
        Khởi tạo dialog đăng nhập.
        
        Args:
            user_controller (UserController): Controller quản lý người dùng
        """
        super().__init__()
        self.user_controller = user_controller
        self.init_ui()
        
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        # Thiết lập cửa sổ
        self.setWindowTitle("Đăng nhập hệ thống")
        self.setFixedSize(400, 300)
        
        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # Tiêu đề
        title_layout = QHBoxLayout()
        title_label = QLabel("ĐĂNG NHẬP HỆ THỐNG QUẢN LÝ SINH VIÊN")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2A66C8; margin-bottom: 20px;")
        title_layout.addWidget(title_label)
        main_layout.addLayout(title_layout)
        
        # Form đăng nhập
        form_layout = QFormLayout()
        form_layout.setContentsMargins(30, 20, 30, 20)
        form_layout.setSpacing(15)
        
        # Tên đăng nhập
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        form_layout.addRow("Tên đăng nhập:", self.username_input)
        
        # Mật khẩu
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Mật khẩu:", self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # Thêm khoảng trống
        main_layout.addStretch(1)
        
        # Nút đăng nhập và thoát
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setStyleSheet("background-color: #4A86E8; color: white; font-weight: bold; padding: 8px;")
        self.login_button.clicked.connect(self.attempt_login)
        
        self.exit_button = QPushButton("Thoát")
        self.exit_button.setStyleSheet("background-color: #9B9B9B; color: white; padding: 8px;")
        self.exit_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(button_layout)
        
        # Thông tin phần mềm
        info_label = QLabel("Phiên bản 1.0 - © 2025 Đại học XYZ")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 10px; color: #888888; margin-top: 10px;")
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
        
        # Kết nối Enter key với nút đăng nhập
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
    
    def attempt_login(self):
        """Thực hiện đăng nhập khi người dùng nhấn nút hoặc Enter."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(
                self, "Lỗi đăng nhập", 
                "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"
            )
            return
        
        # Thực hiện xác thực
        user = self.user_controller.authenticate(username, password)
        
        if user:
            # Đăng nhập thành công
            self.loginSuccessful.emit(user)
            self.accept()
        else:
            # Đăng nhập thất bại
            QMessageBox.warning(
                self, "Lỗi đăng nhập", 
                "Tên đăng nhập hoặc mật khẩu không chính xác!"
            )
            self.password_input.clear()
            self.password_input.setFocus()

class ForgotPasswordDialog(QDialog):
    """
    Dialog quên mật khẩu (phần mở rộng trong tương lai).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quên mật khẩu")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Vui lòng liên hệ quản trị viên để được hỗ trợ đặt lại mật khẩu."))
        
        button = QPushButton("Đóng")
        button.clicked.connect(self.accept)
        layout.addWidget(button)
        
        self.setLayout(layout)
