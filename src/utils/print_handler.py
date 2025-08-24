import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

class PrintHandler:
    def __init__(self, db):
        self.db = db
   
    def print_container_invoice(self, container_id):
        """Generate and export container invoice to Excel optimized for printing"""
        try:
            # Get container details
            container = self.db.get_container_by_id(container_id)
            if not container:
                messagebox.showerror("Error", "Container tidak ditemukan!")
                return
           
            # Get barang in container with pricing
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
           
            if not container_barang:
                messagebox.showwarning("Peringatan", "Container kosong, tidak ada yang akan diprint!")
                return
           
            # Generate Excel invoice
            self._generate_excel_invoice_optimized(container, container_barang, container_id)
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat invoice: {str(e)}")
   
    def _generate_excel_invoice_optimized(self, container, barang_list, container_id):
        """Generate Excel invoice document optimized for A4 printing"""
        try:
            # Create new workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Invoice Container"
           
            # SET PAGE LAYOUT FOR A4 PRINT
            ws.page_setup.paperSize = ws.PAPERSIZE_A4
            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE  # Landscape untuk lebih banyak kolom
            ws.page_setup.fitToPage = True
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0  # Allow multiple pages vertically
            
            # Set margins (dalam inches)
            ws.page_margins = PageMargins(
                left=0.5, right=0.5, top=0.75, bottom=0.75, 
                header=0.3, footer=0.3
            )
            
            # Print settings
            ws.print_options.horizontalCentered = True
            ws.print_area = None  # Will be set later
           
            # Define optimized styles for printing with smaller font
            header_font = Font(name='Arial', size=12, bold=True)  # Smaller
            company_font = Font(name='Arial', size=10, bold=True) # Smaller
            normal_font = Font(name='Arial', size=7)   # Smaller
            small_font = Font(name='Arial', size=6)    # Size 6 as requested
            table_header_font = Font(name='Arial', size=6, bold=True)  # Size 6
           
            center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
            left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
            right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
           
            # Border hanya untuk header dan total row
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
           
            header_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
           
            # Safe way to get container values
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return container.get(key, default) or default
                    else:
                        return container[key] if key in container and container[key] else default
                except:
                    return default
           
            # Header section - COMPACT
            current_row = 1
           
            # Title - Merge to column M (13 kolom untuk tambahan Nama Barang)
            ws.merge_cells(f'A{current_row}:M{current_row}')
            ws[f'A{current_row}'] = "INVOICE CONTAINER"
            ws[f'A{current_row}'].font = header_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 1
           
            # Company info - COMPACT
            ws.merge_cells(f'A{current_row}:M{current_row}')
            ws[f'A{current_row}'] = "CV. CAHAYA KARUNIA | Jl. Teluk Raya Selatan No. 6 Surabaya | Phone: 031-60166017"
            ws[f'A{current_row}'].font = normal_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 2
           
            # Container information - 3 PER KOLOM LAYOUT to save space
            container_info = [
                ("Container No", safe_get('container')),
                ("Feeder", safe_get('feeder')),
                ("Destination", safe_get('destination')),
                ("Party", safe_get('party')),
                ("ETD Sub", safe_get('etd_sub')),
                ("CLS", safe_get('cls')),
                ("Open", safe_get('open')),
                ("Full", safe_get('full')),
                ("Seal", safe_get('seal')),
                ("Ref JOA", safe_get('ref_joa'))
            ]
            
            info_start_row = current_row
            
            # Arrange in 3 columns (4 rows each column, since we have 10 items)
            for i, (label, value) in enumerate(container_info):
                col_group = i // 4  # 0, 1, 2 (3 groups)
                row_in_group = i % 4  # 0, 1, 2, 3 (4 rows per group)
                
                row = info_start_row + row_in_group
                col_start = col_group * 4 + 1  # Columns: 1, 5, 9
                
                # Label
                ws[f'{get_column_letter(col_start)}{row}'] = f"{label}:"
                ws[f'{get_column_letter(col_start)}{row}'].font = small_font
                # Value  
                ws[f'{get_column_letter(col_start + 1)}{row}'] = str(value)
                ws[f'{get_column_letter(col_start + 1)}{row}'].font = small_font
                
                # Set minimal row height untuk container info
                ws.row_dimensions[row].height = 10 # Lebih kecil karena font 6
            
            current_row = info_start_row + 4 + 1  # 4 rows + 1 spacing
           
            # NEW Table headers - Single row, kompak
            headers = ['Tgl', 'Pengirim', 'Penerima', 'Nama Barang', 'Jenis Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Satuan', 'Door', 'Unit Price', 'Price']
           
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = table_header_font
                cell.alignment = center_align
                cell.border = thin_border  # Kembalikan border untuk header
                cell.fill = header_fill
                # Set minimal height untuk header
                ws.row_dimensions[current_row].height = 8  # Lebih kecil karena font 6
           
            current_row += 1
           
            # Table data with GROUPING
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            total_nilai = 0
            
            # Variables untuk tracking grouping
            previous_date = None
            previous_pengirim = None
            previous_penerima = None
           
            for i, barang_row in enumerate(barang_list, 1):
                # Convert sqlite3.Row to dictionary
                barang = dict(barang_row)
    
                # Debug print (optional, bisa dihapus)
                if i == 1:  # Only print first item for debugging
                    print("Barang:", barang)
                
                try:
                    # Safe way to get barang values
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                   
                    # Format date - get tanggal or use current date
                    tanggal = safe_barang_get('tanggal_barang', datetime.now())
                    if isinstance(tanggal, str):
                        try:
                            tanggal = datetime.strptime(tanggal, '%Y-%m-%d')
                        except:
                            tanggal = datetime.now()
                    formatted_date = tanggal.strftime('%d-%b') if isinstance(tanggal, datetime) else '-'
                    
                    pengirim = str(safe_barang_get('sender_name', '-'))
                    penerima = str(safe_barang_get('receiver_name', '-'))
                    nama_barang = str(safe_barang_get('nama_barang', '-'))[:20]  # Truncate
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))[:15]  # Truncate
                    
                    # Door info - bisa dari field door atau alamat
                    door = str(safe_barang_get('door_type', safe_barang_get('alamat_tujuan', '-')))[:10]  # Truncate

                    # Format dimensions - SIMPLIFIED (Kubikasi)
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    kubikasi = f"{p}×{l}×{t}"
                    if len(kubikasi) > 12:
                        kubikasi = kubikasi[:9] + "..."
                   
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    satuan = str(safe_barang_get('satuan', safe_barang_get('unit', 'pcs')))[:6]  # Truncate
                    unit_price = safe_barang_get('harga_per_unit', safe_barang_get('unit_price', 0))
                    total_harga = safe_barang_get('total_harga', 0)
                   
                    # Add to totals
                    try:
                        total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                        total_ton += float(ton) if ton not in [None, '', '-'] else 0
                        total_colli += int(colli) if colli not in [None, '', '-'] else 0
                        total_nilai += float(total_harga) if total_harga not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                   
                    # Format values for display
                    m3_val = float(m3) if m3 not in [None, '', '-'] else 0
                    ton_val = float(ton) if ton not in [None, '', '-'] else 0
                    colli_val = int(colli) if colli not in [None, '', '-'] else 0
                    unit_price_val = float(unit_price) if unit_price not in [None, '', '-'] else 0
                    harga_val = float(total_harga) if total_harga not in [None, '', '-'] else 0
                    
                    # GROUPING LOGIC - Cek apakah tgl, pengirim, penerima sama dengan baris sebelumnya
                    display_date = formatted_date
                    display_pengirim = pengirim
                    display_penerima = penerima
                    
                    if (formatted_date == previous_date and 
                        pengirim == previous_pengirim and 
                        penerima == previous_penerima):
                        # Jika sama dengan baris sebelumnya, kosongkan
                        display_date = ""
                        display_pengirim = ""
                        display_penerima = ""
                    else:
                        # Update tracking variables
                        previous_date = formatted_date
                        previous_pengirim = pengirim
                        previous_penerima = penerima
                   
                    # Fill row data - NEW FORMAT WITH GROUPING and Nama Barang
                    row_data = [
                        display_date,       # Tgl (kosong jika sama dengan sebelumnya)
                        display_pengirim,   # Pengirim (kosong jika sama dengan sebelumnya)  
                        display_penerima,   # Penerima (kosong jika sama dengan sebelumnya)
                        nama_barang,       # Nama Barang
                        jenis_barang,      # Jenis Barang
                        kubikasi,          # Kubikasi
                        m3_val,            # M3
                        ton_val,           # Ton
                        colli_val,         # Col
                        satuan,            # Satuan
                        door,              # Door
                        unit_price_val,    # Unit Price
                        harga_val          # Price
                    ]
                   
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=current_row, column=col, value=value)
                        cell.font = small_font
                        # cell.border = thin_border  # Hapus border untuk data rows
                        # Set minimal row height untuk data
                        ws.row_dimensions[current_row].height = 8  # Lebih kecil karena font 6
                       
                        if col == 1:  # Tgl column
                            cell.alignment = center_align
                        elif col in [7, 8, 9, 12, 13]:  # Numeric columns (M3, Ton, Col, Unit Price, Price)
                            cell.alignment = right_align
                            if col in [12, 13]:  # Unit Price, Price columns
                                cell.number_format = '#,##0'
                            elif col in [7, 8]:  # M3, Ton columns
                                cell.number_format = '0.00'
                        else:
                            cell.alignment = left_align
                   
                    current_row += 1
                   
                except Exception as e:
                    print(f"Error processing barang {i}: {e}")
                    continue
           
            # Total row
            for col in range(1, 14):  # Update range untuk 13 kolom
                cell = ws.cell(row=current_row, column=col)
                cell.border = thin_border  # Kembalikan border untuk total row
                cell.fill = header_fill
                cell.font = table_header_font
               
                if col == 1:
                    cell.value = "TOTAL"
                    cell.alignment = center_align
                elif col == 7:  # M3 total
                    cell.value = total_m3
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 8:  # Ton total
                    cell.value = total_ton
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 9:  # Colli total
                    cell.value = total_colli
                    cell.alignment = right_align
                elif col == 13:  # Price total
                    cell.value = total_nilai
                    cell.number_format = '#,##0'
                    cell.alignment = right_align
           
            current_row += 2
           
            # Summary - COMPACT
            ws[f'A{current_row}'] = f"Total Items: {len(barang_list)} | Total Value: Rp {total_nilai:,.0f} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ws[f'A{current_row}'].font = small_font
           
            # AUTO-ADJUST Column widths berdasarkan konten terpanjang
            # Calculate optimal width untuk setiap kolom
            header_lengths = [len(h) for h in headers]
            
            # Estimate konten width (tambah buffer untuk safety)
            estimated_widths = [
                8,   # Tgl: "24-Aug" = 6 chars + buffer
                20,  # Pengirim: nama company bisa panjang
                20,  # Penerima: nama company bisa panjang  
                25,  # Nama Barang: bisa sangat panjang
                15,  # Jenis Barang: kategori
                12,  # Kubikasi: "50.0×30.0×10.0" = 11 chars
                8,   # M3: "0.02" = 4 chars + buffer
                8,   # Ton: "0.01" = 4 chars + buffer
                6,   # Col: "10" = 2-3 chars + buffer
                8,   # Satuan: "m3/pcs" = 3-5 chars + buffer
                10,  # Door: alamat singkat
                12,  # Unit Price: "150,000" = 7-8 chars + buffer
                12   # Price: "2,250,000" = 9 chars + buffer
            ]
            
            # Apply calculated widths
            for i, width in enumerate(estimated_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
           
            # Set print area
            last_row = current_row
            ws.print_area = f'A1:M{last_row}'
           
            # Add page breaks if needed (every 60 rows karena font dan height lebih kecil)
            header_rows = current_row - len(barang_list) - 1
            if len(barang_list) > 60:
                for i in range(60, len(barang_list), 60):
                    break_row = header_rows + i
                    ws.row_breaks.append(break_row)
           
            # Save file
            filename = f"Invoice_Container_{container_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self._save_excel_file(wb, filename, "INVOICE CONTAINER")
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat Excel invoice: {str(e)}")
   
    def print_customer_packing_list(self, container_id, filter_criteria=None):
        """Generate and export packing list to Excel optimized for printing"""
        try:
            # Get container details
            container = self.db.get_container_by_id(container_id)
            if not container:
                messagebox.showerror("Error", "Container tidak ditemukan!")
                return
           
            # Get barang in container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
           
            if not container_barang:
                messagebox.showwarning("Peringatan", "Container kosong, tidak ada yang akan diprint!")
                return
           
            # No filtering needed anymore since we use sender-receiver combinations
            # Generate Excel packing list
            self._generate_excel_packing_list_optimized(container, container_barang, container_id, filter_criteria)
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat packing list: {str(e)}")
    
    def _generate_excel_packing_list_optimized(self, container, barang_list, container_id, filter_name=None):
        """Generate Excel packing list document optimized for A4 printing - SAMA DENGAN INVOICE TANPA HARGA"""
        try:
            # Create new workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Customer Packing List"
           
            # SET PAGE LAYOUT FOR A4 PRINT
            ws.page_setup.paperSize = ws.PAPERSIZE_A4
            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
            ws.page_setup.fitToPage = True
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0
            
            # Set margins
            ws.page_margins = PageMargins(
                left=0.5, right=0.5, top=0.75, bottom=0.75, 
                header=0.3, footer=0.3
            )
            
            ws.print_options.horizontalCentered = True
           
            # Define optimized styles - SAMA DENGAN INVOICE
            header_font = Font(name='Arial', size=12, bold=True)
            company_font = Font(name='Arial', size=10, bold=True)
            normal_font = Font(name='Arial', size=7)
            small_font = Font(name='Arial', size=6)    # Size 6 
            table_header_font = Font(name='Arial', size=6, bold=True)  # Size 6
           
            center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
            left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
            right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
           
            # Border hanya untuk header dan total row
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
           
            header_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
           
            # Safe way to get container values
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return container.get(key, default) or default
                    else:
                        return container[key] if key in container and container[key] else default
                except:
                    return default
           
            # Header section - COMPACT
            current_row = 1
           
            # Title - Merge to column K (11 kolom tanpa Unit Price & Price)
            ws.merge_cells(f'A{current_row}:K{current_row}')
            ws[f'A{current_row}'] = "CUSTOMER PACKING LIST"
            ws[f'A{current_row}'].font = header_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 1
           
            # Company info - COMPACT
            ws.merge_cells(f'A{current_row}:K{current_row}')
            ws[f'A{current_row}'] = "CV. CAHAYA KARUNIA | Jl. Teluk Raya Selatan No. 6 Surabaya | Phone: 031-60166017"
            ws[f'A{current_row}'].font = normal_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 2
           
            # Container information - 3 PER KOLOM LAYOUT (SAMA DENGAN INVOICE)
            container_info = [
                ("Container No", safe_get('container')),
                ("Feeder", safe_get('feeder')),
                ("Destination", safe_get('destination')),
                ("Party", safe_get('party')),
                ("ETD Sub", safe_get('etd_sub')),
                ("CLS", safe_get('cls')),
                ("Open", safe_get('open')),
                ("Full", safe_get('full')),
                ("Seal", safe_get('seal')),
                ("Ref JOA", safe_get('ref_joa'))
            ]
            
            info_start_row = current_row
            
            # Arrange in 3 columns (4 rows each column, since we have 10 items)
            for i, (label, value) in enumerate(container_info):
                col_group = i // 4  # 0, 1, 2 (3 groups)
                row_in_group = i % 4  # 0, 1, 2, 3 (4 rows per group)
                
                row = info_start_row + row_in_group
                col_start = col_group * 4 + 1  # Columns: 1, 5, 9
                
                # Label
                ws[f'{get_column_letter(col_start)}{row}'] = f"{label}:"
                ws[f'{get_column_letter(col_start)}{row}'].font = small_font
                # Value  
                ws[f'{get_column_letter(col_start + 1)}{row}'] = str(value)
                ws[f'{get_column_letter(col_start + 1)}{row}'].font = small_font
                
                # Set minimal row height untuk container info
                ws.row_dimensions[row].height = 8
            
            current_row = info_start_row + 4 + 1  # 4 rows + 1 spacing
           
            # Table headers - SAMA DENGAN INVOICE TAPI TANPA HARGA
            headers = ['Tgl', 'Pengirim', 'Penerima', 'Nama Barang', 'Jenis Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Satuan', 'Door']
           
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = table_header_font
                cell.alignment = center_align
                cell.border = thin_border  # Border untuk header
                cell.fill = header_fill
                # Set minimal height untuk header
                ws.row_dimensions[current_row].height = 8
           
            current_row += 1
           
            # Table data with GROUPING (SAMA DENGAN INVOICE)
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            
            # Variables untuk tracking grouping
            previous_date = None
            previous_pengirim = None
            previous_penerima = None
           
            for i, barang_row in enumerate(barang_list, 1):
                # Convert sqlite3.Row to dictionary
                barang = dict(barang_row) if hasattr(barang_row, 'keys') else barang_row
    
                try:
                    # Safe way to get barang values
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                   
                    # Format date - get tanggal or use current date
                    tanggal = safe_barang_get('tanggal_barang', datetime.now())
                    if isinstance(tanggal, str):
                        try:
                            tanggal = datetime.strptime(tanggal, '%Y-%m-%d')
                        except:
                            tanggal = datetime.now()
                    formatted_date = tanggal.strftime('%d-%b') if isinstance(tanggal, datetime) else '-'
                    
                    pengirim = str(safe_barang_get('sender_name', '-'))
                    penerima = str(safe_barang_get('receiver_name', '-'))
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))
                    
                    # Door info
                    door = str(safe_barang_get('door_type', safe_barang_get('alamat_tujuan', '-')))[:10]

                    # Format dimensions (Kubikasi)
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    kubikasi = f"{p}×{l}×{t}"
                   
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    satuan = str(safe_barang_get('satuan', safe_barang_get('unit', 'pcs')))[:6]
                   
                    # Add to totals
                    try:
                        total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                        total_ton += float(ton) if ton not in [None, '', '-'] else 0
                        total_colli += int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                   
                    # Format values for display
                    m3_val = float(m3) if m3 not in [None, '', '-'] else 0
                    ton_val = float(ton) if ton not in [None, '', '-'] else 0
                    colli_val = int(colli) if colli not in [None, '', '-'] else 0
                    
                    # GROUPING LOGIC - Cek apakah tgl, pengirim, penerima sama dengan baris sebelumnya
                    display_date = formatted_date
                    display_pengirim = pengirim
                    display_penerima = penerima
                    
                    if (formatted_date == previous_date and 
                        pengirim == previous_pengirim and 
                        penerima == previous_penerima):
                        # Jika sama dengan baris sebelumnya, kosongkan
                        display_date = ""
                        display_pengirim = ""
                        display_penerima = ""
                    else:
                        # Update tracking variables
                        previous_date = formatted_date
                        previous_pengirim = pengirim
                        previous_penerima = penerima
                   
                    # Fill row data - TANPA HARGA
                    row_data = [
                        display_date,       # Tgl (kosong jika sama dengan sebelumnya)
                        display_pengirim,   # Pengirim (kosong jika sama dengan sebelumnya)  
                        display_penerima,   # Penerima (kosong jika sama dengan sebelumnya)
                        nama_barang,       # Nama Barang
                        jenis_barang,      # Jenis Barang
                        kubikasi,          # Kubikasi
                        m3_val,            # M3
                        ton_val,           # Ton
                        colli_val,         # Col
                        satuan,            # Satuan
                        door               # Door
                    ]
                   
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=current_row, column=col, value=value)
                        cell.font = small_font
                        # Tidak ada border untuk data rows
                        # Set minimal row height untuk data
                        ws.row_dimensions[current_row].height = 8
                       
                        if col == 1:  # Tgl column
                            cell.alignment = center_align
                        elif col in [7, 8, 9]:  # Numeric columns (M3, Ton, Col)
                            cell.alignment = right_align
                            if col in [7, 8]:  # M3, Ton columns
                                cell.number_format = '0.00'
                        else:
                            cell.alignment = left_align
                   
                    current_row += 1
                   
                except Exception as e:
                    print(f"Error processing barang {i}: {e}")
                    continue
           
            # Total row
            for col in range(1, 12):  # Update range untuk 11 kolom
                cell = ws.cell(row=current_row, column=col)
                cell.border = thin_border  # Border untuk total row
                cell.fill = header_fill
                cell.font = table_header_font
               
                if col == 1:
                    cell.value = "TOTAL"
                    cell.alignment = center_align
                elif col == 7:  # M3 total
                    cell.value = total_m3
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 8:  # Ton total
                    cell.value = total_ton
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 9:  # Colli total
                    cell.value = total_colli
                    cell.alignment = right_align
           
            current_row += 2
           
            # Summary - COMPACT (tanpa total value karena tanpa harga)
            ws[f'A{current_row}'] = f"Total Items: {len(barang_list)} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ws[f'A{current_row}'].font = small_font
           
            # AUTO-ADJUST Column widths untuk packing list (tanpa harga)
            estimated_widths = [
                8,   # Tgl: "24-Aug" 
                20,  # Pengirim: nama company bisa panjang
                20,  # Penerima: nama company bisa panjang  
                25,  # Nama Barang: bisa sangat panjang
                15,  # Jenis Barang: kategori
                12,  # Kubikasi: "50.0×30.0×10.0"
                8,   # M3: "0.02" 
                8,   # Ton: "0.01" 
                6,   # Col: "10" 
                8,   # Satuan: "m3/pcs" 
                10   # Door: alamat singkat
            ]
            
            # Apply calculated widths
            for i, width in enumerate(estimated_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
           
            # Set print area
            last_row = current_row
            ws.print_area = f'A1:K{last_row}'
           
            # Save file
            filter_suffix = f"_{filter_name}" if filter_name else "_All_Combinations"
            filename = f"PackingList_Container_{container_id}{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self._save_excel_file(wb, filename, "CUSTOMER PACKING LIST")
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat Excel packing list: {str(e)}")
   
    def _save_excel_file(self, workbook, filename, doc_type):
        """Save Excel workbook to file with print preview info"""
        try:
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename,
                title=f"Save {doc_type}"
            )
           
            if file_path:
                workbook.save(file_path)
                messagebox.showinfo(
                    "Sukses",
                    f"📊 {doc_type} berhasil disimpan!\n\n"
                    f"📁 Lokasi: {file_path}\n\n"
                    f"🖨️ OPTIMIZED untuk print A4 Landscape\n"
                    f"💡 Buka Excel → Print Preview untuk melihat hasil print\n"
                    f"⚙️ Pastikan setting printer: A4, Landscape, Fit to 1 page wide"
                )
               
                # Ask if user wants to open the file
                if messagebox.askyesno("Buka File?", f"Apakah Anda ingin membuka file Excel sekarang?"):
                    try:
                        if os.name == 'nt':  # Windows
                            os.startfile(file_path)
                        elif os.name == 'posix':  # macOS and Linux
                            os.system(f'open "{file_path}"')  # macOS
                    except Exception as e:
                        messagebox.showwarning("Info", f"File berhasil disimpan, tapi gagal membuka otomatis.\nSilakan buka manual: {file_path}")
       
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file Excel: {str(e)}")
   
    def show_sender_receiver_selection_dialog(self, container_id):
        """Show dialog to select sender/receiver for packing list"""
        try:
            # Get unique senders and receivers in this container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
            # Convert to dict if needed
            barang_dicts = []
            for b in container_barang:
                if hasattr(b, 'keys'):
                    barang_dicts.append(dict(b))
                else:
                    barang_dicts.append(b)
            
            # Get unique senders (pengirim)
            senders = list(set(b.get('sender_name', '-') for b in barang_dicts if b.get('sender_name')))
            # Get unique receivers (penerima)  
            receivers = list(set(b.get('receiver_name', '-') for b in barang_dicts if b.get('receiver_name')))
            
            # Combine unique combinations of sender-receiver
            sender_receiver_pairs = list(set(
                (b.get('sender_name', '-'), b.get('receiver_name', '-')) 
                for b in barang_dicts 
                if b.get('sender_name') and b.get('receiver_name')
            ))
           
            if not sender_receiver_pairs:
                messagebox.showwarning("Peringatan", "Tidak ada data pengirim/penerima di container ini!")
                return
           
            if len(sender_receiver_pairs) == 1:
                # Only one pair, export directly
                sender, receiver = sender_receiver_pairs[0]
                self.print_sender_receiver_packing_list(container_id, sender, receiver)
                return
           
            # Multiple pairs, show selection dialog
            selection_window = tk.Toplevel()
            selection_window.title("Pilih Pengirim & Penerima")
            selection_window.geometry("600x450")
            selection_window.configure(bg='#ecf0f1')
            selection_window.focus_set()
            selection_window.grab_set()
           
            # Header
            header = tk.Label(
                selection_window,
                text="📊 PILIH PENGIRIM & PENERIMA UNTUK EXCEL PACKING LIST",
                font=('Arial', 14, 'bold'),
                bg='#e67e22',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
           
            # Instructions
            tk.Label(
                selection_window,
                text="Pilih kombinasi pengirim & penerima untuk packing list Excel:",
                font=('Arial', 11),
                bg='#ecf0f1'
            ).pack(pady=10)
           
            # Sender-Receiver list
            list_frame = tk.Frame(selection_window, bg='#ecf0f1')
            list_frame.pack(fill='both', expand=True, padx=20, pady=10)
           
            list_frame.grid_rowconfigure(0, weight=1)
            list_frame.grid_columnconfigure(0, weight=1)
           
            pair_listbox = tk.Listbox(list_frame, font=('Arial', 10), height=12,
                                    selectmode='single', activestyle='dotbox')
           
            # Add "All Combinations" option
            pair_listbox.insert(tk.END, "📊 ALL COMBINATIONS")
           
            # Add individual sender-receiver pairs
            for sender, receiver in sorted(sender_receiver_pairs):
                pair_listbox.insert(tk.END, f"📤 {sender} → 📥 {receiver}")
           
            # Select first item by default
            pair_listbox.selection_set(0)
            pair_listbox.activate(0)
           
            # Scrollbar for listbox
            scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=pair_listbox.yview)
            pair_listbox.configure(yscrollcommand=scrollbar.set)
           
            # Grid layout
            pair_listbox.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')
           
            # Enable mouse wheel scrolling
            def on_mousewheel(event):
                pair_listbox.yview_scroll(int(-1*(event.delta/120)), "units")
           
            pair_listbox.bind("<MouseWheel>", on_mousewheel)
            selection_window.bind("<MouseWheel>", on_mousewheel)
           
            # For Linux
            pair_listbox.bind("<Button-4>", lambda e: pair_listbox.yview_scroll(-1, "units"))
            pair_listbox.bind("<Button-5>", lambda e: pair_listbox.yview_scroll(1, "units"))
           
            # Buttons
            btn_frame = tk.Frame(selection_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', padx=20, pady=15)
           
            def export_selected():
                selection = pair_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Peringatan", "Pilih pengirim & penerima terlebih dahulu!")
                    return
               
                selected_text = pair_listbox.get(selection[0])
               
                if selected_text.startswith("📊 ALL COMBINATIONS"):
                    # Export for all combinations
                    self.print_customer_packing_list(container_id, None)
                else:
                    # Export for specific sender-receiver pair
                    # Parse "📤 SENDER → 📥 RECEIVER"
                    parts = selected_text.replace("📤 ", "").replace("📥 ", "").split(" → ")
                    if len(parts) == 2:
                        sender, receiver = parts[0].strip(), parts[1].strip()
                        self.print_sender_receiver_packing_list(container_id, sender, receiver)
               
                selection_window.destroy()
           
            def on_double_click(event):
                export_selected()
           
            # Bind double click
            pair_listbox.bind("<Double-Button-1>", on_double_click)
           
            # Bind Enter key
            def on_enter(event):
                export_selected()
           
            selection_window.bind("<Return>", on_enter)
            pair_listbox.bind("<Return>", on_enter)
           
            tk.Button(
                btn_frame,
                text="📊 Export to Excel (Print Ready)",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=25,
                pady=10,
                command=export_selected
            ).pack(side='left', padx=(0, 15))
           
            tk.Button(
                btn_frame,
                text="❌ Batal",
                font=('Arial', 12, 'bold'),
                bg='#e74c3c',
                fg='white',
                padx=25,
                pady=10,
                command=selection_window.destroy
            ).pack(side='right')
           
            # Center window
            selection_window.update_idletasks()
            x = (selection_window.winfo_screenwidth() // 2) - (300)
            y = (selection_window.winfo_screenheight() // 2) - (225)
            selection_window.geometry(f"600x450+{x}+{y}")
           
            # Focus on listbox after creation
            selection_window.after(100, lambda: pair_listbox.focus_set())
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat dialog selection: {str(e)}")

    def print_sender_receiver_packing_list(self, container_id, sender_name, receiver_name):
        """Generate packing list for specific sender-receiver combination"""
        try:
            # Get container details
            container = self.db.get_container_by_id(container_id)
            if not container:
                messagebox.showerror("Error", "Container tidak ditemukan!")
                return
           
            # Get barang in container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
           
            if not container_barang:
                messagebox.showwarning("Peringatan", "Container kosong, tidak ada yang akan diprint!")
                return
           
            # Filter for specific sender-receiver combination
            filtered_barang = []
            for b in container_barang:
                barang_dict = dict(b) if hasattr(b, 'keys') else b
                if (barang_dict.get('sender_name') == sender_name and 
                    barang_dict.get('receiver_name') == receiver_name):
                    filtered_barang.append(barang_dict)
            
            if not filtered_barang:
                messagebox.showwarning("Peringatan", f"Tidak ada barang untuk {sender_name} → {receiver_name}!")
                return
           
            # Generate Excel packing list with custom filename
            self._generate_excel_packing_list_optimized(
                container, filtered_barang, container_id, 
                f"{sender_name}_to_{receiver_name}"
            )
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat packing list: {str(e)}")

    def create_print_settings_dialog(self):
        """Dialog untuk setting print preferences"""
        try:
            settings_window = tk.Toplevel()
            settings_window.title("Print Settings")
            settings_window.geometry("400x300")
            settings_window.configure(bg='#ecf0f1')
            settings_window.focus_set()
            settings_window.grab_set()
           
            # Header
            header = tk.Label(
                settings_window,
                text="🖨️ PRINT SETTINGS",
                font=('Arial', 14, 'bold'),
                bg='#3498db',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
           
            # Settings frame
            settings_frame = tk.Frame(settings_window, bg='#ecf0f1')
            settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
           
            # Paper size setting
            tk.Label(settings_frame, text="Paper Size:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(anchor='w')
            paper_var = tk.StringVar(value="A4")
            paper_frame = tk.Frame(settings_frame, bg='#ecf0f1')
            paper_frame.pack(fill='x', pady=5)
            
            tk.Radiobutton(paper_frame, text="A4", variable=paper_var, value="A4", bg='#ecf0f1').pack(side='left')
            tk.Radiobutton(paper_frame, text="Letter", variable=paper_var, value="Letter", bg='#ecf0f1').pack(side='left', padx=20)
           
            # Orientation setting
            tk.Label(settings_frame, text="Orientation:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(15,0))
            orient_var = tk.StringVar(value="Landscape")
            orient_frame = tk.Frame(settings_frame, bg='#ecf0f1')
            orient_frame.pack(fill='x', pady=5)
            
            tk.Radiobutton(orient_frame, text="Landscape (Recommended)", variable=orient_var, value="Landscape", bg='#ecf0f1').pack(side='left')
            tk.Radiobutton(orient_frame, text="Portrait", variable=orient_var, value="Portrait", bg='#ecf0f1').pack(side='left', padx=20)
           
            # Font size setting
            tk.Label(settings_frame, text="Font Size:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(15,0))
            font_var = tk.StringVar(value="Small")
            font_frame = tk.Frame(settings_frame, bg='#ecf0f1')
            font_frame.pack(fill='x', pady=5)
            
            tk.Radiobutton(font_frame, text="Small (Recommended)", variable=font_var, value="Small", bg='#ecf0f1').pack(side='left')
            tk.Radiobutton(font_frame, text="Normal", variable=font_var, value="Normal", bg='#ecf0f1').pack(side='left', padx=20)
           
            # Fit to page setting
            fit_var = tk.BooleanVar(value=True)
            tk.Checkbutton(settings_frame, text="Fit to one page width", variable=fit_var, bg='#ecf0f1', font=('Arial', 11)).pack(anchor='w', pady=(15,0))
           
            # Buttons
            btn_frame = tk.Frame(settings_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', padx=20, pady=15)
           
            def apply_settings():
                # Here you would apply the settings to your print handler
                # For now, just show confirmation
                messagebox.showinfo("Settings Applied", 
                    f"Print settings applied:\n"
                    f"Paper: {paper_var.get()}\n"
                    f"Orientation: {orient_var.get()}\n"
                    f"Font: {font_var.get()}\n"
                    f"Fit to page: {fit_var.get()}")
                settings_window.destroy()
           
            tk.Button(
                btn_frame,
                text="✓ Apply Settings",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=25,
                pady=10,
                command=apply_settings
            ).pack(side='left')
           
            tk.Button(
                btn_frame,
                text="❌ Cancel",
                font=('Arial', 12, 'bold'),
                bg='#e74c3c',
                fg='white',
                padx=25,
                pady=10,
                command=settings_window.destroy
            ).pack(side='right')
           
            # Center window
            settings_window.update_idletasks()
            x = (settings_window.winfo_screenwidth() // 2) - (200)
            y = (settings_window.winfo_screenheight() // 2) - (150)
            settings_window.geometry(f"400x300+{x}+{y}")
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat dialog settings: {str(e)}")