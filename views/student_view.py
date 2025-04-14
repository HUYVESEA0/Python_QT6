from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QGroupBox, QSplitter, QDateEdit,
                            QFileDialog, QFrame)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor
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
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh đại diện", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.set_photo(file_path)
    
    def remove_photo(self):
        """Xóa ảnh đã chọn"""
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
        """Thiết lập giao diện người dùng."""
        main_layout = QVBoxLayout()
        
        # Layout chứa form và ảnh
        form_photo_layout = QHBoxLayout()
        
        # Tạo form nhập liệu
        form_group = QGroupBox("Thông tin sinh viên")
        form_layout = QFormLayout()
        
        # ID sinh viên
        self.id_input = QLineEdit()
        form_layout.addRow("Mã sinh viên:", self.id_input)
        
        # Họ tên
        self.name_input = QLineEdit()
        form_layout.addRow("Họ và tên:", self.name_input)
        
        # Ngày sinh
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        form_layout.addRow("Ngày sinh:", self.dob_input)
        
        # Giới tính
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Nam", "Nữ", "Khác"])
        form_layout.addRow("Giới tính:", self.gender_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # Số điện thoại
        self.phone_input = QLineEdit()
        form_layout.addRow("Số điện thoại:", self.phone_input)
        
        # Địa chỉ
        self.address_input = QLineEdit()
        form_layout.addRow("Địa chỉ:", self.address_input)
        
        # Ngày nhập học
        self.enroll_date_input = QDateEdit()
        self.enroll_date_input.setCalendarPopup(True)
        self.enroll_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Ngày nhập học:", self.enroll_date_input)
        
        # Trạng thái
        self.status_input = QComboBox()
        self.status_input.addItems(["Đang học", "Tạm nghỉ", "Đã tốt nghiệp", "Đã thôi học"])
        form_layout.addRow("Trạng thái:", self.status_input)
        
        form_group.setLayout(form_layout)
        
        # Khung ảnh đại diện
        self.photo_frame = PhotoFrame()
        
        # Thêm form và ảnh vào layout
        form_photo_layout.addWidget(form_group, 3)
        form_photo_layout.addWidget(self.photo_frame, 1)
        
        main_layout.addLayout(form_photo_layout)
        
        # Tạo các nút tác vụ
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Thêm")
        self.add_button.clicked.connect(self.add_student)
        
        self.update_button = QPushButton("Cập nhật")
        self.update_button.clicked.connect(self.update_student)
        
        self.delete_button = QPushButton("Xóa")
        self.delete_button.clicked.connect(self.delete_student)
        
        self.clear_button = QPushButton("Làm mới")
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Tạo ô tìm kiếm
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã, tên, email,...")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Tìm")
        self.search_button.clicked.connect(self.search_students)
        search_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("Tải lại")
        self.refresh_button.clicked.connect(self.load_students)
        search_layout.addWidget(self.refresh_button)
        
        # Nút tìm kiếm nâng cao
        self.advanced_search_button = QPushButton("Tìm kiếm nâng cao")
        self.advanced_search_button.clicked.connect(self.show_advanced_search)
        search_layout.addWidget(self.advanced_search_button)
        
        # Nút xuất dữ liệu
        self.export_button = QPushButton("Xuất dữ liệu")
        self.export_button.clicked.connect(self.export_data)
        search_layout.addWidget(self.export_button)
        
        main_layout.addLayout(search_layout)
        
        # Tạo bảng hiển thị danh sách sinh viên
        main_layout.addWidget(QLabel("Danh sách sinh viên:"))
        
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
        
        main_layout.addWidget(self.table)
        
        # Add the total students label
        self.total_students_label = QLabel("Tổng số: 0 sinh viên")
        main_layout.addWidget(self.total_students_label)
        
        self.setLayout(main_layout)
        
        # Tải danh sách sinh viên
        self.load_students()
    
    def load_students(self):
        """Tải danh sách sinh viên từ cơ sở dữ liệu và hiển thị lên bảng."""
        students = self.student_controller.get_all_students()
        self.populate_table(students)
    
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
        from PyQt6.QtWidgets import QMenu
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