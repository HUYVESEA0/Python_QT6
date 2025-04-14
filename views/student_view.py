from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QGroupBox, QSplitter, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
from models.student import Student
import logging

class StudentView(QWidget):
    """
    Giao diện quản lý sinh viên.
    """
    def __init__(self, student_controller):
        """
        Khởi tạo giao diện quản lý sinh viên.
        
        Args:
            student_controller (StudentController): Controller quản lý sinh viên
        """
        super().__init__()
        self.student_controller = student_controller
        self.selected_student = None
        self.init_ui()
        
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        main_layout = QVBoxLayout()
        
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
        
        # Tạo bảng hiển thị danh sách sinh viên
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Mã SV", "Họ tên", "Ngày sinh", "Giới tính", 
            "Email", "SĐT", "Địa chỉ", "Ngày nhập học", "Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.on_table_clicked)
        
        # Thêm các widget vào layout chính
        main_layout.addWidget(form_group)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(QLabel("Danh sách sinh viên:"))
        main_layout.addWidget(self.table)
        
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
        self.table.setRowCount(0)
        
        for row, student in enumerate(students):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(student.student_id))
            self.table.setItem(row, 1, QTableWidgetItem(student.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(student.date_of_birth))
            self.table.setItem(row, 3, QTableWidgetItem(student.gender))
            self.table.setItem(row, 4, QTableWidgetItem(student.email))
            self.table.setItem(row, 5, QTableWidgetItem(student.phone))
            self.table.setItem(row, 6, QTableWidgetItem(student.address))
            self.table.setItem(row, 7, QTableWidgetItem(student.enrolled_date))
            self.table.setItem(row, 8, QTableWidgetItem(student.status))
    
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
        success = self.student_controller.add_student(student)
        
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
        success = self.student_controller.update_student(student)
        
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
            success = self.student_controller.delete_student(self.selected_student.student_id)
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