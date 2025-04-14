from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QGridLayout, QPushButton, QFrame,
                             QSplitter, QScrollArea, QSpacerItem, QSizePolicy,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPainter, QPen, QAction
import logging
import os

try:
    # Thử import matplotlib
    import matplotlib
    matplotlib.use('Qt5Agg')  # Sử dụng backend Qt5Agg
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logging.warning("Không tìm thấy thư viện matplotlib. Vui lòng cài đặt để hiển thị biểu đồ.")


class StatisticCard(QFrame):
    """
    Card hiển thị thông tin thống kê
    """
    def __init__(self, title, value, icon_path=None, color="#2979ff", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_path = icon_path
        self.color = QColor(color)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện card"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(100)
        self.setObjectName("statisticCard")
        self.setStyleSheet(f"""
            #statisticCard {{
                border: 1px solid #dddddd;
                border-left: 5px solid {self.color.name()};
                border-radius: 5px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon nếu có
        if self.icon_path and os.path.exists(self.icon_path):
            icon_label = QLabel()
            icon = QIcon(self.icon_path)
            icon_label.setPixmap(icon.pixmap(QSize(48, 48)))
            layout.addWidget(icon_label)
        
        # Thông tin
        info_layout = QVBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #757575; font-size: 12px;")
        
        # Make value_label an instance attribute
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.color.name()};")
        
        info_layout.addWidget(title_label)
        info_layout.addWidget(self.value_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()


class ChartWidget(QWidget):
    """
    Widget hiển thị biểu đồ sử dụng Matplotlib
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.has_matplotlib = HAS_MATPLOTLIB
        
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện cho biểu đồ"""
        layout = QVBoxLayout(self)
        
        if self.has_matplotlib:
            # Tạo figure và canvas
            self.figure = Figure(figsize=(5, 4), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            # Hiển thị thông báo nếu không có matplotlib
            message = QLabel("Cài đặt thư viện matplotlib để hiển thị biểu đồ.\npip install matplotlib")
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message.setStyleSheet("font-size: 14px; color: #757575;")
            layout.addWidget(message)
    
    def plot_bar(self, x_data, y_data, title, xlabel, ylabel, color='#2979ff'):
        """
        Vẽ biểu đồ cột
        
        Args:
            x_data: Dữ liệu trục x
            y_data: Dữ liệu trục y
            title: Tiêu đề biểu đồ
            xlabel: Nhãn trục x
            ylabel: Nhãn trục y
            color: Màu sắc biểu đồ
        """
        if not self.has_matplotlib:
            return
        
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        # Tạo subplot
        ax = self.figure.add_subplot(111)
        
        # Vẽ biểu đồ cột
        bars = ax.bar(x_data, y_data, color=color, alpha=0.8)
        
        # Thêm nhãn giá trị trên mỗi cột
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height}',
                    ha='center', va='bottom')
        
        # Thêm tiêu đề và nhãn
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        # Hiển thị lưới
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Cập nhật canvas
        self.canvas.draw()
    
    def plot_pie(self, labels, sizes, title, colors=None):
        """
        Vẽ biểu đồ tròn
        
        Args:
            labels: Nhãn các phần
            sizes: Kích thước các phần
            title: Tiêu đề biểu đồ
            colors: Các màu sắc (tùy chọn)
        """
        if not self.has_matplotlib:
            return
        
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        # Tạo subplot
        ax = self.figure.add_subplot(111)
        
        # Màu mặc định nếu không cung cấp
        if not colors:
            colors = ['#2979ff', '#00c853', '#ff6d00', '#d50000', '#6200ea', '#2962ff', '#00bfa5']
        
        # Vẽ biểu đồ tròn
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90, colors=colors
        )
        
        # Thiết lập font cho văn bản
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
        
        # Đặt tiêu đề
        ax.set_title(title)
        
        # Đảm bảo biểu đồ là hình tròn
        ax.axis('equal')
        
        # Cập nhật canvas
        self.canvas.draw()
    
    def plot_line(self, x_data, y_data, title, xlabel, ylabel, color='#2979ff'):
        """
        Vẽ biểu đồ đường
        
        Args:
            x_data: Dữ liệu trục x
            y_data: Dữ liệu trục y
            title: Tiêu đề biểu đồ
            xlabel: Nhãn trục x
            ylabel: Nhãn trục y
            color: Màu sắc biểu đồ
        """
        if not self.has_matplotlib:
            return
        
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        # Tạo subplot
        ax = self.figure.add_subplot(111)
        
        # Vẽ biểu đồ đường
        line, = ax.plot(x_data, y_data, marker='o', linestyle='-', color=color)
        
        # Thêm tiêu đề và nhãn
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        # Hiển thị lưới
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Đánh số các điểm dữ liệu
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            ax.annotate(f"{y}", (x, y), textcoords="offset points", xytext=(0,10), ha='center')
        
        # Cập nhật canvas
        self.canvas.draw()


class DashboardView(QWidget):
    """
    Giao diện trang tổng quan (Dashboard)
    """
    def __init__(self, student_controller, course_controller, report_controller):
        super().__init__()
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.report_controller = report_controller
        
        # Thiết lập giao diện
        self.init_ui()
        
        # Tải dữ liệu ban đầu
        self.load_data()
        
        # Thiết lập auto-refresh cho dashboard
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(60000)  # Refresh mỗi phút
    
    def init_ui(self):
        """Thiết lập giao diện trang tổng quan"""
        # Layout chính
        main_layout = QVBoxLayout(self)
        
        # Tiêu đề
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Nút refresh
        refresh_button = QPushButton("Tải lại")
        refresh_button.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Khu vực cuộn cho nội dung dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget chính cho dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        
        # Thêm các thành phần vào dashboard
        dashboard_layout.addLayout(self.create_statistics_section())
        dashboard_layout.addWidget(self.create_enrollment_chart_section())
        dashboard_layout.addWidget(self.create_student_status_section())
        dashboard_layout.addWidget(self.create_courses_section())
        
        # Thêm space để có thể cuộn xuống
        dashboard_layout.addStretch()
        
        # Thiết lập widget cho scroll area
        scroll_area.setWidget(dashboard_widget)
        main_layout.addWidget(scroll_area)
    
    def create_statistics_section(self):
        """Tạo khu vực hiển thị thống kê"""
        layout = QGridLayout()
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(15)
        
        # Các card thống kê
        self.total_students_card = StatisticCard(
            "Tổng số sinh viên", "...", 
            "resources/icons/student.png", "#2979ff"
        )
        layout.addWidget(self.total_students_card, 0, 0)
        
        self.total_courses_card = StatisticCard(
            "Tổng số khóa học", "...", 
            "resources/icons/course.png", "#00c853"
        )
        layout.addWidget(self.total_courses_card, 0, 1)
        
        self.total_enrollments_card = StatisticCard(
            "Tổng số đăng ký", "...", 
            "resources/icons/enrollment.png", "#ff6d00"
        )
        layout.addWidget(self.total_enrollments_card, 0, 2)
        
        self.avg_grade_card = StatisticCard(
            "Điểm trung bình", "...", 
            "resources/icons/grade.png", "#d50000"
        )
        layout.addWidget(self.avg_grade_card, 1, 0)
        
        self.max_enrollment_course_card = StatisticCard(
            "Khóa học nhiều SV nhất", "...", 
            "resources/icons/popular.png", "#6200ea"
        )
        layout.addWidget(self.max_enrollment_course_card, 1, 1)
        
        self.recent_activity_card = StatisticCard(
            "Hoạt động gần đây", "...", 
            "resources/icons/activity.png", "#2962ff"
        )
        layout.addWidget(self.recent_activity_card, 1, 2)
        
        return layout
    
    def create_enrollment_chart_section(self):
        """Tạo khu vực biểu đồ đăng ký khóa học"""
        group_box = QGroupBox("Thống kê đăng ký khóa học")
        layout = QVBoxLayout(group_box)
        
        # Tạo chart widget
        self.enrollment_chart = ChartWidget()
        layout.addWidget(self.enrollment_chart)
        
        return group_box
    
    def create_student_status_section(self):
        """Tạo khu vực biểu đồ trạng thái sinh viên"""
        group_box = QGroupBox("Trạng thái sinh viên")
        layout = QVBoxLayout(group_box)
        
        # Tạo chart widget
        self.student_status_chart = ChartWidget()
        layout.addWidget(self.student_status_chart)
        
        return group_box
    
    def create_courses_section(self):
        """Tạo khu vực biểu đồ khóa học theo tín chỉ"""
        group_box = QGroupBox("Khóa học theo tín chỉ")
        layout = QVBoxLayout(group_box)
        
        # Tạo chart widget
        self.courses_chart = ChartWidget()
        layout.addWidget(self.courses_chart)
        
        return group_box
    
    def load_data(self):
        """Tải dữ liệu thống kê và cập nhật giao diện"""
        try:
            # Lấy thống kê cơ bản
            stats = self.report_controller.get_student_course_statistics()
            
            # Cập nhật các card thống kê
            self.total_students_card.value_label.setText(str(stats.get('total_students', 0)))
            self.total_courses_card.value_label.setText(str(stats.get('total_courses', 0)))
            self.total_enrollments_card.value_label.setText(str(stats.get('total_enrollments', 0)))
            
            avg_grade = stats.get('average_grade', 0)
            self.avg_grade_card.value_label.setText(f"{avg_grade:.1f}")
            
            # Lấy khóa học có nhiều sinh viên đăng ký nhất
            top_courses = self.report_controller.get_top_courses_by_enrollment(limit=1)
            if top_courses:
                course = top_courses[0]
                self.max_enrollment_course_card.value_label.setText(
                    f"{course['course_name']} ({course['student_count']} SV)"
                )
            else:
                self.max_enrollment_course_card.value_label.setText("Không có dữ liệu")
            
            # Lấy hoạt động gần đây
            recent_activities = self.report_controller.get_recent_activities(1)
            if recent_activities:
                self.recent_activity_card.value_label.setText(recent_activities[0]['action_description'])
            else:
                self.recent_activity_card.value_label.setText("Không có hoạt động")
            
            # Vẽ biểu đồ đăng ký khóa học
            self.update_enrollment_chart()
            
            # Vẽ biểu đồ trạng thái sinh viên
            self.update_student_status_chart()
            
            # Vẽ biểu đồ khóa học theo tín chỉ
            self.update_courses_chart()
            
        except Exception as e:
            logging.error(f"Lỗi khi tải dữ liệu dashboard: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu dashboard: {str(e)}")
    
    def update_enrollment_chart(self):
        """Cập nhật biểu đồ đăng ký khóa học"""
        try:
            top_courses = self.report_controller.get_top_courses_by_enrollment(limit=5)
            
            if top_courses:
                course_names = [course['course_name'] for course in top_courses]
                student_counts = [course['student_count'] for course in top_courses]
                
                self.enrollment_chart.plot_bar(
                    course_names, 
                    student_counts,
                    "Top 5 khóa học có nhiều sinh viên đăng ký nhất",
                    "Khóa học",
                    "Số lượng sinh viên",
                    "#2979ff"
                )
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật biểu đồ đăng ký: {str(e)}")
    
    def update_student_status_chart(self):
        """Cập nhật biểu đồ trạng thái sinh viên"""
        try:
            status_stats = self.report_controller.get_student_status_statistics()
            
            if status_stats:
                labels = list(status_stats.keys())
                sizes = list(status_stats.values())
                
                self.student_status_chart.plot_pie(
                    labels,
                    sizes,
                    "Trạng thái sinh viên",
                    ["#2979ff", "#00c853", "#ff6d00", "#d50000"]
                )
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật biểu đồ trạng thái sinh viên: {str(e)}")
    
    def update_courses_chart(self):
        """Cập nhật biểu đồ khóa học theo tín chỉ"""
        try:
            credits_stats = self.report_controller.get_course_credits_statistics()
            
            if credits_stats:
                credit_labels = [f"{credit} tín chỉ" for credit in credits_stats.keys()]
                counts = list(credits_stats.values())
                
                self.courses_chart.plot_bar(
                    credit_labels,
                    counts,
                    "Phân bố khóa học theo số tín chỉ",
                    "Số tín chỉ",
                    "Số lượng khóa học",
                    "#00c853"
                )
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật biểu đồ khóa học: {str(e)}")
