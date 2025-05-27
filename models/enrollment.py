class GhiDanh:
    """
    Lớp đại diện cho một bản ghi đăng ký (ghi danh) trong hệ thống.
    """
    def __init__(self, ma_ghi_danh=None, ma_sinh_vien="", ma_khoa_hoc="", ngay_ghi_danh="", diem=None, ho_ten=None, ten_khoa_hoc=None):
        """
        Khởi tạo một đối tượng ghi danh.
        Args:
            ma_ghi_danh (int): Mã ghi danh (PK)
            ma_sinh_vien (str): Mã sinh viên
            ma_khoa_hoc (str): Mã khóa học
            ngay_ghi_danh (str): Ngày ghi danh (YYYY-MM-DD)
            diem (float): Điểm số
            ho_ten (str, optional): Họ tên sinh viên (join)
            ten_khoa_hoc (str, optional): Tên khóa học (join)
        """
        self.ma_ghi_danh = ma_ghi_danh
        self.ma_sinh_vien = ma_sinh_vien
        self.ma_khoa_hoc = ma_khoa_hoc
        self.ngay_ghi_danh = ngay_ghi_danh
        self.diem = diem
        self.ho_ten = ho_ten
        self.ten_khoa_hoc = ten_khoa_hoc

    @classmethod
    def from_dict(cls, data):
        return cls(
            ma_ghi_danh=data.get('ma_ghi_danh'),
            ma_sinh_vien=data.get('ma_sinh_vien', ''),
            ma_khoa_hoc=data.get('ma_khoa_hoc', ''),
            ngay_ghi_danh=data.get('ngay_ghi_danh', ''),
            diem=data.get('diem'),
            ho_ten=data.get('ho_ten'),
            ten_khoa_hoc=data.get('ten_khoa_hoc')
        )

    def to_dict(self):
        return {
            'ma_ghi_danh': self.ma_ghi_danh,
            'ma_sinh_vien': self.ma_sinh_vien,
            'ma_khoa_hoc': self.ma_khoa_hoc,
            'ngay_ghi_danh': self.ngay_ghi_danh,
            'diem': self.diem,
            'ho_ten': self.ho_ten,
            'ten_khoa_hoc': self.ten_khoa_hoc
        }

    def __str__(self):
        return f"{self.ma_ghi_danh}: {self.ma_sinh_vien} - {self.ma_khoa_hoc} ({self.diem})"