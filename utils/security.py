import hashlib
import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_salt(length=16):
    """
    Tạo chuỗi salt ngẫu nhiên
    
    Args:
        length (int): Độ dài của chuỗi salt
        
    Returns:
        str: Chuỗi salt đã mã hóa hex
    """
    return os.urandom(length).hex()

def hash_password(password, salt=None):
    """
    Mã hóa mật khẩu với salt
    
    Args:
        password (str): Mật khẩu cần mã hóa
        salt (str, optional): Salt cho mã hóa, nếu không có sẽ tạo mới
        
    Returns:
        tuple: (password_hash, salt)
    """
    if salt is None:
        salt = generate_salt()
    
    # Kết hợp mật khẩu và salt
    salted_password = (password + salt).encode('utf-8')
    
    # Tạo hash
    hash_obj = hashlib.sha256(salted_password)
    password_hash = hash_obj.hexdigest()
    
    return (password_hash, salt)

def verify_password(password, stored_hash, salt):
    """
    Kiểm tra mật khẩu có khớp với hash đã lưu không
    
    Args:
        password (str): Mật khẩu cần kiểm tra
        stored_hash (str): Hash đã lưu
        salt (str): Salt đã sử dụng
        
    Returns:
        bool: True nếu mật khẩu khớp, False nếu không
    """
    # Tạo hash từ mật khẩu nhập vào và salt
    calculated_hash, _ = hash_password(password, salt)
    
    # So sánh với hash đã lưu
    return calculated_hash == stored_hash

def generate_encryption_key():
    """
    Tạo khóa mã hóa
    
    Returns:
        bytes: Khóa mã hóa
    """
    try:
        return Fernet.generate_key()
    except Exception as e:
        logging.error(f"Lỗi khi tạo khóa mã hóa: {e}")
        return None

def encrypt_data(data, key):
    """
    Mã hóa dữ liệu
    
    Args:
        data (str): Dữ liệu cần mã hóa
        key (bytes): Khóa mã hóa
        
    Returns:
        str: Dữ liệu đã mã hóa
    """
    try:
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        logging.error(f"Lỗi khi mã hóa dữ liệu: {e}")
        return None

def decrypt_data(encrypted_data, key):
    """
    Giải mã dữ liệu
    
    Args:
        encrypted_data (str): Dữ liệu đã mã hóa
        key (bytes): Khóa mã hóa
        
    Returns:
        str: Dữ liệu đã giải mã
    """
    try:
        f = Fernet(key)
        decrypted_data = f.decrypt(base64.b64decode(encrypted_data))
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logging.error(f"Lỗi khi giải mã dữ liệu: {e}")
        return None
