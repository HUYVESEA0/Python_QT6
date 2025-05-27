class Course:
    """
    Lớp đại diện cho một khóa học trong hệ thống.
    """
    def __init__(self, ma_khoa_hoc="", ten_khoa_hoc="", so_tin_chi=0, 
                 giang_vien="", mo_ta="", so_luong_toi_da=50):
        """
        Khởi tạo một đối tượng khóa học.
        Args:
            ma_khoa_hoc (str): Mã khóa học
            ten_khoa_hoc (str): Tên khóa học
            so_tin_chi (int): Số tín chỉ
            giang_vien (str): Giảng viên
            mo_ta (str): Mô tả
            so_luong_toi_da (int): Số lượng sinh viên tối đa
        """
        self.ma_khoa_hoc = ma_khoa_hoc
        self.ten_khoa_hoc = ten_khoa_hoc
        self.so_tin_chi = so_tin_chi
        self.giang_vien = giang_vien
        self.mo_ta = mo_ta
        self.so_luong_toi_da = so_luong_toi_da
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng khóa học từ dictionary.
        Args:
            data (dict): Dictionary chứa dữ liệu khóa học
        Returns:
            Course: Đối tượng khóa học mới
        """
        return cls(
            ma_khoa_hoc=data.get('ma_khoa_hoc', ''),
            ten_khoa_hoc=data.get('ten_khoa_hoc', ''),
            so_tin_chi=data.get('so_tin_chi', 0),
            giang_vien=data.get('giang_vien', ''),
            mo_ta=data.get('mo_ta', ''),
            so_luong_toi_da=data.get('so_luong_toi_da', 50)
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng khóa học thành dictionary.
        
        Returns:
            dict: Dictionary chứa thông tin khóa học
        """
        return {
            'ma_khoa_hoc': self.ma_khoa_hoc,
            'ten_khoa_hoc': self.ten_khoa_hoc,
            'so_tin_chi': self.so_tin_chi,
            'giang_vien': self.giang_vien,
            'mo_ta': self.mo_ta,
            'so_luong_toi_da': self.so_luong_toi_da
        }
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho khóa học.
        
        Returns:
            str: Chuỗi thông tin khóa học
        """
        return f"{self.ma_khoa_hoc} - {self.ten_khoa_hoc} ({self.so_tin_chi} tín chỉ)"