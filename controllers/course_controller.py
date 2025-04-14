from models.course import Course
import logging

class CourseController:
    """
    Controller quản lý các thao tác liên quan đến khóa học.
    """
    def __init__(self, db_manager):
        """
        Khởi tạo controller với tham chiếu đến database manager.
        
        Args:
            db_manager: Đối tượng quản lý cơ sở dữ liệu
        """
        self.db_manager = db_manager
        logging.info("Đã khởi tạo CourseController")
    
    def get_all_courses(self):
        """
        Lấy danh sách tất cả khóa học.
        
        Returns:
            list: Danh sách các đối tượng Course
        """
        query = "SELECT * FROM courses ORDER BY course_id"
        result = self.db_manager.execute_query(query)
        
        courses = []
        for row in result:
            course_data = dict(row)
            courses.append(Course.from_dict(course_data))
            
        logging.info(f"Lấy danh sách khóa học: {len(courses)} khóa học")
        return courses
    
    def get_course_by_id(self, course_id):
        """
        Lấy thông tin khóa học theo ID.
        
        Args:
            course_id (str): Mã khóa học cần tìm
            
        Returns:
            Course: Đối tượng khóa học nếu tìm thấy, None nếu không tồn tại
        """
        query = "SELECT * FROM courses WHERE course_id = ?"
        result = self.db_manager.execute_query(query, (course_id,))
        
        if result:
            course_data = dict(result[0])
            course = Course.from_dict(course_data)
            logging.info(f"Tìm thấy khóa học: {course}")
            return course
        
        logging.warning(f"Không tìm thấy khóa học với ID: {course_id}")
        return None
    
    def search_courses(self, keyword):
        """
        Tìm kiếm khóa học theo từ khóa.
        
        Args:
            keyword (str): Từ khóa tìm kiếm (có thể là ID, tên, giảng viên, v.v.)
            
        Returns:
            list: Danh sách các đối tượng Course phù hợp
        """
        keyword = f"%{keyword}%"
        query = """
        SELECT * FROM courses 
        WHERE course_id LIKE ? OR course_name LIKE ? OR instructor LIKE ? OR description LIKE ?
        ORDER BY course_id
        """
        result = self.db_manager.execute_query(query, (keyword, keyword, keyword, keyword))
        
        courses = []
        for row in result:
            course_data = dict(row)
            courses.append(Course.from_dict(course_data))
            
        logging.info(f"Tìm kiếm khóa học với từ khóa '{keyword}': {len(courses)} kết quả")
        return courses
    
    def add_course(self, course):
        """
        Thêm khóa học mới vào cơ sở dữ liệu.
        
        Args:
            course (Course): Đối tượng khóa học cần thêm
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Kiểm tra xem khóa học đã tồn tại chưa
        existing_course = self.get_course_by_id(course.course_id)
        if existing_course:
            logging.warning(f"Khóa học với ID {course.course_id} đã tồn tại")
            return False
        
        query = """
        INSERT INTO courses 
        (course_id, course_name, credits, instructor, description, max_students)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            course.course_id,
            course.course_name,
            course.credits,
            course.instructor,
            course.description,
            course.max_students
        )
        
        result = self.db_manager.execute_insert(query, params)
        success = result is not None
        
        if success:
            logging.info(f"Đã thêm khóa học: {course}")
        else:
            logging.error(f"Không thể thêm khóa học: {course}")
            
        return success
    
    def update_course(self, course):
        """
        Cập nhật thông tin khóa học.
        
        Args:
            course (Course): Đối tượng khóa học cần cập nhật
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        query = """
        UPDATE courses SET 
            course_name = ?, 
            credits = ?, 
            instructor = ?, 
            description = ?, 
            max_students = ?
        WHERE course_id = ?
        """
        
        params = (
            course.course_name,
            course.credits,
            course.instructor,
            course.description,
            course.max_students,
            course.course_id
        )
        
        rows_affected = self.db_manager.execute_update(query, params)
        success = rows_affected > 0
        
        if success:
            logging.info(f"Đã cập nhật khóa học: {course}")
        else:
            logging.warning(f"Không thể cập nhật khóa học: {course}")
            
        return success
    
    def delete_course(self, course_id):
        """
        Xóa khóa học khỏi cơ sở dữ liệu.
        
        Args:
            course_id (str): Mã khóa học cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        query = "DELETE FROM courses WHERE course_id = ?"
        rows_affected = self.db_manager.execute_delete(query, (course_id,))
        success = rows_affected > 0
        
        if success:
            logging.info(f"Đã xóa khóa học với ID: {course_id}")
        else:
            logging.warning(f"Không thể xóa khóa học với ID: {course_id}")
            
        return success
    
    def get_course_count(self):
        """
        Lấy tổng số khóa học trong hệ thống.
        
        Returns:
            int: Số lượng khóa học
        """
        query = "SELECT COUNT(*) as count FROM courses"
        result = self.db_manager.execute_query(query)
        
        if result:
            return result[0]['count']
        return 0
    
    def get_enrollment_count(self, course_id):
        """
        Lấy số lượng sinh viên đã đăng ký khóa học.
        
        Args:
            course_id (str): Mã khóa học
            
        Returns:
            int: Số lượng sinh viên đã đăng ký
        """
        query = "SELECT COUNT(*) as count FROM enrollments WHERE course_id = ?"
        result = self.db_manager.execute_query(query, (course_id,))
        
        if result:
            return result[0]['count']
        return 0