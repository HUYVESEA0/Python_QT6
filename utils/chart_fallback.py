"""
Module thay thế cho matplotlib khi không có thư viện này
"""
import logging
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Giả lập các tính năng cơ bản của pyplot
class FallbackChart:
    """
    Cung cấp các phương thức thay thế cơ bản cho matplotlib
    """
    def __init__(self):
        self.title = "Chart (Matplotlib not available)"
        self.data = {}
    
    def set_title(self, title):
        self.title = title
    
    def add_data(self, label, value):
        self.data[label] = value
    
    def get_widget(self):
        """
        Tạo widget hiển thị dữ liệu dạng văn bản thay cho biểu đồ
        
        Returns:
            QWidget: Widget hiển thị dữ liệu
        """
        widget = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Thông báo về thư viện thiếu
        msg = QLabel("Matplotlib không khả dụng. Cài đặt thư viện để xem biểu đồ.")
        msg.setStyleSheet("color: #FF5722; margin-bottom: 10px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)
        
        # Hiển thị dữ liệu dạng văn bản
        data_widget = QWidget()
        data_layout = QVBoxLayout()
        
        for label, value in self.data.items():
            data_label = QLabel(f"{label}: {value}")
            data_label.setStyleSheet("padding: 5px;")
            data_layout.addWidget(data_label)
        
        data_widget.setLayout(data_layout)
        data_widget.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; padding: 10px;")
        layout.addWidget(data_widget)
        
        widget.setLayout(layout)
        return widget

# Hàm tương thích với matplotlib.pyplot
def figure(figsize=None, **kwargs):
    logging.warning("Sử dụng chart_fallback thay cho matplotlib")
    return FallbackChart()

# Giả lập các hàm thông dụng của pyplot
def title(text, **kwargs):
    pass

def pie(data, **kwargs):
    pass

def bar(x, height, **kwargs):
    pass

def savefig(path, **kwargs):
    logging.warning(f"Không thể lưu biểu đồ khi không có matplotlib: {path}")

def close():
    pass
