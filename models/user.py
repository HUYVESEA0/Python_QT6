from datetime import datetime

class User:
    """
    Lớp đại diện cho một người dùng trong hệ thống
    """
    
    def __init__(self, ma_nguoi_dung=None, ten_dang_nhap="", ho_ten="", email="",
                 vai_tro="user", trang_thai=True, ngay_tao=None, lan_dang_nhap_cuoi=None, user_id=None):
        """
        Khởi tạo một đối tượng người dùng
        Args:
            ma_nguoi_dung (int): ID người dùng
            ten_dang_nhap (str): Tên đăng nhập
            ho_ten (str): Họ và tên người dùng
            email (str): Địa chỉ email
            vai_tro (str): Vai trò (admin, user, etc.)
            trang_thai (bool): Trạng thái hoạt động
            ngay_tao (str): Ngày tạo tài khoản
            lan_dang_nhap_cuoi (str): Thời gian đăng nhập gần nhất
        """
        self.ma_nguoi_dung = ma_nguoi_dung
        self.ten_dang_nhap = ten_dang_nhap
        self.ho_ten = ho_ten
        self.email = email
        self.vai_tro = vai_tro
        self.trang_thai = trang_thai
        self.ngay_tao = ngay_tao
        self.lan_dang_nhap_cuoi = lan_dang_nhap_cuoi
        self.user_id = user_id  # Add this attribute

    def has_permission(self, required_role: str) -> bool:
        """
        Kiểm tra người dùng có đủ quyền thực hiện hành động yêu cầu không.
        Args:
            required_role (str): Vai trò yêu cầu ('admin', 'manager', 'user', ...)
        Returns:
            bool: True nếu đủ quyền, False nếu không
        """
        role_hierarchy = {
            'admin': 3,
            'manager': 2,
            'user': 1
        }
        user_level = role_hierarchy.get(self.vai_tro, 0)
        required_level = role_hierarchy.get(required_role, 100)
        return user_level >= required_level
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng người dùng từ dictionary
        Args:
            data (dict): Dictionary chứa dữ liệu người dùng
        Returns:
            User: Đối tượng người dùng mới
        """
        trang_thai = data.get('trang_thai', 0) == 1
        return cls(
            ma_nguoi_dung=data.get('ma_nguoi_dung'),
            ten_dang_nhap=data.get('ten_dang_nhap', ''),
            ho_ten=data.get('ho_ten', ''),
            email=data.get('email', ''),
            vai_tro=data.get('vai_tro', 'user'),
            trang_thai=trang_thai,
            ngay_tao=data.get('ngay_tao'),
            lan_dang_nhap_cuoi=data.get('lan_dang_nhap_cuoi')
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng người dùng thành dictionary
        Returns:
            dict: Dictionary chứa thông tin người dùng
        """
        return {
            'ma_nguoi_dung': self.ma_nguoi_dung,
            'ten_dang_nhap': self.ten_dang_nhap,
            'ho_ten': self.ho_ten,
            'email': self.email,
            'vai_tro': self.vai_tro,
            'trang_thai': 1 if self.trang_thai else 0,
            'ngay_tao': self.ngay_tao,
            'lan_dang_nhap_cuoi': self.lan_dang_nhap_cuoi
        }
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho người dùng
        Returns:
            str: Chuỗi thông tin người dùng
        """
        return f"{self.ma_nguoi_dung} - {self.ten_dang_nhap} ({self.vai_tro})"
    
    @property
    def username(self):
        return self.ten_dang_nhap

    @username.setter
    def username(self, value):
        self.ten_dang_nhap = value

    @property
    def role(self):
        return self.vai_tro

    @role.setter
    def role(self, value):
        self.vai_tro = value

    @property
    def full_name(self):
        return self.ho_ten

    @full_name.setter
    def full_name(self, value):
        self.ho_ten = value

    @property
    def is_active(self):
        return self.trang_thai

    @is_active.setter
    def is_active(self, value):
        self.trang_thai = value
