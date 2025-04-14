import sqlite3
import os
import logging

class DatabaseManager:
    """
    Lớp quản lý kết nối và thao tác với cơ sở dữ liệu SQLite.
    """
    def __init__(self, db_path="student_management.db"):
        """Khởi tạo kết nối đến cơ sở dữ liệu."""
        # Tạo thư mục chứa database nếu chưa tồn tại
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # Kết nối đến cơ sở dữ liệu
        self.connect()
        
        # Tạo các bảng nếu chưa tồn tại
        self.create_tables()
        
        logging.info(f"Đã khởi tạo kết nối đến cơ sở dữ liệu: {db_path}")

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