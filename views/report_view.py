from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QGroupBox, QTabWidget, QTextBrowser,QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import logging

# Check if matplotlib is available
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ReportView(QWidget):
    """
    Giao diện hiển thị báo cáo và thống kê.
    """
    def __init__(self, report_controller):
        """
        Khởi tạo giao diện báo cáo và thống kê.
        
        Args:
            report_controller (ReportController): Controller quản lý báo cáo
        """
        super().__init__()
        self.report_controller = report_controller
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        main_layout = QVBoxLayout()
        
        # Tạo tab widget để tổ chức các loại báo cáo
        self.tabs = QTabWidget()
        
        # Tab 1: Thống kê tổng quan
        overview_tab = QWidget()
        self.setup_overview_tab(overview_tab)
        self.tabs.addTab(overview_tab, "Thống kê tổng quan")
        
        # Tab 2: Top khóa học
        top_courses_tab = QWidget()
        self.setup_top_courses_tab(top_courses_tab)
        self.tabs.addTab(top_courses_tab, "Top khóa học")
        
        # Tab 3: Phân phối điểm
        grade_distribution_tab = QWidget()
        self.setup_grade_distribution_tab(grade_distribution_tab)
        self.tabs.addTab(grade_distribution_tab, "Phân phối điểm")
        
        # Tab 4: Kết quả sinh viên
        student_results_tab = QWidget()
        self.setup_student_results_tab(student_results_tab)
        self.tabs.addTab(student_results_tab, "Kết quả sinh viên")
        
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
        
        # Tải dữ liệu cho tab đầu tiên khi hiển thị
        self.load_overview_statistics()
    
    def setup_overview_tab(self, tab):
        """
        Thiết lập tab thống kê tổng quan.

        Args:
            tab (QWidget): Widget tab cần thiết lập.
        """
        layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel("Thống kê tổng quan hệ thống")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Thống kê cơ bản
        stats_group = QGroupBox("Số liệu tổng quan")
        stats_layout = QFormLayout()
        
        self.total_students_label = QLabel("0")
        stats_layout.addRow("Tổng số sinh viên:", self.total_students_label)
        
        self.total_courses_label = QLabel("0")
        stats_layout.addRow("Tổng số khóa học:", self.total_courses_label)
        
        self.total_enrollments_label = QLabel("0")
        stats_layout.addRow("Tổng số lượt đăng ký:", self.total_enrollments_label)
        
        self.avg_grade_label = QLabel("0")
        stats_layout.addRow("Điểm trung bình toàn trường:", self.avg_grade_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Nút làm mới
        refresh_button = QPushButton("Làm mới dữ liệu")
        refresh_button.clicked.connect(self.load_overview_statistics)
        layout.addWidget(refresh_button)
        
        # Thêm khoảng trống ở cuối
        layout.addStretch()
        
        tab.setLayout(layout)
    
    def setup_top_courses_tab(self, tab):
        """
        Thiết lập tab các khóa học được đăng ký nhiều nhất.

        Args:
            tab (QWidget): Widget tab cần thiết lập.
        """
        layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel("Top khóa học được đăng ký nhiều nhất")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Bảng top khóa học
        self.top_courses_table = QTableWidget()
        self.top_courses_table.setColumnCount(3)
        self.top_courses_table.setHorizontalHeaderLabels([
            "Mã khóa học", "Tên khóa học", "Số lượng đăng ký"
        ])
        self.top_courses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.top_courses_table)
        
        # Các tùy chọn hiển thị
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("Số lượng hiển thị:"))
        self.limit_combo = QComboBox()
        self.limit_combo.addItems(["5", "10", "15", "20", "Tất cả"])
        self.limit_combo.currentIndexChanged.connect(self.load_top_courses)
        options_layout.addWidget(self.limit_combo)
        
        refresh_button = QPushButton("Làm mới")
        refresh_button.clicked.connect(self.load_top_courses)
        options_layout.addWidget(refresh_button)
        
        layout.addLayout(options_layout)
        
        tab.setLayout(layout)
    
    def setup_grade_distribution_tab(self, tab):
        """
        Thiết lập tab phân phối điểm.

        Args:
            tab (QWidget): Widget tab cần thiết lập.
        """
        layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel("Phân phối điểm của sinh viên")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Bảng phân phối điểm
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(2)
        self.grades_table.setHorizontalHeaderLabels([
            "Loại điểm", "Số lượng"
        ])
        self.grades_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.grades_table)
        
        # Nút làm mới
        refresh_button = QPushButton("Làm mới dữ liệu")
        refresh_button.clicked.connect(self.load_grade_distribution)
        layout.addWidget(refresh_button)
        
        tab.setLayout(layout)
    
    def setup_student_results_tab(self, tab):
        """
        Thiết lập tab kết quả học tập của sinh viên.

        Args:
            tab (QWidget): Widget tab cần thiết lập.
        """
        layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel("Kết quả học tập của sinh viên")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Form tìm kiếm sinh viên
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Mã sinh viên:"))
        self.student_id_input = QLineEdit()
        search_layout.addWidget(self.student_id_input)
        
        search_button = QPushButton("Xem kết quả")
        search_button.clicked.connect(self.load_student_results)
        search_layout.addWidget(search_button)
        
        layout.addLayout(search_layout)
        
        # Khu vực hiển thị thông tin sinh viên
        self.student_info = QTextBrowser()
        layout.addWidget(QLabel("Thông tin sinh viên:"))
        layout.addWidget(self.student_info, 1)
        
        # Bảng kết quả học tập
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Mã khóa học", "Tên khóa học", "Số tín chỉ", "Điểm"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Kết quả học tập:"))
        layout.addWidget(self.results_table, 2)
        
        tab.setLayout(layout)
    
    def load_overview_statistics(self):
        """Tải thống kê tổng quan từ controller và hiển thị."""
        stats = self.report_controller.get_student_course_statistics()
        
        self.total_students_label.setText(str(stats['total_students']))
        self.total_courses_label.setText(str(stats['total_courses']))
        self.total_enrollments_label.setText(str(stats['total_enrollments']))
        self.avg_grade_label.setText(f"{stats['average_grade']} / 10")
    
    def load_top_courses(self):
        """Tải danh sách các khóa học được đăng ký nhiều nhất."""
        # Xác định số lượng khóa học cần hiển thị
        limit_text = self.limit_combo.currentText()
        if limit_text == "Tất cả":
            limit = 1000  # Một con số đủ lớn
        else:
            limit = int(limit_text)
        
        top_courses = self.report_controller.get_top_courses_by_enrollment(limit)
        
        # Hiển thị dữ liệu trong bảng
        self.top_courses_table.setRowCount(0)
        for row, course in enumerate(top_courses):
            self.top_courses_table.insertRow(row)
            self.top_courses_table.setItem(row, 0, QTableWidgetItem(course['course_id']))
            self.top_courses_table.setItem(row, 1, QTableWidgetItem(course['course_name']))
            self.top_courses_table.setItem(row, 2, QTableWidgetItem(str(course['student_count'])))
    
    def load_grade_distribution(self):
        """Tải phân phối điểm số và hiển thị trong bảng."""
        try:
            # Hiển thị trạng thái đang tải
            old_cursor = self.cursor()
            self.setCursor(Qt.CursorShape.WaitCursor)
            self.grades_table.setRowCount(0)
            
            # Thêm thông báo tải
            loading_row = self.grades_table.rowCount()
            self.grades_table.insertRow(loading_row)
            loading_item = QTableWidgetItem("Đang tải dữ liệu...")
            self.grades_table.setItem(loading_row, 0, loading_item)
            QApplication.processEvents()
            
            # Tải dữ liệu
            grade_distribution = self.report_controller.get_grade_distribution()
            
            # Xóa thông báo tải
            self.grades_table.setRowCount(0)
            
            if not grade_distribution:
                # Hiển thị thông báo nếu không có dữ liệu
                self.grades_table.insertRow(0)
                self.grades_table.setItem(0, 0, QTableWidgetItem("Không có dữ liệu điểm"))
                self.grades_table.setSpan(0, 0, 1, 2)
                self.setCursor(old_cursor)
                return
                
            row = 0
            for grade_range, count in grade_distribution.items():
                self.grades_table.insertRow(row)
                self.grades_table.setItem(row, 0, QTableWidgetItem(str(grade_range)))
                self.grades_table.setItem(row, 1, QTableWidgetItem(str(count)))
                row += 1
                
            # Thêm mã màu cho các dòng trong bảng điểm
            for row in range(self.grades_table.rowCount()):
                grade_range = self.grades_table.item(row, 0).text()
                if "A" in grade_range:
                    self.grades_table.item(row, 0).setBackground(QColor(120, 230, 120)) # Xanh lá
                    self.grades_table.item(row, 1).setBackground(QColor(120, 230, 120))
                elif "B" in grade_range:
                    self.grades_table.item(row, 0).setBackground(QColor(170, 240, 170)) # Xanh lá nhạt
                    self.grades_table.item(row, 1).setBackground(QColor(170, 240, 170))
                elif "C" in grade_range:
                    self.grades_table.item(row, 0).setBackground(QColor(255, 255, 150)) # Vàng nhạt
                    self.grades_table.item(row, 1).setBackground(QColor(255, 255, 150))
                elif "D" in grade_range:
                    self.grades_table.item(row, 0).setBackground(QColor(255, 200, 150)) # Cam nhạt
                    self.grades_table.item(row, 1).setBackground(QColor(255, 200, 150))
                elif "F" in grade_range:
                    self.grades_table.item(row, 0).setBackground(QColor(255, 180, 180)) # Đỏ nhạt
                    self.grades_table.item(row, 1).setBackground(QColor(255, 180, 180))
            
            # Khôi phục con trỏ
            self.setCursor(old_cursor)
                        
        except Exception as e:
            self.setCursor(old_cursor)  # Đảm bảo khôi phục con trỏ trong mọi trường hợp
            logging.error(f"Lỗi khi tải phân phối điểm: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu phân phối điểm: {str(e)}")
    
    def load_student_results(self):
        """Tải kết quả học tập của sinh viên và hiển thị."""
        student_id = self.student_id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã sinh viên!")
            return
        
        # Lấy thông tin sinh viên
        student = None
        try:
            # Giả định có một hàm get_student_by_id trong report_controller
            # Nhưng nếu không có, chúng ta có thể tìm cách khác để lấy thông tin sinh viên
            student_performance = self.report_controller.get_student_performance(student_id)
            
            if student_performance['courses_enrolled'] == 0:
                QMessageBox.warning(self, "Thông báo", f"Không tìm thấy thông tin sinh viên có mã {student_id} hoặc sinh viên chưa đăng ký khóa học nào!")
                self.student_info.setText("")
                self.results_table.setRowCount(0)
                return
            
            # Hiển thị thông tin sinh viên
            student_query = """
            SELECT * FROM students WHERE student_id = ?
            """
            student_result = self.report_controller.db_manager.execute_query(student_query, (student_id,))
            
            if student_result:
                student = student_result[0]
                student_info = f"""
                <h2>Thông tin sinh viên</h2>
                <p><b>Mã số:</b> {student['student_id']}</p>
                <p><b>Họ tên:</b> {student['full_name']}</p>
                <p><b>Giới tính:</b> {student['gender']}</p>
                <p><b>Ngày sinh:</b> {student['date_of_birth']}</p>
                <p><b>Trạng thái:</b> {student['status']}</p>
                <hr>
                <h3>Thông tin học tập</h3>
                <p><b>Số khóa học đã đăng ký:</b> {student_performance['courses_enrolled']}</p>
                <p><b>Số khóa học đã có điểm:</b> {student_performance['courses_completed']}</p>
                <p><b>Điểm trung bình:</b> {student_performance['average_grade']}</p>
                """
                self.student_info.setHtml(student_info)
            else:
                self.student_info.setText(f"Không tìm thấy thông tin sinh viên có mã {student_id}")
            
            # Hiển thị kết quả học tập
            self.results_table.setRowCount(0)
            for row, course in enumerate(student_performance['course_details']):
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(course['course_id']))
                self.results_table.setItem(row, 1, QTableWidgetItem(course['course_name']))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(course['credits'])))
                
                grade_text = str(course['grade']) if course['grade'] is not None else "Chưa có"
                self.results_table.setItem(row, 3, QTableWidgetItem(grade_text))
            
        except Exception as e:
            logging.error(f"Lỗi khi tải kết quả học tập: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể tải kết quả học tập: {e}")

    def load_data(self):
        """Tải dữ liệu thống kê."""
        # ...existing code...
        
        # Thêm vào cuối phương thức
        # Thêm biểu đồ tỷ lệ đậu/rớt nếu có matplotlib
        if HAS_MATPLOTLIB:
            pass_fail_stats = self.report_controller.get_pass_fail_rate()
            if pass_fail_stats and pass_fail_stats['total'] > 0:
                self.pass_fail_chart.figure.clear()
                ax = self.pass_fail_chart.figure.add_subplot(111)
                
                labels = ['Đạt', 'Không đạt']
                sizes = [pass_fail_stats['passed'], pass_fail_stats['failed']]
                colors = ['#4CAF50', '#F44336']
                
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
                ax.set_title("Tỷ lệ đạt/không đạt")
                self.pass_fail_chart.canvas.draw()
