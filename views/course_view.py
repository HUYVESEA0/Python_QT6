from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                          QLabel, QLineEdit, QSpinBox, QPushButton, 
                          QTableWidget, QTableWidgetItem, QHeaderView, 
                          QMessageBox, QGroupBox, QTextEdit)
from PyQt6.QtCore import Qt
from models.course import Course
import logging

class CourseView(QWidget):
    """
    Giao diện quản lý khóa học.
    """
    def __init__(self, course_controller):
        """
        Khởi tạo giao diện quản lý khóa học.
        
        Args:
            course_controller (CourseController): Controller quản lý khóa học
        """
        super().__init__()
        self.course_controller = course_controller
        self.selected_course = None
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        main_layout = QVBoxLayout()
        
        # Tạo form nhập liệu
        form_group = QGroupBox("Thông tin khóa học")
        form_layout = QFormLayout()
        
        # Mã khóa học
        self.id_input = QLineEdit()
        form_layout.addRow("Mã khóa học:", self.id_input)
        
        # Tên khóa học
        self.name_input = QLineEdit()
        form_layout.addRow("Tên khóa học:", self.name_input)
        
        # Số tín chỉ
        self.credits_input = QSpinBox()
        self.credits_input.setMinimum(1)
        self.credits_input.setMaximum(10)
        self.credits_input.setValue(3)
        form_layout.addRow("Số tín chỉ:", self.credits_input)
        
        # Giảng viên
        self.instructor_input = QLineEdit()
        form_layout.addRow("Giảng viên:", self.instructor_input)
        
        # Mô tả
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Mô tả:", self.description_input)
        
        # Số sinh viên tối đa
        self.max_students_input = QSpinBox()
        self.max_students_input.setMinimum(1)
        self.max_students_input.setMaximum(200)
        self.max_students_input.setValue(50)
        form_layout.addRow("Số SV tối đa:", self.max_students_input)
        
        form_group.setLayout(form_layout)
        
        # Tạo các nút tác vụ
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Thêm")
        self.add_button.clicked.connect(self.add_course)
        
        self.update_button = QPushButton("Cập nhật")
        self.update_button.clicked.connect(self.update_course)
        
        self.delete_button = QPushButton("Xóa")
        self.delete_button.clicked.connect(self.delete_course)
        
        self.clear_button = QPushButton("Làm mới")
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Tạo ô tìm kiếm
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã, tên khóa học, giảng viên...")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Tìm")
        self.search_button.clicked.connect(self.search_courses)
        search_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("Tải lại")
        self.refresh_button.clicked.connect(self.load_courses)
        search_layout.addWidget(self.refresh_button)
        
        # Tạo bảng hiển thị danh sách khóa học
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Mã KH", "Tên khóa học", "Tín chỉ", "Giảng viên", 
            "Mô tả", "SV tối đa"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.on_table_clicked)
        
        # Thêm các widget vào layout chính
        main_layout.addWidget(form_group)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(QLabel("Danh sách khóa học:"))
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
        
        # Tải danh sách khóa học
        self.load_courses()
    
    def load_courses(self):
        """Tải danh sách khóa học từ cơ sở dữ liệu và hiển thị lên bảng."""
        courses = self.course_controller.get_all_courses()
        self.populate_table(courses)
    
    def populate_table(self, courses):
        """
        Điền dữ liệu khóa học vào bảng.
        
        Args:
            courses (list): Danh sách các đối tượng Course
        """
        self.table.setRowCount(0)
        
        for row, course in enumerate(courses):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(course.course_id))
            self.table.setItem(row, 1, QTableWidgetItem(course.course_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(course.credits)))
            self.table.setItem(row, 3, QTableWidgetItem(course.instructor))
            self.table.setItem(row, 4, QTableWidgetItem(course.description))
            self.table.setItem(row, 5, QTableWidgetItem(str(course.max_students)))
    
    def on_table_clicked(self):
        """Xử lý sự kiện khi người dùng chọn một dòng trong bảng."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            course_id = self.table.item(selected_row, 0).text()
            self.selected_course = self.course_controller.get_course_by_id(course_id)
            self.display_course(self.selected_course)
    
    def display_course(self, course):
        """
        Hiển thị thông tin khóa học lên form.
        
        Args:
            course (Course): Đối tượng khóa học cần hiển thị
        """
        if not course:
            return
        
        self.id_input.setText(course.course_id)
        self.name_input.setText(course.course_name)
        self.credits_input.setValue(course.credits)
        self.instructor_input.setText(course.instructor)
        self.description_input.setText(course.description)
        self.max_students_input.setValue(course.max_students)
    
    def get_form_data(self):
        """
        Lấy dữ liệu từ form và tạo đối tượng Course.
        
        Returns:
            Course: Đối tượng khóa học từ form
        """
        course_id = self.id_input.text().strip()
        course_name = self.name_input.text().strip()
        credits = self.credits_input.value()
        instructor = self.instructor_input.text().strip()
        description = self.description_input.toPlainText().strip()
        max_students = self.max_students_input.value()
        
        return Course(
            course_id=course_id,
            course_name=course_name,
            credits=credits,
            instructor=instructor,
            description=description,
            max_students=max_students
        )
    
    def add_course(self):
        """Thêm khóa học mới vào hệ thống."""
        # Kiểm tra dữ liệu hợp lệ
        if not self.validate_form_data():
            return
        
        course = self.get_form_data()
        success = self.course_controller.add_course(course)
        
        if success:
            QMessageBox.information(
                self, "Thành công", "Thêm khóa học thành công!"
            )
            self.clear_form()
            self.load_courses()
        else:
            QMessageBox.warning(
                self, "Lỗi", 
                f"Không thể thêm khóa học. Mã số {course.course_id} có thể đã tồn tại."
            )
    
    def update_course(self):
        """Cập nhật thông tin khóa học hiện tại."""
        if not self.selected_course:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn khóa học cần cập nhật."
            )
            return
        
        # Kiểm tra dữ liệu hợp lệ
        if not self.validate_form_data():
            return
        
        course = self.get_form_data()
        success = self.course_controller.update_course(course)
        
        if success:
            QMessageBox.information(
                self, "Thành công", "Cập nhật khóa học thành công!"
            )
            self.selected_course = course
            self.load_courses()
        else:
            QMessageBox.warning(
                self, "Lỗi", "Không thể cập nhật thông tin khóa học."
            )
    
    def delete_course(self):
        """Xóa khóa học hiện tại khỏi hệ thống."""
        if not self.selected_course:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn khóa học cần xóa."
            )
            return
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa", 
            f"Bạn có chắc muốn xóa khóa học {self.selected_course.course_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.course_controller.delete_course(self.selected_course.course_id)
            if success:
                QMessageBox.information(
                    self, "Thành công", "Xóa khóa học thành công!"
                )
                self.clear_form()
                self.load_courses()
            else:
                QMessageBox.warning(
                    self, "Lỗi", "Không thể xóa khóa học. Có thể có sinh viên đã đăng ký khóa học này."
                )
    
    def clear_form(self):
        """Làm mới form nhập liệu."""
        self.id_input.setText("")
        self.name_input.setText("")
        self.credits_input.setValue(3)
        self.instructor_input.setText("")
        self.description_input.setText("")
        self.max_students_input.setValue(50)
        self.selected_course = None
    
    def search_courses(self):
        """Tìm kiếm khóa học theo từ khóa."""
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_courses()
            return
        
        courses = self.course_controller.search_courses(keyword)
        self.populate_table(courses)
        
        if not courses:
            QMessageBox.information(
                self, "Kết quả tìm kiếm", "Không tìm thấy khóa học nào!"
            )
    
    def validate_form_data(self):
        """
        Kiểm tra dữ liệu nhập vào form.
        
        Returns:
            bool: True nếu dữ liệu hợp lệ, False nếu không
        """
        # Kiểm tra mã khóa học
        course_id = self.id_input.text().strip()
        if not course_id:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập mã khóa học!")
            return False
        
        # Kiểm tra tên khóa học
        course_name = self.name_input.text().strip()
        if not course_name:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập tên khóa học!")
            return False
        
        return True