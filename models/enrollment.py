class Course:
    """
    Lớp đại diện cho một khóa học trong hệ thống.
    """
    def __init__(self, course_id="", course_name="", credits=0, 
                 instructor="", description="", max_students=50):
        """
        Khởi tạo một đối tượng khóa học.
        
        Args:
            course_id (str): Mã khóa học
            course_name (str): Tên khóa học
            credits (int): Số tín chỉ
            instructor (str): Giảng viên
            description (str): Mô tả
            max_students (int): Số lượng sinh viên tối đa
        """
        self.course_id = course_id
        self.course_name = course_name
        self.credits = credits
        self.instructor = instructor
        self.description = description
        self.max_students = max_students
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng khóa học từ dictionary.
        
        Args:
            data (dict): Dictionary chứa dữ liệu khóa học
            
        Returns:
            Course: Đối tượng khóa học mới
        """
        return cls(
            course_id=data.get('course_id', ''),
            course_name=data.get('course_name', ''),
            credits=data.get('credits', 0),
            instructor=data.get('instructor', ''),
            description=data.get('description', ''),
            max_students=data.get('max_students', 50)
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng khóa học thành dictionary.
        
        Returns:
            dict: Dictionary chứa thông tin khóa học
        """
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'credits': self.credits,
            'instructor': self.instructor,
            'description': self.description,
            'max_students': self.max_students
        }
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho khóa học.
        
        Returns:
            str: Chuỗi thông tin khóa học
        """
        return f"{self.course_id} - {self.course_name} ({self.credits} tín chỉ)"