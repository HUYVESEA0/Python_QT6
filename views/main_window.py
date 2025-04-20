import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar,
                             QMessageBox, QLabel, QToolBar, QWidget,
                             QMenu, QDialog, QVBoxLayout, QFormLayout, 
                             QPushButton, QLineEdit, QDialogButtonBox,
                             QSplashScreen, QHBoxLayout, QApplication)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont, QImage, QCursor, QActionGroup
from PyQt6.QtCore import Qt, QSize, QTimer, QPoint
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
# Removed ThemeManager import
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
            # Lưu thông tin người dùng hiện tại
            self.current_user = current_user
            
            # Khởi tạo config manager
            from utils.config_manager import ConfigManager
            self.config_manager = ConfigManager()
            
            # Khởi tạo các thành phần quan trọng
            from utils.notification_manager import NotificationManager
            
            # Removed theme manager initialization
            
            # Khởi tạo notification manager
            self.notification_manager = NotificationManager()
            self.notification_manager.set_parent(self)
            # Removed theme manager setter
            
            # Khởi tạo database manager
            from DB.db_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            
            # Khởi tạo các controllers
            from controllers.student_controller import StudentController
            self.student_controller = StudentController(self.db_manager)
            
            from controllers.course_controller import CourseController
            self.course_controller = CourseController(self.db_manager)
            
            from controllers.report_controller import ReportController
            self.report_controller = ReportController(self.db_manager)
            
            # Thiết lập giao diện
            self.init_ui()
            
            # Khôi phục trạng thái cửa sổ
            self.restore_window_state()
            
            # Kiểm tra kết nối cơ sở dữ liệu
            self.check_database_connection()
            
            # Hiển thị thông báo chào mừng
            show_welcome = self.config_manager.get("ui", "show_welcome", True)
            if show_welcome:
                self.show_welcome_notification()
                
        except Exception as e:
            logging.critical(f"Lỗi khởi tạo cửa sổ chính: {e}")
            QMessageBox.critical(
                self,
                "Lỗi nghiêm trọng",
                f"Không thể khởi tạo ứng dụng: {str(e)}.\nVui lòng liên hệ hỗ trợ kỹ thuật."
            )
        
    def init_ui(self):
        """Thiết lập giao diện người dùng với tabbar truyền thống."""
        self.setWindowTitle("Hệ thống Quản lý Sinh viên - Phiên bản 2.0")
        self.setGeometry(100, 100, 1280, 800)
        
        # Thiết lập icon cho ứng dụng
        icon_path = "resources/icons/app_icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Tạo menu bar
        self.create_menu_bar()
        
        # Tạo toolbar
        self.create_toolbar()
        
        # Tạo widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tạo tabbed widget với giao diện truyền thống
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabBarAutoHide(False)  # Hiển thị tab bar
        
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
        
        # Set object names để có thể style riêng trong QSS
        self.dashboard_view.setObjectName("dashboardView")
        self.student_view.setObjectName("studentView")
        self.course_view.setObjectName("courseView")
        self.enrollment_view.setObjectName("enrollmentView")
        self.report_view.setObjectName("reportView")
        self.activity_log_view.setObjectName("activityLogView")
        
        # Thêm các tab với icons
        icons_path = "resources/icons/"
        self.tab_widget.addTab(self.dashboard_view, QIcon(icons_path + "dashboard.png"), "Dashboard")
        self.tab_widget.addTab(self.student_view, QIcon(icons_path + "student.png"), "Sinh viên")
        self.tab_widget.addTab(self.course_view, QIcon(icons_path + "course.png"), "Khóa học")
        self.tab_widget.addTab(self.enrollment_view, QIcon(icons_path + "enrollment.png"), "Đăng ký")
        self.tab_widget.addTab(self.report_view, QIcon(icons_path + "report.png"), "Báo cáo")
        
        # Tab nhật ký chỉ hiển thị với admin
        if self.current_user and self.current_user.role == "admin":
            self.tab_widget.addTab(self.activity_log_view, QIcon(icons_path + "activity.png"), "Nhật ký")
        
        main_layout.addWidget(self.tab_widget)
        
        # Thiết lập status bar với thông tin người dùng
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Hiển thị thông tin người dùng đăng nhập
        if self.current_user:
            user_label = QLabel(f"Người dùng: {self.current_user.full_name} ({self.current_user.role})")
            self.status_bar.addPermanentWidget(user_label)
        
        # Removed theme label
        
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
    
    def create_navbar(self):
        """Tạo navbar hiện đại kết hợp menu và toolbar"""
        icons_path = "resources/icons/"
        
        dashboard_btn = self.navbar.add_tab_button("Dashboard", icons_path + "dashboard.png", 0, "Trang tổng quan")
        student_btn = self.navbar.add_tab_button("Sinh viên", icons_path + "student.png", 1, "Quản lý sinh viên")
        course_btn = self.navbar.add_tab_button("Khóa học", icons_path + "course.png", 2, "Quản lý khóa học")
        enrollment_btn = self.navbar.add_tab_button("Đăng ký", icons_path + "enrollment.png", 3, "Đăng ký khóa học")
        report_btn = self.navbar.add_tab_button("Báo cáo", icons_path + "report.png", 4, "Xem báo cáo thống kê")
        
        # Hiển thị tab nhật ký chỉ cho admin
        if self.current_user and self.current_user.role == "admin":
            log_btn = self.navbar.add_tab_button("Nhật ký", icons_path + "activity.png", 5, "Xem nhật ký hoạt động")
        
        # Thêm menu Hệ thống
        system_btn, system_menu = self.navbar.add_menu_button("Hệ thống", icons_path + "system.png")
        
        # Các hành động trong menu Hệ thống
        self.navbar.add_action_to_menu("Hệ thống", "Đổi mật khẩu", self.change_password, 
                                   icons_path + "password.png", "Ctrl+P")
        
        # Removed theme menu
                                   
        self.navbar.add_separator_to_menu("Hệ thống")
        self.navbar.add_action_to_menu("Hệ thống", "Thoát", self.close, 
                                  icons_path + "exit.png", "Ctrl+Q")
        
        # Thêm menu Trích xuất
        export_btn, export_menu = self.navbar.add_menu_button("Trích xuất", icons_path + "export.png")
        
        # Các hành động trong menu Trích xuất
        self.navbar.add_action_to_menu("Trích xuất", "Danh sách sinh viên", self.export_students, 
                                  icons_path + "student_export.png")
        self.navbar.add_action_to_menu("Trích xuất", "Danh sách khóa học", self.export_courses, 
                                  icons_path + "course_export.png")
        self.navbar.add_action_to_menu("Trích xuất", "Báo cáo thống kê", self.export_report, 
                                  icons_path + "report_export.png")
        
        # Thêm menu Trợ giúp
        help_btn, help_menu = self.navbar.add_menu_button("Trợ giúp", icons_path + "help.png")
        
        # Các hành động trong menu Trợ giúp
        self.navbar.add_action_to_menu("Trợ giúp", "Giới thiệu", self.show_about, 
                                  icons_path + "about.png")
        
        # Thêm các nút bên phải
        # Nút thông báo
        notification_btn = QPushButton()
        notification_btn.setIcon(QIcon(icons_path + "notification.png") if os.path.exists(icons_path + "notification.png") else QIcon())
        notification_btn.setIconSize(QSize(20, 20))
        notification_btn.setToolTip("Hiển thị thông báo")
        notification_btn.setFixedSize(36, 36)
        notification_btn.setObjectName("notificationButton")
        notification_btn.clicked.connect(self.show_test_notification)
        
        # Removed theme button
        
        # Thêm nút vào bên phải navbar
        self.navbar.add_right_aligned_widget(notification_btn)

    def show_search_dialog(self):
        """Hiển thị hộp thoại tìm kiếm"""
        # Chức năng tìm kiếm sẽ được triển khai sau
        self.notification_manager.show_info("Chức năng tìm kiếm đang được phát triển")

    def show_user_menu(self):
        """Hiển thị menu tài khoản người dùng"""
        if not self.current_user:
            return
        
        menu = QMenu(self)
        
        # Hiển thị thông tin người dùng
        user_info = QAction(f"{self.current_user.full_name} ({self.current_user.role})", self)
        user_info.setEnabled(False)
        menu.addAction(user_info)
        
        menu.addSeparator()
        
        # Các tùy chọn tài khoản
        change_pwd_action = QAction("Đổi mật khẩu", self)
        change_pwd_action.triggered.connect(self.change_password)
        menu.addAction(change_pwd_action)
        
        menu.addSeparator()
        
        # Tùy chọn trợ giúp
        help_action = QAction("Trợ giúp", self)
        help_action.triggered.connect(self.show_about)
        menu.addAction(help_action)
        
        menu.addSeparator()
        
        # Tùy chọn đăng xuất
        logout_action = QAction("Đăng xuất", self)
        logout_action.triggered.connect(self.close)
        menu.addAction(logout_action)
        
        # Hiển thị menu dưới nút user
        button = self.sender()
        if button:
            menu.exec(button.mapToGlobal(QPoint(0, button.height())))

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
        """Hiển thị các loại thông báo để thử nghiệm giao diện mới"""
        notification_menu = QMenu(self)
        info_action = notification_menu.addAction("Thông báo thông tin")
        success_action = notification_menu.addAction("Thông báo thành công")
        warning_action = notification_menu.addAction("Thông báo cảnh báo")
        error_action = notification_menu.addAction("Thông báo lỗi")
        multiple_action = notification_menu.addAction("Hiển thị nhiều thông báo")
        
        action = notification_menu.exec(QCursor.pos())
        
        if action == info_action:
            self.notification_manager.show_info("Đây là thông báo thông tin cho người dùng. Bạn có thể tìm hiểu thêm trong phần Trợ giúp.")
        elif action == success_action:
            self.notification_manager.show_success("Thao tác đã được thực hiện thành công! Dữ liệu đã được lưu vào hệ thống.")
        elif action == warning_action:
            self.notification_manager.show_warning("Cảnh báo! Hãy kiểm tra lại thông tin trước khi tiếp tục.")
        elif action == error_action:
            self.notification_manager.show_error("Lỗi! Không thể thực hiện thao tác do thiếu thông tin bắt buộc.")
        elif action == multiple_action:
            # Hiển thị nhiều thông báo để kiểm tra xếp chồng
            self.notification_manager.show_info("Thông báo thông tin #1", timeout=10000)
            QTimer.singleShot(300, lambda: self.notification_manager.show_success("Thông báo thành công #2", timeout=9000))
            QTimer.singleShot(600, lambda: self.notification_manager.show_warning("Thông báo cảnh báo #3", timeout=8000))
            QTimer.singleShot(900, lambda: self.notification_manager.show_error("Thông báo lỗi #4", timeout=7000))
            QTimer.singleShot(1200, lambda: self.notification_manager.show_info("Thông báo thông tin #5", timeout=6000))
    
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
            # Lưu trạng thái cửa sổ
            self.save_window_state()
            
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
    
    def load_icon(self, path):
        """Load icon từ đường dẫn, trả về QIcon trống nếu không tìm thấy file"""
        if os.path.exists(path):
            return QIcon(path)
        return QIcon()

    def create_menu_bar(self):
        """Tạo menu bar cho ứng dụng"""
        menubar = self.menuBar()
        
        # Menu Hệ thống
        system_menu = menubar.addMenu("Hệ thống")
        
        # Action đổi mật khẩu
        change_password_action = QAction("Đổi mật khẩu", self)
        change_password_action.setShortcut("Ctrl+P")
        change_password_action.triggered.connect(self.change_password)
        system_menu.addAction(change_password_action)
        
        # Removed theme menu
        system_menu.addSeparator()
        
        # Action thoát
        exit_action = QAction("Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)
        
        # Menu trích xuất
        export_menu = menubar.addMenu("Trích xuất")        
        export_students_action = QAction("Danh sách sinh viên", self)        
        export_students_action.triggered.connect(self.export_students)        
        export_menu.addAction(export_students_action)        
        
        export_courses_action = QAction("Danh sách khóa học", self)        
        export_courses_action.triggered.connect(self.export_courses)        
        export_menu.addAction(export_courses_action)
        
        export_report_action = QAction("Báo cáo thống kê", self)        
        export_report_action.triggered.connect(self.export_report)        
        export_menu.addAction(export_report_action)        
        
        # Menu trợ giúp        
        help_menu = menubar.addMenu("Trợ giúp")        
        
        about_action = QAction("Giới thiệu", self)        
        about_action.triggered.connect(self.show_about)        
        help_menu.addAction(about_action)
        
    def create_toolbar(self):        
        """Tạo toolbar với các chức năng thường dùng"""        
        toolbar = self.addToolBar("Main Toolbar")        
        toolbar.setIconSize(QSize(24, 24))        
        toolbar.setMovable(False)
        
        icons_path = "resources/icons/"
        
        # Thêm nút thông báo
        notification_action = QAction(QIcon(icons_path + "notification.png"), "Thông báo", self)
        notification_action.triggered.connect(self.show_test_notification)
        toolbar.addAction(notification_action)
        
        # Removed theme button
        
    def save_window_state(self):
        """Lưu trạng thái cửa sổ vào cài đặt"""
        if not self.isMaximized():
            self.config_manager.set("ui", "window_width", self.width())
            self.config_manager.set("ui", "window_height", self.height())
        self.config_manager.set("ui", "window_maximized", self.isMaximized())
        self.config_manager.save_config()

    def restore_window_state(self):
        """Khôi phục trạng thái cửa sổ từ cài đặt"""
        if self.config_manager.get("ui", "remember_window_size", True):
            width = self.config_manager.get("ui", "window_width", 1280)
            height = self.config_manager.get("ui", "window_height", 800)
            maximized = self.config_manager.get("ui", "window_maximized", False)
            
            # Điều chỉnh kích thước dựa trên màn hình hiện tại
            screen_rect = QApplication.primaryScreen().availableGeometry()
            width = min(width, screen_rect.width() - 50)
            height = min(height, screen_rect.height() - 50)
            
            self.resize(width, height)
            if maximized:
                self.showMaximized()