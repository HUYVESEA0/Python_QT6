import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class ExportManager:
    """
    Quản lý xuất dữ liệu ra các định dạng khác nhau (Excel, PDF, CSV, HTML)
    """
    
    @staticmethod
    def export_to_excel(data, column_headers, parent=None, default_filename=None):
        """
        Xuất dữ liệu ra file Excel
        
        Args:
            data (list): Dữ liệu cần xuất
            column_headers (list): Tiêu đề các cột
            parent (QWidget, optional): Widget cha để hiển thị dialog
            default_filename (str, optional): Tên file mặc định
            
        Returns:
            bool: True nếu xuất thành công, False nếu thất bại
        """
        try:
            # Loại bỏ các dòng trống hoàn toàn
            filtered_data = [row for row in data if any(str(cell).strip() for cell in row)]
            if not filtered_data:
                QMessageBox.warning(
                    parent,
                    "Lỗi",
                    "Không có dữ liệu hợp lệ để xuất ra Excel!"
                )
                return False

            if not default_filename:
                default_filename = f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
                
            filename, _ = QFileDialog.getSaveFileName(
                parent,
                "Xuất ra Excel",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not filename:  # Người dùng đã hủy
                return False
                
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(filtered_data, columns=column_headers)
            
            # Xuất ra file Excel
            df.to_excel(filename, index=False)
            
            logging.info(f"Đã xuất dữ liệu ra file Excel: {filename}")
            
            QMessageBox.information(
                parent,
                "Thành công",
                f"Dữ liệu đã được xuất thành công đến:\n{filename}"
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi xuất Excel: {str(e)}")
            QMessageBox.warning(
                parent,
                "Lỗi",
                f"Không thể xuất dữ liệu ra file Excel: {str(e)}"
            )
            return False
    
    @staticmethod
    def export_to_excel_multi_sheet(sheet_data, parent=None, default_filename=None):
        """
        Xuất dữ liệu ra file Excel với nhiều sheet
        
        Args:
            sheet_data (dict): Dictionary với key là tên sheet và value là tuple (headers, data)
            parent (QWidget, optional): Widget cha để hiển thị dialog
            default_filename (str, optional): Tên file mặc định
            
        Returns:
            bool: True nếu xuất thành công, False nếu thất bại
        """
        try:
            if not default_filename:
                default_filename = f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
                
            filename, _ = QFileDialog.getSaveFileName(
                parent,
                "Xuất ra Excel",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not filename:  # Người dùng đã hủy
                return False
                
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Tạo ExcelWriter để ghi nhiều sheet
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, (headers, data) in sheet_data.items():
                    # Tạo DataFrame từ dữ liệu
                    df = pd.DataFrame(data, columns=headers)
                    
                    # Ghi ra sheet tương ứng
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logging.info(f"Đã xuất dữ liệu ra file Excel nhiều sheet: {filename}")
            
            QMessageBox.information(
                parent,
                "Thành công",
                f"Dữ liệu đã được xuất thành công đến:\n{filename}"
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi xuất Excel nhiều sheet: {str(e)}")
            QMessageBox.warning(
                parent,
                "Lỗi",
                f"Không thể xuất dữ liệu ra file Excel: {str(e)}"
            )
            return False
    
    @staticmethod
    def export_to_pdf(data, column_headers, title="Báo cáo", parent=None, default_filename=None):
        """
        Xuất dữ liệu ra file PDF
        
        Args:
            data (list): Dữ liệu cần xuất
            column_headers (list): Tiêu đề các cột
            title (str, optional): Tiêu đề của báo cáo
            parent (QWidget, optional): Widget cha để hiển thị dialog
            default_filename (str, optional): Tên file mặc định
            
        Returns:
            bool: True nếu xuất thành công, False nếu thất bại
        """
        try:
            if not default_filename:
                default_filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                
            filename, _ = QFileDialog.getSaveFileName(
                parent,
                "Xuất ra PDF",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if not filename:  # Người dùng đã hủy
                return False
                
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Tạo PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Tạo nội dung
            elements = []
            
            # Tiêu đề
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                alignment=1,  # Center alignment
                spaceAfter=12
            )
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Thêm ngày tháng
            date_text = f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            elements.append(Paragraph(date_text, styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Chuẩn bị dữ liệu cho bảng
            table_data = [column_headers] + data
            
            # Tạo bảng
            table = Table(table_data, repeatRows=1)
            
            # Tạo style cho bảng
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            # Thêm xen kẽ màu nền cho các dòng để dễ đọc
            for row in range(1, len(table_data)):
                if row % 2 == 0:
                    table_style.add('BACKGROUND', (0, row), (-1, row), colors.lightgrey)
            
            table.setStyle(table_style)
            elements.append(table)
            
            # Xuất PDF
            doc.build(elements)
            
            logging.info(f"Đã xuất dữ liệu ra file PDF: {filename}")
            
            QMessageBox.information(
                parent,
                "Thành công",
                f"Dữ liệu đã được xuất thành công đến:\n{filename}"
            )
            
            return True
        
        except Exception as e:
            logging.error(f"Lỗi khi xuất PDF: {str(e)}")
            QMessageBox.warning(
                parent,
                "Lỗi",
                f"Không thể xuất dữ liệu ra file PDF: {str(e)}"
            )
            return False

    @staticmethod
    def export_to_csv(data, column_headers, parent=None, default_filename=None, delimiter=","):
        """
        Xuất dữ liệu ra file CSV
        
        Args:
            data (list): Dữ liệu cần xuất
            column_headers (list): Tiêu đề các cột
            parent (QWidget, optional): Widget cha để hiển thị dialog
            default_filename (str, optional): Tên file mặc định
            delimiter (str, optional): Ký tự phân cách (mặc định là dấu phẩy)
            
        Returns:
            bool: True nếu xuất thành công, False nếu thất bại
        """
        try:
            if not default_filename:
                default_filename = f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                
            filename, _ = QFileDialog.getSaveFileName(
                parent,
                "Xuất ra CSV",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not filename:  # Người dùng đã hủy
                return False
                
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(data, columns=column_headers)
            
            # Xuất ra file CSV
            df.to_csv(filename, index=False, sep=delimiter, encoding='utf-8')
            
            logging.info(f"Đã xuất dữ liệu ra file CSV: {filename}")
            
            QMessageBox.information(
                parent,
                "Thành công",
                f"Dữ liệu đã được xuất thành công đến:\n{filename}"
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi xuất CSV: {str(e)}")
            QMessageBox.warning(
                parent,
                "Lỗi",
                f"Không thể xuất dữ liệu ra file CSV: {str(e)}"
            )
            return False
    
    @staticmethod
    def export_to_html(data, column_headers, title="Báo cáo", parent=None, default_filename=None):
        """
        Xuất dữ liệu ra file HTML
        
        Args:
            data (list): Dữ liệu cần xuất
            column_headers (list): Tiêu đề các cột
            title (str, optional): Tiêu đề của báo cáo
            parent (QWidget, optional): Widget cha để hiển thị dialog
            default_filename (str, optional): Tên file mặc định
            
        Returns:
            bool: True nếu xuất thành công, False nếu thất bại
        """
        try:
            if not default_filename:
                default_filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
                
            filename, _ = QFileDialog.getSaveFileName(
                parent,
                "Xuất ra HTML",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "HTML Files (*.html);;All Files (*)"
            )
            
            if not filename:  # Người dùng đã hủy
                return False
                
            if not filename.endswith('.html'):
                filename += '.html'
            
            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(data, columns=column_headers)
            
            # CSS style cho bảng
            table_style = """
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                h1 {
                    font-family: Arial, sans-serif;
                    color: #333;
                }
                .date {
                    font-style: italic;
                    color: #666;
                    margin-bottom: 20px;
                }
            </style>
            """
            
            # Tạo HTML từ DataFrame
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{title}</title>
                {table_style}
            </head>
            <body>
                <h1>{title}</h1>
                <p class="date">Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                {df.to_html(index=False)}
            </body>
            </html>
            """
            
            # Ghi file HTML
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"Đã xuất dữ liệu ra file HTML: {filename}")
            
            QMessageBox.information(
                parent,
                "Thành công",
                f"Dữ liệu đã được xuất thành công đến:\n{filename}"
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi xuất HTML: {str(e)}")
            QMessageBox.warning(
                parent,
                "Lỗi",
                f"Không thể xuất dữ liệu ra file HTML: {str(e)}"
            )
            return False
    
    @staticmethod
    def export_empty_template(column_headers, parent=None, default_filename=None):
        """
        Xuất file mẫu rỗng với các trường trùng với cơ sở dữ liệu (Excel/CSV).
        
        Args:
            column_headers (list): Danh sách tên trường (cột)
            parent (QWidget, optional): Widget cha để hiển thị dialog
            default_filename (str, optional): Tên file mặc định
            
        Returns:
            bool: True nếu xuất thành công, False nếu thất bại
        """
        try:
            if not default_filename:
                default_filename = f"import_template_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
                
            filename, _ = QFileDialog.getSaveFileName(
                parent,
                "Xuất file mẫu nhập dữ liệu",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
            )
            
            if not filename:
                return False
            
            if filename.endswith('.csv'):
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(column_headers)
            else:
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                df = pd.DataFrame(columns=column_headers)
                df.to_excel(filename, index=False)
            
            QMessageBox.information(
                parent,
                "Thành công",
                f"Đã xuất file mẫu nhập dữ liệu:\n{filename}"
            )
            
            return True
        
        except Exception as e:
            logging.error(f"Lỗi khi xuất file mẫu nhập dữ liệu: {str(e)}")
            QMessageBox.warning(
                parent,
                "Lỗi",
                f"Không thể xuất file mẫu nhập dữ liệu: {str(e)}"
            )
            return False


