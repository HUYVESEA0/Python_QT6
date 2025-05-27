import logging
from models.course import Course
import sqlite3

class ReportController:
    """
    Controller quản lý các thao tác liên quan đến báo cáo thống kê
    """
    
    def __init__(self, db_manager):
        """
        Khởi tạo ReportController
        
        Args:
            db_manager: Đối tượng quản lý cơ sở dữ liệu
        """
        self.db_manager = db_manager
        logging.info("Đã khởi tạo ReportController")
    
    def get_student_course_statistics(self):
        """
        Lấy thống kê tổng quan về sinh viên và khóa học
        
        Returns:
            dict: Thông tin thống kê cơ bản
        """
        stats = {}
        
        # Tổng số sinh viên
        query = "SELECT COUNT(*) AS count FROM students"
        result = self.db_manager.execute_query(query)
        if result:
            stats['total_students'] = result[0]['count']
        else:
            stats['total_students'] = 0
        
        # Tổng số khóa học
        query = "SELECT COUNT(*) AS count FROM courses"
        result = self.db_manager.execute_query(query)
        if result:
            stats['total_courses'] = result[0]['count']
        else:
            stats['total_courses'] = 0
        
        # Tổng số đăng ký
        query = "SELECT COUNT(*) AS count FROM enrollments"
        result = self.db_manager.execute_query(query)
        if result:
            stats['total_enrollments'] = result[0]['count']
        else:
            stats['total_enrollments'] = 0
        
        # Điểm trung bình
        query = "SELECT AVG(grade) AS avg_grade FROM enrollments WHERE grade IS NOT NULL"
        result = self.db_manager.execute_query(query)
        if result and result[0]['avg_grade'] is not None:
            stats['average_grade'] = result[0]['avg_grade']
        else:
            stats['average_grade'] = 0
        
        return stats
    
    def get_student_status_statistics(self):
        """
        Lấy thống kê trạng thái sinh viên
        
        Returns:
            dict: Dictionary chứa số lượng sinh viên theo từng trạng thái
        """
        query = """
        SELECT status, COUNT(*) AS count 
        FROM students
        GROUP BY status
        ORDER BY count DESC
        """
        result = self.db_manager.execute_query(query)
        
        stats = {}
        if result:
            for row in result:
                stats[row['status']] = row['count']
        
        return stats
    
    def get_student_gender_statistics(self):
        """
        Lấy thống kê giới tính sinh viên
        
        Returns:
            dict: Dictionary chứa số lượng sinh viên theo giới tính
        """
        query = """
        SELECT gender, COUNT(*) AS count 
        FROM students
        GROUP BY gender
        ORDER BY count DESC
        """
        result = self.db_manager.execute_query(query)
        
        stats = {}
        if result:
            for row in result:
                gender = row['gender'] if row['gender'] else "Chưa xác định"
                stats[gender] = row['count']
        
        return stats
    
    def get_top_courses_by_enrollment(self, limit=5):
        """
        Lấy danh sách khóa học có nhiều sinh viên đăng ký nhất
        
        Args:
            limit (int): Số lượng khóa học tối đa cần lấy
            
        Returns:
            list: Danh sách các dictionary chứa thông tin khóa học và số lượng sinh viên
        """
        query = """
        SELECT c.course_id, c.course_name, COUNT(e.student_id) AS student_count
        FROM courses c
        LEFT JOIN enrollments e ON c.course_id = e.course_id
        GROUP BY c.course_id, c.course_name
        ORDER BY student_count DESC
        LIMIT ?
        """
        result = self.db_manager.execute_query(query, (limit,))
        
        return result if result else []
    
    def get_course_credits_statistics(self):
        """
        Lấy thống kê khóa học theo số tín chỉ
        
        Returns:
            dict: Dictionary chứa số lượng khóa học theo số tín chỉ
        """
        query = """
        SELECT credits, COUNT(*) AS count 
        FROM courses
        GROUP BY credits
        ORDER BY credits ASC
        """
        result = self.db_manager.execute_query(query)
        
        stats = {}
        if result:
            for row in result:
                stats[row['credits']] = row['count']
        
        return stats
    
    def get_grade_statistics(self):
        """
        Lấy thống kê điểm số của sinh viên theo phân loại
        
        Returns:
            dict: Dictionary chứa số lượng sinh viên theo từng phân loại điểm
        """
        query = """
        SELECT 
            CASE
                WHEN grade >= 9.0 THEN 'Xuất sắc (9.0 - 10.0)'
                WHEN grade >= 8.0 THEN 'Giỏi (8.0 - 8.9)'
                WHEN grade >= 7.0 THEN 'Khá (7.0 - 7.9)'
                WHEN grade >= 5.0 THEN 'Trung bình (5.0 - 6.9)'
                WHEN grade >= 0.0 THEN 'Yếu (0.0 - 4.9)'
                ELSE 'Chưa có điểm'
            END AS grade_category,
            COUNT(*) AS count
        FROM enrollments
        GROUP BY grade_category
        ORDER BY 
            CASE grade_category
                WHEN 'Xuất sắc (9.0 - 10.0)' THEN 1
                WHEN 'Giỏi (8.0 - 8.9)' THEN 2
                WHEN 'Khá (7.0 - 7.9)' THEN 3
                WHEN 'Trung bình (5.0 - 6.9)' THEN 4
                WHEN 'Yếu (0.0 - 4.9)' THEN 5
                ELSE 6
            END
        """
        result = self.db_manager.execute_query(query)
        
        stats = {}
        if result:
            for row in result:
                stats[row['grade_category']] = row['count']
        
        return stats
    
    def get_student_by_id(self, student_id):
        """
        Lấy thông tin sinh viên theo ID
        
        Args:
            student_id (str): Mã số sinh viên
            
        Returns:
            Student: Đối tượng sinh viên
        """
        from models.student import Student
        query = "SELECT * FROM students WHERE student_id = ?"
        result = self.db_manager.execute_query(query, (student_id,))
        
        if result:
            student_data = dict(result[0])
            return Student.from_dict(student_data)
        
        return None
    
    def get_course_by_id(self, course_id):
        """
        Lấy thông tin khóa học theo ID
        
        Args:
            course_id (str): Mã khóa học
            
        Returns:
            Course: Đối tượng khóa học
        """
        query = "SELECT * FROM courses WHERE course_id = ?"
        result = self.db_manager.execute_query(query, (course_id,))
        
        if result:
            course_data = dict(result[0])
            return Course.from_dict(course_data)
        
        return None
    
    def get_student_performance(self, student_id):
        """
        Lấy thông tin kết quả học tập của sinh viên
        
        Args:
            student_id (str): Mã sinh viên
            
        Returns:
            dict: Thông tin kết quả học tập
        """
        # Tổng số khóa học đăng ký
        query = """
        SELECT COUNT(*) AS count 
        FROM enrollments 
        WHERE student_id = ?
        """
        result = self.db_manager.execute_query(query, (student_id,))
        courses_enrolled = result[0]['count'] if result else 0
        
        # Số khóa học đã hoàn thành (có điểm)
        query = """
        SELECT COUNT(*) AS count 
        FROM enrollments 
        WHERE student_id = ? AND grade IS NOT NULL
        """
        result = self.db_manager.execute_query(query, (student_id,))
        courses_completed = result[0]['count'] if result else 0
        
        # Điểm trung bình
        query = """
        SELECT AVG(grade) AS avg_grade 
        FROM enrollments 
        WHERE student_id = ? AND grade IS NOT NULL
        """
        result = self.db_manager.execute_query(query, (student_id,))
        average_grade = result[0]['avg_grade'] if result and result[0]['avg_grade'] is not None else 0
        
        # Chi tiết từng khóa học
        query = """
        SELECT c.course_id, c.course_name, c.credits, c.instructor, e.grade
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
        ORDER BY c.course_id
        """
        course_details = self.db_manager.execute_query(query, (student_id,))
        
        return {
            'courses_enrolled': courses_enrolled,
            'courses_completed': courses_completed,
            'average_grade': average_grade,
            'course_details': course_details if course_details else []
        }
    
    def get_recent_activities(self, limit=5):
        """
        Lấy các hoạt động gần đây
        
        Args:
            limit (int): Số lượng hoạt động tối đa cần lấy
            
        Returns:
            list: Danh sách các hoạt động gần đây
        """
        query = """
        SELECT a.*, u.ten_dang_nhap
        FROM nhat_ky_hoat_dong a
        LEFT JOIN nguoi_dung u ON a.ma_nguoi_dung = u.ma_nguoi_dung
        ORDER BY a.thoi_gian DESC
        LIMIT ?
        """
        result = self.db_manager.execute_query(query, (limit,))
        
        return result if result else []

    def get_grade_distribution(self):
        """
        Lấy phân phối điểm số của sinh viên theo thang điểm
        
        Returns:
            dict: Dictionary chứa số lượng sinh viên theo từng thang điểm
        """
        query = """
        SELECT 
            CASE
                WHEN grade >= 9.0 AND grade <= 10.0 THEN 'A (9.0 - 10.0)'
                WHEN grade >= 8.0 AND grade < 9.0 THEN 'B+ (8.0 - 8.9)'
                WHEN grade >= 7.0 AND grade < 8.0 THEN 'B (7.0 - 7.9)'
                WHEN grade >= 6.5 AND grade < 7.0 THEN 'C+ (6.5 - 6.9)'
                WHEN grade >= 5.5 AND grade < 6.5 THEN 'C (5.5 - 6.4)'
                WHEN grade >= 5.0 AND grade < 5.5 THEN 'D+ (5.0 - 5.4)'
                WHEN grade >= 4.0 AND grade < 5.0 THEN 'D (4.0 - 4.9)'
                WHEN grade >= 0.0 AND grade < 4.0 THEN 'F (0.0 - 3.9)'
                ELSE 'Chưa có điểm'
            END AS grade_range,
            COUNT(*) AS count
        FROM enrollments
        GROUP BY grade_range
        ORDER BY 
            CASE grade_range
                WHEN 'A (9.0 - 10.0)' THEN 1
                WHEN 'B+ (8.0 - 8.9)' THEN 2
                WHEN 'B (7.0 - 7.9)' THEN 3
                WHEN 'C+ (6.5 - 6.9)' THEN 4
                WHEN 'C (5.5 - 6.4)' THEN 5
                WHEN 'D+ (5.0 - 5.4)' THEN 6
                WHEN 'D (4.0 - 4.9)' THEN 7
                WHEN 'F (0.0 - 3.9)' THEN 8
                ELSE 9
            END
        """
        result = self.db_manager.execute_query(query)
        
        distribution = {}
        if result:
            for row in result:
                distribution[row['grade_range']] = row['count']
        
        return distribution

    def get_pass_fail_rate(self):
        """
        Lấy tỷ lệ đậu/rớt của sinh viên (điểm >= 5.0 là đậu)
        
        Returns:
            dict: Dict chứa số lượng và tỷ lệ đậu/rớt
        """
        query = """
        SELECT 
            SUM(CASE WHEN grade >= 5.0 THEN 1 ELSE 0 END) AS passed,
            SUM(CASE WHEN grade < 5.0 AND grade IS NOT NULL THEN 1 ELSE 0 END) AS failed,
            COUNT(*) AS total
        FROM enrollments
        WHERE grade IS NOT NULL
        """
        
        result = self.db_manager.execute_query(query)
        
        stats = {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'pass_rate': 0,
            'fail_rate': 0
        }
        
        if result and result[0]['total'] > 0:
            stats['passed'] = result[0]['passed']
            stats['failed'] = result[0]['failed']
            stats['total'] = result[0]['total']
            stats['pass_rate'] = (stats['passed'] / stats['total']) * 100
            stats['fail_rate'] = (stats['failed'] / stats['total']) * 100
        
        return stats
    
    def get_enrollment_statistics_by_term(self):
        """
        Lấy thống kê số lượng sinh viên theo học kỳ
        
        Returns:
            list: Danh sách thống kê theo học kỳ
        """
        # Giả sử chúng ta có trường học kỳ trong bảng khóa học
        query = """
        SELECT 
            c.term AS term,
            COUNT(DISTINCT e.student_id) AS student_count,
            COUNT(DISTINCT c.course_id) AS course_count,
            AVG(e.grade) AS avg_grade
        FROM courses c
        JOIN enrollments e ON c.course_id = e.course_id
        WHERE c.term IS NOT NULL
        GROUP BY c.term
        ORDER BY c.term DESC
        """
        
        result = self.db_manager.execute_query(query)
        
        if not result:
            return []
        
        return result

    def get_grade_distribution(self):
        """
        Lấy phân phối điểm số của sinh viên theo khoảng điểm
        
        Returns:
            dict: Dictionary với key là khoảng điểm, value là số lượng sinh viên
        """
        try:
            query = """
                SELECT
                    CASE
                        WHEN grade < 4.0 THEN 'F (0-3.9)'
                        WHEN grade >= 4.0 AND grade < 5.5 THEN 'D (4.0-5.4)'
                        WHEN grade >= 5.5 AND grade < 7.0 THEN 'C (5.5-6.9)'
                        WHEN grade >= 7.0 AND grade < 8.5 THEN 'B (7.0-8.4)'
                        WHEN grade >= 8.5 THEN 'A (8.5-10)'
                    END AS grade_range,
                    COUNT(*) as count
                FROM enrollment
                WHERE grade IS NOT NULL
                GROUP BY grade_range
                ORDER BY MIN(grade)
            """
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            grade_distribution = {}
            for row in results:
                grade_range, count = row
                grade_distribution[grade_range] = count
                
            # Đảm bảo có đủ các khoảng điểm
            all_ranges = ['F (0-3.9)', 'D (4.0-5.4)', 'C (5.5-6.9)', 'B (7.0-8.4)', 'A (8.5-10)']
            for grade_range in all_ranges:
                if grade_range not in grade_distribution:
                    grade_distribution[grade_range] = 0
            
            # Sắp xếp theo thứ tự từ F đến A
            sorted_distribution = {k: grade_distribution[k] for k in all_ranges}
            
            return sorted_distribution
            
        except Exception as e:
            logging.error(f"Lỗi khi lấy phân phối điểm: {e}")
            return {}
    
    def get_gender_statistics(self):
        """
        Lấy thống kê về giới tính của sinh viên
        
        Returns:
            dict: Dictionary với key là giới tính, value là số lượng sinh viên
        """
        try:
            query = """
                SELECT gender, COUNT(*) as count 
                FROM student 
                GROUP BY gender
            """
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            gender_stats = {}
            for row in results:
                gender, count = row
                gender_stats[gender or "Không xác định"] = count
            
            # Đảm bảo có đủ các loại giới tính
            for gender in ["Nam", "Nữ", "Khác"]:
                if gender not in gender_stats:
                    gender_stats[gender] = 0
            
            return gender_stats
            
        except Exception as e:
            logging.error(f"Lỗi khi lấy thống kê giới tính: {e}")
            return {"Nam": 0, "Nữ": 0, "Khác": 0}