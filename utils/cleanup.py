"""
Script dọn dẹp các file tạm thời và không cần thiết
"""
import os
import shutil
import logging
from pathlib import Path
import time

def cleanup_project(project_root=None):
    """
    Xóa các file tạm thời và cache không cần thiết
    
    Args:
        project_root: Đường dẫn thư mục gốc dự án. Nếu None, sẽ sử dụng thư mục hiện tại
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.absolute()
    else:
        project_root = Path(project_root)
    
    logging.info(f"Bắt đầu dọn dẹp dự án tại: {project_root}")
    
    # Các pattern file cần xóa
    patterns_to_remove = [
        "**/*.pyc",        # Python bytecode
        "**/__pycache__",  # Thư mục cache của Python
        "**/*.bak",        # File backup
        "**/*.tmp",        # File tạm thời
        "**/*.log",        # File log (trừ thư mục logs)
        "**/.DS_Store",    # File hệ thống MacOS
        "**/*.pyo",        # Python optimized bytecode
    ]
    
    # Thư mục cần giữ lại
    dirs_to_keep = [
        "logs",    # Thư mục logs (nếu cần)
        "data",    # Thư mục dữ liệu (nếu cần)
    ]
    
    # Xóa các file theo pattern
    files_removed = 0
    dirs_removed = 0
    
    for pattern in patterns_to_remove:
        for path in project_root.glob(pattern):
            # Kiểm tra xem path có nằm trong thư mục cần giữ lại không
            should_keep = any((project_root / dir_keep) in path.parents
                              for dir_keep in dirs_to_keep)

            if should_keep:
                continue
            try:
                if path.is_file():
                    path.unlink()
                    files_removed += 1
                    logging.debug(f"Đã xóa file: {path}")
                elif path.is_dir():
                    shutil.rmtree(path)
                    dirs_removed += 1
                    logging.debug(f"Đã xóa thư mục: {path}")
            except Exception as e:
                logging.error(f"Lỗi khi xóa {path}: {e}")
    
    # Xóa các file ảnh tạm trong thư mục temp
    temp_dir = project_root / "temp"
    if temp_dir.exists():
        try:
            # Chỉ xóa các file cũ (tạo cách đây hơn 1 ngày)
            now = time.time()
            one_day_in_seconds = 24 * 60 * 60
            
            for file_path in temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = now - file_path.stat().st_mtime
                    if file_age > one_day_in_seconds:
                        file_path.unlink()
                        files_removed += 1
                        logging.debug(f"Đã xóa file tạm cũ: {file_path}")
            
            # Xóa thư mục temp nếu trống
            if not any(temp_dir.iterdir()):
                temp_dir.rmdir()
                dirs_removed += 1
                logging.debug(f"Đã xóa thư mục temp rỗng")
        except Exception as e:
            logging.error(f"Lỗi khi xóa thư mục temp: {e}")
    
    logging.info(f"Đã xóa {files_removed} file và {dirs_removed} thư mục")
    return files_removed, dirs_removed

def cleanup_temp_files():
    """
    Dọn dẹp riêng các file tạm thời trong thư mục temp
    """
    temp_dir = Path(__file__).parent.parent / "temp"
    if not temp_dir.exists():
        return 0
    
    files_removed = 0
    try:
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
                files_removed += 1
                logging.debug(f"Đã xóa file tạm: {file_path}")
        
        # Xóa thư mục temp nếu trống
        if not any(temp_dir.iterdir()):
            temp_dir.rmdir()
            logging.debug(f"Đã xóa thư mục temp rỗng")
    except Exception as e:
        logging.error(f"Lỗi khi xóa file tạm: {e}")
    
    return files_removed

if __name__ == "__main__":
    # Cấu hình logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # Chạy hàm dọn dẹp
    cleanup_project()
