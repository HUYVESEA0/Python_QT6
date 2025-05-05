from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QComboBox, QPushButton, 
                           QDialogButtonBox, QGroupBox, QDateEdit, 
                           QCheckBox, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QDate

class AdvancedStudentSearchDialog(QDialog):
    """
    Dialog tìm kiếm sinh viên nâng cao.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tìm kiếm nâng cao")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện dialog."""
        main_layout = QVBoxLayout()
        
        # Nhóm tìm kiếm thông tin cơ bản
        basic_group = QGroupBox("Thông tin cơ bản")
        form_layout = QFormLayout()
        
        # Mã sinh viên
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Nhập mã sinh viên...")
        form_layout.addRow("Mã sinh viên:", self.id_input)
        
        # Họ tên
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập tên sinh viên...")
        form_layout.addRow("Họ tên:", self.name_input)
        
        # Ngày sinh
        date_layout = QHBoxLayout()
        self.use_dob = QCheckBox("Tìm theo ngày sinh")
        date_layout.addWidget(self.use_dob)
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate(2000, 1, 1))
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Từ:"))
        date_range_layout.addWidget(self.from_date)
        date_range_layout.addWidget(QLabel("Đến:"))
        date_range_layout.addWidget(self.to_date)
        
        date_layout.addLayout(date_range_layout)
        form_layout.addRow("Ngày sinh:", date_layout)
        
        # Giới tính
        self.gender_combo = QComboBox()
        self.gender_combo.addItem("Tất cả", "")
        self.gender_combo.addItem("Nam", "Nam")
        self.gender_combo.addItem("Nữ", "Nữ")
        self.gender_combo.addItem("Khác", "Khác")
        form_layout.addRow("Giới tính:", self.gender_combo)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email...")
        form_layout.addRow("Email:", self.email_input)
        
        basic_group.setLayout(form_layout)
        main_layout.addWidget(basic_group)
        
        # Nhóm tìm kiếm thông tin bổ sung
        additional_group = QGroupBox("Thông tin bổ sung")
        add_form = QFormLayout()
        
        # Số điện thoại
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại...")
        add_form.addRow("Số điện thoại:", self.phone_input)
        
        # Địa chỉ
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ...")
        add_form.addRow("Địa chỉ:", self.address_input)
        
        # Ngày nhập học
        enroll_layout = QHBoxLayout()
        self.use_enroll = QCheckBox("Tìm theo ngày nhập học")
        enroll_layout.addWidget(self.use_enroll)
        
        self.enroll_from = QDateEdit()
        self.enroll_from.setCalendarPopup(True)
        self.enroll_from.setDate(QDate(2020, 1, 1))
        
        self.enroll_to = QDateEdit()
        self.enroll_to.setCalendarPopup(True)
        self.enroll_to.setDate(QDate.currentDate())
        
        enroll_range_layout = QHBoxLayout()
        enroll_range_layout.addWidget(QLabel("Từ:"))
        enroll_range_layout.addWidget(self.enroll_from)
        enroll_range_layout.addWidget(QLabel("Đến:"))
        enroll_range_layout.addWidget(self.enroll_to)
        
        enroll_layout.addLayout(enroll_range_layout)
        add_form.addRow("Ngày nhập học:", enroll_layout)
        
        # Trạng thái
        self.status_combo = QComboBox()
        self.status_combo.addItem("Tất cả", "")
        self.status_combo.addItem("Đang học", "Đang học")
        self.status_combo.addItem("Tạm nghỉ", "Tạm nghỉ")
        self.status_combo.addItem("Đã tốt nghiệp", "Đã tốt nghiệp")
        self.status_combo.addItem("Đã thôi học", "Đã thôi học")
        add_form.addRow("Trạng thái:", self.status_combo)
        
        additional_group.setLayout(add_form)
        main_layout.addWidget(additional_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.search_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.search_button.setText("Tìm kiếm")
        
        clear_button = QPushButton("Xóa bộ lọc")
        clear_button.clicked.connect(self.clear_filters)
        button_box.addButton(clear_button, QDialogButtonBox.ButtonRole.ResetRole)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(button_box)
        
        # Kích hoạt/vô hiệu hóa các trường ngày tháng
        self.use_dob.toggled.connect(self.toggle_dob_fields)
        self.use_enroll.toggled.connect(self.toggle_enroll_fields)
        
        # Mặc định là vô hiệu hóa các trường ngày tháng
        self.toggle_dob_fields(False)
        self.toggle_enroll_fields(False)
        
        self.setLayout(main_layout)
    
    def toggle_dob_fields(self, enabled):
        """Bật/tắt các trường ngày sinh."""
        self.from_date.setEnabled(enabled)
        self.to_date.setEnabled(enabled)
    
    def toggle_enroll_fields(self, enabled):
        """Bật/tắt các trường ngày nhập học."""
        self.enroll_from.setEnabled(enabled)
        self.enroll_to.setEnabled(enabled)
    
    def clear_filters(self):
        """Xóa tất cả bộ lọc."""
        self.id_input.clear()
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        
        self.use_dob.setChecked(False)
        self.use_enroll.setChecked(False)
        
        self.gender_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
    
    def validate_dates(self):
        """Kiểm tra ngày tháng hợp lệ."""
        if self.use_dob.isChecked() and self.from_date.date() > self.to_date.date():
            QMessageBox.warning(self, "Lỗi", "Ngày sinh 'Từ ngày' phải nhỏ hơn hoặc bằng 'Đến ngày'!")
            return False
        
        if self.use_enroll.isChecked() and self.enroll_from.date() > self.enroll_to.date():
            QMessageBox.warning(self, "Lỗi", "Ngày nhập học 'Từ ngày' phải nhỏ hơn hoặc bằng 'Đến ngày'!")
            return False
        
        return True
    
    def accept(self):
        """Xử lý khi nhấn nút OK."""
        if self.validate_dates():
            super().accept()
    
    def get_filters(self):
        """
        Lấy các bộ lọc từ dialog.

        Returns:
            dict: Các bộ lọc tìm kiếm.
        """
        filters = {}
        
        # Lấy giá trị từ các trường nhập liệu
        if self.id_input.text().strip():
            filters['student_id'] = self.id_input.text().strip()
        
        if self.name_input.text().strip():
            filters['name'] = self.name_input.text().strip()
        
        if self.email_input.text().strip():
            filters['email'] = self.email_input.text().strip()
        
        if self.phone_input.text().strip():
            filters['phone'] = self.phone_input.text().strip()
        
        if self.address_input.text().strip():
            filters['address'] = self.address_input.text().strip()
        
        # Giới tính
        if self.gender_combo.currentData():
            filters['gender'] = self.gender_combo.currentData()
        
        # Trạng thái
        if self.status_combo.currentData():
            filters['status'] = self.status_combo.currentData()
        
        # Ngày sinh
        if self.use_dob.isChecked():
            filters['dob_from'] = self.from_date.date().toString("yyyy-MM-dd")
            filters['dob_to'] = self.to_date.date().toString("yyyy-MM-dd")
        
        # Ngày nhập học
        if self.use_enroll.isChecked():
            filters['enroll_from'] = self.enroll_from.date().toString("yyyy-MM-dd")
            filters['enroll_to'] = self.enroll_to.date().toString("yyyy-MM-dd")
        
        return filters
