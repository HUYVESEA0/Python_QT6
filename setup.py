"""
Script khởi tạo và chuẩn bị môi trường cho ứng dụng
"""
import os
import logging
import argparse
from pathlib import Path
from utils.migrate_env_to_config import migrate_env_to_config

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_environment():
    """Chuẩn bị môi trường chạy ứng dụng"""
    # Đường dẫn thư mục gốc
    root_dir = Path(__file__).parent.absolute()
    logging.info(f"Chuẩn bị môi trường cho ứng dụng tại: {root_dir}")
    
    # Tạo các thư mục cần thiết
    data_dir = root_dir / "data"
    logs_dir = root_dir / "logs"
    temp_dir = root_dir / "temp"
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    logging.info("Đã tạo các thư mục cần thiết")
    
    # Tạo file cấu hình mặc định
    migrate_env_to_config()
    
    logging.info("Đã hoàn tất chuẩn bị môi trường")
    logging.info("Bạn có thể khởi động ứng dụng bằng lệnh: python main.py")

def main():
    parser = argparse.ArgumentParser(description="Chuẩn bị môi trường chạy ứng dụng")
    parser.add_argument("--force", action="store_true", help="Ghi đè các cấu hình hiện có")
    args = parser.parse_args()
    
    setup_environment()

if __name__ == "__main__":
    main()
