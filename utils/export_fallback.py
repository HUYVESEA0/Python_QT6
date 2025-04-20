"""
Module thay thế cho các thư viện xuất dữ liệu khi không có sẵn
"""
import csv
import logging
import os
from datetime import datetime

class ExportFallback:
    """
    Cung cấp các phương thức xuất dữ liệu thay thế khi không có thư viện
    """
    
    @staticmethod
    def export_to_csv(data, headers, filename):
        """
        Xuất dữ liệu ra file CSV (hỗ trợ mặc định)
        
        Args:
            data (list): Dữ liệu cần xuất
            headers (list): Tiêu đề các cột
            filename (str): Tên file
            
        Returns:
            str: Đường dẫn đến file đã xuất
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            return filename
        except Exception as e:
            logging.error(f"Lỗi khi xuất CSV: {e}")
            return None
    
    @staticmethod
    def export_to_excel(data, headers, filename):
        """
        Xuất dữ liệu ra file CSV thay vì Excel khi không có openpyxl
        
        Args:
            data (list): Dữ liệu cần xuất
            headers (list): Tiêu đề các cột
            filename (str): Tên file
            
        Returns:
            str: Đường dẫn đến file đã xuất
        """
        # Chuyển đuôi file thành .csv
        csv_filename = os.path.splitext(filename)[0] + '.csv'
        logging.warning(f"Thư viện openpyxl không khả dụng. Xuất sang CSV thay thế: {csv_filename}")
        
        return ExportFallback.export_to_csv(data, headers, csv_filename)
    
    @staticmethod
    def export_to_pdf(data, headers, filename, title=None):
        """
        Xuất dữ liệu ra file text thay vì PDF khi không có reportlab
        
        Args:
            data (list): Dữ liệu cần xuất
            headers (list): Tiêu đề các cột
            filename (str): Tên file
            title (str, optional): Tiêu đề báo cáo
            
        Returns:
            str: Đường dẫn đến file đã xuất
        """
        # Chuyển đuôi file thành .txt
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        logging.warning(f"Thư viện reportlab không khả dụng. Xuất sang TXT thay thế: {txt_filename}")
        
        try:
            with open(txt_filename, 'w', encoding='utf-8') as f:
                # Viết tiêu đề
                if title:
                    f.write(f"{title}\n")
                    f.write("=" * len(title) + "\n\n")
                
                # Viết thời gian xuất
                f.write(f"Xuất lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Viết tiêu đề cột
                f.write(" | ".join(headers) + "\n")
                f.write("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)) + "\n")
                
                # Viết dữ liệu
                for row in data:
                    f.write(" | ".join(str(cell) for cell in row) + "\n")
                
            return txt_filename
        except Exception as e:
            logging.error(f"Lỗi khi xuất TXT: {e}")
            return None
    
    @staticmethod
    def export_to_html(data, headers, filename, title=None):
        """
        Xuất dữ liệu ra file HTML
        
        Args:
            data (list): Dữ liệu cần xuất
            headers (list): Tiêu đề các cột
            filename (str): Tên file
            title (str, optional): Tiêu đề báo cáo
            
        Returns:
            str: Đường dẫn đến file đã xuất
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Viết HTML header
                f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                f.write("<meta charset='utf-8'>\n")
                f.write(f"<title>{title or 'Exported Data'}</title>\n")
                
                # Thêm một số CSS đơn giản
                f.write("<style>\n")
                f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
                f.write("table { border-collapse: collapse; width: 100%; }\n")
                f.write("th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }\n")
                f.write("th { background-color: #f2f2f2; }\n")
                f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
                f.write("</style>\n</head>\n<body>\n")
                
                # Tiêu đề báo cáo
                if title:
                    f.write(f"<h1>{title}</h1>\n")
                
                # Thời gian xuất
                f.write(f"<p>Xuất lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
                
                # Bảng dữ liệu
                f.write("<table>\n<thead>\n<tr>\n")
                for header in headers:
                    f.write(f"<th>{header}</th>\n")
                f.write("</tr>\n</thead>\n<tbody>\n")
                
                for row in data:
                    f.write("<tr>\n")
                    for cell in row:
                        f.write(f"<td>{cell}</td>\n")
                    f.write("</tr>\n")
                
                f.write("</tbody>\n</table>\n")
                f.write("</body>\n</html>")
                
            return filename
        except Exception as e:
            logging.error(f"Lỗi khi xuất HTML: {e}")
            return None
