from datetime import datetime

class User:
    """
    Lớp đại diện cho một người dùng trong hệ thống.
    """
    def __init__(self, user_id=None, username="", password_hash="", full_name="", 
                 email="", role="user", is_active=True, created_date=None, last_login=None):
        """
        Khởi tạo một đối tượng người dùng.
        
        Args:
            user_id (int): ID người dùng
            username (str): Tên đăng nhập
            password_hash (str): Mật khẩu đã được mã hóa
            full_name (str): Tên đầy đủ
            email (str): Địa chỉ email
            role (str): Vai trò (admin, teacher, user, etc.)
            is_active (bool): Trạng thái hoạt động
            created_date (str): Ngày tạo tài khoản
            last_login (str): Thời gian đăng nhập gần nhất
        """
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_date = created_date if created_date else datetime.now().strftime("%Y-%m-%d")
        self.last_login = last_login

    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng người dùng từ dictionary.
        
        Args:
            data (dict): Dictionary chứa dữ liệu người dùng
            
        Returns:
            User: Đối tượng người dùng mới
        """
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            is_active=bool(data.get('is_active', 1)),
            created_date=data.get('created_date', ''),
            last_login=data.get('last_login')
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng người dùng thành dictionary.
        
        Returns:
            dict: Dictionary chứa thông tin người dùng
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'is_active': 1 if self.is_active else 0,
            'created_date': self.created_date,
            'last_login': self.last_login
        }
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho người dùng.
        
        Returns:
            str: Chuỗi thông tin người dùng
        """
        return f"{self.username} ({self.full_name})"
