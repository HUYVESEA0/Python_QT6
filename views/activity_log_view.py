from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QTableWidgetItem, QHeaderView, QComboBox, QLabel,
                           QPushButton, QDateEdit, QLineEdit, QGroupBox,
                           QCheckBox, QMessageBox, QMenu)
from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtGui import QColor, QIcon
import logging
import os
from datetime import datetime, timedelta
from utils.export_manager import ExportManager

class ActivityLogView(QWidget):
    """
    Giao diện hiển thị nhật ký hoạt động của hệ thống
    """
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện người dùng"""
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Nhật ký hoạt động hệ thống")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Nút xuất dữ liệu
        self.export_button = QPushButton("Xuất dữ liệu")
        self.export_button.setIcon(QIcon("resources/icons/export.png") if os.path.exists("resources/icons/export.png") else QIcon())
        self.export_button.clicked.connect(self.export_data)
        header_layout.addWidget(self.export_button)
        
        main_layout.addLayout(header_layout)
        
        # Tạo bộ lọc
        filter_box = QGroupBox("Tùy chọn lọc")
        filter_layout = QHBoxLayout()
        
        # Thời gian
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))  # Mặc định là 30 ngày trước
        filter_layout.addWidget(QLabel("Từ:"))
        filter_layout.addWidget(self.date_from)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())  # Mặc định là hiện tại
        filter_layout.addWidget(QLabel("Đến:"))
        filter_layout.addWidget(self.date_to)
        
        # Loại hoạt động
        filter_layout.addWidget(QLabel("Loại:"))
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItem("Tất cả", "")
        self.action_type_combo.addItem("Đăng nhập", "LOGIN")
        self.action_type_combo.addItem("Đăng xuất", "LOGOUT")
        self.action_type_combo.addItem("Thêm", "ADD")
        self.action_type_combo.addItem("Cập nhật", "UPDATE")
        self.action_type_combo.addItem("Xóa", "DELETE")
        self.action_type_combo.addItem("Xuất dữ liệu", "EXPORT")
        filter_layout.addWidget(self.action_type_combo)
        
        # Đối tượng tác động
        filter_layout.addWidget(QLabel("Đối tượng:"))
        self.entity_type_combo = QComboBox()
        self.entity_type_combo.addItem("Tất cả", "")
        self.entity_type_combo.addItem("Sinh viên", "Student")
        self.entity_type_combo.addItem("Khóa học", "Course")
        self.entity_type_combo.addItem("Đăng ký", "Enrollment")
        self.entity_type_combo.addItem("Người dùng", "User")
        filter_layout.addWidget(self.entity_type_combo)
        
        # Từ khóa tìm kiếm
        filter_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa...")
        filter_layout.addWidget(self.search_input)
        
        # Nút áp dụng
        self.apply_filter_button = QPushButton("Áp dụng")
        self.apply_filter_button.clicked.connect(self.load_activities)
        filter_layout.addWidget(self.apply_filter_button)
        
        filter_box.setLayout(filter_layout)
        main_layout.addWidget(filter_box)
        
        # Tạo bảng hiển thị nhật ký
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Thời gian", "Người dùng", "Loại", "Mô tả", "Đối tượng", "Mã đối tượng"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID column
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Time column
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Type column
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Entity column
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Entity ID column
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        # Thêm các nhanh chọn
        quick_filter_layout = QHBoxLayout()
        quick_filter_layout.addWidget(QLabel("Xem nhanh:"))
        
        today_button = QPushButton("Hôm nay")
        today_button.clicked.connect(self.filter_today)
        quick_filter_layout.addWidget(today_button)
        
        yesterday_button = QPushButton("Hôm qua")
        yesterday_button.clicked.connect(self.filter_yesterday)
        quick_filter_layout.addWidget(yesterday_button)
        
        week_button = QPushButton("Tuần này")
        week_button.clicked.connect(self.filter_this_week)
        quick_filter_layout.addWidget(week_button)
        
        month_button = QPushButton("Tháng này")
        month_button.clicked.connect(self.filter_this_month)
        quick_filter_layout.addWidget(month_button)
        
        quick_filter_layout.addStretch()
        
        # Thông tin tổng số bản ghi
        self.record_count_label = QLabel("Tổng số: 0 bản ghi")
        quick_filter_layout.addWidget(self.record_count_label)
        
        main_layout.addLayout(quick_filter_layout)
        
        self.setLayout(main_layout)
        
        # Tải dữ liệu ban đầu
        self.load_activities()
    
    def load_activities(self):
        """Tải danh sách hoạt động dựa trên các bộ lọc"""
        try:
            # Hiển thị trạng thái đang tải
            old_cursor = self.cursor()
            self.setCursor(Qt.CursorShape.WaitCursor)
            
            # Chuẩn bị các điều kiện lọc
            date_from = self.date_from.date().toString("yyyy-MM-dd 00:00:00")
            date_to = self.date_to.date().toString("yyyy-MM-dd 23:59:59")
            action_type = self.action_type_combo.currentData()
            entity_type = self.entity_type_combo.currentData()
            search_keyword = self.search_input.text().strip()
            
            conditions = ["timestamp BETWEEN ? AND ?"]
            params = [date_from, date_to]
            
            if action_type:
                conditions.append("action_type = ?")
                params.append(action_type)
            
            if entity_type:
                conditions.append("entity_type = ?")
                params.append(entity_type)
            
            if search_keyword:
                conditions.append("(action_description LIKE ? OR username LIKE ? OR entity_id LIKE ?)")
                keyword = f"%{search_keyword}%"
                params.extend([keyword, keyword, keyword])
            
            # Sử dụng phương thức get_activities cải tiến
            activities = self.db_manager.get_activities(conditions, params)
            
            # Cập nhật giao diện
            self.populate_table(activities)
            
            # Cập nhật số lượng bản ghi
            self.record_count_label.setText(f"Số lượng bản ghi: {len(activities)}")
            
            # Khôi phục con trỏ
            self.setCursor(old_cursor)
            
        except Exception as e:
            logging.error(f"Lỗi khi tải nhật ký hoạt động: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể tải nhật ký hoạt động: {str(e)}")
            self.setCursor(old_cursor)
    
    def populate_table(self, activities):
        """Điền dữ liệu hoạt động vào bảng"""
        try:
            # Lưu vị trí cuộn hiện tại
            scrollbar = self.table.verticalScrollBar()
            scroll_position = scrollbar.value()
            
            # Tắt cập nhật giao diện và sắp xếp để tăng hiệu suất
            self.table.setUpdatesEnabled(False)
            self.table.setSortingEnabled(False)
            
            # Xóa dữ liệu cũ và đặt số dòng mới
            self.table.setRowCount(0)
            
            if not activities:
                # Hiển thị thông báo khi không có dữ liệu
                self.table.setRowCount(1)
                no_data_item = QTableWidgetItem("Không có hoạt động nào")
                no_data_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(0, 0, no_data_item)
                self.table.setSpan(0, 0, 1, 7)  # Merge tất cả các cột
                
                # Khôi phục cập nhật giao diện
                self.table.setUpdatesEnabled(True)
                return
                
            # Thêm dữ liệu mới
            for row_idx, activity in enumerate(activities):
                self.table.insertRow(row_idx)
                
                # Định dạng thời gian
                timestamp = QDateTime.fromString(activity['timestamp'], "yyyy-MM-dd hh:mm:ss")
                formatted_time = timestamp.toString("dd/MM/yyyy hh:mm:ss")
                
                # Tạo và thêm các item vào bảng
                # Fix: Use 'log_id' instead of 'id' to match the database query
                id_item = QTableWidgetItem(str(activity['log_id']))
                time_item = QTableWidgetItem(formatted_time)
                username_item = QTableWidgetItem(activity['username'] if activity['username'] else "Unknown")
                action_item = QTableWidgetItem(activity['action_type'])
                desc_item = QTableWidgetItem(activity['action_description'] if activity['action_description'] else "")
                entity_item = QTableWidgetItem(activity['entity_type'] if activity['entity_type'] else "")
                entity_id_item = QTableWidgetItem(activity['entity_id'] if activity['entity_id'] else "")
                
                # Căn chỉnh cột thời gian và ID ở giữa
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                entity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                entity_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Đặt màu nền dựa trên loại hành động
                if activity['action_type'] == 'DELETE':
                    action_item.setBackground(QColor(255, 200, 200))
                elif activity['action_type'] == 'ADD':
                    action_item.setBackground(QColor(200, 255, 200))
                elif activity['action_type'] == 'UPDATE':
                    action_item.setBackground(QColor(200, 200, 255))
                
                # Thêm các item vào bảng
                self.table.setItem(row_idx, 0, id_item)
                self.table.setItem(row_idx, 1, time_item)
                self.table.setItem(row_idx, 2, username_item)
                self.table.setItem(row_idx, 3, action_item)
                self.table.setItem(row_idx, 4, desc_item)
                self.table.setItem(row_idx, 5, entity_item)
                self.table.setItem(row_idx, 6, entity_id_item)
            
            # Khôi phục cập nhật giao diện và sắp xếp
            self.table.setUpdatesEnabled(True)
            self.table.setSortingEnabled(True)
            
            # Khôi phục vị trí cuộn
            scrollbar.setValue(scroll_position)
            
        except Exception as e:
            logging.error(f"Lỗi khi điền dữ liệu vào bảng hoạt động: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị dữ liệu hoạt động: {str(e)}")
    
    def export_data(self):
        """Xuất dữ liệu ra các định dạng"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất!")
            return
        
        # Hiển thị menu xuất dữ liệu
        export_menu = QMenu(self)
        export_excel_action = export_menu.addAction("Xuất ra Excel")
        export_pdf_action = export_menu.addAction("Xuất ra PDF")
        
        action = export_menu.exec(self.export_button.mapToGlobal(
            self.export_button.rect().bottomRight()
        ))
        
        if not action:
            return
        
        # Chuẩn bị dữ liệu
        headers = []
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text())
        
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        if action == export_excel_action:
            ExportManager.export_to_excel(
                data, 
                headers, 
                parent=self, 
                default_filename="nhat_ky_hoat_dong.xlsx"
            )
        elif action == export_pdf_action:
            ExportManager.export_to_pdf(
                data, 
                headers, 
                title="Nhật ký hoạt động hệ thống", 
                parent=self, 
                default_filename="nhat_ky_hoat_dong.pdf"
            )
    
    def filter_today(self):
        """Lọc hoạt động của ngày hôm nay"""
        today = QDate.currentDate()
        self.date_from.setDate(today)
        self.date_to.setDate(today)
        self.load_activities()
    
    def filter_yesterday(self):
        """Lọc hoạt động của ngày hôm qua"""
        yesterday = QDate.currentDate().addDays(-1)
        self.date_from.setDate(yesterday)
        self.date_to.setDate(yesterday)
        self.load_activities()
    
    def filter_this_week(self):
        """Lọc hoạt động của tuần này"""
        today = QDate.currentDate()
        # Tính ngày đầu tuần (Thứ Hai)
        days_to_monday = today.dayOfWeek() - 1  # Trong Qt, Thứ Hai là 1
        start_of_week = today.addDays(-days_to_monday)
        
        self.date_from.setDate(start_of_week)
        self.date_to.setDate(today)
        self.load_activities()
    
    def filter_this_month(self):
        """Lọc hoạt động của tháng này"""
        today = QDate.currentDate()
        start_of_month = QDate(today.year(), today.month(), 1)
        
        self.date_from.setDate(start_of_month)
        self.date_to.setDate(today)
        self.load_activities()
