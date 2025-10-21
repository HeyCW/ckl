import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from tkinter import filedialog

class JobOrderWindow:
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("Job Order Management")
        self.window.geometry("1400x800")
        
        # Selected JOA
        self.selected_joa = None
        self.current_data = []
        
        self.setup_ui()
        self.load_joa_list()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # ===== LEFT PANEL - JOA LIST =====
        left_frame = ttk.LabelFrame(main_frame, text="Daftar Job Order Account (JOA)", padding="10")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Cari JOA:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_joa_list())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # JOA Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.joa_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                       font=('Arial', 10), height=30)
        self.joa_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.joa_listbox.yview)
        
        self.joa_listbox.bind('<<ListboxSelect>>', self.on_joa_select)
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_joa_list).pack(fill=tk.X, pady=2)
        
        # ===== RIGHT PANEL - DETAILS =====
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Info frame
        info_frame = ttk.LabelFrame(right_frame, text="Informasi Job Order", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # JOA Info
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        ttk.Label(info_grid, text="No. JOA:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.joa_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.joa_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="Container:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.container_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.container_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="Feeder:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.feeder_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.feeder_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="Destination:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5)
        self.destination_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.destination_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Table frame
        table_frame = ttk.LabelFrame(right_frame, text="Detail Barang dalam JOA", padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ('keterangan', 'unit', 'biaya_per', 'total', 'keterangan2')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=tree_scroll.set,
                                 xscrollcommand=tree_scroll_x.set)
        
        # Column headings
        self.tree.heading('keterangan', text='KETERANGAN')
        self.tree.heading('unit', text='UNIT')
        self.tree.heading('biaya_per', text='BIAYA PER')
        self.tree.heading('total', text='TOTAL')
        self.tree.heading('keterangan2', text='KETERANGAN')
        
        # Column widths
        self.tree.column('keterangan', width=250)
        self.tree.column('unit', width=120)
        self.tree.column('biaya_per', width=150)
        self.tree.column('total', width=150)
        self.tree.column('keterangan2', width=200)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Summary frame
        summary_frame = ttk.Frame(right_frame)
        summary_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(summary_frame, text="TOTAL:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        self.total_label = ttk.Label(summary_frame, text="Rp 0", font=('Arial', 12, 'bold'), foreground='blue')
        self.total_label.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(action_frame, text="📄 Export ke Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🖨️ Print Preview", 
                  command=self.print_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔄 Refresh Data", 
                  command=self.refresh_current_joa).pack(side=tk.LEFT, padx=5)
    
    def load_joa_list(self):
        """Load all JOA numbers from database"""
        try:
            self.joa_listbox.delete(0, tk.END)
            
            # Query untuk mendapatkan semua JOA yang unik
            # Simplified query - just get from containers first
            query = """
                SELECT DISTINCT c.ref_joa, c.container_id, c.container, c.kapal_feeder
                FROM containers c
                WHERE c.ref_joa IS NOT NULL AND c.ref_joa != ''
                ORDER BY c.ref_joa
            """
            
            results = self.db.execute(query)
            self.joa_data = {}
            
            for row in results:
                # Safely access sqlite3.Row data using bracket notation
                try:
                    joa = row['ref_joa']
                    container_id = row['container_id']
                    container = row['container'] if row['container'] else '-'
                    kapal_feeder = row['kapal_feeder'] if row['kapal_feeder'] else None
                    
                    # Get kapal info separately if kapal_feeder exists
                    feeder = '-'
                    destination = '-'
                    etd_sub = '-'
                    
                    if kapal_feeder:
                        try:
                            kapal_query = """
                                SELECT feeder, destination, etd_sub 
                                FROM kapals 
                                WHERE kapal_id = ?
                            """
                            kapal_result = self.db.execute_one(kapal_query, (kapal_feeder,))
                            if kapal_result:
                                feeder = kapal_result['feeder'] if kapal_result['feeder'] else '-'
                                destination = kapal_result['destination'] if kapal_result['destination'] else '-'
                                etd_sub = kapal_result['etd_sub'] if kapal_result['etd_sub'] else '-'
                        except Exception as e:
                            print(f"Warning: Could not get kapal info: {e}")
                    
                    if joa not in self.joa_data:
                        self.joa_data[joa] = {
                            'container_id': container_id,
                            'container': container,
                            'feeder': feeder,
                            'destination': destination,
                            'etd_sub': etd_sub
                        }
                        self.joa_listbox.insert(tk.END, f"JOA: {joa} - {container}")
                        
                except (KeyError, TypeError) as e:
                    print(f"Error processing row: {e}")
                    continue
            
            if self.joa_listbox.size() > 0:
                self.joa_listbox.selection_set(0)
                self.on_joa_select(None)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal memuat daftar JOA:\n{str(e)}")
    
    def filter_joa_list(self):
        """Filter JOA list based on search"""
        search_text = self.search_var.get().lower()
        self.joa_listbox.delete(0, tk.END)
        
        for joa, data in self.joa_data.items():
            display_text = f"JOA: {joa} - {data['container']}"
            if search_text in display_text.lower():
                self.joa_listbox.insert(tk.END, display_text)
    
    def on_joa_select(self, event):
        """Handle JOA selection"""
        selection = self.joa_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.joa_listbox.get(selection[0])
        joa_number = selected_text.split(" - ")[0].replace("JOA: ", "")
        
        self.selected_joa = joa_number
        self.load_joa_details(joa_number)
    
    def load_joa_details(self, joa_number):
        """Load details for selected JOA"""
        try:
            # Update info labels
            joa_info = self.joa_data.get(joa_number, {})
            self.joa_label.config(text=joa_number)
            self.container_label.config(text=joa_info.get('container', '-'))
            self.feeder_label.config(text=joa_info.get('feeder', '-'))
            self.destination_label.config(text=joa_info.get('destination', '-'))
            
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get container_id
            container_id = joa_info.get('container_id')
            
            if not container_id:
                self.total_label.config(text="Rp 0")
                return
            
            # Load barang data
            barang_data = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
            total_biaya = 0
            self.current_data = []
            
            for row in barang_data:
                # Safely access row data - sqlite3.Row supports dict-like access with []
                try:
                    receiver_name = row['receiver_name'] if row['receiver_name'] else '-'
                except (KeyError, TypeError):
                    receiver_name = '-'
                
                try:
                    satuan = row['satuan'] if row['satuan'] else '-'
                except (KeyError, TypeError):
                    satuan = '-'
                
                try:
                    door_type = row['door_type'] if row['door_type'] else '-'
                except (KeyError, TypeError):
                    door_type = '-'
                
                # Format keterangan berdasarkan tipe door
                if door_type == 'PP':
                    keterangan_full = f"{receiver_name} - PORT TO PORT"
                elif door_type == 'PD':
                    keterangan_full = f"{receiver_name} - PORT TO DOOR"
                elif door_type == 'DD':
                    keterangan_full = f"{receiver_name} - DOOR TO DOOR"
                else:
                    keterangan_full = receiver_name
                
                # Determine unit based on satuan
                try:
                    if satuan == 'M3':
                        unit_value = row['m3_barang'] if row['m3_barang'] else 0
                    elif satuan == 'TON':
                        unit_value = row['ton_barang'] if row['ton_barang'] else 0
                    else:
                        unit_value = row['colli_amount'] if row['colli_amount'] else 0
                except (KeyError, TypeError):
                    unit_value = 0
                
                unit_text = f"{unit_value} {satuan}"
                
                try:
                    harga_per_unit = row['harga_per_unit'] if row['harga_per_unit'] else 0
                    total_harga = row['total_harga'] if row['total_harga'] else 0
                except (KeyError, TypeError):
                    harga_per_unit = 0
                    total_harga = 0
                
                # Format currency
                biaya_per_text = f"Rp {harga_per_unit:,.0f}"
                total_text = f"Rp {total_harga:,.0f}"
                
                # Keterangan tambahan (nama barang atau catatan)
                try:
                    keterangan2 = row['nama_barang'] if row['nama_barang'] else '-'
                except (KeyError, TypeError):
                    keterangan2 = '-'
                
                self.tree.insert('', tk.END, values=(
                    keterangan_full,
                    unit_text,
                    biaya_per_text,
                    total_text,
                    keterangan2
                ))
                
                total_biaya += total_harga
                
                # Store for export
                self.current_data.append({
                    'keterangan': keterangan_full,
                    'unit': unit_text,
                    'biaya_per': harga_per_unit,
                    'total': total_harga,
                    'keterangan2': keterangan2
                })
            
            # Update total
            self.total_label.config(text=f"Rp {total_biaya:,.0f}")
            
            # Get delivery costs if any
            try:
                delivery_costs = self.db.get_container_delivery_total(container_id)
                if delivery_costs and len(delivery_costs) > 0:
                    delivery_row = delivery_costs[0]
                    try:
                        delivery_total = delivery_row['total_delivery_cost'] if delivery_row['total_delivery_cost'] else 0
                    except (KeyError, TypeError):
                        delivery_total = 0
                    
                    if delivery_total > 0:
                        # Add delivery cost row
                        self.tree.insert('', tk.END, values=(
                            'BIAYA PENGANTARAN',
                            '-',
                            '-',
                            f"Rp {delivery_total:,.0f}",
                            '-'
                        ))
                        total_biaya += delivery_total
                        self.total_label.config(text=f"Rp {total_biaya:,.0f}")
            except Exception as e:
                print(f"Warning: Could not load delivery costs: {e}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat detail JOA:\n{str(e)}")
    
    def refresh_current_joa(self):
        """Refresh current JOA data"""
        if self.selected_joa:
            self.load_joa_details(self.selected_joa)
    
    def export_to_excel(self):
        """Export current JOA to Excel"""
        if not self.selected_joa:
            messagebox.showwarning("Warning", "Pilih JOA terlebih dahulu!")
            return
        
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"JOA_{self.selected_joa}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            
            if not filename:
                return
            
            # Create workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Job Order"
            
            # Styling
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Title
            ws.merge_cells('A1:E1')
            title_cell = ws['A1']
            title_cell.value = f"JOB ORDER ACCOUNT - {self.selected_joa}"
            title_cell.font = Font(bold=True, size=14)
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Info
            joa_info = self.joa_data.get(self.selected_joa, {})
            ws['A2'] = "Container:"
            ws['B2'] = joa_info.get('container', '-')
            ws['A3'] = "Feeder:"
            ws['B3'] = joa_info.get('feeder', '-')
            ws['A4'] = "Destination:"
            ws['B4'] = joa_info.get('destination', '-')
            ws['A5'] = "ETD:"
            ws['B5'] = joa_info.get('etd_sub', '-')
            
            # Headers
            headers = ['KETERANGAN', 'UNIT', 'BIAYA PER', 'TOTAL', 'KETERANGAN']
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=7, column=col)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Data
            row_num = 8
            total = 0
            for data in self.current_data:
                ws.cell(row=row_num, column=1, value=data['keterangan']).border = border
                ws.cell(row=row_num, column=2, value=data['unit']).border = border
                ws.cell(row=row_num, column=3, value=data['biaya_per']).border = border
                ws.cell(row=row_num, column=3).number_format = '#,##0'
                ws.cell(row=row_num, column=4, value=data['total']).border = border
                ws.cell(row=row_num, column=4).number_format = '#,##0'
                ws.cell(row=row_num, column=5, value=data['keterangan2']).border = border
                total += data['total']
                row_num += 1
            
            # Total row
            ws.cell(row=row_num, column=1, value="TOTAL").font = Font(bold=True)
            ws.cell(row=row_num, column=4, value=total).font = Font(bold=True)
            ws.cell(row=row_num, column=4).number_format = '#,##0'
            
            # Column widths
            ws.column_dimensions['A'].width = 40
            ws.column_dimensions['B'].width = 15
            ws.column_dimensions['C'].width = 18
            ws.column_dimensions['D'].width = 18
            ws.column_dimensions['E'].width = 30
            
            # Save
            wb.save(filename)
            messagebox.showinfo("Success", f"Data berhasil diekspor ke:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor ke Excel:\n{str(e)}")
    
    def print_preview(self):
        """Show print preview window"""
        if not self.selected_joa:
            messagebox.showwarning("Warning", "Pilih JOA terlebih dahulu!")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.window)
        preview_window.title(f"Print Preview - JOA {self.selected_joa}")
        preview_window.geometry("800x600")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                             font=('Courier', 10), wrap=tk.WORD)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Generate preview content
        joa_info = self.joa_data.get(self.selected_joa, {})
        
        content = f"""
{'='*80}
                    JOB ORDER ACCOUNT
                    PURCHASE INVOICE
{'='*80}

No. JOA        : {self.selected_joa}
Container      : {joa_info.get('container', '-')}
Feeder         : {joa_info.get('feeder', '-')}
Destination    : {joa_info.get('destination', '-')}
ETD            : {joa_info.get('etd_sub', '-')}
Tanggal Print  : {datetime.now().strftime('%d-%m-%Y %H:%M')}

{'-'*80}
{'KETERANGAN':<35} {'UNIT':<12} {'BIAYA PER':>15} {'TOTAL':>15}
{'-'*80}
"""
        
        total = 0
        for data in self.current_data:
            content += f"{data['keterangan']:<35} {data['unit']:<12} "
            content += f"Rp {data['biaya_per']:>12,.0f} Rp {data['total']:>12,.0f}\n"
            total += data['total']
        
        content += f"""{'-'*80}
{'TOTAL':>62} Rp {total:>12,.0f}
{'='*80}

Keterangan:
- Port to Port (PP): Dari pelabuhan ke pelabuhan
- Port to Door (PD): Dari pelabuhan ke alamat tujuan
- Door to Door (DD): Dari alamat pengirim ke alamat tujuan
"""
        
        text_widget.insert('1.0', content)
        text_widget.config(state=tk.DISABLED)
        
        # Print button
        btn_frame = ttk.Frame(preview_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="🖨️ Print", 
                  command=lambda: messagebox.showinfo("Info", "Fungsi print akan dihubungkan ke printer")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Close", 
                  command=preview_window.destroy).pack(side=tk.RIGHT, padx=5)