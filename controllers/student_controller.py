from models.student import Student
import logging

class StudentController:
    """
    Controller quản lý các thao tác liên quan đến sinh viên.
    """
    def __init__(self, db_manager):
        """
        Khởi tạo controller với tham chiếu đến database manager.
        
        Args:
            db_manager: Đối tượng quản lý cơ sở dữ liệu
        """
        self.db_manager = db_manager
        logging.info("Đã khởi tạo StudentController")
    
    def get_all_students(self):
        """
        Lấy danh sách tất cả sinh viên.
        
        Returns:
            list: Danh sách các đối tượng Student
        """
        query = "SELECT * FROM students ORDER BY student_id"
        result = self.db_manager.execute_query(query)
        
        students = []
        for row in result:
            # Chuyển đổi từ kết quả sqlite.Row sang dict
            student_data = dict(row)
            students.append(Student.from_dict(student_data))
            
        logging.info(f"Lấy danh sách sinh viên: {len(students)} sinh viên")
        return students
    
    def get_student_by_id(self, student_id):
        """
        Lấy thông tin sinh viên theo ID.
        
        Args:
            student_id (str): Mã số sinh viên cần tìm
            
        Returns:
            Student: Đối tượng sinh viên nếu tìm thấy, None nếu không tồn tại
        """
        query = "SELECT * FROM students WHERE student_id = ?"
        result = self.db_manager.execute_query(query, (student_id,))
        
        if result:
            student_data = dict(result[0])
            student = Student.from_dict(student_data)
            logging.info(f"Tìm thấy sinh viên: {student}")
            return student
        
        logging.warning(f"Không tìm thấy sinh viên với ID: {student_id}")
        return None
    
    def search_students(self, keyword):
        """
        Tìm kiếm sinh viên theo từ khóa.
        
        Args:
            keyword (str): Từ khóa tìm kiếm (có thể là ID, tên, email, v.v.)
            
        Returns:
            list: Danh sách các đối tượng Student phù hợp
        """
        keyword = f"%{keyword}%"
        query = """
        SELECT * FROM students 
        WHERE student_id LIKE ? OR full_name LIKE ? OR email LIKE ? OR phone LIKE ?
        ORDER BY student_id
        """
        result = self.db_manager.execute_query(query, (keyword, keyword, keyword, keyword))
        
        students = []
        for row in result:
            student_data = dict(row)
            students.append(Student.from_dict(student_data))
            
        logging.info(f"Tìm kiếm sinh viên với từ khóa '{keyword}': {len(students)} kết quả")
        return students
    
    def add_student(self, student):
        """
        Thêm sinh viên mới vào cơ sở dữ liệu.
        
        Args:
            student (Student): Đối tượng sinh viên cần thêm
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Kiểm tra xem sinh viên đã tồn tại chưa
        existing_student = self.get_student_by_id(student.student_id)
        if existing_student:
            logging.warning(f"Sinh viên với ID {student.student_id} đã tồn tại")
            return False
        
        query = """
        INSERT INTO students 
        (student_id, full_name, date_of_birth, gender, email, phone, address, enrolled_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            student.student_id,
            student.full_name,
            student.date_of_birth,
            student.gender,
            student.email,
            student.phone,
            student.address,
            student.enrolled_date,
            student.status
        )
        
        result = self.db_manager.execute_insert(query, params)
        success = result is not None
        
        if success:
            logging.info(f"Đã thêm sinh viên: {student}")
        else:
            logging.error(f"Không thể thêm sinh viên: {student}")
            
        return success
    
    def update_student(self, student):
        """
        Cập nhật thông tin sinh viên.
        
        Args:
            student (Student): Đối tượng sinh viên cần cập nhật
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        query = """
        UPDATE students SET 
            full_name = ?, 
            date_of_birth = ?, 
            gender = ?, 
            email = ?, 
            phone = ?, 
            address = ?, 
            enrolled_date = ?, 
            status = ?
        WHERE student_id = ?
        """
        
        params = (
            student.full_name,
            student.date_of_birth,
            student.gender,
            student.email,
            student.phone,
            student.address,
            student.enrolled_date,
            student.status,
            student.student_id
        )
        
        rows_affected = self.db_manager.execute_update(query, params)
        success = rows_affected > 0
        
        if success:
            logging.info(f"Đã cập nhật sinh viên: {student}")
        else:
            logging.warning(f"Không thể cập nhật sinh viên: {student}")
            
        return success
    
    def delete_student(self, student_id):
        """
        Xóa sinh viên khỏi cơ sở dữ liệu.
        
        Args:
            student_id (str): Mã số sinh viên cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        query = "DELETE FROM students WHERE student_id = ?"
        rows_affected = self.db_manager.execute_delete(query, (student_id,))
        success = rows_affected > 0
        
        if success:
            logging.info(f"Đã xóa sinh viên với ID: {student_id}")
        else:
            logging.warning(f"Không thể xóa sinh viên với ID: {student_id}")
            
        return success
    
    def get_student_count(self):
        """
        Lấy tổng số sinh viên trong hệ thống.
        
        Returns:
            int: Số lượng sinh viên
        """
        query = "SELECT COUNT(*) as count FROM students"
        result = self.db_manager.execute_query(query)
        
        if result:
            return result[0]['count']
        return 0