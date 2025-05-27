from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                           QPushButton, QFileDialog, QMessageBox,
                           QDialog, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize, QPoint  # Đảm bảo đã import QRect
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter, QPen, QColor, QBrush, QTransform, QAction
import os
import logging
from utils.path_helper import PathHelper
from utils.cleanup import cleanup_temp_files

class CropDialog(QDialog):
    """Dialog để cắt ảnh"""
    
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cắt ảnh")
        self.setMinimumSize(600, 500)
        self.pixmap = pixmap
        self.cropped_pixmap = None
        self.selection_rect = QRect()
        self.start_point = QPoint()
        self.current_point = QPoint()
        self.dragging = False
        
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        
        # Label hiển thị ảnh và vùng chọn
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event
        self.image_label.paintEvent = self.paint_event
        
        layout.addWidget(self.image_label)
        
        # Nút điều khiển
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Đặt lại")
        reset_button.clicked.connect(self.reset_selection)
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(self.reject)
        
        crop_button = QPushButton("Cắt ảnh")
        crop_button.clicked.connect(self.crop_image)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(crop_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def mouse_press_event(self, event):
        """Xử lý sự kiện nhấn chuột"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.start_point = event.position().toPoint()
            self.current_point = self.start_point
            self.selection_rect = QRect()
            self.image_label.update()
    
    def mouse_move_event(self, event):
        """Xử lý sự kiện di chuyển chuột"""
        if self.dragging:
            self.current_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.current_point).normalized()
            self.image_label.update()
    
    def mouse_release_event(self, event):
        """Xử lý sự kiện thả chuột"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.current_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.current_point).normalized()
            self.image_label.update()
    
    def paint_event(self, event):
        """Vẽ ảnh và vùng chọn"""
        # Vẽ ảnh gốc
        painter = QPainter(self.image_label)
        painter.drawPixmap(self.image_label.rect(), self.pixmap)
        
        # Vẽ vùng chọn
        if not self.selection_rect.isNull():
            pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
            
            # Vẽ overlay bán trong suốt
            overlay = QColor(0, 0, 0, 100)
            painter.fillRect(self.image_label.rect(), overlay)
            
            # Xóa overlay ở vùng chọn
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.selection_rect, Qt.GlobalColor.transparent)
    
    def reset_selection(self):
        """Đặt lại vùng chọn"""
        self.selection_rect = QRect()
        self.image_label.update()
    
    def crop_image(self):
        """Cắt ảnh theo vùng chọn"""
        if self.selection_rect.isNull() or self.selection_rect.width() < 10 or self.selection_rect.height() < 10:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn vùng cắt hợp lệ.")
            return
        
        # Cắt ảnh
        self.cropped_pixmap = self.pixmap.copy(self.selection_rect)
        self.accept()

