from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QGroupBox, QSplitter, QDateEdit,
                            QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
import logging

class EnrollmentView(QWidget):
    """
    Giao diện quản lý đăng ký khóa học.
    """
    def __init__(self, student_controller, course_controller, db_manager):
        """
        Khởi tạo giao diện quản lý đăng ký khóa học.
        
        Args:
            student_controller (StudentController): Controller quản lý sinh viên
            course_controller (CourseController): Controller quản lý khóa học
            db_manager (DatabaseManager): Quản lý cơ sở dữ liệu
        """
        super().__init__()
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.db_manager = db_manager
        self.selected_enrollment = None
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện người dùng."""
        main_layout = QVBoxLayout()
        
        # Tạo form đăng ký
        form_group = QGroupBox("Thông tin đăng ký khóa học")
        form_layout = QFormLayout()
        
        # Chọn sinh viên
        self.student_combo = QComboBox()
        self.student_combo.setEditable(True)
        self.student_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.student_combo.setMaxVisibleItems(10)
        self.student_combo.setMinimumWidth(300)
        form_layout.addRow("Sinh viên:", self.student_combo)
        
        # Chọn khóa học
        self.course_combo = QComboBox()
        self.course_combo.setEditable(True)
        self.course_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.course_combo.setMaxVisibleItems(10)
        self.course_combo.setMinimumWidth(300)
        form_layout.addRow("Khóa học:", self.course_combo)
        
        # Ngày đăng ký
        self.enrollment_date = QDateEdit()
        self.enrollment_date.setCalendarPopup(True)
        self.enrollment_date.setDate(QDate.currentDate())
        form_layout.addRow("Ngày đăng ký:", self.enrollment_date)
        
        # Điểm số
        self.grade_input = QDoubleSpinBox()
        self.grade_input.setRange(0, 10)
        self.grade_input.setDecimals(1)
        self.grade_input.setSingleStep(0.5)
        self.grade_input.setSpecialValueText("Chưa có điểm")
        form_layout.addRow("Điểm số:", self.grade_input)
        
        form_group.setLayout(form_layout)
        
        # Tạo các nút tác vụ
        button_layout = QHBoxLayout()
        
        self.enroll_button = QPushButton("Đăng ký")
        self.enroll_button.clicked.connect(self.enroll_student)
        
        self.update_grade_button = QPushButton("Cập nhật điểm")
        self.update_grade_button.clicked.connect(self.update_grade)
        
        self.unenroll_button = QPushButton("Hủy đăng ký")
        self.unenroll_button.clicked.connect(self.unenroll_student)
        
        self.clear_button = QPushButton("Làm mới")
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.enroll_button)
        button_layout.addWidget(self.update_grade_button)
        button_layout.addWidget(self.unenroll_button)
        button_layout.addWidget(self.clear_button)
        
        # Tạo ô tìm kiếm
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã SV, tên SV, mã hoặc tên khóa học...")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Tìm")
        self.search_button.clicked.connect(self.search_enrollments)
        search_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("Tải lại")
        self.refresh_button.clicked.connect(self.load_enrollments)
        search_layout.addWidget(self.refresh_button)
        
        # Tạo bảng hiển thị danh sách đăng ký
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Mã SV", "Tên sinh viên", "Mã KH", "Tên khóa học", "Điểm"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.on_table_clicked)
        
        # Thêm các widget vào layout chính
        main_layout.addWidget(form_group)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(QLabel("Danh sách đăng ký:"))
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
        
        # Tải dữ liệu
        self.load_students()
        self.load_courses()
        self.load_enrollments()
    
    def load_students(self):
        """Tải danh sách sinh viên cho combo box."""
        self.student_combo.clear()
        students = self.student_controller.get_all_students()
        for student in students:
            display_text = f"{student.student_id} - {student.full_name}"
            # Lưu ID vào userData
            self.student_combo.addItem(display_text, student.student_id)
    
    def load_courses(self):
        """Tải danh sách khóa học cho combo box."""
        self.course_combo.clear()
        courses = self.course_controller.get_all_courses()
        for course in courses:
            display_text = f"{course.course_id} - {course.course_name}"
            # Lưu ID vào userData
            self.course_combo.addItem(display_text, course.course_id)
    
    def load_enrollments(self):
        """Tải danh sách đăng ký khóa học và hiển thị lên bảng."""
        query = """
        SELECT e.enrollment_id, e.student_id, s.full_name, e.course_id, c.course_name, e.grade
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        ORDER BY e.student_id, e.course_id
        """
        enrollments = self.db_manager.execute_query(query)
        self.populate_table(enrollments)
    
    def populate_table(self, enrollments):
        """
        Điền dữ liệu đăng ký vào bảng.
        
        Args:
            enrollments (list): Danh sách các bản ghi đăng ký
        """
        self.table.setRowCount(0)
        
        for row, enrollment in enumerate(enrollments):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(enrollment['student_id']))
            self.table.setItem(row, 1, QTableWidgetItem(enrollment['full_name']))
            self.table.setItem(row, 2, QTableWidgetItem(enrollment['course_id']))
            self.table.setItem(row, 3, QTableWidgetItem(enrollment['course_name']))
            
            # Hiển thị điểm nếu có
            grade_text = str(enrollment['grade']) if enrollment['grade'] is not None else "Chưa có"
            self.table.setItem(row, 4, QTableWidgetItem(grade_text))
            
            # Lưu ID đăng ký vào item để sử dụng sau này
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, enrollment['enrollment_id'])
    
    def on_table_clicked(self):
        """Xử lý sự kiện khi người dùng chọn một dòng trong bảng."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            enrollment_id = self.table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
            student_id = self.table.item(selected_row, 0).text()
            course_id = self.table.item(selected_row, 2).text()
            
            # Lưu thông tin đăng ký đã chọn
            self.selected_enrollment = {
                'enrollment_id': enrollment_id,
                'student_id': student_id,
                'course_id': course_id
            }
            
            # Hiển thị thông tin lên form
            self.display_enrollment(self.selected_enrollment)
    
    def display_enrollment(self, enrollment):
        """
        Hiển thị thông tin đăng ký lên form.
        
        Args:
            enrollment (dict): Thông tin đăng ký
        """
        if not enrollment:
            return
        
        # Tìm và chọn sinh viên trong combo
        student_index = self.student_combo.findData(enrollment['student_id'])
        if student_index >= 0:
            self.student_combo.setCurrentIndex(student_index)
        
        # Tìm và chọn khóa học trong combo
        course_index = self.course_combo.findData(enrollment['course_id'])
        if course_index >= 0:
            self.course_combo.setCurrentIndex(course_index)
        
        # Lấy thông tin chi tiết từ cơ sở dữ liệu
        query = """
        SELECT enrollment_date, grade
        FROM enrollments
        WHERE enrollment_id = ?
        """
        result = self.db_manager.execute_query(query, (enrollment['enrollment_id'],))
        
        if result:
            # Hiển thị ngày đăng ký
            if result[0]['enrollment_date']:
                try:
                    date = QDate.fromString(result[0]['enrollment_date'], "yyyy-MM-dd")
                    self.enrollment_date.setDate(date)
                except:
                    self.enrollment_date.setDate(QDate.currentDate())
            
            # Hiển thị điểm
            if result[0]['grade'] is not None:
                self.grade_input.setValue(result[0]['grade'])
            else:
                self.grade_input.setValue(0)
                self.grade_input.setSpecialValueText("Chưa có điểm")
    
    def enroll_student(self):
        """Đăng ký sinh viên vào khóa học."""
        if self.student_combo.currentIndex() == -1 or self.course_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sinh viên và khóa học!")
            return
        
        student_id = self.student_combo.currentData()
        course_id = self.course_combo.currentData()
        enrollment_date = self.enrollment_date.date().toString("yyyy-MM-dd")
        
        # Kiểm tra xem đã đăng ký chưa
        query = "SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?"
        result = self.db_manager.execute_query(query, (student_id, course_id))
        
        if result:
            QMessageBox.warning(self, "Lỗi", "Sinh viên này đã đăng ký khóa học này rồi!")
            return
        
        # Kiểm tra số lượng sinh viên đã đăng ký khóa học
        enrolled_count = self.course_controller.get_enrollment_count(course_id)
        course = self.course_controller.get_course_by_id(course_id)
        
        if enrolled_count >= course.max_students:
            QMessageBox.warning(self, "Lỗi", "Khóa học này đã đạt số lượng sinh viên tối đa!")
            return
        
        # Thêm đăng ký mới
        query = """
        INSERT INTO enrollments (student_id, course_id, enrollment_date)
        VALUES (?, ?, ?)
        """
        
        result = self.db_manager.execute_insert(query, (student_id, course_id, enrollment_date))
        
        if result is not None:
            QMessageBox.information(self, "Thành công", "Đăng ký khóa học thành công!")
            self.clear_form()
            self.load_enrollments()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể đăng ký khóa học!")
    
    def update_grade(self):
        """Cập nhật điểm số cho sinh viên."""
        if not self.selected_enrollment:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đăng ký từ danh sách!")
            return
        
        grade = self.grade_input.value()
        if grade == 0 and self.grade_input.specialValueText() == "Chưa có điểm":
            grade = None
        
        query = "UPDATE enrollments SET grade = ? WHERE enrollment_id = ?"
        rows_affected = self.db_manager.execute_update(query, (grade, self.selected_enrollment['enrollment_id']))
        
        if rows_affected > 0:
            QMessageBox.information(self, "Thành công", "Đã cập nhật điểm số!")
            self.load_enrollments()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể cập nhật điểm số!")
    
    def unenroll_student(self):
        """Hủy đăng ký khóa học của sinh viên."""
        if not self.selected_enrollment:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đăng ký từ danh sách!")
            return
        
        reply = QMessageBox.question(
            self, "Xác nhận hủy", 
            "Bạn có chắc muốn hủy đăng ký khóa học này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM enrollments WHERE enrollment_id = ?"
            rows_affected = self.db_manager.execute_delete(query, (self.selected_enrollment['enrollment_id'],))
            
            if rows_affected > 0:
                QMessageBox.information(self, "Thành công", "Đã hủy đăng ký khóa học!")
                self.clear_form()
                self.load_enrollments()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể hủy đăng ký khóa học!")
    
    def clear_form(self):
        """Làm mới form nhập liệu."""
        self.student_combo.setCurrentIndex(-1)
        self.course_combo.setCurrentIndex(-1)
        self.enrollment_date.setDate(QDate.currentDate())
        self.grade_input.setValue(0)
        self.grade_input.setSpecialValueText("Chưa có điểm")
        self.selected_enrollment = None
    
    def search_enrollments(self):
        """Tìm kiếm đăng ký theo từ khóa."""
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_enrollments()
            return
        
        keyword = f"%{keyword}%"
        query = """
        SELECT e.enrollment_id, e.student_id, s.full_name, e.course_id, c.course_name, e.grade
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id LIKE ? OR s.full_name LIKE ? OR e.course_id LIKE ? OR c.course_name LIKE ?
        ORDER BY e.student_id, e.course_id
        """
        
        enrollments = self.db_manager.execute_query(query, (keyword, keyword, keyword, keyword))
        self.populate_table(enrollments)
        
        if not enrollments:
            QMessageBox.information(self, "Kết quả tìm kiếm", "Không tìm thấy kết quả nào!")
