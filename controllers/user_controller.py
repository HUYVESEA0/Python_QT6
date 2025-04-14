import logging
from datetime import datetime
from models.user import User

class UserController:
    """
    Controller quản lý các thao tác liên quan đến người dùng
    """
    
    def __init__(self, db_manager):
        """
        Khởi tạo controller với tham chiếu đến database manager
        
        Args:
            db_manager: Đối tượng quản lý cơ sở dữ liệu
        """
        self.db_manager = db_manager
        logging.info("Đã khởi tạo UserController")
        
        # Tạo tài khoản admin mặc định nếu chưa có
        self.db_manager.create_default_admin()
    
    def authenticate(self, username, password):
        """
        Xác thực thông tin đăng nhập của người dùng
        
        Args:
            username (str): Tên đăng nhập
            password (str): Mật khẩu
            
        Returns:
            User: Đối tượng user nếu xác thực thành công, None nếu thất bại
        """
        query = """
        SELECT user_id, username, password_hash, full_name, email, role 
        FROM users 
        WHERE username = ? AND is_active = 1
        """
        
        result = self.db_manager.execute_query(query, (username,))
        
        if not result:
            logging.warning(f"Đăng nhập thất bại: Không tìm thấy người dùng '{username}'")
            return None
        
        user_data = result[0]
        if not self.db_manager.verify_password(password, user_data['password_hash']):
            logging.warning(f"Đăng nhập thất bại: Mật khẩu không đúng cho người dùng '{username}'")
            return None
        
        # Cập nhật thời gian đăng nhập cuối
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_query = "UPDATE users SET last_login = ? WHERE username = ?"
        self.db_manager.execute_update(update_query, (current_time, username))
        
        # Ghi log đăng nhập
        user = User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            full_name=user_data['full_name'],
            email=user_data['email'],
            role=user_data['role']
        )
        
        self.db_manager.log_activity(
            user.user_id, 
            "LOGIN", 
            f"Đăng nhập: {user.username}",
            "User",
            user.user_id
        )
        
        logging.info(f"Đăng nhập thành công: {username}")
        return user
    
    def get_all_users(self):
        """
        Lấy danh sách tất cả người dùng
        
        Returns:
            list: Danh sách các đối tượng User
        """
        query = "SELECT user_id, username, full_name, email, role, is_active, created_date, last_login FROM users"
        result = self.db_manager.execute_query(query)
        
        users = []
        for row in result:
            user_data = dict(row)
            users.append(User.from_dict(user_data))
        
        return users
    
    def get_user_by_id(self, user_id):
        """
        Lấy thông tin người dùng theo ID
        
        Args:
            user_id (int): ID của người dùng cần tìm
            
        Returns:
            User: Đối tượng người dùng nếu tìm thấy, None nếu không
        """
        query = """
        SELECT user_id, username, full_name, email, role, is_active, created_date, last_login 
        FROM users 
        WHERE user_id = ?
        """
        
        result = self.db_manager.execute_query(query, (user_id,))
        
        if result:
            user_data = dict(result[0])
            return User.from_dict(user_data)
            
        return None
    
    def get_user_by_username(self, username):
        """
        Lấy thông tin người dùng theo tên đăng nhập
        
        Args:
            username (str): Tên đăng nhập của người dùng cần tìm
            
        Returns:
            User: Đối tượng người dùng nếu tìm thấy, None nếu không
        """
        query = """
        SELECT user_id, username, full_name, email, role, is_active, created_date, last_login 
        FROM users 
        WHERE username = ?
        """
        
        result = self.db_manager.execute_query(query, (username,))
        
        if result:
            user_data = dict(result[0])
            return User.from_dict(user_data)
            
        return None
    
    def add_user(self, user, password, current_user_id=None):
        """
        Thêm người dùng mới
        
        Args:
            user (User): Đối tượng người dùng cần thêm
            password (str): Mật khẩu ban đầu
            current_user_id (int): ID của người dùng thực hiện hành động
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Kiểm tra xem username đã tồn tại chưa
        existing_user = self.get_user_by_username(user.username)
        if existing_user:
            logging.warning(f"Không thể thêm người dùng: Tên đăng nhập '{user.username}' đã tồn tại")
            return False
        
        # Mã hóa mật khẩu
        password_hash = self.db_manager.hash_password(password)
        
        # Tạo truy vấn
        query = """
        INSERT INTO users (username, password_hash, full_name, email, role, is_active, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        params = (
            user.username,
            password_hash,
            user.full_name,
            user.email,
            user.role,
            1 if user.is_active else 0,
            current_time
        )
        
        user_id = self.db_manager.execute_insert(query, params)
        success = user_id is not None
        
        if success:
            logging.info(f"Đã thêm người dùng: {user.username}")
            
            # Ghi log
            if current_user_id:
                self.db_manager.log_activity(
                    current_user_id,
                    "ADD",
                    f"Thêm người dùng: {user.username}",
                    "User",
                    user_id
                )
        else:
            logging.error(f"Không thể thêm người dùng: {user.username}")
        
        return success
    
    def update_user(self, user, current_user_id=None):
        """
        Cập nhật thông tin người dùng
        
        Args:
            user (User): Đối tượng người dùng cần cập nhật
            current_user_id (int): ID của người dùng thực hiện hành động
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Tạo truy vấn
        query = """
        UPDATE users 
        SET full_name = ?, email = ?, role = ?, is_active = ?
        WHERE user_id = ?
        """
        
        params = (
            user.full_name,
            user.email,
            user.role,
            1 if user.is_active else 0,
            user.user_id
        )
        
        rows_affected = self.db_manager.execute_update(query, params)
        success = rows_affected > 0
        
        if success:
            logging.info(f"Đã cập nhật người dùng: {user.username}")
            
            # Ghi log
            if current_user_id:
                self.db_manager.log_activity(
                    current_user_id,
                    "UPDATE",
                    f"Cập nhật thông tin người dùng: {user.username}",
                    "User",
                    user.user_id
                )
        else:
            logging.warning(f"Không thể cập nhật người dùng: {user.username}")
        
        return success
    
    def delete_user(self, user_id, current_user_id=None):
        """
        Xóa người dùng
        
        Args:
            user_id (int): ID của người dùng cần xóa
            current_user_id (int): ID của người dùng thực hiện hành động
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Không cho phép xóa chính mình
        if user_id == current_user_id:
            logging.warning("Không thể xóa tài khoản đang đăng nhập")
            return False
        
        # Lấy thông tin người dùng để ghi log
        user = self.get_user_by_id(user_id)
        if not user:
            logging.warning(f"Không tìm thấy người dùng với ID {user_id} để xóa")
            return False
            
        # Lưu thông tin để ghi log
        username = user.username
        
        # Thực hiện xóa
        query = "DELETE FROM users WHERE user_id = ?"
        rows_affected = self.db_manager.execute_delete(query, (user_id,))
        success = rows_affected > 0
        
        if success:
            logging.info(f"Đã xóa người dùng: {username}")
            
            # Ghi log
            if current_user_id:
                self.db_manager.log_activity(
                    current_user_id,
                    "DELETE",
                    f"Xóa người dùng: {username}",
                    "User",
                    user_id
                )
        else:
            logging.warning(f"Không thể xóa người dùng với ID: {user_id}")
        
        return success
    
    def change_password(self, username, old_password, new_password):
        """
        Đổi mật khẩu cho người dùng
        
        Args:
            username (str): Tên đăng nhập
            old_password (str): Mật khẩu cũ
            new_password (str): Mật khẩu mới
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Kiểm tra mật khẩu cũ
        query = "SELECT user_id, password_hash FROM users WHERE username = ?"
        result = self.db_manager.execute_query(query, (username,))
        
        if not result:
            logging.warning(f"Đổi mật khẩu thất bại: Không tìm thấy người dùng '{username}'")
            return False
        
        user_data = result[0]
        if not self.db_manager.verify_password(old_password, user_data['password_hash']):
            logging.warning(f"Đổi mật khẩu thất bại: Mật khẩu cũ không đúng cho người dùng '{username}'")
            return False
        
        # Mã hóa mật khẩu mới
        new_password_hash = self.db_manager.hash_password(new_password)
        
        # Cập nhật mật khẩu
        update_query = "UPDATE users SET password_hash = ? WHERE username = ?"
        rows_affected = self.db_manager.execute_update(update_query, (new_password_hash, username))
        
        if rows_affected > 0:
            logging.info(f"Đã đổi mật khẩu cho người dùng: {username}")
            return True
        else:
            logging.error(f"Không thể đổi mật khẩu cho người dùng: {username}")
            return False