class PhotoFrame(QWidget):
    """
    Widget hiển thị và quản lý ảnh đại diện
    """
    photo_changed = pyqtSignal(str)  # Signal phát ra khi thay đổi ảnh
    
    def __init__(self, parent=None, default_size=(150, 180)):
        super().__init__(parent)
        self.setObjectName("photoFrame")
        self.default_size = default_size
        self.photo_path = ""
        self.original_pixmap = None
        self.temp_files = []  # Danh sách các file tạm để quản lý tốt hơn
        self.init_ui()
    
    def init_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        
        # Label hiển thị ảnh
        self.image_label = QLabel()
        self.image_label.setFixedSize(*self.default_size)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Nút chọn ảnh và nút mới
        button_layout = QHBoxLayout()
        
        self.change_button = QPushButton("Chọn ảnh")
        self.change_button.setIcon(QIcon("resources/icons/photo.png") if os.path.exists("resources/icons/photo.png") else QIcon())
        self.change_button.clicked.connect(self.choose_photo)
        button_layout.addWidget(self.change_button)

        # Nút mới: Xem ảnh lớn
        self.view_button = QPushButton("Xem ảnh lớn")
        self.view_button.setIcon(QIcon("resources/icons/view.png") if os.path.exists("resources/icons/view.png") else QIcon())
        self.view_button.clicked.connect(self.view_large_photo)
        button_layout.addWidget(self.view_button)

        # Nút mới: Tải lại ảnh (ví dụ)
        self.reload_button = QPushButton("Tải lại ảnh")
        self.reload_button.setIcon(QIcon("resources/icons/refresh.png") if os.path.exists("resources/icons/refresh.png") else QIcon())
        self.reload_button.clicked.connect(self.reload_photo)
        button_layout.addWidget(self.reload_button)
        
        # Menu ngữ cảnh
        self.context_menu = QMenu(self)
        
        self.select_action = self.context_menu.addAction("Chọn ảnh")
        self.select_action.triggered.connect(self.choose_photo)
        
        self.crop_action = self.context_menu.addAction("Cắt ảnh")
        self.crop_action.triggered.connect(self.crop_photo)
        
        self.rotate_action = self.context_menu.addAction("Xoay ảnh")
        self.rotate_action.triggered.connect(self.rotate_photo)
        
        # Thêm menu bộ lọc
        self.filter_menu = QMenu("Bộ lọc", self.context_menu)
        
        self.grayscale_action = self.filter_menu.addAction("Đen trắng")
        self.grayscale_action.triggered.connect(lambda: self.apply_filter("grayscale"))
        
        self.sepia_action = self.filter_menu.addAction("Sepia")
        self.sepia_action.triggered.connect(lambda: self.apply_filter("sepia"))
        
        self.context_menu.addMenu(self.filter_menu)
        
        self.remove_action = self.context_menu.addAction("Xóa ảnh")
        self.remove_action.triggered.connect(self.remove_photo)
        
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addLayout(button_layout)
        
        # Hiển thị ảnh mặc định
        self.set_default_photo()
        
        # Vô hiệu hóa các action không áp dụng được với ảnh mặc định
        self.crop_action.setEnabled(False)
        self.rotate_action.setEnabled(False)
        self.filter_menu.setEnabled(False)  # Thêm dòng này
        
        self.setLayout(layout)
    
    def set_photo(self, photo_path):
        """
        Đặt ảnh cho frame
        
        Args:
            photo_path (str): Đường dẫn đến file ảnh
        """
        if not photo_path or not os.path.exists(photo_path) or photo_path.endswith("default_avatar.png"):
            self.set_default_photo()
            return
        
        try:
            # Tải ảnh
            self.original_pixmap = QPixmap(photo_path)
            
            # Kiểm tra và resize ảnh nếu quá lớn
            if max(self.original_pixmap.width(), self.original_pixmap.height()) > 1000:
                # Tạo đường dẫn tạm thời cho ảnh đã resize
                temp_dir = PathHelper.get_resource_path("temp")
                PathHelper.ensure_dir(temp_dir)
                
                temp_path = os.path.join(temp_dir, f"resized_{os.path.basename(photo_path)}")
                
                # Resize và lưu ảnh
                scaled_pixmap = self.original_pixmap.scaled(
                    1000, 1000, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled_pixmap.save(temp_path)
                
                # Sử dụng ảnh đã resize
                self.original_pixmap = QPixmap(temp_path)
                photo_path = temp_path
                self.temp_files.append(temp_path)
            
            # Scale ảnh cho vừa với frame
            scaled_pixmap = self.original_pixmap.scaled(
                *self.default_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            self.photo_path = photo_path
            self.photo_changed.emit(photo_path)
            
            # Bật các action cắt và xoay ảnh
            self.crop_action.setEnabled(True)
            self.rotate_action.setEnabled(True)
            self.filter_menu.setEnabled(True)  # Thêm dòng này nếu có action filter
            
        except Exception as e:
            logging.error(f"Lỗi khi đặt ảnh: {str(e)}")
            self.set_default_photo()
            QMessageBox.warning(self, "Lỗi", f"Không thể tải ảnh: {str(e)}")
    
    def init_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        
        # Label hiển thị ảnh
        self.image_label = QLabel()
        self.image_label.setFixedSize(*self.default_size)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Nút chọn ảnh và nút mới
        button_layout = QHBoxLayout()
        
        self.change_button = QPushButton("Chọn ảnh")
        self.change_button.setIcon(QIcon("resources/icons/photo.png") if os.path.exists("resources/icons/photo.png") else QIcon())
        self.change_button.clicked.connect(self.choose_photo)
        button_layout.addWidget(self.change_button)

        # Nút mới: Xem ảnh lớn
        self.view_button = QPushButton("Xem ảnh lớn")
        self.view_button.setIcon(QIcon("resources/icons/view.png") if os.path.exists("resources/icons/view.png") else QIcon())
        self.view_button.clicked.connect(self.view_large_photo)
        button_layout.addWidget(self.view_button)

        # Nút mới: Tải lại ảnh (ví dụ)
        self.reload_button = QPushButton("Tải lại ảnh")
        self.reload_button.setIcon(QIcon("resources/icons/refresh.png") if os.path.exists("resources/icons/refresh.png") else QIcon())
        self.reload_button.clicked.connect(self.reload_photo)
        button_layout.addWidget(self.reload_button)
        
        # Menu ngữ cảnh
        self.context_menu = QMenu(self)
        
        self.select_action = self.context_menu.addAction("Chọn ảnh")
        self.select_action.triggered.connect(self.choose_photo)
        
        self.crop_action = self.context_menu.addAction("Cắt ảnh")
        self.crop_action.triggered.connect(self.crop_photo)
        
        self.rotate_action = self.context_menu.addAction("Xoay ảnh")
        self.rotate_action.triggered.connect(self.rotate_photo)
        
        # Thêm menu bộ lọc
        self.filter_menu = QMenu("Bộ lọc", self.context_menu)
        
        self.grayscale_action = self.filter_menu.addAction("Đen trắng")
        self.grayscale_action.triggered.connect(lambda: self.apply_filter("grayscale"))
        
        self.sepia_action = self.filter_menu.addAction("Sepia")
        self.sepia_action.triggered.connect(lambda: self.apply_filter("sepia"))
        
        self.context_menu.addMenu(self.filter_menu)
        
        self.remove_action = self.context_menu.addAction("Xóa ảnh")
        self.remove_action.triggered.connect(self.remove_photo)
        
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addLayout(button_layout)
        
        # Hiển thị ảnh mặc định
        self.set_default_photo()
        
        # Vô hiệu hóa các action không áp dụng được với ảnh mặc định
        self.crop_action.setEnabled(False)
        self.rotate_action.setEnabled(False)
        self.filter_menu.setEnabled(False)  # Thêm dòng này
        
        self.setLayout(layout)
    
    def set_default_photo(self):
        """Đặt ảnh mặc định"""
        default_path = "resources/default_avatar.png"
        if os.path.exists(default_path):
            pixmap = QPixmap(default_path)
        else:
            pixmap = QPixmap(*self.default_size)
            pixmap.fill(Qt.GlobalColor.lightGray)
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor("#555555"), 2))
            center_x = self.default_size[0] // 2
            head_y = self.default_size[1] // 3
            head_radius = min(self.default_size) // 5
            painter.drawEllipse(center_x - head_radius, head_y - head_radius, 
                               head_radius * 2, head_radius * 2)
            body_top_y = head_y + head_radius + 5
            body_width = int(head_radius * 2.5)
            body_height = self.default_size[1] // 3
            painter.drawRoundedRect(
                QRect(
                    int(center_x - body_width // 2),
                    int(body_top_y),
                    int(body_width),
                    int(body_height)
                ),
                body_width // 4,
                body_width // 4
            )
            painter.end()
        self.original_pixmap = pixmap
        scaled_pixmap = pixmap.scaled(
            *self.default_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.photo_path = ""  # Luôn rỗng với ảnh mặc định
        self.crop_action.setEnabled(False)
        self.rotate_action.setEnabled(False)
        self.filter_menu.setEnabled(False)
        # Không phát tín hiệu photo_changed với ảnh mặc định

    def get_photo_path(self):
        """
        Lấy đường dẫn đến file ảnh
        
        Returns:
            str: Đường dẫn đến file ảnh hiện tại
        """
        # Nếu đang sử dụng ảnh mặc định hoặc không có ảnh, trả về rỗng
        if not self.photo_path or self.photo_path.endswith("default_avatar.png"):
            return ""
        return self.photo_path
    
    def reload_photo(self):
        """Nút tải lại ảnh đại diện (ví dụ: đặt lại về mặc định)"""
        self.set_default_photo()

    def choose_photo(self):
        """Chọn ảnh từ máy tính"""
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh đại diện", "",
            "Ảnh (*.png *.jpg *.jpeg *.bmp);;Tất cả file (*)",
            options=options
        )
        
        if file_name:
            try:
                # Kiểm tra kích thước file
                file_size = os.path.getsize(file_name)
                max_size = 5 * 1024 * 1024  # 5MB
                
                if file_size > max_size:
                    QMessageBox.warning(self, "Cảnh báo", f"File ảnh quá lớn. Vui lòng chọn ảnh nhỏ hơn {max_size/1024/1024:.1f}MB.")
                    return
                
                # Kiểm tra xem có phải là file ảnh hợp lệ không
                image = QImage(file_name)
                if image.isNull():
                    QMessageBox.warning(self, "Cảnh báo", "File không phải là ảnh hợp lệ.")
                    return
                
                self.set_photo(file_name)
                    
            except Exception as e:
                logging.error(f"Lỗi khi chọn ảnh: {str(e)}")
                QMessageBox.warning(self, "Lỗi", f"Không thể tải ảnh: {str(e)}")
    
    def remove_photo(self):
        """Xóa ảnh đang hiển thị"""
        self.set_default_photo()
    
    def crop_photo(self):
        """Cắt ảnh đại diện"""
        if not self.original_pixmap or self.photo_path == "":
            QMessageBox.warning(self, "Cảnh báo", "Không có ảnh để cắt.")
            return
        
        crop_dialog = CropDialog(self.original_pixmap, self)
        if crop_dialog.exec():
            # Cập nhật ảnh đã cắt
            if crop_dialog.cropped_pixmap:
                # Lưu ảnh tạm để sử dụng
                temp_path = os.path.join("temp", f"cropped_{os.path.basename(self.photo_path)}")
                os.makedirs("temp", exist_ok=True)
                crop_dialog.cropped_pixmap.save(temp_path, "PNG")
                
                self.set_photo(temp_path)
    
    def rotate_photo(self):
        """Xoay ảnh đại diện 90 độ theo chiều kim đồng hồ"""
        if not self.original_pixmap or self.photo_path == "":
            QMessageBox.warning(self, "Cảnh báo", "Không có ảnh để xoay.")
            return
        
        # Xoay ảnh 90 độ
        transform = QTransform().rotate(90)
        rotated = self.original_pixmap.transformed(transform)
        
        # Lưu ảnh tạm để sử dụng
        temp_path = os.path.join("temp", f"rotated_{os.path.basename(self.photo_path)}")
        os.makedirs("temp", exist_ok=True)
        rotated.save(temp_path, "PNG")
        
        self.set_photo(temp_path)
    
    def cleanup_temp_files(self):
        """Xóa tất cả các file ảnh tạm đã tạo"""
        # Xóa các file tạm của instance này
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logging.info(f"Đã xóa file ảnh tạm: {temp_file}")
            except Exception as e:
                logging.error(f"Không thể xóa file ảnh tạm {temp_file}: {str(e)}")
        
        self.temp_files.clear()
        
        # Sử dụng chức năng dọn dẹp tổng quát
        cleanup_temp_files()
    
    def apply_filter(self, filter_type="grayscale"):
        """Áp dụng bộ lọc cho ảnh"""
        if not self.original_pixmap or self.photo_path == "":
            QMessageBox.warning(self, "Cảnh báo", "Không có ảnh để áp dụng bộ lọc.")
            return
        
        # Chuyển QPixmap sang QImage để xử lý
        image = self.original_pixmap.toImage()
        
        if filter_type == "grayscale":
            # Chuyển sang ảnh xám
            for y in range(image.height()):
                for x in range(image.width()):
                    pixel = image.pixel(x, y)
                    gray = QColor(pixel).gray()
                    image.setPixel(x, y, QColor(gray, gray, gray).rgb())
        elif filter_type == "sepia":
            # Bộ lọc sepia
            for y in range(image.height()):
                for x in range(image.width()):
                    pixel = image.pixel(x, y)
                    color = QColor(pixel)
                    r, g, b = color.red(), color.green(), color.blue()
                    tr = min(255, int(0.393 * r + 0.769 * g + 0.189 * b))
                    tg = min(255, int(0.349 * r + 0.686 * g + 0.168 * b))
                    tb = min(255, int(0.272 * r + 0.534 * g + 0.131 * b))
                    image.setPixel(x, y, QColor(tr, tg, tb).rgb())
        
        # Lưu ảnh đã lọc
        temp_path = os.path.join("temp", f"filtered_{os.path.basename(self.photo_path)}")
        os.makedirs("temp", exist_ok=True)
        
        # Chuyển QImage trở lại QPixmap và thiết lập
        filtered_pixmap = QPixmap.fromImage(image)
        filtered_pixmap.save(temp_path)
        self.set_photo(temp_path)
    
    def view_large_photo(self):
        """Hiển thị ảnh đại diện ở kích thước lớn hơn trong một dialog mới"""
        if not self.original_pixmap:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Xem ảnh đại diện")
        dlg.setMinimumSize(400, 500)
        vbox = QVBoxLayout(dlg)
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Hiển thị ảnh lớn hơn, giữ nguyên tỉ lệ
        pix = self.original_pixmap.scaled(350, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        lbl.setPixmap(pix)
        vbox.addWidget(lbl)
        btn = QPushButton("Đóng")
        btn.clicked.connect(dlg.accept)
        vbox.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        dlg.exec()

    def show_context_menu(self, pos):
        """Hiển thị menu ngữ cảnh tại vị trí chuột phải"""
        global_pos = self.image_label.mapToGlobal(pos)
        self.context_menu.exec(global_pos)
