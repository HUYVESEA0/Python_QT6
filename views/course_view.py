from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                          QLabel, QLineEdit, QSpinBox, QPushButton, 
                          QTableWidget, QTableWidgetItem, QHeaderView, 
                          QMessageBox, QGroupBox, QTextEdit, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
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
        table_layout = QVBoxLayout()
        
        table_label = QLabel("Danh sách khóa học:")
        table_label.setStyleSheet("font-weight: bold; color: #333;")
        table_layout.addWidget(table_label)
        
        # Thêm bộ lọc nhanh
        from widgets.quick_filter_widget import QuickFilterWidget
        
        filter_fields = {
            "credits": {
                "label": "Số tín chỉ", 
                "type": "combobox",
                "options": [(f"{i} tín chỉ", i) for i in range(1, 11)]
            }
        }
        
        self.quick_filter = QuickFilterWidget(filter_fields)
        self.quick_filter.filterChanged.connect(self.apply_quick_filters)
        table_layout.addWidget(self.quick_filter)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Mã khóa học", "Tên khóa học", "Tín chỉ", 
            "Giảng viên", "Mô tả", "Số SV tối đa"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.on_table_clicked)
        
        # Thêm chức năng sắp xếp khi click vào header
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)
        
        table_layout.addWidget(self.table)
        
        # Hiển thị tổng số khóa học và phân trang
        footer_layout = QHBoxLayout()
        
        self.total_courses_label = QLabel("Tổng số: 0 khóa học")
        self.total_courses_label.setStyleSheet("font-weight: bold;")
        footer_layout.addWidget(self.total_courses_label)
        
        footer_layout.addStretch()
        
        # Thêm phân trang
        from widgets.pagination_widget import PaginationWidget
        
        self.pagination = PaginationWidget()
        self.pagination.pageChanged.connect(self.change_page)
        self.pagination.pageSizeChanged.connect(self.change_page_size)
        footer_layout.addWidget(self.pagination)
        
        table_layout.addLayout(footer_layout)
        
        # Thêm các widget vào layout chính
        main_layout.addWidget(form_group)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addLayout(table_layout)
        
        self.setLayout(main_layout)
        
        # Khởi tạo biến phân trang
        self.current_page = 1
        self.page_size = 20
        self.filtered_courses = []
        
        # Tải danh sách khóa học
        self.load_courses()
    
    def load_courses(self):
        """Tải danh sách khóa học từ cơ sở dữ liệu và hiển thị lên bảng."""
        courses = self.course_controller.get_all_courses()
        self.filtered_courses = courses
        self.pagination.update_total_items(len(courses))
        self.populate_table_with_pagination()
    
    def populate_table(self, courses):
        """
        Điền dữ liệu khóa học vào bảng.

        Args:
            courses (list): Danh sách các đối tượng Course.
        """
        self.table.setRowCount(0)
        
        for row, course in enumerate(courses):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(course.ma_khoa_hoc))
            self.table.setItem(row, 1, QTableWidgetItem(course.ten_khoa_hoc))
            self.table.setItem(row, 2, QTableWidgetItem(str(course.so_tin_chi)))
            self.table.setItem(row, 3, QTableWidgetItem(course.giang_vien))
            self.table.setItem(row, 4, QTableWidgetItem(course.mo_ta))
            self.table.setItem(row, 5, QTableWidgetItem(str(course.so_luong_toi_da)))
    
    def populate_table_with_pagination(self):
        """Hiển thị dữ liệu trên trang hiện tại."""
        start_idx = (self.current_page - 1) * self.page_size
        
        # Nếu page_size là -1 thì hiển thị tất cả
        if self.page_size == -1:
            courses_to_show = self.filtered_courses
        else:
            courses_to_show = self.filtered_courses[start_idx:start_idx + self.page_size]
        
        self.populate_table(courses_to_show)
        self.total_courses_label.setText(f"Tổng số: {len(self.filtered_courses)} khóa học")
    
    def change_page(self, page):
        """Xử lý khi thay đổi trang."""
        self.current_page = page
        self.populate_table_with_pagination()
    
    def change_page_size(self, size):
        """Xử lý khi thay đổi số lượng mục trên trang."""
        self.page_size = size
        self.current_page = 1  # Reset về trang đầu tiên
        self.populate_table_with_pagination()
    
    def apply_quick_filters(self, filters):
        """
        Áp dụng bộ lọc nhanh và hiển thị kết quả.

        Args:
            filters (dict): Dictionary chứa các bộ lọc.
        """
        # Lấy tất cả khóa học
        all_courses = self.course_controller.get_all_courses()
        
        # Áp dụng bộ lọc
        filtered_courses = all_courses
        
        for field, value in filters.items():
            if field == "credits" and value:
                filtered_courses = [c for c in filtered_courses if c.credits == int(value)]
            elif field == "search_text" and value:
                search_text = value.lower()
                filtered_courses = [c for c in filtered_courses if 
                                  search_text in c.course_id.lower() or
                                  search_text in c.course_name.lower() or
                                  search_text in (c.instructor.lower() if c.instructor else "")]
        
        # Cập nhật dữ liệu hiển thị
        self.filtered_courses = filtered_courses
        self.pagination.update_total_items(len(filtered_courses))
        self.current_page = 1  # Reset về trang đầu tiên
        self.populate_table_with_pagination()
    
    def sort_table(self, column_index, order):
        """
        Sắp xếp bảng dữ liệu theo cột được chọn.

        Args:
            column_index (int): Chỉ số cột.
            order (Qt.SortOrder): Thứ tự sắp xếp.
        """
        # Các trường tương ứng với cột trong bảng
        column_fields = [
            "course_id", "course_name", "credits", 
            "instructor", "description", "max_students"
        ]
        
        if 0 <= column_index < len(column_fields):
            field = column_fields[column_index]
            
            # Sắp xếp dữ liệu
            reverse_order = (order == Qt.SortOrder.DescendingOrder)
            
            self.filtered_courses.sort(
                key=lambda c: getattr(c, field) if getattr(c, field) is not None else "",
                reverse=reverse_order
            )
            
            # Cập nhật hiển thị
            self.populate_table_with_pagination()
    
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
            course (Course): Đối tượng khóa học cần hiển thị.
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
            Course: Đối tượng khóa học từ form.
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
        
        # Thêm từ khóa tìm kiếm vào bộ lọc nhanh
        filters = self.quick_filter.current_filters.copy()
        if keyword:
            filters["search_text"] = keyword
        else:
            if "search_text" in filters:
                del filters["search_text"]
        
        # Áp dụng bộ lọc
        self.apply_quick_filters(filters)
    
    def validate_form_data(self):
        """
        Kiểm tra dữ liệu nhập vào form.

        Returns:
            bool: True nếu dữ liệu hợp lệ, False nếu không.
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