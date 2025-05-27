from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QGroupBox, QSplitter, QDateEdit,
                            QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
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
        self.enrollment_table = QTableWidget()
        self.enrollment_table.setColumnCount(5)
        self.enrollment_table.setHorizontalHeaderLabels([
            "Mã đăng ký", "Sinh viên", "Khóa học", "Ngày đăng ký", "Điểm"
        ])
        
        # Cải thiện hiển thị bằng cách điều chỉnh độ rộng cột phù hợp
        header = self.enrollment_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Mã đăng ký - ngắn gọn
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Sinh viên - có thể dài
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Khóa học - có thể dài
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Ngày - độ dài cố định
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Điểm - ngắn gọn
        
        self.enrollment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.enrollment_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.enrollment_table.clicked.connect(self.on_table_clicked)
        
        # Thêm các widget vào layout chính
        main_layout.addWidget(form_group)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(QLabel("Danh sách đăng ký:"))
        main_layout.addWidget(self.enrollment_table)
        # Thêm label tổng số đăng ký
        self.enrollment_count_label = QLabel("Tổng số đăng ký: 0")
        main_layout.addWidget(self.enrollment_count_label)

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
            display_text = f"{student.ma_sinh_vien} - {student.ho_ten}"
            # Lưu mã sinh viên vào userData
            self.student_combo.addItem(display_text, student.ma_sinh_vien)
    
    def load_courses(self):
        """Tải danh sách khóa học cho combo box."""
        self.course_combo.clear()
        courses = self.course_controller.get_all_courses()
        for course in courses:
            display_text = f"{course.ma_khoa_hoc} - {course.ten_khoa_hoc}"
            # Lưu mã khóa học vào userData
            self.course_combo.addItem(display_text, course.ma_khoa_hoc)
    
    def load_enrollments(self):
        """Tải danh sách đăng ký khóa học và hiển thị lên bảng."""
        query = """
        SELECT e.ma_ghi_danh, e.ma_sinh_vien, s.ho_ten, e.ma_khoa_hoc, c.ten_khoa_hoc, e.ngay_ghi_danh, e.diem
        FROM ghi_danh e
        JOIN sinh_vien s ON e.ma_sinh_vien = s.ma_sinh_vien
        JOIN khoa_hoc c ON e.ma_khoa_hoc = c.ma_khoa_hoc
        ORDER BY e.ma_sinh_vien, e.ma_khoa_hoc
        """
        enrollments = self.db_manager.execute_query(query)
        self.populate_table(enrollments)
    
    def populate_table(self, enrollments):
        """
        Điền dữ liệu đăng ký vào bảng.

        Args:
            enrollments (list): Danh sách các bản ghi đăng ký.
        """
        self.enrollment_table.setRowCount(0)
        
        for row, enrollment in enumerate(enrollments):
            self.enrollment_table.insertRow(row)
            item_ma_ghi_danh = QTableWidgetItem(str(enrollment['ma_ghi_danh']))
            self.enrollment_table.setItem(row, 0, item_ma_ghi_danh)
            self.enrollment_table.setItem(row, 1, QTableWidgetItem(enrollment['ma_sinh_vien']))
            self.enrollment_table.setItem(row, 2, QTableWidgetItem(enrollment['ma_khoa_hoc']))
            self.enrollment_table.setItem(row, 3, QTableWidgetItem(enrollment['ngay_ghi_danh']))
            # Hiển thị điểm nếu có
            diem_text = str(enrollment['diem']) if enrollment['diem'] is not None else "Chưa có"
            self.enrollment_table.setItem(row, 4, QTableWidgetItem(diem_text))
            # Lưu ID đăng ký vào item để sử dụng sau này
            if item_ma_ghi_danh is not None:
                item_ma_ghi_danh.setData(Qt.ItemDataRole.UserRole, enrollment['ma_ghi_danh'])
    
    def on_table_clicked(self):
        """Xử lý sự kiện khi người dùng chọn một dòng trong bảng."""
        selected_row = self.enrollment_table.currentRow()
        if selected_row >= 0:
            item_ma_ghi_danh = self.enrollment_table.item(selected_row, 0)
            item_ma_sinh_vien = self.enrollment_table.item(selected_row, 1)
            item_ma_khoa_hoc = self.enrollment_table.item(selected_row, 2)
            ma_ghi_danh = item_ma_ghi_danh.data(Qt.ItemDataRole.UserRole) if item_ma_ghi_danh is not None else None
            ma_sinh_vien = item_ma_sinh_vien.text() if item_ma_sinh_vien is not None else ""
            ma_khoa_hoc = item_ma_khoa_hoc.text() if item_ma_khoa_hoc is not None else ""
            # Lưu thông tin đăng ký đã chọn
            self.selected_enrollment = {
                'ma_ghi_danh': ma_ghi_danh,
                'ma_sinh_vien': ma_sinh_vien,
                'ma_khoa_hoc': ma_khoa_hoc
            }
            # Hiển thị thông tin lên form
            self.display_enrollment(self.selected_enrollment)
    
    def display_enrollment(self, enrollment):
        """
        Hiển thị thông tin đăng ký lên form.

        Args:
            enrollment (dict): Thông tin đăng ký.
        """
        if not enrollment:
            return
        
        # Tìm và chọn sinh viên trong combo
        student_index = self.student_combo.findData(enrollment['ma_sinh_vien'])
        if student_index >= 0:
            self.student_combo.setCurrentIndex(student_index)
        # Tìm và chọn khóa học trong combo
        course_index = self.course_combo.findData(enrollment['ma_khoa_hoc'])
        if course_index >= 0:
            self.course_combo.setCurrentIndex(course_index)
        # Lấy thông tin chi tiết từ cơ sở dữ liệu
        query = """
        SELECT ngay_ghi_danh, diem
        FROM ghi_danh
        WHERE ma_ghi_danh = ?
        """
        result = self.db_manager.execute_query(query, (enrollment['ma_ghi_danh'],))
        if result:
            # Hiển thị ngày đăng ký
            if result[0]['ngay_ghi_danh']:
                try:
                    date = QDate.fromString(result[0]['ngay_ghi_danh'], "yyyy-MM-dd")
                    self.enrollment_date.setDate(date)
                except:
                    self.enrollment_date.setDate(QDate.currentDate())
            # Hiển thị điểm
            if result[0]['diem'] is not None:
                self.grade_input.setValue(result[0]['diem'])
            else:
                self.grade_input.setValue(0)
                self.grade_input.setSpecialValueText("Chưa có điểm")
    
    def enroll_student(self):
        """Đăng ký sinh viên vào khóa học."""
        if self.student_combo.currentIndex() == -1 or self.course_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sinh viên và khóa học!")
            return
        
        ma_sinh_vien = self.student_combo.currentData()
        ma_khoa_hoc = self.course_combo.currentData()
        ngay_ghi_danh = self.enrollment_date.date().toString("yyyy-MM-dd")
        # Kiểm tra xem đã đăng ký chưa
        query = "SELECT * FROM ghi_danh WHERE ma_sinh_vien = ? AND ma_khoa_hoc = ?"
        result = self.db_manager.execute_query(query, (ma_sinh_vien, ma_khoa_hoc))
        if result:
            QMessageBox.warning(self, "Lỗi", "Sinh viên này đã đăng ký khóa học này rồi!")
            return
        # Kiểm tra số lượng sinh viên đã đăng ký khóa học
        enrolled_count = self.course_controller.get_enrollment_count(ma_khoa_hoc)
        course = self.course_controller.get_course_by_id(ma_khoa_hoc)
        if enrolled_count >= course.so_luong_toi_da:
            QMessageBox.warning(self, "Lỗi", "Khóa học này đã đạt số lượng sinh viên tối đa!")
            return
        # Thêm đăng ký mới
        query = """
        INSERT INTO ghi_danh (ma_sinh_vien, ma_khoa_hoc, ngay_ghi_danh)
        VALUES (?, ?, ?)
        """
        result = self.db_manager.execute_insert(query, (ma_sinh_vien, ma_khoa_hoc, ngay_ghi_danh))
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
        
        diem = self.grade_input.value()
        if diem == 0 and self.grade_input.specialValueText() == "Chưa có điểm":
            diem = None
        query = "UPDATE ghi_danh SET diem = ? WHERE ma_ghi_danh = ?"
        rows_affected = self.db_manager.execute_update(query, (diem, self.selected_enrollment['ma_ghi_danh']))
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
            query = "DELETE FROM ghi_danh WHERE ma_ghi_danh = ?"
            rows_affected = self.db_manager.execute_delete(query, (self.selected_enrollment['ma_ghi_danh'],))
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
        SELECT e.ma_ghi_danh, e.ma_sinh_vien, s.ho_ten, e.ma_khoa_hoc, c.ten_khoa_hoc, e.ngay_ghi_danh, e.diem
        FROM ghi_danh e
        JOIN sinh_vien s ON e.ma_sinh_vien = s.ma_sinh_vien
        JOIN khoa_hoc c ON e.ma_khoa_hoc = c.ma_khoa_hoc
        WHERE e.ma_sinh_vien LIKE ? OR s.ho_ten LIKE ? OR e.ma_khoa_hoc LIKE ? OR c.ten_khoa_hoc LIKE ?
        ORDER BY e.ma_sinh_vien, e.ma_khoa_hoc
        """
        enrollments = self.db_manager.execute_query(query, (keyword, keyword, keyword, keyword))
        self.populate_table(enrollments)
        if not enrollments:
            QMessageBox.information(self, "Kết quả tìm kiếm", "Không tìm thấy kết quả nào!")
    
    def populate_enrollment_table(self, enrollments):
        """
        Điền dữ liệu đăng ký vào bảng.

        Args:
            enrollments (list): Danh sách các đăng ký.
        """
        # Tắt việc cập nhật giao diện để tăng hiệu suất
        self.enrollment_table.setUpdatesEnabled(False)
        self.enrollment_table.setSortingEnabled(False)
        
        # Lưu vị trí cuộn hiện tại
        scrollbar = self.enrollment_table.verticalScrollBar()
        scroll_position = 0
        if scrollbar is not None:
            scroll_position = scrollbar.value()
        
        # Xóa tất cả các dòng
        self.enrollment_table.setRowCount(0)
        
        # Đặt số dòng mới
        if enrollments:
            self.enrollment_table.setRowCount(len(enrollments))
            
            for row, enrollment in enumerate(enrollments):
                # ID đăng ký
                id_item = QTableWidgetItem(str(enrollment.enrollment_id))
                
                # Mã sinh viên (có thể lấy tên sinh viên nếu có)
                student_id_item = QTableWidgetItem(enrollment.student_id)
                if hasattr(enrollment, 'student_name'):
                    student_id_item.setToolTip(enrollment.student_name)
                
                # Mã khóa học (có thể lấy tên khóa học nếu có)
                course_id_item = QTableWidgetItem(enrollment.course_id)
                if hasattr(enrollment, 'course_name'):
                    course_id_item.setToolTip(enrollment.course_name)
                
                # Ngày đăng ký
                date_item = QTableWidgetItem(enrollment.enrollment_date)
                
                # Điểm số
                grade = enrollment.grade if enrollment.grade is not None else ''
                grade_item = QTableWidgetItem(str(grade))
                
                # Thiết lập màu nền cho điểm theo thang điểm
                if enrollment.grade is not None:
                    if enrollment.grade >= 8.5:
                        grade_item.setBackground(QColor(120, 230, 120))  # A: Xanh lá đậm
                    elif enrollment.grade >= 7.0:
                        grade_item.setBackground(QColor(170, 240, 170))  # B: Xanh lá nhạt
                    elif enrollment.grade >= 5.5:
                        grade_item.setBackground(QColor(255, 255, 150))  # C: Vàng nhạt
                    elif enrollment.grade >= 4.0:
                        grade_item.setBackground(QColor(255, 200, 150))  # D: Cam nhạt
                    else:
                        grade_item.setBackground(QColor(255, 180, 180))  # F: Đỏ nhạt
                
                # Đặt các item vào bảng
                self.enrollment_table.setItem(row, 0, id_item)
                self.enrollment_table.setItem(row, 1, student_id_item)
                self.enrollment_table.setItem(row, 2, course_id_item)
                self.enrollment_table.setItem(row, 3, date_item)
                self.enrollment_table.setItem(row, 4, grade_item)
        
        # Khôi phục tính năng cập nhật giao diện và vị trí cuộn
        self.enrollment_table.setSortingEnabled(True)
        self.enrollment_table.setUpdatesEnabled(True)
        if scrollbar is not None:
            scrollbar.setValue(scroll_position)
        
        # Cập nhật tổng số đăng ký
        self.update_enrollment_count()
    
    def update_enrollment_count(self):
        """Cập nhật tổng số đăng ký hiển thị."""
        count = self.enrollment_table.rowCount()
        self.enrollment_count_label.setText(f"Tổng số đăng ký: {count}")
