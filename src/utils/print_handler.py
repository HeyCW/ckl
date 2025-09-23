import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import traceback
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins
from src.widget.pdf_packing_list_generator import PDFPackingListGenerator

class PrintHandler:
    def __init__(self, db):
        self.pdf_generator = PDFPackingListGenerator(db)
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
        """Generate Excel invoice document optimized for A4 printing with profit calculation"""
        try:
            # Create new workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Invoice Packing List"
        
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
        
            # Define optimized styles
            header_font = Font(name='Arial', size=12, bold=True)
            company_font = Font(name='Arial', size=10, bold=True)
            normal_font = Font(name='Arial', size=7)
            small_font = Font(name='Arial', size=6)
            table_header_font = Font(name='Arial', size=6, bold=True)
            profit_header_font = Font(name='Arial', size=8, bold=True)
            profit_font = Font(name='Arial', size=7)
        
            center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
            left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
            right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
        
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
            # header_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
            # profit_header_fill = PatternFill(start_color='FFE6CC', end_color='FFE6CC', fill_type='solid')
        
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
        
            # Title
            ws.merge_cells(f'A{current_row}:M{current_row}')
            ws[f'A{current_row}'] = "INVOICE CONTAINER"
            ws[f'A{current_row}'].font = header_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 1
        
            # Company info
            ws.merge_cells(f'A{current_row}:M{current_row}')
            ws[f'A{current_row}'] = "CV. CAHAYA KARUNIA | Jl. Teluk Raya Selatan No. 6 Surabaya | Phone: 031-60166017"
            ws[f'A{current_row}'].font = normal_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 2
        
            # Container information - 3 columns layout
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
            
            for i, (label, value) in enumerate(container_info):
                col_group = i // 4
                row_in_group = i % 4
                
                row = info_start_row + row_in_group
                col_start = col_group * 4 + 1
                
                ws[f'{get_column_letter(col_start)}{row}'] = f"{label}:"
                ws[f'{get_column_letter(col_start)}{row}'].font = small_font
                ws[f'{get_column_letter(col_start + 1)}{row}'] = str(value)
                ws[f'{get_column_letter(col_start + 1)}{row}'].font = small_font
                
                ws.row_dimensions[row].height = 10
            
            current_row = info_start_row + 4 + 1
        
            # Table headers
            headers = ['Tgl', 'Pengirim', 'Penerima', 'Nama Barang', 'Jenis Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Satuan', 'Door', 'Unit Price', 'Price']
        
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = table_header_font
                cell.alignment = center_align
                cell.border = thin_border
                # cell.fill = header_fill
                ws.row_dimensions[current_row].height = 8
        
            current_row += 1
        
            # Table data with GROUPING
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            total_nilai = 0
            
            previous_date = None
            previous_pengirim = None
            previous_penerima = None
        
            for i, barang_row in enumerate(barang_list, 1):
                barang = dict(barang_row)

                try:
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                
                    # Format date
                    tanggal = safe_barang_get('tanggal_barang', datetime.now())
                    if isinstance(tanggal, str):
                        try:
                            tanggal = datetime.strptime(tanggal, '%Y-%m-%d')
                        except:
                            tanggal = datetime.now()
                    formatted_date = tanggal.strftime('%d-%b') if isinstance(tanggal, datetime) else '-'
                    
                    pengirim = str(safe_barang_get('sender_name', '-'))
                    penerima = str(safe_barang_get('receiver_name', '-'))
                    nama_barang = str(safe_barang_get('nama_barang', '-'))[:20]
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))[:15]
                    
                    door = str(safe_barang_get('door_type', safe_barang_get('alamat_tujuan', '-')))[:10]

                    # Format dimensions
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    kubikasi = f"{p}×{l}×{t}"
                    if len(kubikasi) > 12:
                        kubikasi = kubikasi[:9] + "..."
                
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    satuan = str(safe_barang_get('satuan', safe_barang_get('unit', 'pcs')))[:6]
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
                
                    # Format values
                    m3_val = float(m3) if m3 not in [None, '', '-'] else 0
                    ton_val = float(ton) if ton not in [None, '', '-'] else 0
                    colli_val = int(colli) if colli not in [None, '', '-'] else 0
                    unit_price_val = float(unit_price) if unit_price not in [None, '', '-'] else 0
                    harga_val = float(total_harga) if total_harga not in [None, '', '-'] else 0
                    
                    # GROUPING LOGIC
                    display_date = formatted_date
                    display_pengirim = pengirim
                    display_penerima = penerima
                    
                    if (formatted_date == previous_date and 
                        pengirim == previous_pengirim and 
                        penerima == previous_penerima):
                        display_date = ""
                        display_pengirim = ""
                        display_penerima = ""
                    else:
                        previous_date = formatted_date
                        previous_pengirim = pengirim
                        previous_penerima = penerima
                
                    # Fill row data
                    row_data = [
                        display_date, display_pengirim, display_penerima, nama_barang,
                        jenis_barang, kubikasi, m3_val, ton_val, colli_val, satuan,
                        door, unit_price_val, harga_val
                    ]
                
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=current_row, column=col, value=value)
                        cell.font = small_font
                        ws.row_dimensions[current_row].height = 8
                    
                        if col == 1:
                            cell.alignment = center_align
                        elif col in [7, 8, 9, 12, 13]:
                            cell.alignment = right_align
                            if col in [12, 13]:
                                cell.number_format = '#,##0'
                            elif col in [7, 8]:
                                cell.number_format = '0.00'
                        else:
                            cell.alignment = left_align
                
                    current_row += 1
                
                except Exception as e:
                    print(f"Error processing barang {i}: {e}")
                    continue
        
            # Total row
            for col in range(1, 14):
                cell = ws.cell(row=current_row, column=col)
                cell.border = thin_border
                # cell.fill = header_fill
                cell.font = table_header_font
            
                if col == 1:
                    cell.value = "TOTAL"
                    cell.alignment = center_align
                elif col == 7:
                    cell.value = total_m3
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 8:
                    cell.value = total_ton
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 9:
                    cell.value = total_colli
                    cell.alignment = right_align
                elif col == 13:
                    cell.value = total_nilai
                    cell.number_format = '#,##0'
                    cell.alignment = right_align
        
            current_row += 3  # Space before profit calculation
        
            # ===== PROFIT CALCULATION SECTION - HANYA JIKA ADA DATA =====
            
            # Get cost data from database
            try:
                costs_surabaya = self._get_container_costs(container_id, 'Surabaya')
                costs_destinasi = self._get_container_costs(container_id, container.get('destination', 'Samarinda'))
            except Exception as e:
                print(f"Error getting costs from database: {e}")
                costs_surabaya = None
                costs_destinasi = None

            # HANYA TAMPILKAN PROFIT CALCULATION JIKA ADA DATA COST
            if costs_surabaya or costs_destinasi:
                # Jika salah satu kosong, buat dictionary kosong
                if not costs_surabaya:
                    costs_surabaya = {}
                if not costs_destinasi:
                    costs_destinasi = {}
                
                # Calculate totals - hanya dari data yang ada
                def safe_sum_costs(costs_dict):
                    if not costs_dict:
                        return 0
                    total = 0
                    for value in costs_dict.values():
                        try:
                            if isinstance(value, (tuple, list)):
                                total += float(value[0]) if len(value) > 0 else 0
                            else:
                                total += float(value) if value else 0
                        except (ValueError, TypeError):
                            continue
                    return total
                
                total_biaya_surabaya = safe_sum_costs(costs_surabaya)
                total_biaya_samarinda = safe_sum_costs(costs_destinasi)
                total_biaya = total_biaya_surabaya + total_biaya_samarinda
                profit_lcl = total_nilai - total_biaya
                
                # BIAYA SURABAYA SECTION - HANYA JIKA ADA DATA
                if costs_surabaya:
                    ws.merge_cells(f'A{current_row}:L{current_row}')
                    ws[f'A{current_row}'] = "Biaya Surabaya"
                    ws[f'A{current_row}'].font = profit_header_font
                    ws[f'A{current_row}'].alignment = left_align
                    # ws[f'A{current_row}'].fill = profit_header_fill
                    ws[f'A{current_row}'].border = thin_border
                    
                    ws[f'M{current_row}'] = "Cost (Rp)"
                    ws[f'M{current_row}'].font = profit_header_font
                    ws[f'M{current_row}'].alignment = right_align
                    # ws[f'M{current_row}'].fill = profit_header_fill
                    ws[f'M{current_row}'].border = thin_border
                    current_row += 1
                    
                    # Biaya Surabaya items
                    for cost_name, cost_value in costs_surabaya.items():
                        ws[f'A{current_row}'] = cost_name
                        ws[f'A{current_row}'].font = profit_font
                        ws[f'A{current_row}'].alignment = left_align
                        
                        # Safe handling untuk cost_value
                        try:
                            if isinstance(cost_value, (tuple, list)) and len(cost_value) >= 2:
                                cost_desc = str(cost_value[1])
                                cost_amount = float(cost_value[0])
                            else:
                                cost_desc = ""
                                cost_amount = float(cost_value) if cost_value else 0
                        except (ValueError, TypeError):
                            cost_desc = ""
                            cost_amount = 0

                        ws[f'B{current_row}'] = cost_desc
                        ws[f'B{current_row}'].font = profit_font
                        ws[f'B{current_row}'].alignment = left_align

                        ws[f'M{current_row}'] = cost_amount
                        ws[f'M{current_row}'].font = profit_font
                        ws[f'M{current_row}'].alignment = right_align
                        ws[f'M{current_row}'].number_format = '#,##0'
                        current_row += 1
                    
                    # Total Biaya Surabaya
                    ws[f'M{current_row}'] = total_biaya_surabaya
                    ws[f'M{current_row}'].font = Font(name='Arial', size=8, bold=True)
                    ws[f'M{current_row}'].alignment = right_align
                    ws[f'M{current_row}'].number_format = '#,##0'
                    ws[f'M{current_row}'].border = thin_border
                    current_row += 2
                
                # BIAYA DESTINASI SECTION - HANYA JIKA ADA DATA
                if costs_destinasi:
                    destination_name = container.get('destination', 'Destinasi')
                    ws.merge_cells(f'A{current_row}:L{current_row}')
                    ws[f'A{current_row}'] = f"Biaya {destination_name}"
                    ws[f'A{current_row}'].font = profit_header_font
                    ws[f'A{current_row}'].alignment = left_align
                    # ws[f'A{current_row}'].fill = profit_header_fill
                    ws[f'A{current_row}'].border = thin_border

                    ws[f'M{current_row}'] = "Cost (Rp)"
                    ws[f'M{current_row}'].font = profit_header_font
                    ws[f'M{current_row}'].alignment = right_align
                    # ws[f'M{current_row}'].fill = profit_header_fill
                    ws[f'M{current_row}'].border = thin_border
                    current_row += 1
                    
                    # Biaya Destinasi items
                    for cost_name, cost_value in costs_destinasi.items():
                        ws[f'A{current_row}'] = cost_name
                        ws[f'A{current_row}'].font = profit_font
                        ws[f'A{current_row}'].alignment = left_align
                        
                        try:
                            if isinstance(cost_value, (tuple, list)) and len(cost_value) >= 2:
                                cost_desc = str(cost_value[1])
                                cost_amount = float(cost_value[0])
                            else:
                                cost_desc = ""
                                cost_amount = float(cost_value) if cost_value else 0
                        except (ValueError, TypeError):
                            cost_desc = ""
                            cost_amount = 0

                        ws[f'B{current_row}'] = cost_desc
                        ws[f'B{current_row}'].font = profit_font
                        ws[f'B{current_row}'].alignment = left_align

                        ws[f'M{current_row}'] = cost_amount
                        ws[f'M{current_row}'].font = profit_font
                        ws[f'M{current_row}'].alignment = right_align
                        ws[f'M{current_row}'].number_format = '#,##0'
                        current_row += 1
                    
                    # Total Biaya Destinasi
                    ws[f'M{current_row}'] = total_biaya_samarinda
                    ws[f'M{current_row}'].font = Font(name='Arial', size=8, bold=True)
                    ws[f'M{current_row}'].alignment = right_align
                    ws[f'M{current_row}'].number_format = '#,##0'
                    ws[f'M{current_row}'].border = thin_border
                    current_row += 2
                
                # PROFIT CALCULATION - HANYA JIKA ADA BIAYA
                if costs_surabaya or costs_destinasi:
                    ws.merge_cells(f'A{current_row}:L{current_row}')
                    ws[f'A{current_row}'] = "PROFIT LCL"
                    ws[f'A{current_row}'].font = Font(name='Arial', size=10, bold=True)
                    ws[f'A{current_row}'].alignment = left_align
                    ws[f'A{current_row}'].fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
                    ws[f'A{current_row}'].border = thin_border
                    
                    ws[f'M{current_row}'] = profit_lcl
                    ws[f'M{current_row}'].font = Font(name='Arial', size=10, bold=True)
                    ws[f'M{current_row}'].alignment = right_align
                    ws[f'M{current_row}'].number_format = '#,##0'
                    ws[f'M{current_row}'].fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
                    ws[f'M{current_row}'].border = thin_border
                    current_row += 2
            else:
                # Jika tidak ada data cost sama sekali, skip profit section
                pass

            # Summary - update untuk mencakup status cost
            # if costs_surabaya or costs_destinasi:
            #     summary_text = f"Total Items: {len(barang_list)} | Total Revenue: Rp {total_nilai:,.0f} | Total Cost: Rp {total_biaya:,.0f} | Profit: Rp {profit_lcl:,.0f} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            # else:
            #     summary_text = f"Total Items: {len(barang_list)} | Total Revenue: Rp {total_nilai:,.0f} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # ws[f'A{current_row}'] = summary_text
            # ws[f'A{current_row}'].font = small_font
        
            # AUTO-ADJUST Column widths
            estimated_widths = [
                8,   # Tgl
                20,  # Pengirim
                20,  # Penerima  
                25,  # Nama Barang
                15,  # Jenis Barang
                12,  # Kubikasi
                8,   # M3
                8,   # Ton
                6,   # Col
                8,   # Satuan
                10,  # Door
                12,  # Unit Price
                12   # Price
            ]
            
            # Apply calculated widths
            for i, width in enumerate(estimated_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
        
            # Set print area
            last_row = current_row
            ws.print_area = f'A1:M{last_row}'
        
            # Add page breaks if needed
            if len(barang_list) > 40:  # Reduced because of profit section
                header_rows = current_row - len(barang_list) - 1
                for i in range(40, len(barang_list), 40):
                    break_row = header_rows + i
                    ws.row_breaks.append(break_row)
        
            # Save file
            filename = f"Invoice_Container_{container_id}_with_Profit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self._save_excel_file(wb, filename, "INVOICE CONTAINER WITH PROFIT CALCULATION")
        
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat Excel invoice: {str(e)}")
            print(f"Full error: {traceback.format_exc()}")
            
        
    def _get_container_costs(self, container_id, location):
        """Get container costs from database by location (SURABAYA or SAMARINDA)"""
        try:
            # Query untuk mengambil biaya dari database
            result = self.db.execute("""
                SELECT description, cost_description, cost 
                FROM container_delivery_costs 
                WHERE container_id = ? AND delivery = ?
                ORDER BY id
            """, (container_id, location))
            
            # Convert to dictionary - return only cost values as numbers
            costs_dict = {}
            for row in result:
                # Use description as key, cost as value (convert to float)
                key = row['description']
                value = (float(row['cost']), row['cost_description'])
                costs_dict[key] = value
            
            return costs_dict if costs_dict else None
            
        except Exception as e:
            print(f"Error getting container costs: {e}")
            return None

    # [Other methods remain the same...]
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
        """Show dialog to select sender-receiver combinations for packing list"""
        try:
            # Get all sender-receiver combinations in the container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
            if not container_barang:
                messagebox.showwarning("Peringatan", "Container kosong!")
                return
            
            # Get unique sender-receiver combinations
            combinations = set()
            for barang in container_barang:
                # Handle both dict and sqlite3.Row objects
                if hasattr(barang, 'keys'):  # sqlite3.Row object
                    sender = barang['sender_name'] if 'sender_name' in barang.keys() and barang['sender_name'] else '-'
                    receiver = barang['receiver_name'] if 'receiver_name' in barang.keys() and barang['receiver_name'] else '-'
                else:  # dict object
                    sender = barang.get('sender_name', '-')
                    receiver = barang.get('receiver_name', '-')
                combinations.add((sender, receiver))
            
            combinations = sorted(list(combinations))
            
            if not combinations:
                messagebox.showwarning("Peringatan", "Tidak ada data pengirim-penerima!")
                return
            
            # If only one combination, print directly
            if len(combinations) == 1:
                sender, receiver = combinations[0]
                filter_criteria = {'sender_name': sender, 'receiver_name': receiver}
                self.print_customer_packing_list(container_id, filter_criteria)
                return
            
            # Create selection dialog
            dialog = tk.Toplevel()
            dialog.title("Pilih Pengirim - Penerima")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.grab_set()  # Make dialog modal
            
            # Center the dialog
            dialog.transient()
            
            # Header
            header_frame = ttk.Frame(dialog)
            header_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(header_frame, text="Pilih kombinasi Pengirim - Penerima untuk Packing List:", 
                    font=('Arial', 10, 'bold')).pack(anchor='w')
            
            # Listbox with scrollbar
            list_frame = ttk.Frame(dialog)
            list_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side='right', fill='y')
            
            # Listbox
            listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                font=('Arial', 9), height=15)
            listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=listbox.yview)
            
            # Populate listbox
            for i, (sender, receiver) in enumerate(combinations):
                display_text = f"{i+1:2d}. {sender} → {receiver}"
                listbox.insert(tk.END, display_text)
            
            # Select first item by default
            if combinations:
                listbox.selection_set(0)
            
            # Button frame
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill='x', padx=10, pady=10)
            
            # Result variable
            selected_combination = None
            
            def on_print():
                nonlocal selected_combination
                selection = listbox.curselection()
                if selection:
                    idx = selection[0]
                    selected_combination = combinations[idx]
                    dialog.destroy()
            
            def on_print_all():
                nonlocal selected_combination
                selected_combination = "ALL"
                dialog.destroy()
            
            def on_cancel():
                dialog.destroy()
            
            # Buttons
            ttk.Button(button_frame, text="Print Packing List Terpilih", 
                    command=on_print).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Print Semua (Terpisah)", 
                    command=on_print_all).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Batal", 
                    command=on_cancel).pack(side='right', padx=5)
            
            # Bind double-click to print
            listbox.bind('<Double-1>', lambda e: on_print())
            
            # Wait for dialog to close
            dialog.wait_window()
            
            # Process selection
            if selected_combination:
                if selected_combination == "ALL":
                    # Print separate packing list for each combination
                    for sender, receiver in combinations:
                        filter_criteria = {'sender_name': sender, 'receiver_name': receiver}
                        self.print_customer_packing_list(container_id, filter_criteria)
                else:
                    # Print selected combination
                    sender, receiver = selected_combination
                    filter_criteria = {'sender_name': sender, 'receiver_name': receiver}
                    self.print_customer_packing_list(container_id, filter_criteria)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menampilkan dialog pemilihan: {str(e)}")

    def _generate_excel_packing_list_optimized(self, container, barang_list, container_id, filter_criteria=None):
        """Generate Excel packing list document optimized for A4 printing"""
        try:
            # Filter barang if criteria provided
            if filter_criteria:
                filtered_barang = []
                sender_filter = filter_criteria.get('sender_name', '')
                receiver_filter = filter_criteria.get('receiver_name', '')
                
                for barang in barang_list:
                    # Handle both dict and sqlite3.Row objects
                    if hasattr(barang, 'keys'):  # sqlite3.Row object
                        sender = barang['sender_name'] if 'sender_name' in barang.keys() and barang['sender_name'] else ''
                        receiver = barang['receiver_name'] if 'receiver_name' in barang.keys() and barang['receiver_name'] else ''
                    else:  # dict object
                        sender = barang.get('sender_name', '')
                        receiver = barang.get('receiver_name', '')
                    
                    if sender == sender_filter and receiver == receiver_filter:
                        filtered_barang.append(barang)
                
                barang_list = filtered_barang
                
                if not barang_list:
                    messagebox.showwarning("Peringatan", "Tidak ada barang untuk kombinasi yang dipilih!")
                    return
            
            # Create new workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Packing List"
        
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
        
            # Define styles
            header_font = Font(name='Arial', size=14, bold=True)
            company_font = Font(name='Arial', size=10, bold=True)
            normal_font = Font(name='Arial', size=8)
            small_font = Font(name='Arial', size=7)
            table_header_font = Font(name='Arial', size=8, bold=True)
        
            center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
            left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
            right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
        
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
            # header_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
        
            # Safe way to get container values
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return container.get(key, default) or default
                    else:
                        return container[key] if key in container and container[key] else default
                except:
                    return default
        
            # Header section
            current_row = 1
        
            # Title
            ws.merge_cells(f'A{current_row}:K{current_row}')
            ws[f'A{current_row}'] = "PACKING LIST"
            ws[f'A{current_row}'].font = header_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 1
        
            # Company info
            ws.merge_cells(f'A{current_row}:K{current_row}')
            ws[f'A{current_row}'] = "CV. CAHAYA KARUNIA | Jl. Teluk Raya Selatan No. 6 Surabaya | Phone: 031-60166017"
            ws[f'A{current_row}'].font = normal_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 2
        
            # Container information
            container_info = [
                ("Container No", safe_get('container')),
                ("Feeder", safe_get('feeder')),
                ("Destination", safe_get('destination')),
                ("Party", safe_get('party')),
                ("ETD Sub", safe_get('etd_sub')),
                ("CLS", safe_get('cls'))
            ]
            
            # Show sender-receiver info if filtered
            if filter_criteria:
                sender = filter_criteria.get('sender_name', '')
                receiver = filter_criteria.get('receiver_name', '')
                container_info.extend([
                    ("Pengirim", sender),
                    ("Penerima", receiver)
                ])

            info_start_row = current_row
            
            for i, (label, value) in enumerate(container_info):
                col_group = i // 4
                row_in_group = i % 4
                
                row = info_start_row + row_in_group
                col_start = col_group * 3 + 1
                
                ws[f'{get_column_letter(col_start)}{row}'] = f"{label}:"
                ws[f'{get_column_letter(col_start)}{row}'].font = small_font
                ws[f'{get_column_letter(col_start + 1)}{row}'] = str(value)
                ws[f'{get_column_letter(col_start + 1)}{row}'].font = small_font
                
                ws.row_dimensions[row].height = 12
            
            current_row = info_start_row + 4 + 1
        
            # Table headers - simplified for packing list
            headers = ['No', 'Tanggal', 'Nama Barang', 'Jenis Barang', 'Dimensi (cm)', 'M3', 'Ton', 'Colli', 'Satuan', 'Keterangan', 'Door']
        
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = table_header_font
                cell.alignment = center_align
                cell.border = thin_border
                # cell.fill = header_fill
                ws.row_dimensions[current_row].height = 12
        
            current_row += 1
        
            # Table data
            total_m3 = 0
            total_ton = 0
            total_colli = 0
        
            for i, barang_row in enumerate(barang_list, 1):
                # Handle both dict and sqlite3.Row objects
                if hasattr(barang_row, 'keys'):  # sqlite3.Row object
                    barang = {key: barang_row[key] for key in barang_row.keys()}
                else:
                    barang = dict(barang_row)
                
                try:
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                
                    # Format date
                    tanggal = safe_barang_get('tanggal_barang', datetime.now())
                    if isinstance(tanggal, str):
                        try:
                            tanggal = datetime.strptime(tanggal, '%Y-%m-%d')
                        except:
                            tanggal = datetime.now()
                    formatted_date = tanggal.strftime('%d-%b-%Y') if isinstance(tanggal, datetime) else '-'
                    
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))
                    
                    # Format dimensions
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    dimensi = f"{p}×{l}×{t}"
                
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    satuan = str(safe_barang_get('satuan', safe_barang_get('unit', 'pcs')))
                    keterangan = str(safe_barang_get('keterangan', safe_barang_get('notes', '-')))
                    door = str(safe_barang_get('door_type', safe_barang_get('alamat_tujuan', '-')))
                
                    # Add to totals
                    try:
                        total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                        total_ton += float(ton) if ton not in [None, '', '-'] else 0
                        total_colli += int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                
                    # Format values
                    m3_val = float(m3) if m3 not in [None, '', '-'] else 0
                    ton_val = float(ton) if ton not in [None, '', '-'] else 0
                    colli_val = int(colli) if colli not in [None, '', '-'] else 0
                    
                    # Fill row data
                    row_data = [
                        i, formatted_date, nama_barang, jenis_barang,
                        dimensi, m3_val, ton_val, colli_val, satuan, keterangan, door
                    ]
                
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=current_row, column=col, value=value)
                        cell.font = small_font
                        cell.border = thin_border
                        ws.row_dimensions[current_row].height = 10
                    
                        if col == 1:  # No
                            cell.alignment = center_align
                        elif col in [6, 7, 8]:  # M3, Ton, Colli
                            cell.alignment = right_align
                            if col in [6, 7]:
                                cell.number_format = '0.00'
                        else:
                            cell.alignment = left_align
                
                    current_row += 1
                
                except Exception as e:
                    print(f"Error processing barang {i}: {e}")
                    continue
        
            # Total row
            for col in range(1, 12):
                cell = ws.cell(row=current_row, column=col)
                cell.border = thin_border
                # cell.fill = header_fill
                cell.font = table_header_font
            
                if col == 1:
                    cell.value = "TOTAL"
                    cell.alignment = center_align
                elif col == 6:
                    cell.value = total_m3
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 7:
                    cell.value = total_ton
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 8:
                    cell.value = total_colli
                    cell.alignment = right_align
        
            current_row += 2
        
            # Summary
            summary_text = f"Total Items: {len(barang_list)} | Total M3: {total_m3:.2f} | Total Ton: {total_ton:.2f} | Total Colli: {total_colli} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            if filter_criteria:
                summary_text = f"Pengirim: {filter_criteria.get('sender_name', '')} → Penerima: {filter_criteria.get('receiver_name', '')} | " + summary_text
            
            ws[f'A{current_row}'] = summary_text
            ws[f'A{current_row}'].font = small_font
        
            # AUTO-ADJUST Column widths
            estimated_widths = [
                5,   # No
                12,  # Tanggal
                25,  # Nama Barang
                15,  # Jenis Barang
                15,  # Dimensi
                8,   # M3
                8,   # Ton
                6,   # Colli
                8,   # Satuan
                20,  # Keterangan
                15   # Door
            ]
            
            # Apply calculated widths
            for i, width in enumerate(estimated_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
        
            # Set print area
            last_row = current_row
            ws.print_area = f'A1:K{last_row}'
        
            # Save file
            filter_suffix = ""
            if filter_criteria:
                sender = filter_criteria.get('sender_name', 'Unknown')[:10]
                receiver = filter_criteria.get('receiver_name', 'Unknown')[:10]
                filter_suffix = f"_{sender}_to_{receiver}"
            
            filename = f"PackingList_Container_{container_id}{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self._save_excel_file(wb, filename, "PACKING LIST")
        
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat Excel packing list: {str(e)}")
            
    def print_customer_packing_list_pdf(self, container_id, filter_criteria=None):
        """Generate PDF packing list with signature support"""
        print(f"[DEBUG] PrintHandler.print_customer_packing_list_pdf called")
        print(f"[DEBUG] container_id: {container_id}, filter_criteria: {filter_criteria}")
        
        self.pdf_generator.generate_pdf_packing_list_with_signature(container_id, filter_criteria)
    
      
            
    def show_sender_receiver_selection_dialog_pdf(self, container_id):
        """Enhanced dialog for selecting sender-receiver combinations - inline implementation"""
        print(f"[DEBUG] show_sender_receiver_selection_dialog_pdf called")
        
        try:
            # Get all sender-receiver combinations in the container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
            if not container_barang:
                messagebox.showwarning("Peringatan", "Container kosong!")
                return
            
            # Get unique sender-receiver combinations
            combinations = set()
            for barang in container_barang:
                if hasattr(barang, 'keys'):
                    sender = barang['sender_name'] if 'sender_name' in barang.keys() and barang['sender_name'] else '-'
                    receiver = barang['receiver_name'] if 'receiver_name' in barang.keys() and barang['receiver_name'] else '-'
                else:
                    sender = barang.get('sender_name', '-')
                    receiver = barang.get('receiver_name', '-')
                combinations.add((sender, receiver))
            
            combinations = sorted(list(combinations))
            print(f"[DEBUG] Found {len(combinations)} combinations")
            
            if not combinations:
                messagebox.showwarning("Peringatan", "Tidak ada data pengirim-penerima!")
                return
            
            # If only one combination, use it directly
            if len(combinations) == 1:
                sender, receiver = combinations[0]
                filter_criteria = {'sender_name': sender, 'receiver_name': receiver}
                self.print_customer_packing_list_pdf(container_id, filter_criteria)
                return
            
            # Create selection dialog directly in method
            try:
                dialog = tk.Toplevel()
                dialog.title("Pilih Kombinasi PDF")
                dialog.geometry("600x500")
                dialog.resizable(False, False)
                dialog.grab_set()
                dialog.transient()
                
                
                # Center dialog
                dialog.geometry("+%d+%d" % (dialog.winfo_screenwidth()//2 - 300, 
                                            dialog.winfo_screenheight()//2 - 250))
                
                # Variables for dialog
                selected_combinations = []
                dialog_result = {"cancelled": True}
                
                # Main frame
                main_frame = ttk.Frame(dialog)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                # Title
                title_label = ttk.Label(main_frame, 
                                        text=f"Ditemukan {len(combinations)} kombinasi pengirim-penerima:",
                                        font=('Arial', 12, 'bold'))
                title_label.pack(pady=(0, 15))
                
                # Instructions
                instruction_label = ttk.Label(main_frame,
                                            text="Pilih kombinasi yang ingin dibuat PDF-nya:",
                                            font=('Arial', 10))
                instruction_label.pack(pady=(0, 10))
                
                # Scrollable frame for checkboxes
                scroll_frame = ttk.Frame(main_frame)
                scroll_frame.pack(fill='both', expand=True, pady=(0, 15))
                
                canvas = tk.Canvas(scroll_frame, height=250)
                scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Checkboxes for each combination
                checkbox_vars = []
                for i, (sender, receiver) in enumerate(combinations):
                    var = tk.BooleanVar()
                    checkbox_vars.append(var)
                    
                    # Create checkbox with formatted text
                    cb_text = f"{sender} → {receiver}"
                    checkbox = ttk.Checkbutton(scrollable_frame, 
                                                text=cb_text,
                                                variable=var)
                    checkbox.pack(anchor='w', pady=3, padx=15)
                
                # Select/Deselect All buttons
                select_frame = ttk.Frame(main_frame)
                select_frame.pack(fill='x', pady=(0, 15))
                
                def select_all():
                    for var in checkbox_vars:
                        var.set(True)
                
                def deselect_all():
                    for var in checkbox_vars:
                        var.set(False)
                
                ttk.Button(select_frame, text="Pilih Semua", 
                            command=select_all).pack(side='left', padx=(0, 10))
                ttk.Button(select_frame, text="Hapus Semua", 
                            command=deselect_all).pack(side='left')
                
                # Info label
                info_label = ttk.Label(main_frame,
                                        text="Tip: Pilih beberapa kombinasi untuk membuat PDF terpisah untuk masing-masing",
                                        font=('Arial', 8),
                                        foreground='blue')
                info_label.pack(pady=(10, 0))
                
                # Button frame
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill='x', pady=(20, 0))
                
                def on_create_pdf():
                    # Validate selection
                    selected_count = sum(var.get() for var in checkbox_vars)
                    if selected_count == 0:
                        messagebox.showwarning("Peringatan", "Pilih minimal satu kombinasi!")
                        return
                    
                    # Get selected combinations
                    selected_combinations.clear()
                    for i, var in enumerate(checkbox_vars):
                        if var.get():
                            selected_combinations.append(combinations[i])
                    
                    dialog_result["cancelled"] = False
                    dialog.destroy()
                
                def on_cancel():
                    dialog_result["cancelled"] = True
                    dialog.destroy()
                
                ttk.Button(button_frame, text="Buat PDF Terpilih", 
                            command=on_create_pdf).pack(side='left', padx=(0, 10))
                ttk.Button(button_frame, text="Batal", 
                            command=on_cancel).pack(side='right')
                
                # Bind keyboard shortcuts
                dialog.bind("<Return>", lambda e: on_create_pdf())
                dialog.bind("<Escape>", lambda e: on_cancel())
                
                print("[DEBUG] Enhanced dialog created, waiting for user input...")
                
                # Wait for dialog to close
                dialog.wait_window()
                
                # Process selection
                if not dialog_result["cancelled"] and selected_combinations:
                    print(f"[DEBUG] User selected {len(selected_combinations)} combinations")
                    
                    # Create PDF for each selected combination
                    for sender, receiver in selected_combinations:
                        filter_criteria = {'sender_name': sender, 'receiver_name': receiver}
                        print(f"[DEBUG] Creating PDF for: {sender} -> {receiver}")
                        self.print_customer_packing_list_pdf(container_id, filter_criteria)
                    
                    # Show summary
                    messagebox.showinfo("Selesai", 
                                        f"Berhasil membuat {len(selected_combinations)} file PDF!")
                else:
                    print("[DEBUG] User cancelled or no selection made")
                    
            except Exception as dialog_error:
                print(f"[ERROR] Enhanced dialog error: {dialog_error}")
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                
        except Exception as e:
            print(f"[ERROR] Error in combination selection: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Error: {str(e)}")            