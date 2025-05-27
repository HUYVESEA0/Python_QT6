from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QGridLayout, QPushButton, QFrame,
                             QSplitter, QScrollArea, QSpacerItem, QSizePolicy,
                             QComboBox, QMessageBox, QGraphicsDropShadowEffect,
                             QStackedWidget)
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QColor, QPainter, QPen, QAction, QPixmap
from widgets.empty_state_widget import EmptyStateWidget
import logging
import os

try:
    # Thử import matplotlib
    import matplotlib
    matplotlib.use('QtAgg')  # Sử dụng backend QtAgg (mới)
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
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
        
        # Thêm sự kiểm tra khi không có dữ liệu
        if not x_data or not y_data:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Không có dữ liệu", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12, color='gray')
            ax.axis('off')
            self.canvas.draw()
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
        
        # Thêm sự kiểm tra khi không có dữ liệu
        if not sizes or sum(sizes) == 0:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Không có dữ liệu", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12, color='gray')
            ax.axis('off')
            self.canvas.draw()
            return
        
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        # Tạo subplot
        ax = self.figure.add_subplot(111)
        
        # Màu mặc định nếu không cung cấp
        if not colors:
            colors = ['#2979ff', '#00c853', '#ff6d00', '#d50000', '#6200ea', '#2962ff', '#00bfa5']
        
        # Vẽ biểu đồ tròn
        pie_result = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90, colors=colors
        )
        if len(pie_result) == 3:
            wedges, texts, autotexts = pie_result
        else:
            wedges, texts = pie_result
            autotexts = []
        
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
        
    # Thêm biểu đồ phân phối điểm số
    def plot_grade_distribution(self, grade_data, title="Phân phối điểm số"):
        """
        Vẽ biểu đồ phân phối điểm số
        
        Args:
            grade_data (dict): Dict với key là khoảng điểm, value là số lượng
            title (str): Tiêu đề biểu đồ
        """
        if not self.has_matplotlib:
            return
            
        # Kiểm tra dữ liệu trống
        if not grade_data:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Không có dữ liệu điểm số", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12, color='gray')
            ax.axis('off')
            self.canvas.draw()
            return
            
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        # Tạo subplot
        ax = self.figure.add_subplot(111)
        
        # Chuẩn bị dữ liệu
        categories = list(grade_data.keys())
        values = list(grade_data.values())
        colors = ['#d50000', '#ff6d00', '#ffeb3b', '#8bc34a', '#00c853']  # Màu từ đỏ đến xanh
        
        # Vẽ biểu đồ cột
        bars = ax.bar(categories, values, color=colors)
        
        # Thêm nhãn giá trị trên mỗi cột
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height}', ha='center', va='bottom')
        
        # Thiết lập tiêu đề và nhãn
        ax.set_title(title)
        ax.set_xlabel("Khoảng điểm")
        ax.set_ylabel("Số lượng sinh viên")
        
        # Hiển thị lưới
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Cập nhật canvas
        self.canvas.draw()
        
    # Thêm biểu đồ tỷ lệ giới tính
    def plot_gender_distribution(self, gender_data, title="Tỷ lệ giới tính"):
        """
        Vẽ biểu đồ tỷ lệ giới tính
        
        Args:
            gender_data (dict): Dict với key là giới tính, value là số lượng
            title (str): Tiêu đề biểu đồ
        """
        if not self.has_matplotlib:
            return
            
        # Kiểm tra dữ liệu trống
        if not gender_data or sum(gender_data.values()) == 0:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Không có dữ liệu về giới tính", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12, color='gray')
            ax.axis('off')
            self.canvas.draw()
            return
            
        # Xóa biểu đồ cũ
        self.figure.clear()
        
        # Tạo subplot
        ax = self.figure.add_subplot(111)
        
        # Chuẩn bị dữ liệu
        labels = list(gender_data.keys())
        sizes = list(gender_data.values())
        colors = ['#2979ff', '#f06292', '#9c27b0']  # Nam, Nữ, Khác
        
        # Vẽ biểu đồ tròn
        pie_result = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90, colors=colors
        )
        if len(pie_result) == 3:
            wedges, texts, autotexts = pie_result
        else:
            wedges, texts = pie_result
            autotexts = []
        
        # Thiết lập font cho văn bản
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
        
        # Thiết lập tiêu đề
        ax.set_title(title)
        
        # Đảm bảo biểu đồ là hình tròn
        ax.axis('equal')
        
        # Cập nhật canvas
        self.canvas.draw()


