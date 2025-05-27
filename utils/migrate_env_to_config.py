"""
Script để tạo file config.json mặc định từ .env hoặc các giá trị mặc định
"""
import os
import json
import logging
from pathlib import Path
from dotenv import dotenv_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def migrate_env_to_config():
    """Tạo file config.json từ file .env hoặc giá trị mặc định"""
    root_dir = Path(__file__).parent.parent.absolute()
    
    # Đường dẫn file .env và config.json
    env_file = root_dir / '.env'
    config_file = root_dir / 'data' / 'config.json'
    
    # Đảm bảo thư mục data tồn tại
    os.makedirs(config_file.parent, exist_ok=True)
    
    # Đọc nội dung từ file .env nếu có
    env_data = {}
    if env_file.exists():
        logging.info(f"Đang đọc cấu hình từ file .env: {env_file}")
        env_data = dotenv_values(env_file)
    else:
        logging.warning(f"Không tìm thấy file .env tại: {env_file}")
        logging.info("Sẽ sử dụng giá trị mặc định để tạo config.json")
    
    # Tạo cấu trúc config mới
    config = {}
    
    # Đọc config hiện tại nếu có
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logging.info(f"Đã đọc cấu hình hiện tại từ: {config_file}")
        except Exception as e:
            logging.error(f"Lỗi khi đọc file config hiện tại: {e}")
            config = {}
    
    # Đảm bảo có các section chính
    if 'app' not in config:
        config['app'] = {}
    if 'database' not in config:
        config['database'] = {}
    if 'security' not in config:
        config['security'] = {}
    if 'ui' not in config:
        config['ui'] = {}
    
    # Cấu hình mặc định cho app
    if 'name' not in config['app']:
        config['app']['name'] = "Hệ thống Quản lý Sinh viên"
    if 'version' not in config['app']:
        config['app']['version'] = "2.0.0"
    if 'language' not in config['app']:
        config['app']['language'] = "vi_VN"
    if 'environment' not in config['app']:
        config['app']['environment'] = env_data.get('APP_ENV', 'development')
    if 'log_level' not in config['app']:
        config['app']['log_level'] = env_data.get('LOG_LEVEL', 'INFO')

    # Cấu hình database
    if 'path' not in config['database']:
        config['database']['path'] = env_data.get('DB_PATH', 'data/app.db')
    if 'backup_on_exit' not in config['database']:
        config['database']['backup_on_exit'] = True

    # Cấu hình security
    if 'secret_key' not in config['security']:
        config['security']['secret_key'] = env_data.get('SECRET_KEY', 'dev-key-for-development-only')
    if 'algorithm' not in config['security']:
        config['security']['algorithm'] = env_data.get('ENCRYPTION_ALGORITHM', 'HS256')
    if 'token_expiry_hours' not in config['security']:
        token_expiry = env_data.get('TOKEN_EXPIRY_HOURS', '24')
        config['security']['token_expiry_hours'] = int(token_expiry)

    # Cấu hình UI
    if 'theme' not in config['ui']:
        config['ui']['theme'] = "light"
    if 'show_welcome' not in config['ui']:
        config['ui']['show_welcome'] = True
    if 'window_width' not in config['ui']:
        config['ui']['window_width'] = 1280
    if 'window_height' not in config['ui']:
        config['ui']['window_height'] = 720
    if 'window_maximized' not in config['ui']:
        config['ui']['window_maximized'] = False
    
    # Lưu cấu hình mới vào config.json
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        if env_file.exists():
            logging.info(f"Đã di chuyển cấu hình từ .env sang {config_file}")
        else:
            logging.info(f"Đã tạo file cấu hình mặc định tại {config_file}")
        return True
    except Exception as e:
        logging.error(f"Lỗi khi lưu file config: {e}")
        return False

if __name__ == "__main__":
    migrate_env_to_config()
