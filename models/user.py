from datetime import datetime

class User:
    """
    Lớp đại diện cho một người dùng trong hệ thống
    """
    
    def __init__(self, user_id=None, username="", full_name="", email="",
                 role="user", is_active=True, created_date=None, last_login=None):
        """
        Khởi tạo một đối tượng người dùng
        
        Args:
            user_id (int): ID người dùng
            username (str): Tên đăng nhập
            full_name (str): Họ và tên người dùng
            email (str): Địa chỉ email
            role (str): Vai trò (admin, user, etc.)
            is_active (bool): Trạng thái hoạt động
            created_date (str): Ngày tạo tài khoản
            last_login (str): Thời gian đăng nhập gần nhất
        """
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_date = created_date
        self.last_login = last_login
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng người dùng từ dictionary
        
        Args:
            data (dict): Dictionary chứa dữ liệu người dùng
            
        Returns:
            User: Đối tượng người dùng mới
        """
        is_active = data.get('is_active', 0) == 1
        
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            is_active=is_active,
            created_date=data.get('created_date'),
            last_login=data.get('last_login')
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng người dùng thành dictionary
        
        Returns:
            dict: Dictionary chứa thông tin người dùng
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'is_active': 1 if self.is_active else 0,
            'created_date': self.created_date,
            'last_login': self.last_login
        }
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho người dùng
        
        Returns:
            str: Chuỗi thông tin người dùng
        """
        return f"{self.username} ({self.role})"
