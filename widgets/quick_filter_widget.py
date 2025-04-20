from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QComboBox, QToolButton, QMenu)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QAction
import os

class QuickFilterWidget(QWidget):
    """
    Widget bộ lọc nhanh cho bảng dữ liệu
    """
    # Signal phát ra khi thay đổi bộ lọc
    filterChanged = pyqtSignal(dict)
    
    def __init__(self, filter_fields=None, parent=None):
        """
        Khởi tạo widget bộ lọc
        
        Args:
            filter_fields (dict): Dictionary chứa cấu hình các trường lọc
                                  {field_name: {"label": str, "type": str, "options": list}}
            parent (QWidget): Widget cha
        """
        super().__init__(parent)
        self.filter_fields = filter_fields or {}
        self.current_filters = {}
        self.filter_widgets = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện cho widget bộ lọc nhanh"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Thêm tiêu đề
        filter_label = QLabel("Bộ lọc:")
        filter_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(filter_label)
        
        # Thêm các trường lọc dựa trên cấu hình
        for field_name, config in self.filter_fields.items():
            # Tạo label
            label = QLabel(config.get("label", field_name))
            layout.addWidget(label)
            
            # Tạo widget điều khiển phù hợp với loại trường
            field_type = config.get("type", "text")
            if field_type == "text":
                widget = QLineEdit()
                widget.setPlaceholderText(f"Nhập {config.get('label', field_name).lower()}")
                widget.textChanged.connect(lambda text, field=field_name: self.on_filter_changed(field, text))
            elif field_type == "combobox":
                widget = QComboBox()
                options = config.get("options", [])
                widget.addItem("Tất cả", "")  # Thêm lựa chọn "Tất cả"
                for option in options:
                    if isinstance(option, tuple) and len(option) == 2:
                        widget.addItem(option[0], option[1])
                    else:
                        widget.addItem(str(option), option)
                widget.currentIndexChanged.connect(
                    lambda idx, cb=widget, field=field_name: 
                    self.on_filter_changed(field, cb.currentData())
                )
            else:
                continue  # Bỏ qua nếu không hỗ trợ loại trường
            
            layout.addWidget(widget)
            self.filter_widgets[field_name] = widget
        
        # Thêm nút làm mới
        self.reset_btn = QToolButton()
        self.reset_btn.setIcon(QIcon("resources/icons/refresh.png") if os.path.exists("resources/icons/refresh.png") else QIcon())
        self.reset_btn.setToolTip("Làm mới bộ lọc")
        self.reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(self.reset_btn)
        
        # Thêm nút bộ lọc nâng cao (nếu cần)
        self.advanced_btn = QToolButton()
        self.advanced_btn.setIcon(QIcon("resources/icons/filter.png") if os.path.exists("resources/icons/filter.png") else QIcon())
        self.advanced_btn.setToolTip("Bộ lọc nâng cao")
        self.advanced_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Tạo menu bộ lọc nâng cao
        self.filter_menu = QMenu(self)
        self.setup_filter_menu()
        self.advanced_btn.setMenu(self.filter_menu)
        
        layout.addWidget(self.advanced_btn)
        
        # Thêm nút áp dụng
        self.apply_btn = QPushButton("Áp dụng")
        self.apply_btn.clicked.connect(self.apply_filters)
        layout.addWidget(self.apply_btn)
        
        # Chỉ áp dụng filters khi nhấn nút hoặc khi combobox thay đổi
        # (không áp dụng khi đang nhập text để tránh quá nhiều request)
        
    def setup_filter_menu(self):
        """Thiết lập menu bộ lọc nâng cao"""
        # Ví dụ cho một số bộ lọc phổ biến - có thể tùy chỉnh dựa trên nhu cầu cụ thể
        
        # Bộ lọc theo ngày
        date_menu = QMenu("Lọc theo ngày", self.filter_menu)
        date_menu.addAction("Hôm nay").triggered.connect(lambda: self.set_date_filter("today"))
        date_menu.addAction("7 ngày gần đây").triggered.connect(lambda: self.set_date_filter("last_7_days"))
        date_menu.addAction("30 ngày gần đây").triggered.connect(lambda: self.set_date_filter("last_30_days"))
        date_menu.addAction("Tháng này").triggered.connect(lambda: self.set_date_filter("this_month"))
        date_menu.addAction("Năm nay").triggered.connect(lambda: self.set_date_filter("this_year"))
        self.filter_menu.addMenu(date_menu)
        
        # Các lựa chọn lọc khác
        self.filter_menu.addSeparator()
        self.filter_menu.addAction("Tùy chỉnh...").triggered.connect(self.show_advanced_filter_dialog)
    
    def on_filter_changed(self, field_name, value):
        """
        Xử lý khi giá trị của một trường lọc thay đổi
        
        Args:
            field_name (str): Tên trường
            value: Giá trị mới
        """
        # Cập nhật giá trị bộ lọc hiện tại
        if value:
            self.current_filters[field_name] = value
        elif field_name in self.current_filters:
            del self.current_filters[field_name]
    
    def apply_filters(self):
        """Áp dụng bộ lọc hiện tại"""
        # Phát tín hiệu với bộ lọc hiện tại
        self.filterChanged.emit(dict(self.current_filters))
    
    def reset_filters(self):
        """Đặt lại tất cả các bộ lọc về giá trị mặc định"""
        # Đặt lại giá trị các widget
        for field_name, widget in self.filter_widgets.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)  # Chọn "Tất cả"
        
        # Xóa các bộ lọc hiện tại
        self.current_filters.clear()
        
        # Phát tín hiệu với bộ lọc trống
        self.filterChanged.emit({})
    
    def set_date_filter(self, filter_type):
        """
        Thiết lập bộ lọc theo ngày
        
        Args:
            filter_type (str): Loại bộ lọc ngày
        """
        # Cập nhật bộ lọc ngày
        self.current_filters["date_filter"] = filter_type
        
        # Phát tín hiệu với bộ lọc hiện tại
        self.filterChanged.emit(dict(self.current_filters))
    
    def show_advanced_filter_dialog(self):
        """Hiển thị hộp thoại bộ lọc nâng cao"""
        # Trong triển khai thực tế, bạn có thể mở một dialog phức tạp hơn ở đây
        pass
