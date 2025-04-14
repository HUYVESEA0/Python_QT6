from datetime import datetime

class Student:
    """
    Lớp đại diện cho một sinh viên trong hệ thống.
    """
    def __init__(self, student_id="", full_name="", date_of_birth=None, 
                 gender="", email="", phone="", address="", 
                 enrolled_date=None, status="Active"):
        """
        Khởi tạo một đối tượng sinh viên.
        
        Args:
            student_id (str): Mã số sinh viên
            full_name (str): Họ và tên sinh viên
            date_of_birth (str): Ngày sinh (định dạng YYYY-MM-DD)
            gender (str): Giới tính
            email (str): Địa chỉ email
            phone (str): Số điện thoại
            address (str): Địa chỉ
            enrolled_date (str): Ngày nhập học (định dạng YYYY-MM-DD)
            status (str): Trạng thái của sinh viên (Active, Inactive, Graduated, etc.)
        """
        self.student_id = student_id
        self.full_name = full_name
        self.date_of_birth = date_of_birth if date_of_birth else ""
        self.gender = gender
        self.email = email
        self.phone = phone
        self.address = address
        self.enrolled_date = enrolled_date if enrolled_date else datetime.now().strftime("%Y-%m-%d")
        self.status = status

    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng sinh viên từ dictionary.
        
        Args:
            data (dict): Dictionary chứa dữ liệu sinh viên
            
        Returns:
            Student: Đối tượng sinh viên mới
        """
        return cls(
            student_id=data.get('student_id', ''),
            full_name=data.get('full_name', ''),
            date_of_birth=data.get('date_of_birth', ''),
            gender=data.get('gender', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            enrolled_date=data.get('enrolled_date', ''),
            status=data.get('status', 'Active')
        )
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng sinh viên thành dictionary.
        
        Returns:
            dict: Dictionary chứa thông tin sinh viên
        """
        return {
            'student_id': self.student_id,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'enrolled_date': self.enrolled_date,
            'status': self.status
        }
    
    def __str__(self):
        """
        Định dạng chuỗi đại diện cho sinh viên.
        
        Returns:
            str: Chuỗi thông tin sinh viên
        """
        return f"{self.student_id} - {self.full_name}"