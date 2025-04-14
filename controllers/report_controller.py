import logging
from datetime import datetime

class ReportController:
    """
    Controller quản lý các báo cáo và thống kê.
    """
    def __init__(self, db_manager):
        """
        Khởi tạo controller với tham chiếu đến database manager.
        
        Args:
            db_manager: Đối tượng quản lý cơ sở dữ liệu
        """
        self.db_manager = db_manager
        logging.info("Đã khởi tạo ReportController")
    
    def get_student_course_statistics(self):
        """
        Lấy thống kê số lượng sinh viên và khóa học.
        
        Returns:
            dict: Dictionary chứa các thống kê cơ bản
        """
        stats = {}
        
        # Tổng số sinh viên
        query = "SELECT COUNT(*) as count FROM students"
        result = self.db_manager.execute_query(query)
        stats['total_students'] = result[0]['count'] if result else 0
        
        # Tổng số khóa học
        query = "SELECT COUNT(*) as count FROM courses"
        result = self.db_manager.execute_query(query)
        stats['total_courses'] = result[0]['count'] if result else 0
        
        # Tổng số đăng ký
        query = "SELECT COUNT(*) as count FROM enrollments"
        result = self.db_manager.execute_query(query)
        stats['total_enrollments'] = result[0]['count'] if result else 0
        
        # Điểm trung bình của tất cả các khóa học
        query = "SELECT AVG(grade) as avg_grade FROM enrollments WHERE grade IS NOT NULL"
        result = self.db_manager.execute_query(query)
        stats['average_grade'] = round(result[0]['avg_grade'], 2) if result and result[0]['avg_grade'] else 0
        
        logging.info("Đã lấy thống kê cơ bản về sinh viên và khóa học")
        return stats
    
    def get_top_courses_by_enrollment(self, limit=5):
        """
        Lấy danh sách các khóa học có nhiều sinh viên đăng ký nhất.
        
        Args:
            limit (int): Số lượng khóa học muốn lấy
        
        Returns:
            list: Danh sách các khóa học kèm số lượng sinh viên đăng ký
        """
        query = """
        SELECT c.course_id, c.course_name, COUNT(e.student_id) as student_count
        FROM courses c
        LEFT JOIN enrollments e ON c.course_id = e.course_id
        GROUP BY c.course_id
        ORDER BY student_count DESC
        LIMIT ?
        """
        
        result = self.db_manager.execute_query(query, (limit,))
        top_courses = []
        
        for row in result:
            top_courses.append(dict(row))
        
        logging.info(f"Đã lấy {len(top_courses)} khóa học có nhiều sinh viên đăng ký nhất")
        return top_courses
    
    def get_grade_distribution(self):
        """
        Lấy phân phối điểm số của sinh viên.
        
        Returns:
            dict: Dictionary chứa phân phối điểm
        """
        grade_ranges = {
            'A (8.5-10)': 0,
            'B (7.0-8.4)': 0,
            'C (5.5-6.9)': 0,
            'D (4.0-5.4)': 0,
            'F (0-3.9)': 0
        }
        
        query = "SELECT grade FROM enrollments WHERE grade IS NOT NULL"
        result = self.db_manager.execute_query(query)
        
        for row in result:
            grade = row['grade']
            if grade >= 8.5:
                grade_ranges['A (8.5-10)'] += 1
            elif grade >= 7.0:
                grade_ranges['B (7.0-8.4)'] += 1
            elif grade >= 5.5:
                grade_ranges['C (5.5-6.9)'] += 1
            elif grade >= 4.0:
                grade_ranges['D (4.0-5.4)'] += 1
            else:
                grade_ranges['F (0-3.9)'] += 1
        
        logging.info("Đã lấy phân phối điểm của sinh viên")
        return grade_ranges
    
    def get_student_performance(self, student_id):
        """
        Lấy thông tin về kết quả học tập của sinh viên.
        
        Args:
            student_id (str): Mã số sinh viên
            
        Returns:
            dict: Dictionary chứa thông tin kết quả học tập
        """
        performance = {
            'student_id': student_id,
            'courses_enrolled': 0,
            'courses_completed': 0,
            'average_grade': 0.0,
            'course_details': []
        }
        
        # Thông tin cơ bản
        query = """
        SELECT 
            COUNT(*) as total_courses,
            COUNT(CASE WHEN grade IS NOT NULL THEN 1 ELSE NULL END) as completed_courses,
            AVG(grade) as avg_grade
        FROM enrollments
        WHERE student_id = ?
        """
        
        result = self.db_manager.execute_query(query, (student_id,))
        if result:
            performance['courses_enrolled'] = result[0]['total_courses']
            performance['courses_completed'] = result[0]['completed_courses']
            performance['average_grade'] = round(result[0]['avg_grade'], 2) if result[0]['avg_grade'] else 0.0
        
        # Chi tiết khóa học
        query = """
        SELECT 
            c.course_id, 
            c.course_name, 
            c.credits, 
            e.enrollment_date,
            e.grade
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
        ORDER BY e.enrollment_date DESC
        """
        
        result = self.db_manager.execute_query(query, (student_id,))
        for row in result:
            performance['course_details'].append(dict(row))
        
        logging.info(f"Đã lấy thông tin kết quả học tập của sinh viên {student_id}")
        return performance