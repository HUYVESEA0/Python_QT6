"""
Script chạy các tác vụ bảo trì cho ứng dụng
"""
import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def setup_environment():
    """Thiết lập môi trường và thêm thư mục gốc vào sys.path"""
    # Lấy thư mục gốc của ứng dụng
    script_dir = Path(__file__).parent.absolute()
    
    # Thêm thư mục gốc vào sys.path nếu chưa có
    if str(script_dir) not in sys.path:
        sys.path.append(str(script_dir))
    
    return script_dir

def cleanup_project():
    """Dọn dẹp các file tạm thời và không cần thiết"""
    from utils.cleanup import cleanup_project
    return cleanup_project()

def optimize_database():
    """Tối ưu hóa cơ sở dữ liệu"""
    from utils.config_manager import ConfigManager
    from DB.db_manager import DatabaseManager
    
    config_manager = ConfigManager()
    db_manager = DatabaseManager(config_manager.get('DB_PATH'))
    
    logging.info("Đang tối ưu hóa cơ sở dữ liệu...")
    result = db_manager.optimize_database()
    
    if result:
        logging.info("Đã tối ưu hóa cơ sở dữ liệu thành công.")
    else:
        logging.error("Không thể tối ưu hóa cơ sở dữ liệu.")
    
    db_manager.close()
    return result

def backup_database():
    """Tạo bản sao lưu của cơ sở dữ liệu"""
    from utils.config_manager import ConfigManager
    from DB.db_manager import DatabaseManager
    
    config_manager = ConfigManager()
    db_manager = DatabaseManager(config_manager.get('DB_PATH'))
    
    # Tạo tên file backup với timestamp
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = str(backup_dir / f"student_db_backup_{timestamp}.db")
    
    logging.info(f"Đang tạo bản sao lưu cơ sở dữ liệu tại: {backup_path}")
    result = db_manager.backup_database(backup_path)
    
    if result:
        logging.info("Đã tạo bản sao lưu cơ sở dữ liệu thành công.")
    else:
        logging.error("Không thể tạo bản sao lưu cơ sở dữ liệu.")
    
    db_manager.close()
    return result

def main():
    """Hàm chính chạy các tác vụ bảo trì theo tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Chạy các tác vụ bảo trì cho ứng dụng.")
    
    parser.add_argument("--cleanup", action="store_true", help="Dọn dẹp các file tạm thời")
    parser.add_argument("--optimize-db", action="store_true", help="Tối ưu hóa cơ sở dữ liệu")
    parser.add_argument("--backup-db", action="store_true", help="Tạo bản sao lưu cơ sở dữ liệu")
    parser.add_argument("--all", action="store_true", help="Thực hiện tất cả các tác vụ bảo trì")
    
    args = parser.parse_args()
    
    # Thiết lập môi trường
    setup_environment()
    
    # Nếu không có tham số, hiển thị hướng dẫn
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Thực hiện các tác vụ theo tham số
    if args.cleanup or args.all:
        cleanup_project()
    
    if args.optimize_db or args.all:
        optimize_database()
    
    if args.backup_db or args.all:
        backup_database()
    
    logging.info("Hoàn tất các tác vụ bảo trì.")

if __name__ == "__main__":
    main()
