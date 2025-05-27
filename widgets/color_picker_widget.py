from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QColorDialog, QFrame, QSlider, QGroupBox, QGridLayout)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QBrush

class ColorSwatch(QFrame):
    """Widget hiển thị mẫu màu"""
    colorClicked = pyqtSignal(QColor)
    
    def __init__(self, color=None, parent=None, size=None):
        super().__init__(parent)
        self.color = QColor(color or "#FFFFFF")
        self.selected = False
        self.hover = False
        
        if size:
            self.setFixedSize(size)
        else:
            self.setFixedSize(30, 30)
            
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(self.color.name())
        
    def setColor(self, color):
        self.color = QColor(color)
        self.setToolTip(self.color.name())
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Vẽ nền
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        
        # Vẽ hình vuông bo tròn
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 4, 4)
        
        # Vẽ viền khi được chọn hoặc hover
        if self.selected or self.hover:
            if self.selected:
                painter.setPen(Qt.GlobalColor.white if self.color.lightnessF() < 0.6 else Qt.GlobalColor.black)
            else:
                painter.setPen(Qt.GlobalColor.gray)
                
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, 4, 4)
            
    def enterEvent(self, event):
        self.hover = True
        self.update()
        
    def leaveEvent(self, event):
        self.hover = False
        self.update()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.colorClicked.emit(self.color)
            self.selected = True
            self.update()
            
    def setSelected(self, selected):
        self.selected = selected
        self.update()


class ColorPickerWidget(QWidget):
    """Widget cho phép chọn màu với các màu đề xuất"""
    colorChanged = pyqtSignal(str)  # Emit mã màu hex khi có thay đổi
    
    def __init__(self, initial_color="#007BFF", parent=None):
        super().__init__(parent)
        self.setObjectName("colorPickerWidget")
        self.current_color = QColor(initial_color)
        self.preset_colors = [
            # Material Design colors
            "#F44336", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", 
            "#2196F3", "#03A9F4", "#00BCD4", "#009688", "#4CAF50",
            "#8BC34A", "#CDDC39", "#FFEB3B", "#FFC107", "#FF9800", 
            "#FF5722", "#795548", "#9E9E9E", "#607D8B", "#000000"
        ]
        self.swatches = []
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Hiển thị màu hiện tại
        color_preview_layout = QHBoxLayout()
        
        self.color_preview = ColorSwatch(self.current_color, size=QSize(60, 30))
        color_preview_layout.addWidget(self.color_preview)
        
        # Nhãn hiển thị mã màu
        self.color_code_label = QLabel(self.current_color.name().upper())
        color_preview_layout.addWidget(self.color_code_label)
        
        # Nút chọn màu tùy chỉnh
        self.custom_color_btn = QPushButton("Chọn màu...")
        self.custom_color_btn.clicked.connect(self.choose_custom_color)
        color_preview_layout.addWidget(self.custom_color_btn)
        
        # Thêm vào layout chính
        main_layout.addLayout(color_preview_layout)
        
        # Grid hiển thị các màu đề xuất
        preset_group = QGroupBox("Màu đề xuất")
        preset_layout = QGridLayout(preset_group)
        preset_layout.setContentsMargins(5, 10, 5, 5)
        preset_layout.setSpacing(4)
        
        # Thêm các mẫu màu vào grid
        for i, color in enumerate(self.preset_colors):
            row, col = divmod(i, 5)
            swatch = ColorSwatch(color)
            swatch.colorClicked.connect(self.on_preset_color_clicked)
            self.swatches.append(swatch)
            preset_layout.addWidget(swatch, row, col)
            
            # Đánh dấu màu hiện tại nếu trùng với một trong các màu đề xuất
            if QColor(color) == self.current_color:
                swatch.setSelected(True)
        
        main_layout.addWidget(preset_group)
        
    def on_preset_color_clicked(self, color):
        """Xử lý khi người dùng chọn một màu đề xuất"""
        # Cập nhật màu hiện tại
        self.set_color(color.name())
        
        # Cập nhật trạng thái các swatch
        self.update_selected_swatches(color)
        
    def update_selected_swatches(self, selected_color):
        """Cập nhật trạng thái selected cho các swatch"""
        for swatch in self.swatches:
            swatch.setSelected(swatch.color.name() == selected_color.name())
    
    def choose_custom_color(self):
        """Mở hộp thoại chọn màu tùy chỉnh"""
        color = QColorDialog.getColor(
            self.current_color, self, "Chọn màu", 
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        
        if color.isValid():
            # Cập nhật màu hiện tại
            self.set_color(color.name())
            
            # Cập nhật trạng thái các swatch
            self.update_selected_swatches(color)
    
    def set_color(self, color_str):
        """Đặt màu hiện tại và phát signal"""
        self.current_color = QColor(color_str)
        self.color_preview.setColor(self.current_color)
        self.color_code_label.setText(self.current_color.name().upper())
        
        # Phát signal
        self.colorChanged.emit(self.current_color.name())
    
    def get_color(self):
        """Lấy màu hiện tại dạng hex"""
        return self.current_color.name()
