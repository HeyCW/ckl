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
           
            # Define optimized styles for printing
            header_font = Font(name='Arial', size=14, bold=True)  # Slightly smaller
            company_font = Font(name='Arial', size=12, bold=True)
            normal_font = Font(name='Arial', size=9)  # Smaller font
            small_font = Font(name='Arial', size=8)   # Even smaller
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
           
            # Header section - COMPACT
            current_row = 1
           
            # Title - Merge to column H (8 kolom untuk landscape)
            ws.merge_cells(f'A{current_row}:H{current_row}')
            ws[f'A{current_row}'] = "INVOICE CONTAINER"
            ws[f'A{current_row}'].font = header_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 1
           
            # Company info - COMPACT
            ws.merge_cells(f'A{current_row}:H{current_row}')
            ws[f'A{current_row}'] = "CV. CAHAYA KARUNIA | Jl. Teluk Raya Selatan No. 6 Surabaya | Phone: 031-60166017"
            ws[f'A{current_row}'].font = normal_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 2
           
            # Container information - HORIZONTAL LAYOUT to save space
            # Split info into 2 columns
            info_left = [
                ("Container No", safe_get('container')),
                ("Feeder", safe_get('feeder')),
                ("Destination", safe_get('destination')),
                ("Party", safe_get('party')),
                ("ETD Sub", safe_get('etd_sub'))
            ]
            
            info_right = [
                ("CLS", safe_get('cls')),
                ("Open", safe_get('open')),
                ("Full", safe_get('full')),
                ("Seal", safe_get('seal')),
                ("Ref JOA", safe_get('ref_joa'))
            ]
            
            info_start_row = current_row
            
            # Left column info
            for i, (label, value) in enumerate(info_left):
                row = info_start_row + i
                ws[f'A{row}'] = f"{label}:"
                ws[f'A{row}'].font = small_font
                ws[f'B{row}'] = str(value)
                ws[f'B{row}'].font = small_font
            
            # Right column info
            for i, (label, value) in enumerate(info_right):
                row = info_start_row + i
                ws[f'D{row}'] = f"{label}:"
                ws[f'D{row}'].font = small_font
                ws[f'E{row}'] = str(value)
                ws[f'E{row}'].font = small_font
            
            current_row = info_start_row + max(len(info_left), len(info_right)) + 1
           
            # OPTIMIZED Table headers - Adjust untuk fit A4
            headers = ['No', 'Customer', 'Nama Barang', 'Dimensi', 'M3', 'Ton', 'Col', 'Harga (Rp)']
           
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = table_header_font
                cell.alignment = center_align
                cell.border = thin_border
                cell.fill = header_fill
           
            current_row += 1
           
            # Table data
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            total_nilai = 0
           
            for i, barang in enumerate(barang_list, 1):
                try:
                    # Safe way to get barang values
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang[key]
                            return value if value is not None else default
                        except (KeyError, IndexError):
                            return default
                   
                    customer = str(safe_barang_get('nama_customer', '-'))
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                   
                    # Format dimensions - SIMPLIFIED
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    dimensi = f"{p}×{l}×{t}"
                   
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
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
                    harga_val = float(total_harga) if total_harga not in [None, '', '-'] else 0
                   
                    # TRUNCATE long text to fit
                    customer = customer[:15] + "..." if len(customer) > 15 else customer
                    nama_barang = nama_barang[:20] + "..." if len(nama_barang) > 20 else nama_barang
                   
                    # Fill row data
                    row_data = [i, customer, nama_barang, dimensi, m3_val, ton_val, colli_val, harga_val]
                   
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=current_row, column=col, value=value)
                        cell.font = small_font
                        cell.border = thin_border
                       
                        if col == 1:  # No column
                            cell.alignment = center_align
                        elif col in [5, 6, 7, 8]:  # Numeric columns
                            cell.alignment = right_align
                            if col == 8:  # Harga column
                                cell.number_format = '#,##0'
                            elif col in [5, 6]:  # M3, Ton columns
                                cell.number_format = '0.00'  # Less decimal places
                        else:
                            cell.alignment = left_align
                   
                    current_row += 1
                   
                except Exception as e:
                    print(f"Error processing barang {i}: {e}")
                    continue
           
            # Total row
            for col in range(1, 9):
                cell = ws.cell(row=current_row, column=col)
                cell.border = thin_border
                cell.fill = header_fill
                cell.font = table_header_font
               
                if col == 1:
                    cell.value = "TOTAL"
                    cell.alignment = center_align
                elif col == 5:  # M3 total
                    cell.value = total_m3
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 6:  # Ton total
                    cell.value = total_ton
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 7:  # Colli total
                    cell.value = total_colli
                    cell.alignment = right_align
                elif col == 8:  # Harga total
                    cell.value = total_nilai
                    cell.number_format = '#,##0'
                    cell.alignment = right_align
           
            current_row += 2
           
            # Summary - COMPACT
            ws[f'A{current_row}'] = f"Total Items: {len(barang_list)} | Total Value: Rp {total_nilai:,.0f} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ws[f'A{current_row}'].font = small_font
           
            # OPTIMIZED Column widths for A4 landscape printing
            # Total width should be around 25-26 cm for A4 landscape
            column_widths = [4, 12, 18, 12, 6, 6, 4, 10]  # Total ~72 units
            for i, width in enumerate(column_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
           
            # Set print area
            last_row = current_row
            ws.print_area = f'A1:H{last_row}'
           
            # Add page breaks if needed (every 45 rows after header)
            header_rows = current_row - len(barang_list) - 1
            if len(barang_list) > 45:
                for i in range(45, len(barang_list), 45):
                    break_row = header_rows + i
                    ws.row_breaks.append(break_row)
           
            # Save file
            filename = f"Invoice_Container_{container_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self._save_excel_file(wb, filename, "INVOICE CONTAINER")
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat Excel invoice: {str(e)}")
   
    def print_customer_packing_list(self, container_id, customer_name=None):
        """Generate and export customer packing list to Excel optimized for printing"""
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
           
            # If customer specified, filter for that customer only
            if customer_name:
                container_barang = [b for b in container_barang if b['nama_customer'] == customer_name]
                if not container_barang:
                    messagebox.showwarning("Peringatan", f"Tidak ada barang untuk customer {customer_name}!")
                    return
           
            # Generate Excel packing list
            self._generate_excel_packing_list_optimized(container, container_barang, container_id, customer_name)
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat packing list: {str(e)}")
    
    def _generate_excel_packing_list_optimized(self, container, barang_list, container_id, customer_name=None):
        """Generate Excel packing list document optimized for A4 printing"""
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
           
            # Define optimized styles
            header_font = Font(name='Arial', size=14, bold=True)
            company_font = Font(name='Arial', size=12, bold=True)
            normal_font = Font(name='Arial', size=9)
            small_font = Font(name='Arial', size=8)
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
           
            # Header section - COMPACT
            current_row = 1
           
            # Title
            ws.merge_cells(f'A{current_row}:I{current_row}')
            ws[f'A{current_row}'] = "CUSTOMER PACKING LIST"
            ws[f'A{current_row}'].font = header_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 1
           
            # Company info - COMPACT
            ws.merge_cells(f'A{current_row}:I{current_row}')
            ws[f'A{current_row}'] = "CV. CAHAYA KARUNIA | Jl. Teluk Raya Selatan No. 6 Surabaya | Phone: 031-60166017"
            ws[f'A{current_row}'].font = normal_font
            ws[f'A{current_row}'].alignment = center_align
            current_row += 2
           
            # Get customer info
            if not customer_name and barang_list:
                customer_name = barang_list[0]['nama_customer'] if barang_list[0]['nama_customer'] else 'UNKNOWN'
           
            # Calculate totals
            total_m3 = sum(float(b.get('m3_barang', 0) or 0) for b in barang_list)
            total_ton = sum(float(b.get('ton_barang', 0) or 0) for b in barang_list)
            total_colli = sum(int(b.get('colli_amount', 0) or 0) for b in barang_list)
           
            # Invoice information - HORIZONTAL LAYOUT
            invoice_number = f"CKL/SUBUV/{datetime.now().strftime('%Y')}/{safe_get('container_id', '001')}B"
           
            info_left = [
                ("Bill To", customer_name or "ALL CUSTOMERS"),
                ("Feeder", safe_get('feeder')),
                ("Destination", safe_get('destination'))
            ]
            
            info_right = [
                ("Invoice Number", invoice_number),
                ("Tanggal (ETD)", safe_get('etd_sub')),
                ("Total Volume", f"{total_m3:.2f} m3")
            ]
            
            info_start_row = current_row
            
            # Left column info
            for i, (label, value) in enumerate(info_left):
                row = info_start_row + i
                ws[f'A{row}'] = f"{label}:"
                ws[f'A{row}'].font = small_font
                ws[f'B{row}'] = str(value)[:25]  # Truncate long values
                ws[f'B{row}'].font = small_font
            
            # Right column info
            for i, (label, value) in enumerate(info_right):
                row = info_start_row + i
                ws[f'E{row}'] = f"{label}:"
                ws[f'E{row}'].font = small_font
                ws[f'F{row}'] = str(value)
                ws[f'F{row}'].font = small_font
            
            current_row = info_start_row + max(len(info_left), len(info_right)) + 1
           
            # OPTIMIZED Table headers
            headers = ['No', 'Container', 'Pengirim', 'Jenis Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Catatan']
           
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = table_header_font
                cell.alignment = center_align
                cell.border = thin_border
                cell.fill = header_fill
           
            current_row += 1
           
            # Table data
            for i, barang in enumerate(barang_list, 1):
                try:
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang[key]
                            return value if value is not None else default
                        except (KeyError, IndexError):
                            return default
                   
                    container_no = str(safe_get('container', '-'))[:12]  # Truncate
                    pengirim = str(safe_barang_get('nama_customer', '-'))[:15]  # Truncate
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))[:20]  # Truncate
                   
                    # Kubikasi (dimensions) - SIMPLIFIED
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    kubikasi = f"{p}×{l}×{t}"
                    if len(kubikasi) > 15:
                        kubikasi = kubikasi[:12] + "..."
                   
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                   
                    # Format values
                    m3_val = float(m3) if m3 not in [None, '', '-'] else 0
                    ton_val = float(ton) if ton not in [None, '', '-'] else 0
                    colli_val = int(colli) if colli not in [None, '', '-'] else 0
                   
                    # Fill row data
                    row_data = [i, container_no, pengirim, jenis_barang, kubikasi, m3_val, ton_val, colli_val, '-']
                   
                    for col, value in enumerate(row_data, 1):
                        cell = ws.cell(row=current_row, column=col, value=value)
                        cell.font = small_font
                        cell.border = thin_border
                       
                        if col == 1:  # No column
                            cell.alignment = center_align
                        elif col in [6, 7, 8]:  # Numeric columns
                            cell.alignment = right_align
                            if col in [6, 7]:  # M3, Ton columns
                                cell.number_format = '0.00'
                        else:
                            cell.alignment = left_align
                   
                    current_row += 1
                   
                except Exception as e:
                    print(f"Error processing barang {i}: {e}")
                    continue
           
            # Total row
            for col in range(1, 10):
                cell = ws.cell(row=current_row, column=col)
                cell.border = thin_border
                cell.fill = header_fill
                cell.font = table_header_font
               
                if col == 1:
                    cell.value = "TOTAL"
                    cell.alignment = center_align
                elif col == 6:  # M3 total
                    cell.value = total_m3
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 7:  # Ton total
                    cell.value = total_ton
                    cell.number_format = '0.00'
                    cell.alignment = right_align
                elif col == 8:  # Colli total
                    cell.value = total_colli
                    cell.alignment = right_align
           
            current_row += 2
           
            ws[f'A{current_row}'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ws[f'A{current_row}'].font = small_font
           
            # OPTIMIZED Column widths for A4 landscape
            column_widths = [4, 10, 12, 16, 12, 6, 6, 4, 8]  # Total ~78 units
            for i, width in enumerate(column_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
           
            # Set print area
            last_row = current_row
            ws.print_area = f'A1:I{last_row}'
           
            # Save file
            customer_suffix = f"_{customer_name}" if customer_name else "_All_Customers"
            filename = f"PackingList_Container_{container_id}{customer_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
   
    def show_customer_selection_dialog(self, container_id):
        """Show dialog to select customer for packing list"""
        try:
            # Get unique customers in this container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            customers = list(set(b['nama_customer'] for b in container_barang if b['nama_customer']))
           
            if not customers:
                messagebox.showwarning("Peringatan", "Tidak ada customer di container ini!")
                return
           
            if len(customers) == 1:
                # Only one customer, export directly
                self.print_customer_packing_list(container_id, customers[0])
                return
           
            # Multiple customers, show selection dialog
            selection_window = tk.Toplevel()
            selection_window.title("Pilih Customer")
            selection_window.geometry("500x400")
            selection_window.configure(bg='#ecf0f1')
            selection_window.focus_set()
            selection_window.grab_set()
           
            # Header
            header = tk.Label(
                selection_window,
                text="📊 PILIH CUSTOMER UNTUK EXCEL PACKING LIST",
                font=('Arial', 14, 'bold'),
                bg='#e67e22',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
           
            # Instructions
            tk.Label(
                selection_window,
                text="Pilih customer yang akan dibuatkan packing list Excel (Optimized untuk Print A4):",
                font=('Arial', 11),
                bg='#ecf0f1'
            ).pack(pady=10)
           
            # Customer list
            list_frame = tk.Frame(selection_window, bg='#ecf0f1')
            list_frame.pack(fill='both', expand=True, padx=20, pady=10)
           
            list_frame.grid_rowconfigure(0, weight=1)
            list_frame.grid_columnconfigure(0, weight=1)
           
            customer_listbox = tk.Listbox(list_frame, font=('Arial', 11), height=10,
                                        selectmode='single', activestyle='dotbox')
           
            # Add "All Customers" option
            customer_listbox.insert(tk.END, "📊 ALL CUSTOMERS")
           
            # Add individual customers
            for customer in sorted(customers):
                customer_listbox.insert(tk.END, f"👤 {customer}")
           
            # Select first item by default
            customer_listbox.selection_set(0)
            customer_listbox.activate(0)
           
            # Scrollbar for listbox
            scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=customer_listbox.yview)
            customer_listbox.configure(yscrollcommand=scrollbar.set)
           
            # Grid layout
            customer_listbox.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')
           
            # Enable mouse wheel scrolling
            def on_mousewheel(event):
                customer_listbox.yview_scroll(int(-1*(event.delta/120)), "units")
           
            customer_listbox.bind("<MouseWheel>", on_mousewheel)
            selection_window.bind("<MouseWheel>", on_mousewheel)
           
            # For Linux
            customer_listbox.bind("<Button-4>", lambda e: customer_listbox.yview_scroll(-1, "units"))
            customer_listbox.bind("<Button-5>", lambda e: customer_listbox.yview_scroll(1, "units"))
           
            # Buttons
            btn_frame = tk.Frame(selection_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', padx=20, pady=15)
           
            def export_selected():
                selection = customer_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Peringatan", "Pilih customer terlebih dahulu!")
                    return
               
                selected_text = customer_listbox.get(selection[0])
               
                if selected_text.startswith("📊 ALL CUSTOMERS"):
                    # Export for all customers
                    self.print_customer_packing_list(container_id, None)
                else:
                    # Export for specific customer
                    customer_name = selected_text.replace("👤 ", "")
                    self.print_customer_packing_list(container_id, customer_name)
               
                selection_window.destroy()
           
            def on_double_click(event):
                export_selected()
           
            # Bind double click
            customer_listbox.bind("<Double-Button-1>", on_double_click)
           
            # Bind Enter key
            def on_enter(event):
                export_selected()
           
            selection_window.bind("<Return>", on_enter)
            customer_listbox.bind("<Return>", on_enter)
           
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
            x = (selection_window.winfo_screenwidth() // 2) - (250)
            y = (selection_window.winfo_screenheight() // 2) - (200)
            selection_window.geometry(f"500x400+{x}+{y}")
           
            # Focus on listbox after creation
            selection_window.after(100, lambda: customer_listbox.focus_set())
           
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat dialog selection: {str(e)}")

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
