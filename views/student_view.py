from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QGroupBox, QSplitter, QDateEdit,
                            QFileDialog, QFrame, QMenu)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor, QAction
from models.student import Student
import logging
import os

class PhotoFrame(QFrame):
    """Frame hiển thị và chọn ảnh đại diện"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_path = ""
        self.default_photo = QPixmap("resources/default_avatar.png")
        self.current_pixmap = self.default_photo
        self.setup_ui()
    
    def setup_ui(self):
        self.setMinimumSize(150, 200)
        self.setMaximumSize(150, 200)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        
        # Photo label
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_default_photo()
        layout.addWidget(self.photo_label)
        
        # Button to change photo
        self.change_photo_btn = QPushButton("Chọn ảnh")
        self.change_photo_btn.clicked.connect(self.browse_photo)
        layout.addWidget(self.change_photo_btn)
        
        # Button to remove photo
        self.remove_photo_btn = QPushButton("Xóa ảnh")
        self.remove_photo_btn.clicked.connect(self.remove_photo)
        layout.addWidget(self.remove_photo_btn)
    
    def set_default_photo(self):
        """Đặt ảnh mặc định"""
        if not self.default_photo.isNull():
            self.current_pixmap = self.default_photo.scaled(
                140, 160, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            # Tạo pixmap trống nếu không có ảnh mặc định
            self.current_pixmap = QPixmap(140, 160)
            self.current_pixmap.fill(Qt.GlobalColor.lightGray)
            
        self.photo_label.setPixmap(self.current_pixmap)
        self.photo_path = ""
    
    def set_photo(self, photo_path):
        """Đặt ảnh từ đường dẫn"""
        if photo_path and os.path.exists(photo_path):
            self.photo_path = photo_path
            pixmap = QPixmap(photo_path)
            self.current_pixmap = pixmap.scaled(
                140, 160, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.photo_label.setPixmap(self.current_pixmap)
        else:
            self.set_default_photo()
    
    def browse_photo(self):
        """Mở dialog chọn ảnh từ máy tính"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Chọn ảnh đại diện",
            "",
            "Ảnh (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.set_photo(file_path)
    
    def remove_photo(self):
        """Xóa ảnh đại diện và trở lại ảnh mặc định"""
        self.set_default_photo()
    
    def get_photo_path(self):
        """Trả về đường dẫn đến ảnh đã chọn"""
        return self.photo_path
        
    def cleanup_temp_files(self):
        """
        Dọn dẹp các file ảnh tạm nếu có
        """
        # Simple implementation since this class doesn't track temp files
        # but the method needs to exist for compatibility
        pass

