import re
from datetime import datetime
from PyQt6.QtCore import QDate

class Validator:
    """
    Lớp chứa các hàm kiểm tra tính hợp lệ của dữ liệu.
    """
    
    @staticmethod
    def is_valid_email(email):
        """
        Kiểm tra email có hợp lệ không.
        
        Args:
            email (str): Địa chỉ email cần kiểm tra
            
        Returns:
            bool: True nếu hợp lệ, False nếu không
        """
        if not email:
            return True  # Email trống là hợp lệ (vì không bắt buộc)
        
        # Sử dụng regex để kiểm tra định dạng email
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone):
        """
        Kiểm tra số điện thoại có hợp lệ không.
        
        Args:
            phone (str): Số điện thoại cần kiểm tra
            
        Returns:
            bool: True nếu hợp lệ, False nếu không
        """
        if not phone:
            return True  # Số điện thoại trống là hợp lệ (vì không bắt buộc)
        
        # Chỉ chấp nhận số và một số ký tự đặc biệt
        pattern = r'^[0-9+\-\(\) ]{8,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def is_valid_student_id(student_id):
        """
        Kiểm tra mã sinh viên có hợp lệ không.
        
        Args:
            student_id (str): Mã sinh viên cần kiểm tra
            
        Returns:
            bool: True nếu hợp lệ, False nếu không
        """
        if not student_id:
            return False  # Mã sinh viên không được trống
        
        # Mã sinh viên hợp lệ (ví dụ: chữ và số, độ dài từ 5-10)
        pattern = r'^[a-zA-Z0-9]{5,10}$'
        return bool(re.match(pattern, student_id))
    
    @staticmethod
    def is_valid_course_id(course_id):
        """
        Kiểm tra mã khóa học có hợp lệ không.
        
        Args:
            course_id (str): Mã khóa học cần kiểm tra
            
        Returns:
            bool: True nếu hợp lệ, False nếu không
        """
        if not course_id:
            return False  # Mã khóa học không được trống
        
        # Mã khóa học hợp lệ (ví dụ: chữ và số, độ dài từ 2-10)
        pattern = r'^[a-zA-Z0-9]{2,10}$'
        return bool(re.match(pattern, course_id))


class DateUtils:
    """
    Lớp chứa các tiện ích xử lý ngày tháng.
    """
    
    @staticmethod
    def format_date(date_str, input_format="%Y-%m-%d", output_format="%d/%m/%Y"):
        """
        Chuyển đổi định dạng ngày tháng.
        
        Args:
            date_str (str): Chuỗi ngày tháng cần chuyển đổi
            input_format (str): Định dạng đầu vào
            output_format (str): Định dạng đầu ra
            
        Returns:
            str: Chuỗi ngày tháng đã chuyển đổi định dạng
        """
        if not date_str:
            return ""
        
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except ValueError:
            return date_str
    
    @staticmethod
    def qdate_to_string(qdate, format_str="%Y-%m-%d"):
        """
        Chuyển đổi từ QDate sang string.
        
        Args:
            qdate (QDate): Đối tượng QDate
            format_str (str): Định dạng chuỗi đầu ra
            
        Returns:
            str: Chuỗi ngày tháng theo định dạng
        """
        if not isinstance(qdate, QDate):
            return ""
        
        return qdate.toString(format_str)
    
    @staticmethod
    def string_to_qdate(date_str, format_str="%Y-%m-%d"):
        """
        Chuyển đổi từ string sang QDate.
        
        Args:
            date_str (str): Chuỗi ngày tháng
            format_str (str): Định dạng chuỗi đầu vào
            
        Returns:
            QDate: Đối tượng QDate
        """
        if not date_str:
            return QDate.currentDate()
        
        try:
            date_obj = datetime.strptime(date_str, format_str)
            return QDate(date_obj.year, date_obj.month, date_obj.day)
        except ValueError:
            return QDate.currentDate()


class StringUtils:
    """
    Lớp chứa các tiện ích xử lý chuỗi.
    """
    
    @staticmethod
    def normalize_name(name):
        """
        Chuẩn hóa tên người (viết hoa chữ cái đầu mỗi từ).
        
        Args:
            name (str): Tên cần chuẩn hóa
            
        Returns:
            str: Tên đã chuẩn hóa
        """
        if not name:
            return ""
        
        # Loại bỏ khoảng trắng thừa và chuẩn hóa
        normalized = " ".join(name.strip().split())
        return normalized.title()
    
    @staticmethod
    def truncate_text(text, max_length=50, ellipsis="..."):
        """
        Cắt ngắn chuỗi nếu quá dài.
        
        Args:
            text (str): Chuỗi cần cắt ngắn
            max_length (int): Độ dài tối đa
            ellipsis (str): Chuỗi hiển thị khi cắt ngắn
            
        Returns:
            str: Chuỗi đã cắt ngắn
        """
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(ellipsis)] + ellipsis
