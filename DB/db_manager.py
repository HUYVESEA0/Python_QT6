import sqlite3
import os
import logging
import secrets
import hashlib
import shutil
from datetime import datetime
from utils.config_manager import ConfigManager

class DatabaseManager:
    """
    Lớp quản lý kết nối và thao tác với cơ sở dữ liệu SQLite.
    """
    
    def __init__(self, db_path: str | None):
        """
        Khởi tạo kết nối cơ sở dữ liệu
        
        Args:
            db_path (str, optional): Đường dẫn đến file cơ sở dữ liệu
        """
        # Ensure self.cursor is always defined
        self.connection = None
        self.cursor = None
        try:
            config_manager = ConfigManager()
            
            if db_path is None:
                db_path = config_manager.get_db_path()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.db_path = db_path
            # self.connection and self.cursor are already set to None above
            self.connect()

            # Thêm thuộc tính photos_dir
            self.photos_dir = os.path.join(os.path.dirname(db_path), "photos")
            os.makedirs(self.photos_dir, exist_ok=True)
            
            # Initialize temp_files list to track temporary files for cleanup
            self.temp_files = []

        except (sqlite3.Error, OSError, ValueError) as e:
            logging.error("Error initializing database connection: %s", str(e))
            raise

    # Add a property to alias connection as conn for compatibility
    @property
    def conn(self):
        """Alias for connection attribute to maintain compatibility with other code."""
        return self.connection

    def _create_connection(self, db_path: str | None):
        """
        Create a database connection to the SQLite database specified by db_path.
        
        Args:
            db_path (str): Path to the SQLite database file
            
        Returns:
            Connection object or None
        """
        try:
            if db_path is None:
                raise ValueError("Database path cannot be None.")
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            logging.info("Connected to database at %s", db_path)
            return connection
        except sqlite3.Error as e:
            logging.error("Error connecting to database: %s", e)         
            return None
        except (OSError, ValueError) as e:
            # More specific than generic Exception - catches file system errors and value errors
            logging.error("General error in _create_connection: %s", e)
            return None

    def connect(self):
        """Thiết lập kết nối đến cơ sở dữ liệu."""
        if self.connection is None:
            self.connection = self._create_connection(self.db_path)
        if self.connection:
            self.cursor = self.connection.cursor()

    def close(self):
        """Close database connection."""
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
                logging.info("Database connection closed successfully")
        except sqlite3.Error as e:
            logging.error("Error closing database connection: %s",e)

    def commit(self):
        """Lưu các thay đổi vào cơ sở dữ liệu."""
        if self.connection:
            self.connection.commit()

    def _ensure_connection(self):
        """Ensure that the database connection and cursor are available."""
        if not hasattr(self, 'cursor') or self.cursor is None or self.connection is None:
            self.connect()

    def create_tables(self):
        """Tạo các bảng trong cơ sở dữ liệu nếu chưa tồn tại (tên tiếng Việt)."""
        self._ensure_connection()
        try:
            # Bảng Sinh viên
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinh_vien (
                ma_sinh_vien TEXT PRIMARY KEY,
                ho_ten TEXT NOT NULL,
                ngay_sinh TEXT,
                gioi_tinh TEXT,
                email TEXT,
                so_dien_thoai TEXT,
                dia_chi TEXT,
                ngay_nhap_hoc TEXT,
                trang_thai TEXT,
                duong_dan_anh TEXT
            )
            ''')
            # Bảng Khóa học
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS khoa_hoc (
                ma_khoa_hoc TEXT PRIMARY KEY,
                ten_khoa_hoc TEXT NOT NULL,
                so_tin_chi INTEGER,
                giang_vien TEXT,
                mo_ta TEXT,
                so_luong_toi_da INTEGER
            )
            ''')
            # Bảng Ghi danh (Đăng ký khóa học)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ghi_danh (
                ma_ghi_danh INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_sinh_vien TEXT,
                ma_khoa_hoc TEXT,
                ngay_ghi_danh TEXT,
                diem REAL,
                FOREIGN KEY (ma_sinh_vien) REFERENCES sinh_vien (ma_sinh_vien) ON DELETE CASCADE,
                FOREIGN KEY (ma_khoa_hoc) REFERENCES khoa_hoc (ma_khoa_hoc) ON DELETE CASCADE,
                UNIQUE(ma_sinh_vien, ma_khoa_hoc)
            )
            ''')
            # Bảng Người dùng
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nguoi_dung (
                ma_nguoi_dung INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_dang_nhap TEXT UNIQUE NOT NULL,
                mat_khau_ma_hoa TEXT NOT NULL,
                ho_ten TEXT,
                email TEXT,
                vai_tro TEXT,
                kich_hoat INTEGER DEFAULT 1,
                ngay_tao TEXT,
                lan_dang_nhap_cuoi TEXT
            )
            ''')
            # Bảng nhật ký hoạt động
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nhat_ky_hoat_dong (
                ma_nhat_ky INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_nguoi_dung INTEGER,
                loai_hoat_dong TEXT NOT NULL,
                mo_ta_hoat_dong TEXT,
                loai_doi_tuong TEXT,
                ma_doi_tuong TEXT,
                thoi_gian TEXT NOT NULL,
                FOREIGN KEY (ma_nguoi_dung) REFERENCES nguoi_dung(ma_nguoi_dung)
            )
            ''')
            self.commit()
            logging.info("Đã tạo các bảng tiếng Việt trong cơ sở dữ liệu")
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
        self._ensure_connection()
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
        except (ValueError, TypeError, IndexError) as e:
            logging.error(f"Lỗi khi xác thực mật khẩu: {e}")
            return False
    
    def create_default_admin(self):
        """
        Tạo tài khoản admin mặc định nếu chưa tồn tại.
        """
        try:
            query = "SELECT COUNT(*) as count FROM nguoi_dung WHERE vai_tro = 'admin'"
            result = self.execute_query(query)
            
            if result and result[0]['count'] == 0:
                # Không có tài khoản admin nào, tạo tài khoản mặc định
                admin_password = "admin123"  # Mật khẩu mặc định
                mat_khau_ma_hoa = self.hash_password(admin_password)
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                insert_query = """
                INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_ma_hoa, ho_ten, email, vai_tro, kich_hoat, ngay_tao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    "admin",  # ten_dang_nhap
                    mat_khau_ma_hoa,  # mat_khau_ma_hoa
                    "Administrator",  # ho_ten
                    "admin@example.com",  # email
                    "admin",  # vai_tro
                    1,  # kich_hoat
                    current_time  # ngay_tao
                )
                
                self.cursor.execute(insert_query, params)
                self.commit()
                
                logging.info("Đã tạo tài khoản admin mặc định")
        except Exception as e:
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
        except OSError as e:
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
        self._ensure_connection()
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
        self._ensure_connection()
        try:
            query = """
            SELECT 
                a.log_id as log_id, -- Changed from 'id' to 'log_id'
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
        self._ensure_connection()
        query = """
        SELECT 
            a.log_id as id, 
            a.timestamp, 
            a.user_id,
            u.username, 
            u.ho_ten,
            a.action_type, 
            a.action_description, 
            a.entity_type, 
            a.entity_id
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
        self._ensure_connection()
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
        self._ensure_connection()
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
        except (OSError, sqlite3.Error, shutil.Error) as e:
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
            except OSError as e:
                logging.error(f"Không thể xóa file tạm {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def ensure_tables_exist(self):
        """Ensure all required tables exist in the database."""
        self._ensure_connection()
        try:
            # Tạo lại tất cả các bảng cần thiết nếu chưa có
            self.create_tables()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error ensuring tables exist: {e}")
            return False