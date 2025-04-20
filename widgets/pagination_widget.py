from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
import os

class PaginationWidget(QWidget):
    """
    Widget hiển thị điều khiển phân trang cho bảng dữ liệu lớn
    """
    # Signal phát ra khi thay đổi trang hoặc số lượng mục trên trang
    pageChanged = pyqtSignal(int)  # Trang hiện tại
    pageSizeChanged = pyqtSignal(int)  # Số mục trên mỗi trang
    
    def __init__(self, total_items=0, items_per_page=20, current_page=1, parent=None):
        """
        Khởi tạo widget phân trang
        
        Args:
            total_items (int): Tổng số mục
            items_per_page (int): Số mục trên mỗi trang
            current_page (int): Trang hiện tại
            parent (QWidget): Widget cha
        """
        super().__init__(parent)
        self.total_items = total_items
        self.items_per_page = items_per_page
        self.current_page = current_page
        
        self.setup_ui()
        self.update_labels()
    
    def setup_ui(self):
        """Thiết lập giao diện cho widget phân trang"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Thông tin về tổng số mục và số trang
        self.info_label = QLabel()
        layout.addWidget(self.info_label)
        
        # Spacer để đẩy các nút sang phải
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Combobox chọn số mục trên trang
        layout.addWidget(QLabel("Hiển thị:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50", "100", "Tất cả"])
        
        # Thiết lập giá trị mặc định
        default_index = 1  # Mặc định là 20
        if self.items_per_page == 10:
            default_index = 0
        elif self.items_per_page == 50:
            default_index = 2
        elif self.items_per_page == 100:
            default_index = 3
        elif self.items_per_page == -1:  # Tất cả
            default_index = 4
        self.page_size_combo.setCurrentIndex(default_index)
        
        self.page_size_combo.currentIndexChanged.connect(self.on_page_size_changed)
        layout.addWidget(self.page_size_combo)
        
        # Điều hướng trang
        self.first_page_btn = QPushButton()
        self.first_page_btn.setIcon(QIcon("resources/icons/first_page.png") if os.path.exists("resources/icons/first_page.png") else QIcon())
        self.first_page_btn.setToolTip("Trang đầu")
        self.first_page_btn.clicked.connect(self.go_to_first_page)
        layout.addWidget(self.first_page_btn)
        
        self.prev_page_btn = QPushButton()
        self.prev_page_btn.setIcon(QIcon("resources/icons/prev_page.png") if os.path.exists("resources/icons/prev_page.png") else QIcon())
        self.prev_page_btn.setToolTip("Trang trước")
        self.prev_page_btn.clicked.connect(self.go_to_prev_page)
        layout.addWidget(self.prev_page_btn)
        
        # Hiển thị trang hiện tại
        self.page_label = QLabel()
        layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton()
        self.next_page_btn.setIcon(QIcon("resources/icons/next_page.png") if os.path.exists("resources/icons/next_page.png") else QIcon())
        self.next_page_btn.setToolTip("Trang tiếp theo")
        self.next_page_btn.clicked.connect(self.go_to_next_page)
        layout.addWidget(self.next_page_btn)
        
        self.last_page_btn = QPushButton()
        self.last_page_btn.setIcon(QIcon("resources/icons/last_page.png") if os.path.exists("resources/icons/last_page.png") else QIcon())
        self.last_page_btn.setToolTip("Trang cuối")
        self.last_page_btn.clicked.connect(self.go_to_last_page)
        layout.addWidget(self.last_page_btn)
    
    def update_labels(self):
        """Cập nhật các nhãn hiển thị thông tin phân trang"""
        # Tính toán tổng số trang
        if self.items_per_page <= 0:
            total_pages = 1
        else:
            total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        
        # Đảm bảo trang hiện tại nằm trong phạm vi hợp lệ
        self.current_page = max(1, min(self.current_page, total_pages))
        
        # Tính toán phạm vi hiển thị hiện tại
        if self.items_per_page <= 0 or self.total_items == 0:
            range_start = 0
            range_end = self.total_items
        else:
            range_start = (self.current_page - 1) * self.items_per_page + 1
            range_end = min(range_start + self.items_per_page - 1, self.total_items)
        
        # Cập nhật nhãn thông tin
        if self.total_items == 0:
            self.info_label.setText("Không có mục nào")
            self.page_label.setText("0/0")
        else:
            self.info_label.setText(f"Hiển thị {range_start}-{range_end} trên {self.total_items}")
            self.page_label.setText(f"{self.current_page}/{total_pages}")
        
        # Cập nhật trạng thái nút điều hướng
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)
        self.last_page_btn.setEnabled(self.current_page < total_pages)
    
    def update_total_items(self, total_items):
        """
        Cập nhật tổng số mục và làm mới hiển thị
        
        Args:
            total_items (int): Tổng số mục mới
        """
        self.total_items = total_items
        self.update_labels()
    
    def go_to_first_page(self):
        """Chuyển đến trang đầu tiên"""
        if self.current_page != 1:
            self.current_page = 1
            self.update_labels()
            self.pageChanged.emit(self.current_page)
    
    def go_to_prev_page(self):
        """Chuyển đến trang trước"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_labels()
            self.pageChanged.emit(self.current_page)
    
    def go_to_next_page(self):
        """Chuyển đến trang tiếp theo"""
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page) if self.items_per_page > 0 else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_labels()
            self.pageChanged.emit(self.current_page)
    
    def go_to_last_page(self):
        """Chuyển đến trang cuối cùng"""
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page) if self.items_per_page > 0 else 1
        if self.current_page != total_pages:
            self.current_page = total_pages
            self.update_labels()
            self.pageChanged.emit(self.current_page)
    
    def on_page_size_changed(self, index):
        """Xử lý khi thay đổi số mục trên trang"""
        # Chuyển đổi index sang số mục trên trang
        items_per_page_map = {0: 10, 1: 20, 2: 50, 3: 100, 4: -1}  # -1 nghĩa là tất cả
        self.items_per_page = items_per_page_map.get(index, 20)
        
        # Reset trang về 1 khi thay đổi số mục trên trang
        self.current_page = 1
        
        self.update_labels()
        self.pageSizeChanged.emit(self.items_per_page)
