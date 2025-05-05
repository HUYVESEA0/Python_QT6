from models.student import Student
import logging
import os

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
    
    def add_student(self, student, photo_file_path=None, current_user_id=None):
        """
        Thêm sinh viên vào cơ sở dữ liệu.
        
        Args:
            student (Student): Đối tượng sinh viên
            photo_file_path (str, optional): Đường dẫn đến file ảnh đại diện
            current_user_id (int, optional): ID của người dùng thực hiện
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Kiểm tra sinh viên đã tồn tại chưa
        if self.get_student_by_id(student.student_id):
            logging.warning(f"Sinh viên đã tồn tại với ID: {student.student_id}")
            return False
        
        # Xử lý ảnh đại diện nếu có
        saved_photo_path = ""
        if photo_file_path:
            # Nếu là ảnh mặc định thì không lưu
            if photo_file_path.endswith("default_avatar.png"):
                saved_photo_path = ""
            else:
                try:
                    saved_photo_path = self.db_manager.save_student_photo(student.student_id, photo_file_path)
                except Exception as e:
                    logging.error("Lỗi khi lưu ảnh sinh viên: %s", e)

        # Tạo truy vấn
        query = """
        INSERT INTO students (
            student_id, full_name, date_of_birth, gender, email, 
            phone, address, enrolled_date, status, photo_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            student.student_id, student.full_name, student.date_of_birth,
            student.gender, student.email, student.phone, student.address,
            student.enrolled_date, student.status, saved_photo_path
        )
        
        try:
            inserted_id = self.db_manager.execute_insert(query, params)
            success = inserted_id is not None
            
            if success:
                logging.info(f"Đã thêm sinh viên: {student.student_id} - {student.full_name}")

                # Ghi nhật ký hoạt động
                if current_user_id:
                    self.db_manager.log_activity(
                        current_user_id,
                        "ADD",
                        f"Thêm sinh viên: {student.full_name}",
                        "Student",
                        student.student_id
                    )
            else:
                logging.warning(f"Không thể thêm sinh viên: {student.student_id}")
                
            return success
        except Exception as e:
            logging.error("Lỗi khi thêm sinh viên: %s", e)
            return False
    
    def update_student(self, student, photo_file_path=None, current_user_id=None):
        """
        Cập nhật thông tin sinh viên.
        
        Args:
            student (Student): Đối tượng sinh viên cần cập nhật
            photo_file_path (str): Đường dẫn đến file ảnh mới (nếu có)
            current_user_id (int): ID của người dùng thực hiện hành động
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Lấy thông tin sinh viên hiện tại
        existing_student = self.get_student_by_id(student.student_id)
        if not existing_student:
            logging.warning(f"Không tìm thấy sinh viên với ID {student.student_id} để cập nhật")
            return False
        
        # Xử lý ảnh đại diện nếu có thay đổi
        if photo_file_path:
            # Nếu là ảnh mặc định thì xóa ảnh cũ và không lưu mới
            if photo_file_path.endswith("default_avatar.png"):
                if existing_student.photo_path:
                    self.db_manager.delete_student_photo(existing_student.photo_path)
                student.photo_path = ""
            else:
                if existing_student.photo_path:
                    self.db_manager.delete_student_photo(existing_student.photo_path)
                photo_path = self.db_manager.save_student_photo(student.student_id, photo_file_path)
                student.photo_path = photo_path
        else:
            student.photo_path = existing_student.photo_path
        
        query = """
        UPDATE students SET 
            full_name = ?, 
            date_of_birth = ?, 
            gender = ?, 
            email = ?, 
            phone = ?, 
            address = ?, 
            enrolled_date = ?, 
            status = ?,
            photo_path = ?
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
            student.photo_path,
            student.student_id
        )
        
        rows_affected = self.db_manager.execute_update(query, params)
        success = rows_affected > 0
        
        if success:
            logging.info("Đã cập nhật sinh viên: %s", student)
            
            # Ghi nhật ký hoạt động
            if current_user_id:
                self.db_manager.log_activity(
                    user_id=current_user_id,
                    action_type="UPDATE",
                    action_description=f"Cập nhật thông tin sinh viên: {student.full_name}",
                    entity_type="Student",
                    entity_id=student.student_id
                )
        else:
            logging.warning("Không thể cập nhật sinh viên: %s", student)
            
        return success
    
    def delete_student(self, student_id, current_user_id=None):
        """
        Xóa sinh viên khỏi cơ sở dữ liệu.
        
        Args:
            student_id (str): Mã số sinh viên cần xóa
            current_user_id (int): ID của người dùng thực hiện hành động
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy thông tin sinh viên để lưu nhật ký và xóa ảnh
            student = self.get_student_by_id(student_id)
            if not student:
                logging.warning(f"Không tìm thấy sinh viên với ID {student_id} để xóa")
                return False
            
            # Lưu thông tin để ghi nhật ký
            student_name = student.full_name
            
            # Xóa ảnh nếu có
            if student.photo_path and os.path.exists(student.photo_path):
                try:
                    self.db_manager.delete_student_photo(student.photo_path)
                except Exception as e:
                    logging.error(f"Lỗi khi xóa ảnh sinh viên: {e}")
            
            # Xóa sinh viên
            query = "DELETE FROM students WHERE student_id = ?"
            rows_affected = self.db_manager.execute_delete(query, (student_id,))
            success = rows_affected > 0
            
            if success:
                logging.info(f"Đã xóa sinh viên với ID: {student_id}")
                
                # Ghi nhật ký hoạt động
                if current_user_id:
                    self.db_manager.log_activity(
                        user_id=current_user_id,
                        action_type="DELETE",
                        action_description=f"Xóa sinh viên: {student_name}",
                        entity_type="Student",
                        entity_id=student_id
                    )
            else:
                logging.warning(f"Không thể xóa sinh viên với ID: {student_id}")
                
            return success
        except Exception as e:
            logging.error(f"Lỗi khi xóa sinh viên: {e}")
            return False
    
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
        
    def advanced_search(self, filters):
        """
        Tìm kiếm sinh viên với nhiều điều kiện lọc.
        
        Args:
            filters (dict): Các điều kiện lọc
            
        Returns:
            list: Danh sách các đối tượng Student phù hợp
        """
        conditions = []
        params = []
        
        # Xây dựng các điều kiện tìm kiếm từ filters
        if 'student_id' in filters and filters['student_id']:
            conditions.append("student_id LIKE ?")
            params.append(f"%{filters['student_id']}%")
            
        if 'name' in filters and filters['name']:
            conditions.append("full_name LIKE ?")
            params.append(f"%{filters['name']}%")
            
        if 'gender' in filters and filters['gender']:
            conditions.append("gender = ?")
            params.append(filters['gender'])
            
        if 'status' in filters and filters['status']:
            conditions.append("status = ?")
            params.append(filters['status'])
            
        # Thêm các điều kiện khác tùy theo yêu cầu
        
        # Nếu không có điều kiện nào, trả về tất cả sinh viên
        if not conditions:
            return self.get_all_students()
            
        # Tạo câu truy vấn
        query = "SELECT * FROM students WHERE " + " AND ".join(conditions) + " ORDER BY student_id"
        
        # Thực thi truy vấn
        result = self.db_manager.execute_query(query, tuple(params))
        
        students = []
        for row in result:
            student_data = dict(row)
            students.append(Student.from_dict(student_data))
            
        logging.info(f"Tìm kiếm nâng cao: {len(students)} kết quả")
        return students