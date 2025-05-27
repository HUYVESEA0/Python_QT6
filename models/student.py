from datetime import datetime
import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class Student:
    """
    Lớp đại diện cho một sinh viên trong hệ thống.
    """
    def __init__(self, ma_sinh_vien="", ho_ten="", ngay_sinh=None, 
                 gioi_tinh="", email="", so_dien_thoai="", dia_chi="", 
                 ngay_nhap_hoc=None, trang_thai="Đang học", duong_dan_anh=""):
        """
        Khởi tạo một đối tượng sinh viên.
        
        Args:
            ma_sinh_vien (str): Mã số sinh viên
            ho_ten (str): Họ và tên sinh viên
            ngay_sinh (str): Ngày sinh (định dạng YYYY-MM-DD)
            gioi_tinh (str): Giới tính
            email (str): Địa chỉ email
            so_dien_thoai (str): Số điện thoại
            dia_chi (str): Địa chỉ
            ngay_nhap_hoc (str): Ngày nhập học (định dạng YYYY-MM-DD)
            trang_thai (str): Trạng thái của sinh viên
            duong_dan_anh (str): Đường dẫn đến file ảnh đại diện
        """
        self.ma_sinh_vien = ma_sinh_vien
        self.ho_ten = ho_ten
        self.ngay_sinh = ngay_sinh if ngay_sinh else ""
        self.gioi_tinh = gioi_tinh
        self.email = email
        self.so_dien_thoai = so_dien_thoai
        self.dia_chi = dia_chi
        self.ngay_nhap_hoc = ngay_nhap_hoc if ngay_nhap_hoc else datetime.now().strftime("%Y-%m-%d")
        self.trang_thai = trang_thai
        # Nếu là ảnh mặc định thì để rỗng
        if duong_dan_anh and duong_dan_anh.endswith("default_avatar.png"):
            self.duong_dan_anh = ""
        else:
            self.duong_dan_anh = duong_dan_anh

    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng sinh viên từ dictionary.
        Args:
            data (dict): Dictionary chứa dữ liệu sinh viên
        Returns:
            Student: Đối tượng sinh viên mới
        """
        duong_dan_anh = data.get('duong_dan_anh', '')
        if duong_dan_anh and duong_dan_anh.endswith("default_avatar.png"):
            duong_dan_anh = ""
        return cls(
            ma_sinh_vien=data.get('ma_sinh_vien', ''),
            ho_ten=data.get('ho_ten', ''),
            ngay_sinh=data.get('ngay_sinh', ''),
            gioi_tinh=data.get('gioi_tinh', ''),
            email=data.get('email', ''),
            so_dien_thoai=data.get('so_dien_thoai', ''),
            dia_chi=data.get('dia_chi', ''),
            ngay_nhap_hoc=data.get('ngay_nhap_hoc', ''),
            trang_thai=data.get('trang_thai', 'Đang học'),
            duong_dan_anh=duong_dan_anh
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng sinh viên thành dictionary.
        Returns:
            dict: Dictionary chứa thông tin sinh viên
        """
        duong_dan_anh = self.duong_dan_anh
        if duong_dan_anh and duong_dan_anh.endswith("default_avatar.png"):
            duong_dan_anh = ""
        return {
            'ma_sinh_vien': self.ma_sinh_vien,
            'ho_ten': self.ho_ten,
            'ngay_sinh': self.ngay_sinh,
            'gioi_tinh': self.gioi_tinh,
            'email': self.email,
            'so_dien_thoai': self.so_dien_thoai,
            'dia_chi': self.dia_chi,
            'ngay_nhap_hoc': self.ngay_nhap_hoc,
            'trang_thai': self.trang_thai,
            'duong_dan_anh': duong_dan_anh
        }
    
    def get_photo(self, default_size=(100, 100)):
        """
        Lấy ảnh đại diện của sinh viên
        
        Args:
            default_size (tuple): Kích thước (width, height) mặc định
            
        Returns:
            QPixmap: Ảnh đại diện dạng QPixmap
        """
        if self.duong_dan_anh and os.path.exists(self.duong_dan_anh):
            pixmap = QPixmap(self.duong_dan_anh)
            return pixmap.scaled(*default_size, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        else:
            # Trả về ảnh mặc định
            default_path = "resources/default_avatar.png"
            if os.path.exists(default_path):
                pixmap = QPixmap(default_path)
            else:
                # Tạo ảnh pixmap trống nếu không tìm thấy ảnh mặc định
                pixmap = QPixmap(*default_size)
                pixmap.fill(Qt.GlobalColor.lightGray)
            return pixmap.scaled(*default_size, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho sinh viên.
        Returns:
            str: Chuỗi thông tin sinh viên
        """
        return f"{self.ma_sinh_vien} - {self.ho_ten}"