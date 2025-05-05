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
                student_id=str(row.get("student_id", "")).strip(),
                full_name=str(row.get("full_name", "")).strip(),
                date_of_birth=str(row.get("date_of_birth", "")).strip(),
                gender=str(row.get("gender", "")).strip(),
                email=str(row.get("email", "")).strip(),
                phone=str(row.get("phone", "")).strip(),
                address=str(row.get("address", "")).strip(),
                enrolled_date=str(row.get("enrolled_date", "")).strip(),
                status=str(row.get("status", "")).strip(),
                photo_path=""
            )
            if student.student_id and student.full_name:
                students.append(student)
        return students
