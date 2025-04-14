# Hệ thống Quản lý Sinh viên

## Tổng quan

Phần mềm Quản lý Sinh viên là ứng dụng desktop được phát triển bằng Python và PyQt6, cung cấp một giải pháp toàn diện để quản lý thông tin sinh viên, khóa học, và đăng ký học trong một cơ sở giáo dục. Phần mềm này được thiết kế với giao diện thân thiện, dễ sử dụng và chức năng phong phú.

## Tính năng chính

- **Quản lý sinh viên**: Thêm, sửa, xóa và tìm kiếm thông tin sinh viên
- **Quản lý khóa học**: Tạo, cập nhật và quản lý các khóa học
- **Quản lý đăng ký**: Đăng ký sinh viên vào khóa học, cập nhật điểm số
- **Báo cáo thống kê**: Tạo các báo cáo về tình trạng sinh viên, khóa học và kết quả học tập
- **Dashboard**: Hiển thị thông tin tổng quan và các chỉ số quan trọng
- **Tìm kiếm nâng cao**: Tìm kiếm sinh viên với nhiều tiêu chí
- **Trích xuất dữ liệu**: Xuất báo cáo và dữ liệu ra Excel, PDF
- **Nhật ký hoạt động**: Theo dõi các hoạt động của người dùng trong hệ thống
- **Theme tùy chỉnh**: Chế độ sáng/tối và các theme tùy chỉnh
- **Thông báo thông minh**: Hệ thống thông báo với animation và phân loại

## Yêu cầu hệ thống

- Python 3.8 trở lên
- PyQt6
- SQLite3
- Các thư viện Python khác được liệt kê trong tệp `requirements.txt`

## Cài đặt

1. Clone repository từ GitHub:
```bash
git clone https://github.com/yourusername/student-management-system.git
cd student-management-system
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

3. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

4. Chạy ứng dụng:
```bash
python main.py
```

Hoặc sử dụng tập lệnh chạy `run_app.bat` (trên Windows) hoặc `run_app.sh` (trên Linux/MacOS).

## Cấu trúc thư mục
