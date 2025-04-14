import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar,
                             QMessageBox, QLabel, QToolBar, QWidget,
                             QMenu, QDialog, QVBoxLayout, QFormLayout, 
                             QPushButton, QLineEdit, QDialogButtonBox,
                             QSplashScreen)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont, QImage, QCursor
from PyQt6.QtCore import Qt, QSize, QTimer
from DB.db_manager import DatabaseManager
from controllers.student_controller import StudentController
from controllers.course_controller import CourseController
from controllers.report_controller import ReportController
from controllers.user_controller import UserController
from views.student_view import StudentView
from views.course_view import CourseView
from views.enrollment_view import EnrollmentView
from views.report_view import ReportView
from views.dashboard_view import DashboardView
from views.activity_log_view import ActivityLogView
from utils.theme_manager import ThemeManager
from utils.notification_manager import NotificationManager, NotificationType
from utils.config_manager import ConfigManager
import logging

class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng quản lý sinh viên.
    """
    def __init__(self, current_user=None):
        super().__init__()
        
        try:
            # Lưu thông tin người dùng đăng nhập
            self.current_user = current_user
            
            # Khởi tạo cơ sở dữ liệu
            self.db_manager = DatabaseManager()
            
            # Kiểm tra tính toàn vẹn cơ sở dữ liệu
            if not self.db_manager.check_database_integrity():
                QMessageBox.warning(
                    self,
                    "Cảnh báo",
                    "Phát hiện vấn đề với cơ sở dữ liệu. Hãy liên hệ quản trị viên để khắc phục."
                )
            
            # Khởi tạo controllers
            self.student_controller = StudentController(self.db_manager)
            self.course_controller = CourseController(self.db_manager)
            self.report_controller = ReportController(self.db_manager)
            self.user_controller = UserController(self.db_manager)
            
            # Khởi tạo config manager
            self.config_manager = ConfigManager()
            
            # Khởi tạo theme manager
            self.theme_manager = ThemeManager()
            
            # Khởi tạo notification manager
            self.notification_manager = NotificationManager()
            self.notification_manager.set_parent(self)  # Thiết lập parent
            
            # Thiết lập giao diện
            self.init_ui()
            
            # Áp dụng theme lưu trong cài đặt
            self.theme_manager.apply_current_theme()
            
            # Hiển thị thông báo chào mừng
            if self.config_manager.get("ui", "show_welcome", True):
                self.show_welcome_notification()
                
        except Exception as e:
            logging.critical(f"Lỗi khởi tạo cửa sổ chính: {e}")
            QMessageBox.critical(
                self,
                "Lỗi nghiêm trọng",
                f"Không thể khởi tạo ứng dụng: {str(e)}.\nVui lòng liên hệ hỗ trợ kỹ thuật."
            )
        
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        self.setWindowTitle("Hệ thống Quản lý Sinh viên - Phiên bản 2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Thêm menu
        self.create_menu()
        
        # Thêm toolbar
        self.create_toolbar()
        
        # Tạo tabbed widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        
        # Thêm các tab
        self.dashboard_view = DashboardView(
            self.student_controller, 
            self.course_controller,
            self.report_controller
        )
        self.student_view = StudentView(
            self.student_controller, 
            current_user_id=self.current_user.user_id if self.current_user else None
        )
        self.course_view = CourseView(self.course_controller)
        self.enrollment_view = EnrollmentView(self.student_controller, self.course_controller, self.db_manager)
        self.report_view = ReportView(self.report_controller)
        self.activity_log_view = ActivityLogView(self.db_manager)
        
        self.tab_widget.addTab(self.dashboard_view, QIcon("resources/icons/dashboard.png") if os.path.exists("resources/icons/dashboard.png") else QIcon(), "Dashboard")
        self.tab_widget.addTab(self.student_view, QIcon("resources/icons/student.png") if os.path.exists("resources/icons/student.png") else QIcon(), "Sinh viên")
        self.tab_widget.addTab(self.course_view, QIcon("resources/icons/course.png") if os.path.exists("resources/icons/course.png") else QIcon(), "Khóa học")
        self.tab_widget.addTab(self.enrollment_view, QIcon("resources/icons/enrollment.png") if os.path.exists("resources/icons/enrollment.png") else QIcon(), "Đăng ký")
        self.tab_widget.addTab(self.report_view, QIcon("resources/icons/report.png") if os.path.exists("resources/icons/report.png") else QIcon(), "Báo cáo")
        
        # Chỉ hiển thị tab nhật ký cho admin
        if self.current_user and self.current_user.role == "admin":
            self.tab_widget.addTab(self.activity_log_view, QIcon("resources/icons/log.png") if os.path.exists("resources/icons/log.png") else QIcon(), "Nhật ký")
        
        # Thiết lập widget trung tâm
        self.setCentralWidget(self.tab_widget)
        
        # Tạo status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Hiển thị thông tin người dùng đăng nhập
        if self.current_user:
            user_info = f"Người dùng: {self.current_user.full_name} ({self.current_user.role})"
            self.user_label = QLabel(user_info)
            self.status_bar.addPermanentWidget(self.user_label)
        
        # Hiển thị theme hiện tại
        self.theme_label = QLabel(f"Theme: {self.theme_manager.get_current_theme().capitalize()}")
        self.status_bar.addPermanentWidget(self.theme_label)
        
        # Hiển thị thông báo sẵn sàng
        self.status_label = QLabel("Hệ thống đã sẵn sàng")
        self.status_bar.addWidget(self.status_label)
        
        logging.info("Đã khởi tạo giao diện người dùng")
        
        # Thêm timer để kiểm tra kết nối cơ sở dữ liệu định kỳ
        self.connection_check_timer = QTimer(self)
        self.connection_check_timer.timeout.connect(self.check_database_connection)
        self.connection_check_timer.start(60000)  # Kiểm tra mỗi 60 giây
    
    def check_database_connection(self):
        """Kiểm tra kết nối đến cơ sở dữ liệu."""
        if not self.db_manager.connection:
            try:
                self.db_manager.connect()
                if self.db_manager.connection:
                    self.notification_manager.show_success("Đã khôi phục kết nối đến cơ sở dữ liệu")
            except:
                self.notification_manager.show_warning("Mất kết nối đến cơ sở dữ liệu. Đang thử kết nối lại...")
    
    def create_menu(self):
        """Tạo thanh menu của ứng dụng."""
        menu_bar = self.menuBar()
        
        # Menu Hệ thống
        system_menu = menu_bar.addMenu('&Hệ thống')
        
        # - Dashboard
        dashboard_action = QAction(QIcon("resources/icons/dashboard.png") if os.path.exists("resources/icons/dashboard.png") else QIcon(), '&Dashboard', self)
        dashboard_action.setStatusTip('Hiển thị trang tổng quan')
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        system_menu.addAction(dashboard_action)
        
        system_menu.addSeparator()
        
        # - Đổi theme
        theme_menu = QMenu('Giao diện', self)
        light_theme_action = QAction('Chế độ sáng', self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        dark_theme_action = QAction('Chế độ tối', self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        toggle_theme_action = QAction('Chuyển đổi chế độ', self)
        toggle_theme_action.setShortcut('Ctrl+T')
        toggle_theme_action.triggered.connect(self.toggle_theme)
        
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)
        theme_menu.addAction(toggle_theme_action)
        system_menu.addMenu(theme_menu)
        
        # - Đổi mật khẩu
        change_pwd_action = QAction('Đổi &mật khẩu', self)
        change_pwd_action.setStatusTip('Thay đổi mật khẩu đăng nhập')
        change_pwd_action.triggered.connect(self.change_password)
        system_menu.addAction(change_pwd_action)
        
        system_menu.addSeparator()
        
        # - Thoát
        exit_action = QAction('&Thoát', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Thoát khỏi ứng dụng')
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)
        
        # Menu Quản lý
        manage_menu = menu_bar.addMenu('&Quản lý')
        
        # - Sinh viên
        student_action = QAction(QIcon("resources/icons/student.png") if os.path.exists("resources/icons/student.png") else QIcon(), '&Sinh viên', self)
        student_action.setStatusTip('Quản lý sinh viên')
        student_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        manage_menu.addAction(student_action)
        
        # - Khóa học
        course_action = QAction(QIcon("resources/icons/course.png") if os.path.exists("resources/icons/course.png") else QIcon(), '&Khóa học', self)
        course_action.setStatusTip('Quản lý khóa học')
        course_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        manage_menu.addAction(course_action)
        
        # - Đăng ký
        enrollment_action = QAction(QIcon("resources/icons/enrollment.png") if os.path.exists("resources/icons/enrollment.png") else QIcon(), 'Đăng &ký khóa học', self)
        enrollment_action.setStatusTip('Quản lý đăng ký khóa học')
        enrollment_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        manage_menu.addAction(enrollment_action)
        
        # Menu Báo cáo
        report_menu = menu_bar.addMenu('&Báo cáo')
        
        # - Thống kê
        stats_action = QAction(QIcon("resources/icons/report.png") if os.path.exists("resources/icons/report.png") else QIcon(), '&Thống kê', self)
        stats_action.setStatusTip('Xem báo cáo thống kê')
        stats_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        report_menu.addAction(stats_action)
        
        # - Nhật ký hoạt động (chỉ dành cho admin)
        if self.current_user and self.current_user.role == "admin":
            log_action = QAction(QIcon("resources/icons/log.png") if os.path.exists("resources/icons/log.png") else QIcon(), '&Nhật ký hoạt động', self)
            log_action.setStatusTip('Xem nhật ký hoạt động của hệ thống')
            log_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))
            report_menu.addAction(log_action)
        
        # Menu trích xuất
        export_menu = menu_bar.addMenu('&Trích xuất')
        
        # - Xuất danh sách sinh viên
        export_students_action = QAction('Danh sách sinh viên', self)
        export_students_action.setStatusTip('Xuất danh sách sinh viên ra file Excel')
        export_students_action.triggered.connect(self.export_students)
        export_menu.addAction(export_students_action)
        
        # - Xuất danh sách khóa học
        export_courses_action = QAction('Danh sách khóa học', self)
        export_courses_action.setStatusTip('Xuất danh sách khóa học ra file Excel')
        export_courses_action.triggered.connect(self.export_courses)
        export_menu.addAction(export_courses_action)
        
        # - Xuất báo cáo
        export_report_action = QAction('Báo cáo thống kê', self)
        export_report_action.setStatusTip('Xuất báo cáo thống kê ra file PDF')
        export_report_action.triggered.connect(self.export_report)
        export_menu.addAction(export_report_action)
        
        # Menu Trợ giúp
        help_menu = menu_bar.addMenu('&Trợ giúp')
        
        # - Giới thiệu
        about_action = QAction('&Giới thiệu', self)
        about_action.setStatusTip('Thông tin về ứng dụng')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Tạo thanh công cụ của ứng dụng."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Button Dashboard
        dashboard_action = QAction(QIcon("resources/icons/dashboard.png") if os.path.exists("resources/icons/dashboard.png") else QIcon(), "Dashboard", self)
        dashboard_action.setStatusTip("Dashboard")
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(dashboard_action)
        
        # Button Sinh viên
        student_action = QAction(QIcon("resources/icons/student.png") if os.path.exists("resources/icons/student.png") else QIcon(), "Sinh viên", self)
        student_action.setStatusTip("Quản lý sinh viên")
        student_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(student_action)
        
        # Button Khóa học
        course_action = QAction(QIcon("resources/icons/course.png") if os.path.exists("resources/icons/course.png") else QIcon(), "Khóa học", self)
        course_action.setStatusTip("Quản lý khóa học")
        course_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(course_action)
        
        # Button Đăng ký
        enrollment_action = QAction(QIcon("resources/icons/enrollment.png") if os.path.exists("resources/icons/enrollment.png") else QIcon(), "Đăng ký", self)
        enrollment_action.setStatusTip("Đăng ký khóa học")
        enrollment_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        toolbar.addAction(enrollment_action)
        
        # Button Báo cáo
        report_action = QAction(QIcon("resources/icons/report.png") if os.path.exists("resources/icons/report.png") else QIcon(), "Báo cáo", self)
        report_action.setStatusTip("Xem báo cáo thống kê")
        report_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        toolbar.addAction(report_action)
        
        # Thêm separator
        toolbar.addSeparator()
        
        # Toggle Theme button
        theme_action = QAction(QIcon("resources/icons/theme.png") if os.path.exists("resources/icons/theme.png") else QIcon(), "Đổi giao diện", self)
        theme_action.setStatusTip("Chuyển đổi giữa chế độ sáng/tối")
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)
        
        # Button Thông báo
        notification_action = QAction(QIcon("resources/icons/notification.png") if os.path.exists("resources/icons/notification.png") else QIcon(), "Thông báo", self)
        notification_action.setStatusTip("Hiển thị thông báo thử nghiệm")
        notification_action.triggered.connect(self.show_test_notification)
        toolbar.addAction(notification_action)
        
        # Button trợ giúp
        help_action = QAction(QIcon("resources/icons/help.png") if os.path.exists("resources/icons/help.png") else QIcon(), "Trợ giúp", self)
        help_action.setStatusTip("Hiển thị trợ giúp")
        help_action.triggered.connect(self.show_about)
        toolbar.addAction(help_action)
    
    def change_theme(self, theme_name):
        """Thay đổi theme của ứng dụng"""
        if self.theme_manager.set_theme(theme_name):
            self.theme_label.setText(f"Theme: {theme_name.capitalize()}")
            self.status_label.setText(f"Đã chuyển sang giao diện {theme_name.capitalize()}")
            # Hiển thị thông báo
            self.notification_manager.show_info(f"Đã chuyển sang giao diện {theme_name.capitalize()}")
    
    def toggle_theme(self):
        """Chuyển đổi giữa chế độ sáng và tối"""
        new_theme = self.theme_manager.toggle_theme()
        self.theme_label.setText(f"Theme: {new_theme.capitalize()}")
        self.status_label.setText(f"Đã chuyển sang giao diện {new_theme.capitalize()}")
        # Hiển thị thông báo
        self.notification_manager.show_info(f"Đã chuyển sang giao diện {new_theme.capitalize()}")
    
    def show_welcome_notification(self):
        """Hiển thị thông báo chào mừng"""
        greeting = "Buổi sáng" if 5 <= datetime.now().hour < 12 else "Buổi chiều" if 12 <= datetime.now().hour < 18 else "Buổi tối"
        username = self.current_user.full_name if self.current_user and self.current_user.full_name else "Người dùng"
        
        # Hiển thị thông báo chào mừng
        welcome_msg = f"{greeting} tốt lành, {username}! Chào mừng bạn đến với Hệ thống Quản lý Sinh viên."
        self.notification_manager.show_success(welcome_msg, timeout=8000)
        
        # Hiển thị thông tin hệ thống
        student_count = self.student_controller.get_student_count()
        course_count = self.course_controller.get_course_count()
        system_info = f"Hệ thống hiện có {student_count} sinh viên và {course_count} khóa học."
        
        # Đặt timer để hiển thị thông báo thứ hai sau thông báo đầu tiên
        QTimer.singleShot(1500, lambda: self.notification_manager.show_info(system_info, timeout=7000))
    
    def show_test_notification(self):
        """Hiển thị các loại thông báo để thử nghiệm"""
        notification_menu = QMenu(self)
        info_action = notification_menu.addAction("Thông báo thông tin")
        success_action = notification_menu.addAction("Thông báo thành công")
        warning_action = notification_menu.addAction("Thông báo cảnh báo")
        error_action = notification_menu.addAction("Thông báo lỗi")
        
        action = notification_menu.exec(QCursor.pos())
        
        if action == info_action:
            self.notification_manager.show_info("Đây là thông báo thông tin cho người dùng.")
        elif action == success_action:
            self.notification_manager.show_success("Thao tác đã được thực hiện thành công!")
        elif action == warning_action:
            self.notification_manager.show_warning("Cảnh báo! Hãy kiểm tra lại thông tin.")
        elif action == error_action:
            self.notification_manager.show_error("Lỗi! Không thể thực hiện thao tác.")
    
    def show_about(self):
        """Hiển thị hộp thoại giới thiệu về ứng dụng."""
        about_text = (
            "<h2>Hệ thống Quản lý Sinh viên</h2>"
            "<p><b>Phiên bản 2.0</b></p>"
            "<p>Phần mềm quản lý sinh viên hiện đại với giao diện thân thiện, dễ sử dụng</p>"
            "<p>Tính năng nổi bật:</p>"
            "<ul>"
            "<li>Dashboard tổng quan trực quan</li>"
            "<li>Giao diện tối/sáng tùy chỉnh</li>"
            "<li>Biểu đồ thống kê chuyên nghiệp</li>"
            "<li>Quản lý ảnh đại diện sinh viên</li>"
            "<li>Hệ thống thông báo hiện đại</li>"
            "<li>Xuất dữ liệu ra Excel và PDF</li>"
            "<li>Quản lý dữ liệu hiệu quả</li>"
            "</ul>"
            "<p>&copy; 2025 - Đại học XYZ</p>"
        )
        
        # Tạo QMessageBox với HTML formatting
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Giới thiệu")
        msg_box.setText(about_text)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        # Thêm logo nếu có
        if os.path.exists("resources/logo.png"):
            pixmap = QPixmap("resources/logo.png")
            msg_box.setIconPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
            
        msg_box.exec()
    
    def change_password(self):
        """Hiển thị hộp thoại đổi mật khẩu."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Đổi mật khẩu")
        dialog.setMinimumWidth(350)
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
                    self.notification_manager.show_success("Mật khẩu đã được thay đổi thành công!")
                    
                    # Ghi log
                    if self.current_user:
                        self.db_manager.log_activity(
                            self.current_user.user_id,
                            "UPDATE",
                            "Thay đổi mật khẩu",
                            "User",
                            self.current_user.user_id
                        )
                else:
                    QMessageBox.warning(self, "Lỗi", "Mật khẩu cũ không đúng!")
                    self.notification_manager.show_error("Không thể thay đổi mật khẩu. Mật khẩu cũ không đúng!")
    
    def export_students(self):
        """Xuất danh sách sinh viên ra Excel"""
        from utils.export_manager import ExportManager
        
        students = self.student_controller.get_all_students()
        if not students:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu sinh viên để xuất!")
            return
        
        # Chuẩn bị dữ liệu
        headers = ["Mã SV", "Họ tên", "Ngày sinh", "Giới tính", "Email", "SĐT", "Địa chỉ", "Ngày nhập học", "Trạng thái"]
        data = []
        
        for student in students:
            data.append([
                student.student_id,
                student.full_name,
                student.date_of_birth,
                student.gender,
                student.email,
                student.phone,
                student.address,
                student.enrolled_date,
                student.status
            ])
        
        # Xuất ra Excel
        success = ExportManager.export_to_excel(
            data, 
            headers, 
            parent=self, 
            default_filename="danh_sach_sinh_vien.xlsx"
        )
        
        if success and self.current_user:
            self.db_manager.log_activity(
                self.current_user.user_id,
                "EXPORT",
                "Xuất danh sách sinh viên ra Excel",
                "Student",
                None
            )
    
    def export_courses(self):
        """Xuất danh sách khóa học ra Excel"""
        from utils.export_manager import ExportManager
        
        courses = self.course_controller.get_all_courses()
        if not courses:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu khóa học để xuất!")
            return
        
        # Chuẩn bị dữ liệu
        headers = ["Mã KH", "Tên khóa học", "Tín chỉ", "Giảng viên", "Mô tả", "SV tối đa"]
        data = []
        
        for course in courses:
            data.append([
                course.course_id,
                course.course_name,
                course.credits,
                course.instructor,
                course.description,
                course.max_students
            ])
        
        # Xuất ra Excel
        success = ExportManager.export_to_excel(
            data, 
            headers, 
            parent=self, 
            default_filename="danh_sach_khoa_hoc.xlsx"
        )
        
        if success and self.current_user:
            self.db_manager.log_activity(
                self.current_user.user_id,
                "EXPORT",
                "Xuất danh sách khóa học ra Excel",
                "Course",
                None
            )
    
    def export_report(self):
        """Xuất báo cáo thống kê ra PDF"""
        # Chuyển đến tab báo cáo trước để người dùng thấy dữ liệu
        self.tab_widget.setCurrentIndex(4)
        
        # Hiển thị thông báo cho biết đang chuyển đến tab báo cáo
        self.notification_manager.show_info("Đã chuyển đến tab Báo cáo. Vui lòng sử dụng nút 'Xuất PDF' trên tab để xuất báo cáo.")
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ."""
        try:
            reply = QMessageBox.question(
                self, "Xác nhận thoát", 
                "Bạn có chắc muốn thoát khỏi ứng dụng?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Dọn dẹp tài nguyên tạm thời
                if hasattr(self, "student_view") and self.student_view and hasattr(self.student_view, "photo_frame"):
                    self.student_view.photo_frame.cleanup_temp_files()
                
                # Tạo bản sao lưu nếu cài đặt cho phép
                if self.config_manager.get("database", "backup_on_exit", True):
                    self.db_manager.backup_database()
                
                # Tối ưu hóa cơ sở dữ liệu khi thoát
                try:
                    self.db_manager.optimize_database()
                except:
                    pass
                
                # Ghi log đăng xuất
                if self.current_user:
                    self.db_manager.log_activity(
                        self.current_user.user_id,
                        "LOGOUT",
                        f"Đăng xuất: {self.current_user.username}",
                        "User",
                        self.current_user.user_id
                    )
                
                # Đóng kết nối cơ sở dữ liệu trước khi thoát
                self.db_manager.close()
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            logging.error(f"Lỗi khi đóng ứng dụng: {e}")
            # Đảm bảo ứng dụng đóng ngay cả khi có lỗi
            event.accept()