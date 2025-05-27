import pandas as pd
from models.student import Student

class ImportManager:
    @staticmethod
    def import_students(file_path):
        """
        Đọc file Excel/CSV và trả về danh sách đối tượng Student.
        """
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        # Chuẩn hóa tên cột
        df.columns = [c.strip().lower() for c in df.columns]
        students = []
        for _, row in df.iterrows():
            student = Student(
                ma_sinh_vien=str(row.get("student_id", "")).strip(),
                ho_ten=str(row.get("full_name", "")).strip(),
                ngay_sinh=str(row.get("date_of_birth", "")).strip(),
                gioi_tinh=str(row.get("gender", "")).strip(),
                email=str(row.get("email", "")).strip(),
                so_dien_thoai=str(row.get("phone", "")).strip(),
                dia_chi=str(row.get("address", "")).strip(),
                ngay_nhap_hoc=str(row.get("enrolled_date", "")).strip(),
                trang_thai=str(row.get("status", "")).strip(),
                duong_dan_anh=""
            )
            if student.ma_sinh_vien and student.ho_ten:
                students.append(student)
        return students
