import sqlite3
import os
import logging
import hashlib

class DatabaseManager:
    """
    Lớp quản lý kết nối và thao tác với cơ sở dữ liệu SQLite.
    """
    def __init__(self, db_path="app.db"):
        """Khởi tạo kết nối đến cơ sở dữ liệu."""
        # Ensure db_path has a directory component
        if os.path.dirname(db_path) == '':
            # If no directory specified, use 'data' directory in the current directory
            data_dir = os.path.join(os.getcwd(), "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, db_path)
        else:
            # If directory is specified, ensure it exists
            directory = os.path.dirname(db_path)
            os.makedirs(directory, exist_ok=True)
            self.db_path = db_path
        
        self.connection = None
        self.cursor = None
        
        # Kết nối đến cơ sở dữ liệu
        self.connect()
        
        # Tạo các bảng nếu chưa tồn tại
        self.create_tables()
        
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
        if self.connection:
            self.connection.close()
            logging.info("Đã đóng kết nối cơ sở dữ liệu")

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
                status TEXT
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
        Mã hóa mật khẩu sử dụng SHA-256.
        
        Args:
            password (str): Mật khẩu cần mã hóa
            
        Returns:
            str: Chuỗi mật khẩu đã được mã hóa
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """
        Kiểm tra mật khẩu có khớp với mã hash không.
        
        Args:
            password (str): Mật khẩu cần kiểm tra
            password_hash (str): Mã hash đã lưu
            
        Returns:
            bool: True nếu mật khẩu khớp, False nếu không
        """
        return self.hash_password(password) == password_hash
    
    def create_default_admin(self):
        """
        Tạo tài khoản admin mặc định nếu chưa tồn tại.
        """
        admin_exists = self.execute_query("SELECT COUNT(*) as count FROM users WHERE username = ?", ("admin",))
        
        if admin_exists[0]['count'] == 0:
            # Tạo tài khoản admin với mật khẩu mặc định là "admin"
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            query = """
            INSERT INTO users (username, password_hash, full_name, email, role, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.execute_insert(query, (
                "admin",
                self.hash_password("admin"),
                "Administrator",
                "admin@example.com",
                "admin",
                current_date
            ))
            
            logging.info("Đã tạo tài khoản admin mặc định")