class StudentView(QWidget):
    """
    Giao diện quản lý sinh viên.
    """
    def __init__(self, student_controller, current_user_id=None):
        """
        Khởi tạo giao diện quản lý sinh viên.
        
        Args:
            student_controller (StudentController): Controller quản lý sinh viên
            current_user_id (int): ID của người dùng hiện tại
        """
        super().__init__()
        self.student_controller = student_controller
        self.selected_student = None
        self.current_user_id = current_user_id
        self.init_ui()
        
    def init_ui(self):
        """Thiết lập giao diện người dùng hiện đại."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tiêu đề và nút chính
        header_layout = QHBoxLayout()
        title = QLabel("Quản lý sinh viên")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2979ff;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.export_button = QPushButton("Xuất dữ liệu")
        self.export_button.setIcon(QIcon("resources/icons/export.png") if os.path.exists("resources/icons/export.png") else QIcon())
        self.export_button.clicked.connect(self.export_data)
        header_layout.addWidget(self.export_button)
        
        main_layout.addLayout(header_layout)
        
        # Chia giao diện thành 2 phần: form bên trái và bảng bên phải
        content_layout = QHBoxLayout()
        
        # --- PHẦN FORM NHẬP LIỆU ---
        form_container = QWidget()
        form_container.setFixedWidth(400)  # Điều chỉnh độ rộng phù hợp
        form_layout = QVBoxLayout(form_container)
        
        # Layout chứa form và ảnh
        form_group = QGroupBox("Thông tin sinh viên")
        form_fields = QFormLayout()
        
        # ID sinh viên
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Nhập mã sinh viên")
        form_fields.addRow("Mã sinh viên:", self.id_input)
        
        # Họ tên
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập họ và tên")
        form_fields.addRow("Họ và tên:", self.name_input)
        
        # Ngày sinh
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        form_fields.addRow("Ngày sinh:", self.dob_input)
        
        # Giới tính
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Nam", "Nữ", "Khác"])
        form_fields.addRow("Giới tính:", self.gender_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@mail.com")
        form_fields.addRow("Email:", self.email_input)
        
        # Số điện thoại
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("0123456789")
        form_fields.addRow("Số điện thoại:", self.phone_input)
        
        # Địa chỉ
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ")
        form_fields.addRow("Địa chỉ:", self.address_input)
        
        # Ngày nhập học
        self.enroll_date_input = QDateEdit()
        self.enroll_date_input.setCalendarPopup(True)
        self.enroll_date_input.setDate(QDate.currentDate())
        form_fields.addRow("Ngày nhập học:", self.enroll_date_input)
        
        # Trạng thái
        self.status_input = QComboBox()
        self.status_input.addItems(["Đang học", "Tạm nghỉ", "Đã tốt nghiệp", "Đã thôi học"])
        form_fields.addRow("Trạng thái:", self.status_input)
        
        form_group.setLayout(form_fields)
        form_layout.addWidget(form_group)
        
        # Khung ảnh đại diện
        photo_group = QGroupBox("Ảnh đại diện")
        photo_layout = QVBoxLayout()
        self.photo_frame = PhotoFrame()
        photo_layout.addWidget(self.photo_frame)
        photo_group.setLayout(photo_layout)
        form_layout.addWidget(photo_group)
        
        # Các nút tác vụ
        button_group = QGroupBox("Thao tác")
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Thêm")
        self.add_button.setObjectName("addButton")  # Set object name cho styling
        self.add_button.setIcon(QIcon("resources/icons/add.png") if os.path.exists("resources/icons/add.png") else QIcon())
        self.add_button.clicked.connect(self.add_student)
        
        self.update_button = QPushButton("Cập nhật")
        self.update_button.setIcon(QIcon("resources/icons/update.png") if os.path.exists("resources/icons/update.png") else QIcon())
        self.update_button.clicked.connect(self.update_student)
        
        self.delete_button = QPushButton("Xóa")
        self.delete_button.setObjectName("deleteButton")  # Set object name cho styling
        self.delete_button.setIcon(QIcon("resources/icons/delete.png") if os.path.exists("resources/icons/delete.png") else QIcon())
        self.delete_button.clicked.connect(self.delete_student)
        
        self.clear_button = QPushButton("Làm mới")
        self.clear_button.setIcon(QIcon("resources/icons/clear.png") if os.path.exists("resources/icons/clear.png") else QIcon())
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        button_group.setLayout(button_layout)
        form_layout.addWidget(button_group)
        
        # --- PHẦN BẢNG DỮ LIỆU ---
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        
        # Tạo ô tìm kiếm
        search_group = QGroupBox("Tìm kiếm")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã, tên, email,...")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Tìm")
        self.search_button.setIcon(QIcon("resources/icons/search.png") if os.path.exists("resources/icons/search.png") else QIcon())
        self.search_button.clicked.connect(self.search_students)
        search_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("Tải lại")
        self.refresh_button.setIcon(QIcon("resources/icons/refresh.png") if os.path.exists("resources/icons/refresh.png") else QIcon())
        self.refresh_button.clicked.connect(self.load_students)
        search_layout.addWidget(self.refresh_button)
        
        self.advanced_search_button = QPushButton("Tìm kiếm nâng cao")
        self.advanced_search_button.setIcon(QIcon("resources/icons/advanced_search.png") if os.path.exists("resources/icons/advanced_search.png") else QIcon())
        self.advanced_search_button.clicked.connect(self.show_advanced_search)
        search_layout.addWidget(self.advanced_search_button)
        
        search_group.setLayout(search_layout)
        table_layout.addWidget(search_group)
        
        # Bảng hiển thị danh sách sinh viên
        table_label = QLabel("Danh sách sinh viên:")
        table_label.setStyleSheet("font-weight: bold; color: #333;")
        table_layout.addWidget(table_label)
        
        # Thêm bộ lọc nhanh
        from widgets.quick_filter_widget import QuickFilterWidget
        
        filter_fields = {
            "status": {
                "label": "Trạng thái", 
                "type": "combobox",
                "options": [("Đang học", "Đang học"), ("Tạm nghỉ", "Tạm nghỉ"), 
                          ("Đã tốt nghiệp", "Đã tốt nghiệp"), ("Đã thôi học", "Đã thôi học")]
            },
            "gender": {
                "label": "Giới tính", 
                "type": "combobox",
                "options": [("Nam", "Nam"), ("Nữ", "Nữ"), ("Khác", "Khác")]
            }
        }
        
        self.quick_filter = QuickFilterWidget(filter_fields)
        self.quick_filter.filterChanged.connect(self.apply_quick_filters)
        table_layout.addWidget(self.quick_filter)
        
        # Bảng sinh viên
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Mã SV", "Họ tên", "Ngày sinh", "Giới tính", 
            "Email", "SĐT", "Địa chỉ", "Ngày nhập học", "Trạng thái"
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
        
        # Hiển thị tổng số sinh viên và phân trang
        footer_layout = QHBoxLayout()
        
        self.total_students_label = QLabel("Tổng số: 0 sinh viên")
        self.total_students_label.setStyleSheet("font-weight: bold;")
        footer_layout.addWidget(self.total_students_label)
        
        footer_layout.addStretch()
        
        # Thêm phân trang
        from widgets.pagination_widget import PaginationWidget
        
        self.pagination = PaginationWidget()
        self.pagination.pageChanged.connect(self.change_page)
        self.pagination.pageSizeChanged.connect(self.change_page_size)
        footer_layout.addWidget(self.pagination)
        
        table_layout.addLayout(footer_layout)
        
        # Thêm các container vào layout chính
        content_layout.addWidget(form_container)
        content_layout.addWidget(table_container)
        content_layout.setStretch(1, 1)  # Cho phép table_container mở rộng
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        
        # Khởi tạo biến phân trang
        self.current_page = 1
        self.page_size = 20
        self.filtered_students = []
        
        # Tải danh sách sinh viên
        self.load_students()
    
    def load_students(self):
        """Tải danh sách sinh viên từ cơ sở dữ liệu và hiển thị lên bảng."""
        students = self.student_controller.get_all_students()
        self.filtered_students = students
        self.pagination.update_total_items(len(students))
        self.populate_table_with_pagination()
    
    def populate_table_with_pagination(self):
        """Hiển thị dữ liệu trên trang hiện tại"""
        start_idx = (self.current_page - 1) * self.page_size
        
        # Nếu page_size là -1 thì hiển thị tất cả
        if self.page_size == -1:
            students_to_show = self.filtered_students
        else:
            students_to_show = self.filtered_students[start_idx:start_idx + self.page_size]
        
        self.populate_table(students_to_show)
        self.total_students_label.setText(f"Tổng số: {len(self.filtered_students)} sinh viên")
    
    def populate_table(self, students):
        """
        Điền dữ liệu sinh viên vào bảng.
        
        Args:
            students (list): Danh sách các đối tượng Student
        """
        # Tắt việc cập nhật giao diện để tăng hiệu suất
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        
        # Lưu trạng thái của thanh cuộn để khôi phục sau
        scrollbar = self.table.verticalScrollBar()
        scroll_position = scrollbar.value()
        
        # Xóa tất cả các dòng hiện có
        self.table.setRowCount(0)
        
        # Thiết lập số dòng mới (tốc độ hơn là thêm từng dòng một)
        self.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # Tạo các item trong bảng
            id_item = QTableWidgetItem(student.student_id)
            name_item = QTableWidgetItem(student.full_name)
            dob_item = QTableWidgetItem(student.date_of_birth)
            gender_item = QTableWidgetItem(student.gender)
            email_item = QTableWidgetItem(student.email)
            phone_item = QTableWidgetItem(student.phone)
            address_item = QTableWidgetItem(student.address)
            enrolled_date_item = QTableWidgetItem(student.enrolled_date)
            status_item = QTableWidgetItem(student.status)
            
            # Thiết lập các item vào bảng
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, dob_item)
            self.table.setItem(row, 3, gender_item)
            self.table.setItem(row, 4, email_item)
            self.table.setItem(row, 5, phone_item)
            self.table.setItem(row, 6, address_item)
            self.table.setItem(row, 7, enrolled_date_item)
            self.table.setItem(row, 8, status_item)
            
            # Thiết lập màu nền dựa trên trạng thái sinh viên
            if student.status == "Đang học":
                status_item.setBackground(QColor(200, 255, 200))  # Xanh lá nhạt
            elif student.status == "Tạm nghỉ":
                status_item.setBackground(QColor(255, 255, 200))  # Vàng nhạt
            elif student.status == "Đã tốt nghiệp":
                status_item.setBackground(QColor(200, 200, 255))  # Xanh dương nhạt
            elif student.status == "Đã thôi học":
                status_item.setBackground(QColor(255, 200, 200))  # Đỏ nhạt
        
        # Khôi phục tính năng cập nhật giao diện và vị trí cuộn
        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)
        scrollbar.setValue(scroll_position)
        
        # Cập nhật nhãn tổng số sinh viên
        self.total_students_label.setText(f"Tổng số: {len(students)} sinh viên")
    
    def change_page(self, page):
        """Xử lý khi thay đổi trang"""
        self.current_page = page
        self.populate_table_with_pagination()

    def change_page_size(self, size):
        """Xử lý khi thay đổi số lượng mục trên trang"""
        self.page_size = size
        self.current_page = 1  # Reset về trang đầu tiên
        self.populate_table_with_pagination()

    def apply_quick_filters(self, filters):
        """
        Áp dụng bộ lọc nhanh và hiển thị kết quả
        
        Args:
            filters (dict): Dictionary chứa các bộ lọc
        """
        # Lấy tất cả sinh viên
        all_students = self.student_controller.get_all_students()
        
        # Áp dụng bộ lọc
        filtered_students = all_students
        
        for field, value in filters.items():
            if field == "status" and value:
                filtered_students = [s for s in filtered_students if s.status == value]
            elif field == "gender" and value:
                filtered_students = [s for s in filtered_students if s.gender == value]
            elif field == "search_text" and value:
                search_text = value.lower()
                filtered_students = [s for s in filtered_students if 
                                    search_text in s.student_id.lower() or
                                    search_text in s.full_name.lower() or
                                    search_text in s.email.lower()]
        
        # Cập nhật dữ liệu hiển thị
        self.filtered_students = filtered_students
        self.pagination.update_total_items(len(filtered_students))
        self.current_page = 1  # Reset về trang đầu tiên
        self.populate_table_with_pagination()

    def sort_table(self, column_index, order):
        """
        Sắp xếp bảng dữ liệu theo cột được chọn
        
        Args:
            column_index (int): Chỉ số cột
            order (Qt.SortOrder): Thứ tự sắp xếp
        """
        # Các trường tương ứng với cột trong bảng
        column_fields = [
            "student_id", "full_name", "date_of_birth", "gender",
            "email", "phone", "address", "enrolled_date", "status"
        ]
        
        if 0 <= column_index < len(column_fields):
            field = column_fields[column_index]
            
            # Sắp xếp dữ liệu
            reverse_order = (order == Qt.SortOrder.DescendingOrder)
            
            self.filtered_students.sort(
                key=lambda s: getattr(s, field) if getattr(s, field) is not None else "",
                reverse=reverse_order
            )
            
            # Cập nhật hiển thị
            self.populate_table_with_pagination()

    def on_table_clicked(self):
        """Xử lý sự kiện khi người dùng chọn một dòng trong bảng."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            student_id = self.table.item(selected_row, 0).text()
            self.selected_student = self.student_controller.get_student_by_id(student_id)
            self.display_student(self.selected_student)
    
    def display_student(self, student):
        """
        Hiển thị thông tin sinh viên lên form.
        
        Args:
            student (Student): Đối tượng sinh viên cần hiển thị
        """
        if not student:
            return
        
        self.id_input.setText(student.student_id)
        self.name_input.setText(student.full_name)
        
        if student.date_of_birth:
            try:
                dob = QDate.fromString(student.date_of_birth, "yyyy-MM-dd")
                self.dob_input.setDate(dob)
            except:
                self.dob_input.setDate(QDate.currentDate())
        
        gender_index = 0
        if student.gender == "Nữ":
            gender_index = 1
        elif student.gender == "Khác":
            gender_index = 2
        self.gender_input.setCurrentIndex(gender_index)
        
        self.email_input.setText(student.email)
        self.phone_input.setText(student.phone)
        self.address_input.setText(student.address)
        
        if student.enrolled_date:
            try:
                enrolled = QDate.fromString(student.enrolled_date, "yyyy-MM-dd")
                self.enroll_date_input.setDate(enrolled)
            except:
                self.enroll_date_input.setDate(QDate.currentDate())
        
        status_index = 0
        if student.status == "Đang học":
            status_index = 0
        elif student.status == "Tạm nghỉ":
            status_index = 1
        elif student.status == "Đã tốt nghiệp":
            status_index = 2
        elif student.status == "Đã thôi học":
            status_index = 3
        self.status_input.setCurrentIndex(status_index)
        
        # Hiển thị ảnh đại diện
        self.photo_frame.set_photo(student.photo_path)
    
    def get_form_data(self):
        """
        Lấy dữ liệu từ form và tạo đối tượng Student.
        
        Returns:
            Student: Đối tượng sinh viên từ form
        """
        student_id = self.id_input.text().strip()
        full_name = self.name_input.text().strip()
        date_of_birth = self.dob_input.date().toString("yyyy-MM-dd")
        gender = self.gender_input.currentText()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        enrolled_date = self.enroll_date_input.date().toString("yyyy-MM-dd")
        status = self.status_input.currentText()
        
        return Student(
            student_id=student_id,
            full_name=full_name,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email,
            phone=phone,
            address=address,
            enrolled_date=enrolled_date,
            status=status
        )
    
    def add_student(self):
        """Thêm sinh viên mới vào hệ thống."""
        # Kiểm tra dữ liệu hợp lệ
        if not self.validate_form_data():
            return
        
        student = self.get_form_data()
        photo_path = self.photo_frame.get_photo_path()
        
        success = self.student_controller.add_student(
            student, 
            photo_file_path=photo_path,
            current_user_id=self.current_user_id
        )
        
        if success:
            QMessageBox.information(
                self, "Thành công", "Thêm sinh viên thành công!"
            )
            self.clear_form()
            self.load_students()
        else:
            QMessageBox.warning(
                self, "Lỗi", 
                f"Không thể thêm sinh viên. Mã số {student.student_id} có thể đã tồn tại."
            )
    
    def update_student(self):
        """Cập nhật thông tin sinh viên hiện tại."""
        if not self.selected_student:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn sinh viên cần cập nhật."
            )
            return
        
        # Kiểm tra dữ liệu hợp lệ
        if not self.validate_form_data():
            return
        
        student = self.get_form_data()
        photo_path = self.photo_frame.get_photo_path()
        
        # Nếu không chọn ảnh mới, giữ nguyên ảnh cũ
        use_new_photo = photo_path != "" and photo_path != self.selected_student.photo_path
        
        success = self.student_controller.update_student(
            student, 
            photo_file_path=photo_path if use_new_photo else None,
            current_user_id=self.current_user_id
        )
        
        if success:
            QMessageBox.information(
                self, "Thành công", "Cập nhật sinh viên thành công!"
            )
            self.selected_student = student
            self.load_students()
        else:
            QMessageBox.warning(
                self, "Lỗi", "Không thể cập nhật thông tin sinh viên."
            )
    
    def delete_student(self):
        """Xóa sinh viên hiện tại khỏi hệ thống."""
        if not self.selected_student:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn sinh viên cần xóa."
            )
            return
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa", 
            f"Bạn có chắc muốn xóa sinh viên {self.selected_student.full_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.student_controller.delete_student(
                self.selected_student.student_id,
                current_user_id=self.current_user_id
            )
            if success:
                QMessageBox.information(
                    self, "Thành công", "Xóa sinh viên thành công!"
                )
                self.clear_form()
                self.load_students()
            else:
                QMessageBox.warning(
                    self, "Lỗi", "Không thể xóa sinh viên."
                )
    
    def clear_form(self):
        """Làm mới form nhập liệu."""
        self.id_input.setText("")
        self.name_input.setText("")
        self.dob_input.setDate(QDate.currentDate())
        self.gender_input.setCurrentIndex(0)
        self.email_input.setText("")
        self.phone_input.setText("")
        self.address_input.setText("")
        self.enroll_date_input.setDate(QDate.currentDate())
        self.status_input.setCurrentIndex(0)
        self.photo_frame.set_default_photo()
        self.selected_student = None
    
    def search_students(self):
        """Tìm kiếm sinh viên theo từ khóa."""
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
        
        if not keyword:
            self.load_students()
            return
        
        students = self.student_controller.search_students(keyword)
        self.populate_table(students)
        
        if not students:
            QMessageBox.information(
                self, "Kết quả tìm kiếm", "Không tìm thấy sinh viên nào!"
            )
    
    def show_advanced_search(self):
        """Hiển thị giao diện tìm kiếm nâng cao"""
        from views.advanced_search_dialog import AdvancedStudentSearchDialog
        dialog = AdvancedStudentSearchDialog(self)
        if dialog.exec():
            filters = dialog.get_filters()
            students = self.student_controller.advanced_search(filters)
            self.populate_table(students)
            
            if not students:
                QMessageBox.information(
                    self, "Kết quả tìm kiếm", "Không tìm thấy sinh viên nào!"
                )
    
    def export_data(self):
        """Xuất dữ liệu sinh viên ra các định dạng"""
        from utils.export_manager import ExportManager
        
        # Lấy dữ liệu từ bảng hiện tại
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        if rows == 0:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất!")
            return
        
        # Chuẩn bị dữ liệu
        headers = []
        for col in range(cols):
            headers.append(self.table.horizontalHeaderItem(col).text())
        
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        # Hiển thị menu xuất dữ liệu
        export_menu = QMenu(self)
        export_excel_action = export_menu.addAction("Xuất ra Excel")
        export_pdf_action = export_menu.addAction("Xuất ra PDF")
        
        action = export_menu.exec(self.export_button.mapToGlobal(
            self.export_button.rect().bottomRight()
        ))
        
        if action == export_excel_action:
            ExportManager.export_to_excel(
                data, 
                headers, 
                parent=self, 
                default_filename="danh_sach_sinh_vien.xlsx"
            )
        elif action == export_pdf_action:
            ExportManager.export_to_pdf(
                data, 
                headers, 
                title="Danh sách sinh viên", 
                parent=self, 
                default_filename="danh_sach_sinh_vien.pdf"
            )
    
    def validate_form_data(self):
        """
        Kiểm tra dữ liệu nhập vào form.
        
        Returns:
            bool: True nếu dữ liệu hợp lệ, False nếu không
        """
        # Kiểm tra mã sinh viên
        student_id = self.id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập mã sinh viên!")
            return False
        
        # Kiểm tra họ tên
        full_name = self.name_input.text().strip()
        if not full_name:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập họ tên sinh viên!")
            return False
        
        # Kiểm tra email
        email = self.email_input.text().strip()
        if email and '@' not in email:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Email không hợp lệ!")
            return False
        
        return True