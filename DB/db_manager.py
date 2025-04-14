import sqlite3
import os
import logging
import hashlib
import shutil
import secrets
import sys
from datetime import datetime

# Add the project root to Python path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.path_helper import PathHelper

class DatabaseManager:
    """
    Lớp quản lý kết nối và thao tác với cơ sở dữ liệu SQLite.
    """
    
    def __init__(self, db_name="student_management.db"):
        """
        Khởi tạo kết nối đến cơ sở dữ liệu.
        
        Args:
            db_name (str): Tên của file cơ sở dữ liệu
        """
        # Tạo thư mục data nếu không tồn tại
        data_dir = PathHelper.get_resource_path("data")
        PathHelper.ensure_dir(data_dir)
        
        # Thiết lập đường dẫn cơ sở dữ liệu
        self.db_path = os.path.join(data_dir, db_name)
        
        # Tạo thư mục cho ảnh sinh viên
        self.photos_dir = os.path.join(data_dir, "student_photos")
        PathHelper.ensure_dir(self.photos_dir)
        
        # Tạo thư mục temp nếu chưa tồn tại (cho xử lý ảnh tạm thời)
        self.temp_dir = PathHelper.get_resource_path("temp")
        PathHelper.ensure_dir(self.temp_dir)
        
        # Danh sách file tạm để xử lý và xóa sau khi không dùng nữa
        self.temp_files = []
        
        self.connection = None
        self.cursor = None
        
        # Kết nối đến cơ sở dữ liệu
        self.connect()
        
        # Tạo các bảng nếu chưa tồn tại
        self.create_tables()
        
        # Tạo tài khoản admin mặc định nếu chưa có
        self.create_default_admin()
        
        logging.info(f"Đã khởi tạo kết nối đến cơ sở dữ liệu: {self.db_path}")

    def connect(self):
        """Thiết lập kết nối đến cơ sở dữ liệu."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Trả về kết quả dưới dạng dictionary
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi kết nối đến cơ sở dữ liệu: {e}")
            return False

    def close(self):
        """Đóng kết nối cơ sở dữ liệu."""
        try:
            # Dọn dẹp tài nguyên trước khi đóng kết nối
            self.cleanup()
            
            if self.connection:
                self.connection.close()
                self.connection = None
                self.cursor = None
                logging.info("Đã đóng kết nối đến cơ sở dữ liệu")
        except Exception as e:
            logging.error(f"Lỗi khi đóng kết nối cơ sở dữ liệu: {e}")

    def commit(self):
        """Lưu các thay đổi vào cơ sở dữ liệu."""
        if self.connection:
            self.connection.commit()

    def create_tables(self):
        """Tạo các bảng trong cơ sở dữ liệu nếu chưa tồn tại."""
        try:
            # Bảng Sinh viên
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                date_of_birth TEXT,
                gender TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                enrolled_date TEXT,
                status TEXT,
                photo_path TEXT
            )
            ''')
            
            # Bảng Khóa học
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                credits INTEGER,
                instructor TEXT,
                description TEXT,
                max_students INTEGER
            )
            ''')
            
            # Bảng Đăng ký khóa học
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                course_id TEXT,
                enrollment_date TEXT,
                grade REAL,
                FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            )
            ''')
            
            # Bảng Người dùng (cho đăng nhập)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                role TEXT,
                is_active INTEGER DEFAULT 1,
                created_date TEXT,
                last_login TEXT
            )
            ''')
            
            # Bảng nhật ký hoạt động
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT NOT NULL,
                action_description TEXT,
                entity_type TEXT,
                entity_id TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            
            self.commit()
            logging.info("Đã tạo các bảng trong cơ sở dữ liệu")
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi tạo bảng: {e}")

    def execute_query(self, query, parameters=()):
        """
        Thực thi truy vấn SQL và trả về kết quả.
        
        Args:
            query (str): Câu truy vấn SQL
            parameters (tuple): Các tham số cho truy vấn
            
        Returns:
            list: Danh sách các kết quả từ truy vấn
        """
        try:
            self.cursor.execute(query, parameters)
            self.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi thực thi truy vấn: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Parameters: {parameters}")
            return []

    def execute_insert(self, query, parameters=()):
        """
        Thực thi truy vấn INSERT và trả về ID của bản ghi mới.
        
        Args:
            query (str): Câu truy vấn INSERT
            parameters (tuple): Các tham số cho truy vấn
            
        Returns:
            int: ID của bản ghi vừa được thêm vào
        """
        try:
            self.cursor.execute(query, parameters)
            self.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi thêm dữ liệu: {e}")
            return None

    def execute_update(self, query, parameters=()):
        """
        Thực thi truy vấn UPDATE và trả về số bản ghi bị ảnh hưởng.
        
        Args:
            query (str): Câu truy vấn UPDATE
            parameters (tuple): Các tham số cho truy vấn
            
        Returns:
            int: Số bản ghi bị ảnh hưởng
        """
        try:
            self.cursor.execute(query, parameters)
            self.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi cập nhật dữ liệu: {e}")
            return 0

    def execute_delete(self, query, parameters=()):
        """
        Thực thi truy vấn DELETE và trả về số bản ghi bị xóa.
        
        Args:
            query (str): Câu truy vấn DELETE
            parameters (tuple): Các tham số cho truy vấn
            
        Returns:
            int: Số bản ghi bị xóa
        """
        try:
            self.cursor.execute(query, parameters)
            self.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi xóa dữ liệu: {e}")
            return 0

    def hash_password(self, password):
        """
        Mã hóa mật khẩu sử dụng SHA-256 với salt.
        
        Args:
            password (str): Mật khẩu cần mã hóa
            
        Returns:
            str: Chuỗi mật khẩu đã được mã hóa kèm salt, định dạng 'salt:hash'
        """
        # Tạo salt ngẫu nhiên
        salt = secrets.token_hex(16)
        # Kết hợp mật khẩu và salt
        salted_password = (password + salt).encode('utf-8')
        # Tạo hash
        password_hash = hashlib.sha256(salted_password).hexdigest()
        # Trả về chuỗi kết hợp salt và hash
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, stored_hash):
        """
        Kiểm tra mật khẩu có khớp với mã hash không.
        
        Args:
            password (str): Mật khẩu cần kiểm tra
            stored_hash (str): Mã hash đã lưu (định dạng 'salt:hash')
            
        Returns:
            bool: True nếu mật khẩu khớp, False nếu không
        """
        try:
            # Kiểm tra xem stored_hash có phải định dạng mới (salt:hash) không
            if ':' in stored_hash:
                # Tách salt và hash
                salt, hash_value = stored_hash.split(':', 1)
                # Tạo hash mới từ mật khẩu nhập vào và salt đã lưu
                salted_password = (password + salt).encode('utf-8')
                calculated_hash = hashlib.sha256(salted_password).hexdigest()
                # So sánh hash
                return calculated_hash == hash_value
            else:
                # Xử lý tương thích ngược với định dạng cũ (chỉ hash không có salt)
                old_hash = hashlib.sha256(password.encode()).hexdigest()
                return old_hash == stored_hash
        except Exception as e:
            logging.error(f"Lỗi khi xác thực mật khẩu: {e}")
            return False
    
    def create_default_admin(self):
        """
        Tạo tài khoản admin mặc định nếu chưa tồn tại.
        """
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
            result = self.execute_query(query)
            
            if result and result[0]['count'] == 0:
                # Không có tài khoản admin nào, tạo tài khoản mặc định
                admin_password = "admin123"  # Mật khẩu mặc định
                password_hash = self.hash_password(admin_password)
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                insert_query = """
                INSERT INTO users (username, password_hash, full_name, email, role, is_active, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    "admin",  # username
                    password_hash,  # password_hash
                    "Administrator",  # full_name
                    "admin@example.com",  # email
                    "admin",  # role
                    1,  # is_active
                    current_time  # created_date
                )
                
                self.cursor.execute(insert_query, params)
                self.commit()
                
                logging.info("Đã tạo tài khoản admin mặc định")
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi tạo tài khoản admin mặc định: {e}")
    
    def save_student_photo(self, student_id, photo_file_path):
        """
        Lưu ảnh đại diện sinh viên
        
        Args:
            student_id (str): Mã số sinh viên
            photo_file_path (str): Đường dẫn đến file ảnh nguồn
            
        Returns:
            str: Đường dẫn đến ảnh đã lưu
        """
        if not os.path.exists(photo_file_path):
            logging.error(f"Không tìm thấy file ảnh: {photo_file_path}")
            return ""
        
        # Lấy phần mở rộng của file
        _, file_extension = os.path.splitext(photo_file_path)
        
        # Tạo tên file mới (mã sinh viên + timestamp để tránh trùng lặp)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{student_id}_{timestamp}{file_extension}"
        
        # Đường dẫn đến file ảnh mới
        new_file_path = os.path.join(self.photos_dir, new_filename)
        
        try:
            # Copy file ảnh đến thư mục lưu trữ
            shutil.copy2(photo_file_path, new_file_path)
            logging.info(f"Đã lưu ảnh sinh viên: {new_file_path}")
            return new_file_path
        except Exception as e:
            logging.error(f"Lỗi khi lưu ảnh sinh viên: {e}")
            return ""
    
    def delete_student_photo(self, photo_path):
        """
        Xóa file ảnh đại diện sinh viên
        
        Args:
            photo_path (str): Đường dẫn đến file ảnh
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        if not photo_path or not os.path.exists(photo_path):
            return False
        
        try:
            os.remove(photo_path)
            logging.info(f"Đã xóa ảnh sinh viên: {photo_path}")
            return True
        except Exception as e:
            logging.error(f"Lỗi khi xóa ảnh sinh viên: {e}")
            return False
    
    def log_activity(self, user_id, action_type, action_description, entity_type=None, entity_id=None):
        """
        Ghi nhật ký hoạt động
        
        Args:
            user_id (int): ID của người dùng thực hiện hành động
            action_type (str): Loại hành động (ADD, UPDATE, DELETE, LOGIN, etc.)
            action_description (str): Mô tả hành động
            entity_type (str): Loại đối tượng tác động (Student, Course, etc.)
            entity_id (str): ID của đối tượng tác động
            
        Returns:
            int: ID của bản ghi nhật ký hoặc None nếu có lỗi
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            query = """
            INSERT INTO activity_log 
            (user_id, action_type, action_description, entity_type, entity_id, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (user_id, action_type, action_description, entity_type, entity_id, current_time)
            
            self.cursor.execute(query, params)
            self.commit()
            
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi ghi nhật ký hoạt động: {e}")
            return None
            
    def get_activities(self, conditions=None, params=None, limit=100):
        """
        Lấy danh sách các hoạt động theo điều kiện
        
        Args:
            conditions (list): Danh sách các điều kiện WHERE
            params (list/tuple): Các tham số cho điều kiện
            limit (int): Giới hạn số lượng kết quả
            
        Returns:
            list: Danh sách các hoạt động
        """
        try:
            query = """
            SELECT 
                a.log_id as id, 
                a.timestamp, 
                u.username, 
                a.action_type, 
                a.action_description, 
                a.entity_type, 
                a.entity_id
            FROM activity_log a
            LEFT JOIN users u ON a.user_id = u.user_id
            """
            
            # Xử lý điều kiện
            if conditions and len(conditions) > 0:
                query += " WHERE " + " AND ".join(conditions)
                
            # Sắp xếp và giới hạn
            query += " ORDER BY a.timestamp DESC"
            
            if limit > 0:
                query += f" LIMIT {limit}"
                
            # Xử lý tham số
            if params is None:
                params = ()
            elif isinstance(params, list):
                params = tuple(params)
                
            return self.execute_query(query, params)
            
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi lấy danh sách hoạt động: {e}")
            return []
    
    def get_recent_activities(self, limit=20):
        """
        Lấy danh sách các hoạt động gần đây
        
        Args:
            limit (int): Số lượng hoạt động tối đa cần lấy
            
        Returns:
            list: Danh sách các hoạt động
        """
        query = """
        SELECT a.*, u.username, u.full_name 
        FROM activity_log a
        LEFT JOIN users u ON a.user_id = u.user_id
        ORDER BY a.timestamp DESC
        LIMIT ?
        """
        return self.execute_query(query, (limit,))

    def check_database_integrity(self):
        """
        Kiểm tra tính toàn vẹn của cơ sở dữ liệu
        
        Returns:
            bool: True nếu cơ sở dữ liệu không có vấn đề, False nếu có lỗi
        """
        try:
            # Kiểm tra tính toàn vẹn bằng pragma
            self.cursor.execute("PRAGMA integrity_check")
            result = self.cursor.fetchone()[0]
            
            if result == "ok":
                logging.info("Kiểm tra toàn vẹn cơ sở dữ liệu: OK")
                return True
            else:
                logging.error(f"Lỗi toàn vẹn cơ sở dữ liệu: {result}")
                return False
                
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi kiểm tra toàn vẹn cơ sở dữ liệu: {e}")
            return False
            
    def optimize_database(self):
        """
        Tối ưu hóa cơ sở dữ liệu
        
        Returns:
            bool: True nếu tối ưu thành công, False nếu có lỗi
        """
        try:
            # VACUUM để giải phóng không gian đĩa không sử dụng
            self.cursor.execute("VACUUM")
            
            # Phân tích lại để tối ưu hóa các index
            self.cursor.execute("ANALYZE")
            
            logging.info("Đã tối ưu hóa cơ sở dữ liệu")
            return True
            
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi tối ưu hóa cơ sở dữ liệu: {e}")
            return False

    def backup_database(self, backup_path=None):
        """
        Tạo bản sao lưu của cơ sở dữ liệu
        
        Args:
            backup_path (str, optional): Đường dẫn tệp sao lưu.
                                        Nếu None, sẽ tạo đường dẫn mặc định
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Nếu không có đường dẫn sao lưu, tạo đường dẫn mặc định
            if backup_path is None:
                backups_dir = os.path.join("data", "backups")
                os.makedirs(backups_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                db_name = os.path.basename(self.db_path)
                backup_name = f"{os.path.splitext(db_name)[0]}_{timestamp}.db"
                backup_path = os.path.join(backups_dir, backup_name)
            
            # Đóng kết nối hiện tại nếu có
            if self.connection:
                self.connection.close()
                self.connection = None
                self.cursor = None
                
            # Sao chép tệp
            shutil.copy2(self.db_path, backup_path)
            
            # Tái kết nối
            self.connect()
            
            logging.info(f"Đã tạo bản sao lưu cơ sở dữ liệu tại: {backup_path}")
            return True
        except Exception as e:
            logging.error(f"Lỗi khi tạo bản sao lưu cơ sở dữ liệu: {e}")
            
            # Đảm bảo kết nối được thiết lập lại
            if not self.connection:
                self.connect()
                
            return False

    def cleanup(self):
        """
        Dọn dẹp tài nguyên khi đóng kết nối
        """
        # Xóa các file tạm
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logging.info(f"Đã xóa file tạm: {temp_file}")
            except Exception as e:
                logging.error(f"Không thể xóa file tạm {temp_file}: {e}")
        
        self.temp_files.clear()