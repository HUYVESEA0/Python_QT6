import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar,
                             QMessageBox, QLabel, QToolBar)
from PyQt6.QtGui import QIcon, QAction  # QAction moved here from QtWidgets
from PyQt6.QtCore import QSize
from DB.db_manager import DatabaseManager
from controllers.student_controller import StudentController
from controllers.course_controller import CourseController
from controllers.report_controller import ReportController
from controllers.user_controller import UserController
from views.student_view import StudentView
from views.course_view import CourseView
from views.enrollment_view import EnrollmentView
from views.report_view import ReportView
import logging

class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng quản lý sinh viên.
    """
    def __init__(self, current_user=None):
        super().__init__()
        
        # Lưu thông tin người dùng đăng nhập
        self.current_user = current_user
        
        # Khởi tạo cơ sở dữ liệu
        self.db_manager = DatabaseManager(None)
        
        # Khởi tạo controllers
        self.student_controller = StudentController(self.db_manager)
        self.course_controller = CourseController(self.db_manager)
        self.report_controller = ReportController(self.db_manager)
        self.user_controller = UserController(self.db_manager)
        
        # Thiết lập giao diện
        self.init_ui()
        
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        self.setWindowTitle("Hệ thống Quản lý Sinh viên")
        self.setGeometry(100, 100, 1000, 700)
        
        # Thêm menu
        self.create_menu()
        
        # Thêm toolbar
        self.create_toolbar()
        
        # Tạo tabbed widget
        self.tab_widget = QTabWidget()
        
        # Thêm các tab
        self.student_view = StudentView(self.student_controller)
        self.course_view = CourseView(self.course_controller)
        self.enrollment_view = EnrollmentView(self.student_controller, self.course_controller, self.db_manager)
        self.report_view = ReportView(self.report_controller)
        
        self.tab_widget.addTab(self.student_view, "Quản lý Sinh viên")
        self.tab_widget.addTab(self.course_view, "Quản lý Khóa học")
        self.tab_widget.addTab(self.enrollment_view, "Đăng ký Khóa học")
        self.tab_widget.addTab(self.report_view, "Báo cáo & Thống kê")
        
        # Thiết lập widget trung tâm
        self.setCentralWidget(self.tab_widget)
        
        # Tạo status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Hiển thị thông tin người dùng đăng nhập
        if self.current_user:
            user_info = f"Người dùng: {self.current_user.ho_ten} ({self.current_user.vai_tro})"
            self.user_label = QLabel(user_info)
            self.status_bar.addPermanentWidget(self.user_label)
        
        # Hiển thị thông báo sẵn sàng
        self.status_label = QLabel("Hệ thống đã sẵn sàng")
        self.status_bar.addWidget(self.status_label)
        
        logging.info("Đã khởi tạo giao diện người dùng")
    
    def create_menu(self):
        """Tạo thanh menu của ứng dụng."""
        # Get the menu bar - ensure it's created first
        menu_bar = self.menuBar()
        
        if menu_bar is None:
            logging.warning("Menu bar is None, creating a new one")
            # Create a menu bar explicitly if needed
            menu_bar = self.menuBar()  # Use QMainWindow's built-in method
            self.setMenuBar(menu_bar)
        
        # Menu Hệ thống
        system_menu = menu_bar.addMenu('&Hệ thống')
        
        # Check if the system_menu was created successfully
        if system_menu is None:
            logging.error("Failed to create system menu")
            # Try creating the menu directly as a fallback
            from PyQt6.QtWidgets import QMenu
            system_menu = QMenu("&Hệ thống", menu_bar)
            menu_bar.addMenu(system_menu)
        
        # - Đổi mật khẩu
        change_pwd_action = QAction('Đổi &mật khẩu', self)
        change_pwd_action.setStatusTip('Thay đổi mật khẩu đăng nhập')
        change_pwd_action.triggered.connect(self.change_password)
        
        # Only add action if the menu exists
        if system_menu is not None:
            system_menu.addAction(change_pwd_action)
        
        # Only add separator if the menu exists
        if system_menu is not None:
            system_menu.addSeparator()
        
        # - Thoát
        exit_action = QAction('&Thoát', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Thoát khỏi ứng dụng')
        exit_action.triggered.connect(self.close)
        
        # Only add action if the menu exists
        if system_menu is not None:
            system_menu.addAction(exit_action)
        
        # Menu Quản lý
        manage_menu = menu_bar.addMenu('&Quản lý')
        
        # Check if the manage_menu was created successfully
        if manage_menu is None:
            logging.error("Failed to create manage menu")
            # Try creating the menu directly as a fallback
            manage_menu = QMenu("&Quản lý", menu_bar)
            menu_bar.addMenu(manage_menu)
        
        # - Sinh viên
        student_action = QAction('&Sinh viên', self)
        student_action.setStatusTip('Quản lý sinh viên')
        student_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        
        # Only add action if the menu exists
        if manage_menu is not None:
            manage_menu.addAction(student_action)
        
        # - Khóa học
        course_action = QAction('&Khóa học', self)
        course_action.setStatusTip('Quản lý khóa học')
        course_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        
        # Only add action if the menu exists
        if manage_menu is not None:
            manage_menu.addAction(course_action)
        
        # - Đăng ký
        enrollment_action = QAction('Đăng &ký khóa học', self)
        enrollment_action.setStatusTip('Quản lý đăng ký khóa học')
        enrollment_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        
        # Only add action if the menu exists
        if manage_menu is not None:
            manage_menu.addAction(enrollment_action)
        
        # Menu Báo cáo
        report_menu = menu_bar.addMenu('&Báo cáo')
        
        # Check if the report_menu was created successfully
        if report_menu is None:
            logging.error("Failed to create report menu")
            # Try creating the menu directly as a fallback
            report_menu = QMenu("&Báo cáo", menu_bar)
            menu_bar.addMenu(report_menu)
        
        # - Thống kê
        stats_action = QAction('&Thống kê', self)
        stats_action.setStatusTip('Xem báo cáo thống kê')
        stats_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        
        # Only add action if the menu exists
        if report_menu is not None:
            report_menu.addAction(stats_action)
        
        # Menu Trợ giúp
        help_menu = menu_bar.addMenu('&Trợ giúp')
        
        # Check if the help_menu was created successfully
        if help_menu is None:
            logging.error("Failed to create help menu")
            # Try creating the menu directly as a fallback
            help_menu = QMenu("&Trợ giúp", menu_bar)
            menu_bar.addMenu(help_menu)
        
        # - Giới thiệu
        about_action = QAction('&Giới thiệu', self)
        about_action.setStatusTip('Hiển thị thông tin về ứng dụng')
        about_action.triggered.connect(self.show_about)
        
        # Only add action if the menu exists
        if help_menu is not None:
            help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Tạo thanh công cụ của ứng dụng."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Button Sinh viên
        student_action = QAction(QIcon("resources/icons/student.png") if os.path.exists("resources/icons/student.png") else QIcon(), "Sinh viên", self)
        student_action.setStatusTip("Quản lý sinh viên")
        student_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(student_action)
        
        # Button Khóa học
        course_action = QAction(QIcon("resources/icons/course.png") if os.path.exists("resources/icons/course.png") else QIcon(), "Khóa học", self)
        course_action.setStatusTip("Quản lý khóa học")
        course_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(course_action)
        
        # Button Đăng ký
        enrollment_action = QAction(QIcon("resources/icons/enrollment.png") if os.path.exists("resources/icons/enrollment.png") else QIcon(), "Đăng ký", self)
        enrollment_action.setStatusTip("Đăng ký khóa học")
        enrollment_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(enrollment_action)
        
        # Button Báo cáo
        report_action = QAction(QIcon("resources/icons/report.png") if os.path.exists("resources/icons/report.png") else QIcon(), "Báo cáo", self)
        report_action.setStatusTip("Xem báo cáo thống kê")
        report_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        toolbar.addAction(report_action)
    
    def show_about(self):
        """Hiển thị hộp thoại giới thiệu về ứng dụng."""
        about_text = (
            "Hệ thống Quản lý Sinh viên\n"
            "Phiên bản 1.0\n\n"
            "Một ứng dụng quản lý dễ hiểu, dễ sử dụng cho sinh viên\n\n"
            "© 2025 - Đại học XYZ"
        )
        QMessageBox.about(self, "Giới thiệu", about_text)
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ."""
        reply = QMessageBox.question(
            self, "Xác nhận thoát", 
            "Bạn có chắc muốn thoát khỏi ứng dụng?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Đóng kết nối cơ sở dữ liệu trước khi thoát
            self.db_manager.close()
            logging.info("Ứng dụng đã đóng")
            event.accept()
        else:
            event.ignore()
    
    def change_password(self):
        """Hiển thị hộp thoại đổi mật khẩu."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QPushButton, QLineEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Đổi mật khẩu")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        old_password = QLineEdit()
        old_password.setEchoMode(QLineEdit.EchoMode.Password)
        new_password = QLineEdit()
        new_password.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_password = QLineEdit()
        confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("Mật khẩu cũ:", old_password)
        form.addRow("Mật khẩu mới:", new_password)
        form.addRow("Xác nhận mật khẩu:", confirm_password)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec():
            old_pwd = old_password.text()
            new_pwd = new_password.text()
            confirm_pwd = confirm_password.text()
            
            if new_pwd != confirm_pwd:
                QMessageBox.warning(self, "Lỗi", "Xác nhận mật khẩu không khớp!")
                return
            
            if len(new_pwd) < 4:
                QMessageBox.warning(self, "Lỗi", "Mật khẩu mới phải có ít nhất 4 ký tự!")
                return
            
            if self.current_user:
                success = self.user_controller.change_password(self.current_user.username, old_pwd, new_pwd)
                if success:
                    QMessageBox.information(self, "Thành công", "Đổi mật khẩu thành công!")
                else:
                    QMessageBox.warning(self, "Lỗi", "Mật khẩu cũ không đúng!")