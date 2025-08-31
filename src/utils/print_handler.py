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
        """Generate Excel invoice document optimized for A4 printing with profit calculation"""
        try:
            # Create new workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Invoice Container"
        
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
        
            header_fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
            profit_header_fill = PatternFill(start_color='FFE6CC', end_color='FFE6CC', fill_type='solid')
        
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

            print(container_info)

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
                cell.fill = header_fill
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
                cell.fill = header_fill
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
        
            # ===== PROFIT CALCULATION SECTION - ALIGNED WITH MAIN TABLE =====
            
            # Get cost data from database or use default values
            try:
                costs_surabaya = self._get_container_costs(container_id, 'Surabaya')
                costs_destinasi = self._get_container_costs(container_id, container.get('destination', 'Samarinda'))
            except Exception as e:
                print(f"Error getting costs from database: {e}")
                costs_surabaya = None
                costs_destinasi = None

            # If no data in database, use default template
            if not costs_surabaya:
                costs_surabaya = {
                    "THC Surabaya": 5942656,
                    "Frezh": 600000,
                    "Bl. LCL": 5400000,
                    "Seal": 100000,
                    "Bl. Cleaning Container": 100000,
                    "Bl. Ops Stuffing Dalam": 160000,
                    "Bl. Antol Barang": 75000,
                    "Bl. Oper Depo": 225000,
                    "Bl. Admin": 187500,
                    "TPT1 25": 10000,
                    "TPT1 21": 20000,
                    "Pajak": 213313
                }

            if not costs_destinasi:
                costs_destinasi = {
                    "Trucking Samarinda Port-SMA": 1674990,
                    "THC SMD": 4212219,
                    "Dooring Barang Ringan": 270000,
                    "Baseh Ijin & depo Samarinda": 225000,
                    "Bl. Lab Empty": 159000,
                    "Bl. Ops Samarinda": 135000,
                    "Bl. Sewa JPL & Adm": 55000,
                    "Bl. Forklift Samarinda": 350000,
                    "Bl. Lolo": 220000,
                    "Rekolasi Samarinda": 940000
                }
            
            # Calculate totals
            total_biaya_surabaya = sum(val[0] for val in costs_surabaya.values())
            total_biaya_samarinda = sum(val[0] for val in costs_destinasi.values())
            total_biaya = total_biaya_surabaya + total_biaya_samarinda
            profit_lcl = total_nilai - total_biaya
            
            # BIAYA SURABAYA SECTION - ALIGNED WITH MAIN TABLE
            ws.merge_cells(f'A{current_row}:L{current_row}')
            ws[f'A{current_row}'] = "Biaya Surabaya"
            ws[f'A{current_row}'].font = profit_header_font
            ws[f'A{current_row}'].alignment = left_align
            ws[f'A{current_row}'].fill = profit_header_fill
            ws[f'A{current_row}'].border = thin_border
            
            # Value column header - aligned with Price column (column M)
            ws[f'M{current_row}'] = "Cost (Rp)"
            ws[f'M{current_row}'].font = profit_header_font
            ws[f'M{current_row}'].alignment = right_align
            ws[f'M{current_row}'].fill = profit_header_fill
            ws[f'M{current_row}'].border = thin_border
            current_row += 1
            
            # Biaya Surabaya items
            for cost_name, cost_value in costs_surabaya.items():
                ws[f'A{current_row}'] = cost_name
                ws[f'A{current_row}'].font = profit_font
                ws[f'A{current_row}'].alignment = left_align
                
                ws[f'B{current_row}'] = cost_value[1]
                ws[f'B{current_row}'].font = profit_font
                ws[f'B{current_row}'].alignment = left_align

                ws[f'M{current_row}'] = cost_value[0]
                ws[f'M{current_row}'].font = profit_font
                ws[f'M{current_row}'].alignment = right_align
                ws[f'M{current_row}'].number_format = '#,##0'
                current_row += 1
            
            # Total Biaya Surabaya
            ws[f'A{current_row}'] = ""
            ws[f'M{current_row}'] = total_biaya_surabaya
            ws[f'M{current_row}'].font = Font(name='Arial', size=8, bold=True)
            ws[f'M{current_row}'].alignment = right_align
            ws[f'M{current_row}'].number_format = '#,##0'
            ws[f'M{current_row}'].border = thin_border
            current_row += 2
            
            # BIAYA SAMARINDA SECTION - ALIGNED WITH MAIN TABLE
            ws.merge_cells(f'A{current_row}:L{current_row}')
            ws[f'A{current_row}'] = f"Biaya {container_info[2][1]}"
            ws[f'A{current_row}'].font = profit_header_font
            ws[f'A{current_row}'].alignment = left_align
            ws[f'A{current_row}'].fill = profit_header_fill
            ws[f'A{current_row}'].border = thin_border

            # Value column header - aligned with Price column (column M)
            ws[f'M{current_row}'] = "Cost (Rp)"
            ws[f'M{current_row}'].font = profit_header_font
            ws[f'M{current_row}'].alignment = right_align
            ws[f'M{current_row}'].fill = profit_header_fill
            ws[f'M{current_row}'].border = thin_border
            current_row += 1
            
            # Biaya Samarinda items
            for cost_name, cost_value in costs_destinasi.items():
                ws[f'A{current_row}'] = cost_name
                ws[f'A{current_row}'].font = profit_font
                ws[f'A{current_row}'].alignment = left_align
                
                ws[f'B{current_row}'] = cost_value[1]
                ws[f'B{current_row}'].font = profit_font
                ws[f'B{current_row}'].alignment = left_align

                ws[f'M{current_row}'] = cost_value[0]
                ws[f'M{current_row}'].font = profit_font
                ws[f'M{current_row}'].alignment = right_align
                ws[f'M{current_row}'].number_format = '#,##0'
                current_row += 1
            
            # Total Biaya Samarinda
            ws[f'A{current_row}'] = ""
            ws[f'M{current_row}'] = total_biaya_samarinda
            ws[f'M{current_row}'].font = Font(name='Arial', size=8, bold=True)
            ws[f'M{current_row}'].alignment = right_align
            ws[f'M{current_row}'].number_format = '#,##0'
            ws[f'M{current_row}'].border = thin_border
            current_row += 2
            
            # PROFIT CALCULATION - ALIGNED WITH MAIN TABLE
            ws.merge_cells(f'A{current_row}:L{current_row}')
            ws[f'A{current_row}'] = "PROFIT LCL"
            ws[f'A{current_row}'].font = Font(name='Arial', size=10, bold=True)
            ws[f'A{current_row}'].alignment = left_align
            ws[f'A{current_row}'].fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')  # Light green
            ws[f'A{current_row}'].border = thin_border
            
            ws[f'M{current_row}'] = profit_lcl
            ws[f'M{current_row}'].font = Font(name='Arial', size=10, bold=True)
            ws[f'M{current_row}'].alignment = right_align
            ws[f'M{current_row}'].number_format = '#,##0'
            ws[f'M{current_row}'].fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')  # Light green
            ws[f'M{current_row}'].border = thin_border
            current_row += 2
        
            # Summary - COMPACT
            ws[f'A{current_row}'] = f"Total Items: {len(barang_list)} | Total Revenue: Rp {total_nilai:,.0f} | Total Cost: Rp {total_biaya:,.0f} | Profit: Rp {profit_lcl:,.0f} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ws[f'A{current_row}'].font = small_font
        
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
                cell.fill = header_fill
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
                cell.fill = header_fill
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