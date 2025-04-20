import jwt
import logging
from datetime import datetime, timedelta
from utils.config_manager import ConfigManager

class AuthManager:
    """
    Quản lý xác thực và phân quyền người dùng
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Sử dụng ConfigManager để lấy cấu hình bảo mật
        self.config_manager = ConfigManager()
        self.secret_key = self.config_manager.get_secret_key()
        
        # Lấy thời hạn token từ biến môi trường hoặc sử dụng giá trị mặc định
        token_expiry = self.config_manager.get('TOKEN_EXPIRY_HOURS')
        self.token_expiry = int(token_expiry) if token_expiry else 24
        
        # Lấy thuật toán mã hóa từ biến môi trường hoặc sử dụng mặc định
        self.algorithm = self.config_manager.get('ENCRYPTION_ALGORITHM', 'HS256')
    
    def authenticate(self, username, password):
        """
        Xác thực người dùng
        
        Args:
            username (str): Tên đăng nhập
            password (str): Mật khẩu
            
        Returns:
            dict: Thông tin người dùng nếu xác thực thành công, None nếu thất bại
        """
        query = """
        SELECT 
            user_id, username, password_hash, full_name, email, role, is_active 
        FROM users 
        WHERE username = ? AND is_active = 1
        """
        
        result = self.db_manager.execute_query(query, (username,))
        
        if not result:
            logging.warning(f"Đăng nhập thất bại: Không tìm thấy người dùng '{username}'")
            return None
        
        user_data = result[0]
        
        # Kiểm tra mật khẩu
        if not self.db_manager.verify_password(password, user_data['password_hash']):
            logging.warning(f"Đăng nhập thất bại: Mật khẩu không đúng cho người dùng '{username}'")
            return None
        
        # Cập nhật thời gian đăng nhập cuối
        self._update_last_login(user_data['user_id'])
        
        # Ghi nhật ký đăng nhập
        self.db_manager.log_activity(
            user_data['user_id'],
            "LOGIN",
            f"Đăng nhập thành công: {username}",
            "User",
            user_data['user_id']
        )
        
        return user_data
    
    def _update_last_login(self, user_id):
        """
        Cập nhật thời gian đăng nhập cuối cho người dùng
        
        Args:
            user_id (int): ID của người dùng
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_query = "UPDATE users SET last_login = ? WHERE user_id = ?"
            self.db_manager.execute_update(update_query, (current_time, user_id))
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật thời gian đăng nhập cuối: {e}")
    
    def generate_token(self, user_data):
        """
        Tạo JWT token cho người dùng
        
        Args:
            user_data (dict): Thông tin người dùng
            user_data (dict): Thông tin người dùng
            
        Returns:
            str: JWT token
        """
        try:
            payload = {
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'role': user_data['role'],
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry)
            }
            
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            logging.error(f"Lỗi khi tạo JWT token: {e}")
            return None

    def verify_token(self, token):
        """
        Xác minh JWT token
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Thông tin người dùng nếu token hợp lệ, None nếu không
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Kiểm tra người dùng có còn tồn tại và active
            query = """
            SELECT user_id, username, role, is_active 
            FROM users 
            WHERE user_id = ? AND is_active = 1
            """
            
            result = self.db_manager.execute_query(query, (payload['user_id'],))
            
            if not result:
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            logging.warning("Token đã hết hạn")
            return None
        except jwt.InvalidTokenError:
            logging.warning("Token không hợp lệ")
            return None
        except Exception as e:
            logging.error(f"Lỗi khi xác minh token: {e}")
            return None
    
    def has_permission(self, user_role, required_role):
        """
        Kiểm tra người dùng có quyền truy cập không
        
        Args:
            user_role (str): Vai trò của người dùng
            required_role (str): Vai trò yêu cầu
            
        Returns:
            bool: True nếu có quyền, False nếu không
        """
        role_hierarchy = {
            'admin': 100,
            'manager': 50,
            'teacher': 30,
            'user': 10
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 100)  # Mặc định cao nhất nếu không tìm thấy
        
        return user_level >= required_level
