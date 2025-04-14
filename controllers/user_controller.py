import logging
from datetime import datetime
from models.user import User

class UserController:
    """
    Controller quản lý các thao tác liên quan đến người dùng và xác thực.
    """
    def __init__(self, db_manager):
        """
        Khởi tạo controller với tham chiếu đến database manager.
        
        Args:
            db_manager: Đối tượng quản lý cơ sở dữ liệu
        """
        self.db_manager = db_manager
        logging.info("Đã khởi tạo UserController")
        
        # Tạo tài khoản admin mặc định nếu chưa tồn tại
        self.db_manager.create_default_admin()
    
    def authenticate(self, username, password):
        """
        Xác thực người dùng dựa trên tên đăng nhập và mật khẩu.
        
        Args:
            username (str): Tên đăng nhập
            password (str): Mật khẩu
            
        Returns:
            User: Đối tượng User nếu xác thực thành công, None nếu thất bại
        """
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        result = self.db_manager.execute_query(query, (username,))
        
        if not result:
            logging.warning(f"Không tìm thấy người dùng: {username}")
            return None
        
        user_data = dict(result[0])
        if not self.db_manager.verify_password(password, user_data['password_hash']):
            logging.warning(f"Mật khẩu không đúng cho người dùng: {username}")
            return None
        
        # Cập nhật thời gian đăng nhập gần nhất
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_query = "UPDATE users SET last_login = ? WHERE user_id = ?"
        self.db_manager.execute_update(update_query, (current_time, user_data['user_id']))
        
        # Tạo đối tượng User từ dữ liệu
        user = User.from_dict(user_data)
        logging.info(f"Người dùng đăng nhập thành công: {username}")
        return user
    
    def get_all_users(self):
        """
        Lấy danh sách tất cả người dùng.
        
        Returns:
            list: Danh sách các đối tượng User
        """
        query = "SELECT * FROM users ORDER BY username"
        result = self.db_manager.execute_query(query)
        
        users = []
        for row in result:
            user_data = dict(row)
            users.append(User.from_dict(user_data))
            
        logging.info(f"Lấy danh sách người dùng: {len(users)} người dùng")
        return users
    
    def get_user_by_username(self, username):
        """
        Lấy thông tin người dùng theo tên đăng nhập.
        
        Args:
            username (str): Tên đăng nhập cần tìm
            
        Returns:
            User: Đối tượng người dùng nếu tìm thấy, None nếu không tồn tại
        """
        query = "SELECT * FROM users WHERE username = ?"
        result = self.db_manager.execute_query(query, (username,))
        
        if result:
            user_data = dict(result[0])
            user = User.from_dict(user_data)
            logging.info(f"Tìm thấy người dùng: {user}")
            return user
        
        logging.warning(f"Không tìm thấy người dùng với tên đăng nhập: {username}")
        return None
    
    def add_user(self, user, password):
        """
        Thêm người dùng mới vào hệ thống.
        
        Args:
            user (User): Đối tượng người dùng cần thêm
            password (str): Mật khẩu ban đầu (chưa mã hóa)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Kiểm tra xem người dùng đã tồn tại chưa
        existing_user = self.get_user_by_username(user.username)
        if existing_user:
            logging.warning(f"Người dùng với username {user.username} đã tồn tại")
            return False
        
        # Mã hóa mật khẩu
        password_hash = self.db_manager.hash_password(password)
        user.password_hash = password_hash
        
        query = """
        INSERT INTO users 
        (username, password_hash, full_name, email, role, is_active, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user.username,
            user.password_hash,
            user.full_name,
            user.email,
            user.role,
            1 if user.is_active else 0,
            user.created_date
        )
        
        result = self.db_manager.execute_insert(query, params)
        success = result is not None
        
        if success:
            logging.info(f"Đã thêm người dùng: {user}")
        else:
            logging.error(f"Không thể thêm người dùng: {user}")
            
        return success
    
    def change_password(self, username, old_password, new_password):
        """
        Thay đổi mật khẩu người dùng.
        
        Args:
            username (str): Tên đăng nhập
            old_password (str): Mật khẩu cũ
            new_password (str): Mật khẩu mới
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Xác thực người dùng với mật khẩu cũ
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        # Mã hóa mật khẩu mới
        new_password_hash = self.db_manager.hash_password(new_password)
        
        # Cập nhật mật khẩu
        query = "UPDATE users SET password_hash = ? WHERE username = ?"
        rows_affected = self.db_manager.execute_update(query, (new_password_hash, username))
        
        success = rows_affected > 0
        if success:
            logging.info(f"Đã đổi mật khẩu cho người dùng: {username}")
        else:
            logging.error(f"Không thể đổi mật khẩu cho người dùng: {username}")
            
        return success