class DashboardView(QWidget):
    """
    Giao diện trang tổng quan (Dashboard).
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
        """Thiết lập giao diện trang tổng quan."""
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
        
        # Thêm chỉ dẫn khi có quá ít dữ liệu
        self.info_label = QLabel("Thống kê sẽ chính xác hơn khi có nhiều dữ liệu sinh viên và khóa học")
        self.info_label.setStyleSheet("color: #757575; font-style: italic;")
        main_layout.insertWidget(1, self.info_label)
        
        # Khu vực cuộn cho nội dung dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget chính cho dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        
        # Thêm các thành phần vào dashboard với bố cục mới
        dashboard_layout.addLayout(self.create_statistics_section())
        
        # Bố trí hàng đầu với 2 biểu đồ chính
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(self.create_enrollment_chart_section())
        row1_layout.addWidget(self.create_student_status_section())
        dashboard_layout.addLayout(row1_layout)
        
        # Bố trí hàng thứ hai với biểu đồ khóa học và phân phối điểm số
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(self.create_courses_section())
        row2_layout.addWidget(self.create_grade_distribution_section())
        dashboard_layout.addLayout(row2_layout)
        
        # Bố trí hàng thứ ba với biểu đồ giới tính và thống kê khác
        row3_layout = QHBoxLayout()
        row3_layout.addWidget(self.create_gender_distribution_section())
        # Có thể thêm các thành phần khác vào đây
        dashboard_layout.addLayout(row3_layout)
        
        # Thêm space để có thể cuộn xuống
        dashboard_layout.addStretch()
        
        # Thiết lập widget cho scroll area
        scroll_area.setWidget(dashboard_widget)
        main_layout.addWidget(scroll_area)
    
    def create_statistics_section(self):
        """Tạo khu vực hiển thị thống kê với thiết kế card hiện đại."""
        layout = QGridLayout()
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(15)
        
        # Các card thống kê với hiệu ứng và animation
        self.total_students_card = self.create_statistic_card(
            "Tổng số sinh viên", "...", 
            "resources/icons/student.png", "#2979ff"
        )
        self.total_students_card.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.total_students_card, 0, 0)
        
        self.total_courses_card = self.create_statistic_card(
            "Tổng số khóa học", "...", 
            "resources/icons/course.png", "#00c853"
        )
        layout.addWidget(self.total_courses_card, 0, 1)
        
        self.total_enrollments_card = self.create_statistic_card(
            "Tổng số đăng ký", "...", 
            "resources/icons/enrollment.png", "#ff6d00"
        )
        layout.addWidget(self.total_enrollments_card, 0, 2)
        
        self.avg_grade_card = self.create_statistic_card(
            "Điểm trung bình", "...", 
            "resources/icons/grade.png", "#d50000"
        )
        layout.addWidget(self.avg_grade_card, 1, 0)
        
        self.max_enrollment_course_card = self.create_statistic_card(
            "Khóa học nhiều SV nhất", "...", 
            "resources/icons/popular.png", "#6200ea"
        )
        layout.addWidget(self.max_enrollment_course_card, 1, 1)
        
        self.recent_activity_card = self.create_statistic_card(
            "Hoạt động gần đây", "...", 
            "resources/icons/activity.png", "#2962ff"
        )
        layout.addWidget(self.recent_activity_card, 1, 2)
        
        return layout

    def create_statistic_card(self, title, value, icon_path="", color="#2979ff"):
        """Tạo card hiển thị thông tin thống kê với thiết kế hiện đại và animation."""
        # Tạo frame chính với drop shadow và kiểu dáng mới
        card = QFrame()
        card.setObjectName("statCard")
        card.setProperty("color", color)
        
        # Tạo drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        card.setGraphicsEffect(shadow)
        
        # Layout cho card
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon (nếu có)
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                card_layout.addWidget(icon_label)
        
        # Thông tin
        info_layout = QVBoxLayout()
        
        # Tiêu đề
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        info_layout.addWidget(title_label)
        
        # Giá trị
        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        info_layout.addWidget(value_label)
        
        # Lưu reference để cập nhật giá trị sau
        setattr(card, "value_label", value_label)
        setattr(card, "title_label", title_label)
        
        card_layout.addLayout(info_layout)
        card_layout.setStretch(1, 1)  # Cho phép info_layout mở rộng
        
        return card
    
    def create_enrollment_chart_section(self):
        """Tạo khu vực biểu đồ đăng ký khóa học."""
        group_box = QGroupBox("Thống kê đăng ký khóa học")
        layout = QVBoxLayout(group_box)
        
        # Tạo chart widget
        self.enrollment_chart = ChartWidget()
        layout.addWidget(self.enrollment_chart)
        
        return group_box
    
    def create_student_status_section(self):
        """Tạo khu vực biểu đồ trạng thái sinh viên."""
        group_box = QGroupBox("Trạng thái sinh viên")
        layout = QVBoxLayout(group_box)
        
        # Tạo chart widget
        self.student_status_chart = ChartWidget()
        layout.addWidget(self.student_status_chart)
        
        return group_box
    
    def create_courses_section(self):
        """Tạo khu vực biểu đồ khóa học theo tín chỉ."""
        group_box = QGroupBox("Khóa học theo tín chỉ")
        layout = QVBoxLayout(group_box)
        
        # Tạo chart widget
        self.courses_chart = ChartWidget()
        layout.addWidget(self.courses_chart)
        
        return group_box
    
    # Thêm section cho phân phối điểm số
    def create_grade_distribution_section(self):
        """Tạo khu vực biểu đồ phân phối điểm số."""
        group_box = QGroupBox("Phân phối điểm số")
        layout = QVBoxLayout(group_box)
        
        # Widget hiển thị biểu đồ hoặc trạng thái trống
        self.stacked_grade_widget = QStackedWidget()
        
        # Tạo chart widget
        self.grade_chart = ChartWidget()
        self.stacked_grade_widget.addWidget(self.grade_chart)
        
        # Tạo empty state widget
        self.empty_grade_state = EmptyStateWidget(
            message="Chưa có dữ liệu về điểm số.\nThêm sinh viên và đánh giá để xem thống kê.",
            action_text="Đi đến đăng ký khóa học",
            icon_path="resources/icons/grade.png"
        )
        self.empty_grade_state.actionTriggered.connect(lambda: self.parent().parent().parent().tab_widget.setCurrentIndex(3))
        self.stacked_grade_widget.addWidget(self.empty_grade_state)
        
        layout.addWidget(self.stacked_grade_widget)
        
        return group_box
    
    # Thêm section cho phân phối giới tính
    def create_gender_distribution_section(self):
        """Tạo khu vực biểu đồ phân phối giới tính."""
        group_box = QGroupBox("Tỷ lệ giới tính")
        layout = QVBoxLayout(group_box)
        
        # Widget hiển thị biểu đồ hoặc trạng thái trống
        self.stacked_gender_widget = QStackedWidget()
        
        # Tạo chart widget
        self.gender_chart = ChartWidget()
        self.stacked_gender_widget.addWidget(self.gender_chart)
        
        # Tạo empty state widget
        self.empty_gender_state = EmptyStateWidget(
            message="Chưa có đủ dữ liệu để hiển thị tỷ lệ giới tính.\nThêm sinh viên để xem biểu đồ.",
            action_text="Đi đến quản lý sinh viên",
            icon_path="resources/icons/student.png"
        )
        self.empty_gender_state.actionTriggered.connect(lambda: self.parent().parent().parent().tab_widget.setCurrentIndex(1))
        self.stacked_gender_widget.addWidget(self.empty_gender_state)
        
        layout.addWidget(self.stacked_gender_widget)
        
        return group_box
    
    def load_data(self):
        """Tải dữ liệu thống kê và cập nhật giao diện với trạng thái trống nếu cần."""
        try:
            # Lấy thống kê cơ bản
            stats = self.report_controller.get_student_course_statistics()
            
            # Cập nhật các card thống kê với animation
            if hasattr(self.total_students_card, "value_label"):
                self.animate_value(self.total_students_card.value_label, str(stats.get('total_students', 0)))
            if hasattr(self.total_courses_card, "value_label"):
                self.animate_value(self.total_courses_card.value_label, str(stats.get('total_courses', 0)))
            if hasattr(self.total_enrollments_card, "value_label"):
                self.animate_value(self.total_enrollments_card.value_label, str(stats.get('total_enrollments', 0)))
            avg_grade = stats.get('average_grade', 0)
            if hasattr(self.avg_grade_card, "value_label"):
                self.animate_value(self.avg_grade_card.value_label, f"{avg_grade:.1f}")
            
            # Hiển thị thông báo hữu ích nếu có ít dữ liệu
            if stats.get('total_students', 0) < 5:
                self.info_label.setText("Thêm ít nhất 5 sinh viên để có thống kê chính xác hơn")
                self.info_label.setStyleSheet("color: #ff6d00; font-style: italic;")
            elif stats.get('total_courses', 0) < 3:
                self.info_label.setText("Thêm khóa học để có thống kê đầy đủ hơn")
                self.info_label.setStyleSheet("color: #ff6d00; font-style: italic;")
            else:
                self.info_label.setText("")
            
            # Lấy khóa học có nhiều sinh viên đăng ký nhất
            top_courses = self.report_controller.get_top_courses_by_enrollment(limit=1)
            if top_courses:
                course = top_courses[0]
                if hasattr(self.max_enrollment_course_card, "value_label"):
                    self.max_enrollment_course_card.value_label.setText(
                        f"{course['course_name']} ({course['student_count']} SV)"
                    )
            else:
                if hasattr(self.max_enrollment_course_card, "value_label"):
                    self.max_enrollment_course_card.value_label.setText("Không có dữ liệu")
            
            # Lấy hoạt động gần đây
            recent_activities = self.report_controller.get_recent_activities(1)
            if recent_activities:
                if hasattr(self.recent_activity_card, "value_label"):
                    self.recent_activity_card.value_label.setText(recent_activities[0]['action_description'])
            else:
                if hasattr(self.recent_activity_card, "value_label"):
                    self.recent_activity_card.value_label.setText("Không có hoạt động")
            
            # Vẽ các biểu đồ hiện có
            self.update_enrollment_chart()
            self.update_student_status_chart()
            self.update_courses_chart()
            
            # Vẽ biểu đồ điểm số mới
            self.update_grade_distribution_chart()
            
            # Vẽ biểu đồ giới tính mới
            self.update_gender_distribution_chart()
            
        except Exception as e:
            logging.error(f"Lỗi khi tải dữ liệu dashboard: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu dashboard: {str(e)}")
    
    def animate_value(self, label, new_value):
        """Tạo hiệu ứng animation khi thay đổi giá trị của label."""
        try:
            old_value = label.text()
            if old_value == new_value:
                return
                
            # Hiệu ứng nhấp nháy khi thay đổi giá trị
            original_style = label.styleSheet()
            label.setStyleSheet(original_style + "; color: #ff6d00;")
            label.setText(new_value)
            
            # Sử dụng QTimer để reset màu sau 500ms
            QTimer.singleShot(500, lambda: label.setStyleSheet(original_style))
        except Exception as e:
            logging.error(f"Lỗi khi tạo animation: {str(e)}")
            label.setText(new_value)
    
    def update_enrollment_chart(self):
        """Cập nhật biểu đồ đăng ký khóa học."""
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
        """Cập nhật biểu đồ trạng thái sinh viên."""
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
        """Cập nhật biểu đồ khóa học theo tín chỉ."""
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
    
    def update_grade_distribution_chart(self):
        """Cập nhật biểu đồ phân phối điểm số."""
        try:
            grade_distribution = self.report_controller.get_grade_distribution()
            
            if grade_distribution and sum(grade_distribution.values()) > 0:
                self.grade_chart.plot_grade_distribution(grade_distribution)
                self.stacked_grade_widget.setCurrentIndex(0)  # Hiển thị biểu đồ
            else:
                self.stacked_grade_widget.setCurrentIndex(1)  # Hiển thị trạng thái trống
                
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật biểu đồ phân phối điểm: {str(e)}")
            self.stacked_grade_widget.setCurrentIndex(1)  # Hiển thị trạng thái trống nếu có lỗi
    
    def update_gender_distribution_chart(self):
        """Cập nhật biểu đồ tỷ lệ giới tính."""
        try:
            gender_stats = self.report_controller.get_gender_statistics()
            
            if gender_stats and sum(gender_stats.values()) > 0:
                self.gender_chart.plot_gender_distribution(gender_stats)
                self.stacked_gender_widget.setCurrentIndex(0)  # Hiển thị biểu đồ
            else:
                self.stacked_gender_widget.setCurrentIndex(1)  # Hiển thị trạng thái trống
                
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật biểu đồ giới tính: {str(e)}")
            self.stacked_gender_widget.setCurrentIndex(1)  # Hiển thị trạng thái trống nếu có lỗi
