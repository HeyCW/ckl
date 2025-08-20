import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

class PrintHandler:
    def __init__(self, db):
        self.db = db
    
    def print_container_invoice(self, container_id):
        """Generate and print container invoice based on first image"""
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
            
            # Generate invoice content
            invoice_content = self._generate_invoice_content(container, container_barang)
            
            # Save to file or send to printer
            self._save_or_print_document(invoice_content, f"Invoice_Container_{container_id}", "INVOICE CONTAINER")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat invoice: {str(e)}")
    
    def print_customer_packing_list(self, container_id, customer_name=None):
        """Generate and print customer packing list based on second image"""
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
                container_barang = [b for b in container_barang if b.get('nama_customer') == customer_name]
                if not container_barang:
                    messagebox.showwarning("Peringatan", f"Tidak ada barang untuk customer {customer_name}!")
                    return
            
            # Generate packing list content
            packing_content = self._generate_packing_list_content(container, container_barang, customer_name)
            
            # Save to file or send to printer
            customer_suffix = f"_{customer_name}" if customer_name else "_All_Customers"
            self._save_or_print_document(packing_content, f"PackingList_Container_{container_id}{customer_suffix}", "CUSTOMER PACKING LIST")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat packing list: {str(e)}")
    
    def _generate_invoice_content(self, container, barang_list):
        """Generate invoice content based on first image format"""
        
        # Safe way to get container values
        def safe_get(key, default='-'):
            try:
                if hasattr(container, 'get'):
                    return container.get(key, default) or default
                else:
                    return container[key] if key in container and container[key] else default
            except:
                return default
        
        # Header information
        content = []
        content.append("=" * 80)
        content.append("                           INVOICE CONTAINER")
        content.append("                          CV. CAHAYA KARUNIA")
        content.append("                    Jl. Teluk Raya Selatan No. 6 Surabaya")
        content.append("                         Phone: 031-60166017")
        content.append("=" * 80)
        content.append("")
        
        # Container information
        content.append(f"Container No    : {safe_get('container')}")
        content.append(f"Feeder         : {safe_get('feeder')}")
        content.append(f"Destination    : {safe_get('destination')}")
        content.append(f"Party          : {safe_get('party')}")
        content.append(f"ETD Sub        : {safe_get('etd_sub')}")
        content.append(f"CLS            : {safe_get('cls')}")
        content.append(f"Open           : {safe_get('open')}")
        content.append(f"Full           : {safe_get('full')}")
        content.append(f"Seal           : {safe_get('seal')}")
        content.append(f"Ref JOA        : {safe_get('ref_joa')}")
        content.append("")
        content.append("-" * 80)
        
        # Table header
        content.append(f"{'No':<3} {'Customer':<15} {'Nama Barang':<20} {'Jenis':<10} {'Dimensi':<12} {'M3':<8} {'Ton':<8} {'Col':<5} {'Harga':<12}")
        content.append("-" * 80)
        
        # Table content
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
                
                customer = str(safe_barang_get('nama_customer', '-'))[:14]
                nama_barang = str(safe_barang_get('nama_barang', '-'))[:19]
                jenis = str(safe_barang_get('jenis_barang', '-'))[:9]
                
                # Format dimensions
                p = safe_barang_get('panjang_barang', '-')
                l = safe_barang_get('lebar_barang', '-')
                t = safe_barang_get('tinggi_barang', '-')
                dimensi = f"{p}x{l}x{t}"[:11]
                
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
                m3_str = f"{float(m3):.3f}" if m3 not in [None, '', '-'] else '-'
                ton_str = f"{float(ton):.3f}" if ton not in [None, '', '-'] else '-'
                colli_str = str(colli) if colli not in [None, '', '-'] else '-'
                harga_str = f"{float(total_harga):,.0f}" if total_harga not in [None, '', '-'] else '-'
                
                content.append(f"{i:<3} {customer:<15} {nama_barang:<20} {jenis:<10} {dimensi:<12} {m3_str:<8} {ton_str:<8} {colli_str:<5} {harga_str:<12}")
                
            except Exception as e:
                print(f"Error processing barang {i}: {e}")
                continue
        
        content.append("-" * 80)
        # Fixed format string - separate the formatting
        total_m3_str = f"{total_m3:.3f}"
        total_ton_str = f"{total_ton:.3f}"
        total_colli_str = str(total_colli)
        total_nilai_str = f"{total_nilai:,.0f}"
        
        content.append(f"{'TOTAL':<60} {total_m3_str:<8} {total_ton_str:<8} {total_colli_str:<5} {total_nilai_str}")
        content.append("=" * 80)
        content.append("")
        content.append(f"Total Items: {len(barang_list)}")
        content.append(f"Total Value: Rp {total_nilai:,.0f}")
        content.append("")
        content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(content)
    
    def _generate_packing_list_content(self, container, barang_list, customer_name=None):
        """Generate packing list content based on second image format"""
        
        # Safe way to get container values
        def safe_get(key, default='-'):
            try:
                if hasattr(container, 'get'):
                    return container.get(key, default) or default
                else:
                    return container[key] if key in container and container[key] else default
            except:
                return default
        
        # Header information
        content = []
        content.append("=" * 80)
        content.append("                        CUSTOMER PACKING LIST")
        content.append("                          CV. CAHAYA KARUNIA")
        content.append("                    Jl. Teluk Raya Selatan No. 6 Surabaya")
        content.append("                         Phone: 031-60166017")
        content.append("=" * 80)
        content.append("")
        
        # Get customer info (use first customer if not specified)
        if not customer_name and barang_list:
            customer_name = barang_list[0].get('nama_customer', 'UNKNOWN')
        
        # Calculate totals for this customer
        total_m3 = 0
        total_ton = 0
        total_colli = 0
        
        for barang in barang_list:
            try:
                m3 = barang.get('m3_barang', 0)
                ton = barang.get('ton_barang', 0)
                colli = barang.get('colli_amount', 0)
                
                total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                total_ton += float(ton) if ton not in [None, '', '-'] else 0
                total_colli += int(colli) if colli not in [None, '', '-'] else 0
            except (ValueError, TypeError):
                continue
        
        # Invoice information
        invoice_number = f"CKL/SUBUV/{datetime.now().strftime('%Y')}/{safe_get('container_id', '001')}B"
        
        content.append(f"Bill To (Nama Customer)    : {customer_name}")
        content.append("")
        content.append(f"Feeder (Nama Kapal)        : {safe_get('feeder')}")
        content.append(f"Destination (Tujuan)       : {safe_get('destination')}")
        content.append(f"Party (Volume)             : {total_m3:.3f} m3")
        content.append("")
        content.append(f"Invoice Number             : {invoice_number}")
        content.append(f"Tanggal (ETD)              : {safe_get('etd_sub')}")
        content.append("")
        content.append("=" * 80)
        
        # Table header
        content.append(f"{'No':<3} {'No Container':<12} {'Pengirim':<15} {'Jenis Barang':<20} {'Kubikasi':<10} {'M3':<8} {'Ton':<8} {'Col':<5} {'Catatan':<10}")
        content.append("-" * 80)
        
        # Table content
        for i, barang in enumerate(barang_list, 1):
            try:
                # Safe way to get barang values
                def safe_barang_get(key, default='-'):
                    try:
                        value = barang[key]
                        return value if value is not None else default
                    except (KeyError, IndexError):
                        return default
                
                container_no = str(safe_get('container', '-'))[:11]
                pengirim = str(safe_barang_get('nama_customer', '-'))[:14]
                jenis_barang = str(safe_barang_get('jenis_barang', '-'))[:19]
                
                # Kubikasi (dimensions)
                p = safe_barang_get('panjang_barang', '-')
                l = safe_barang_get('lebar_barang', '-')
                t = safe_barang_get('tinggi_barang', '-')
                kubikasi = f"{p}x{l}x{t}"[:9]
                
                m3 = safe_barang_get('m3_barang', 0)
                ton = safe_barang_get('ton_barang', 0)
                colli = safe_barang_get('colli_amount', 0)
                
                # Format values for display
                m3_str = f"{float(m3):.3f}" if m3 not in [None, '', '-'] else '-'
                ton_str = f"{float(ton):.3f}" if ton not in [None, '', '-'] else '-'
                colli_str = str(colli) if colli not in [None, '', '-'] else '-'
                
                content.append(f"{i:<3} {container_no:<12} {pengirim:<15} {jenis_barang:<20} {kubikasi:<10} {m3_str:<8} {ton_str:<8} {colli_str:<5} {'-':<10}")
                
            except Exception as e:
                print(f"Error processing barang {i}: {e}")
                continue
        
        content.append("-" * 80)
        # Fixed format string for packing list total
        total_m3_str = f"{total_m3:.3f}"
        total_ton_str = f"{total_ton:.3f}"
        total_colli_str = str(total_colli)
        
        content.append(f"{'TOTAL':<60} {total_m3_str:<8} {total_ton_str:<8} {total_colli_str}")
        content.append("=" * 80)
        content.append("")
        content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(content)
    
    def _save_or_print_document(self, content, filename, doc_type):
        """Save document to file or prepare for printing"""
        try:
            # Create print dialog window
            print_window = tk.Toplevel()
            print_window.title(f"Print {doc_type}")
            print_window.geometry("800x600")
            print_window.configure(bg='#ecf0f1')
            
            # Header
            header = tk.Label(
                print_window,
                text=f"📄 PREVIEW {doc_type}",
                font=('Arial', 16, 'bold'),
                bg='#3498db',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
            
            # Text preview
            preview_frame = tk.Frame(print_window, bg='#ffffff', relief='solid', bd=1)
            preview_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            text_widget = tk.Text(preview_frame, font=('Courier', 9), wrap='none')
            
            # Scrollbars
            v_scrollbar = tk.Scrollbar(preview_frame, orient='vertical', command=text_widget.yview)
            h_scrollbar = tk.Scrollbar(preview_frame, orient='horizontal', command=text_widget.xview)
            text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            preview_frame.grid_rowconfigure(0, weight=1)
            preview_frame.grid_columnconfigure(0, weight=1)
            
            # Insert content
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')
            
            # Button frame
            btn_frame = tk.Frame(print_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', padx=20, pady=10)
            
            def save_to_file():
                try:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                        initialname=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    )
                    
                    if file_path:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        messagebox.showinfo("Sukses", f"File berhasil disimpan ke:\n{file_path}")
                        print_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menyimpan file: {str(e)}")
            
            def print_document():
                try:
                    # Save to temporary file for printing
                    temp_filename = f"temp_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    temp_path = os.path.join(os.path.expanduser("~"), "Desktop", temp_filename)
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Try to print using default system printer
                    if os.name == 'nt':  # Windows
                        os.startfile(temp_path, "print")
                    else:  # Linux/Mac
                        os.system(f"lpr {temp_path}")
                    
                    messagebox.showinfo("Info", f"Dokumen dikirim ke printer.\nFile sementara: {temp_path}")
                    print_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal mencetak: {str(e)}\nSilakan simpan file dan cetak manual.")
            
            # Buttons
            tk.Button(
                btn_frame,
                text="🖨️ Print",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=20,
                pady=8,
                command=print_document
            ).pack(side='left', padx=(0, 10))
            
            tk.Button(
                btn_frame,
                text="💾 Save to File",
                font=('Arial', 12, 'bold'),
                bg='#3498db',
                fg='white',
                padx=20,
                pady=8,
                command=save_to_file
            ).pack(side='left', padx=(0, 10))
            
            tk.Button(
                btn_frame,
                text="❌ Close",
                font=('Arial', 12, 'bold'),
                bg='#e74c3c',
                fg='white',
                padx=20,
                pady=8,
                command=print_window.destroy
            ).pack(side='right')
            
            # Center window
            print_window.update_idletasks()
            x = (print_window.winfo_screenwidth() // 2) - (400)
            y = (print_window.winfo_screenheight() // 2) - (300)
            print_window.geometry(f"800x600+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat preview: {str(e)}")
    
    def show_customer_selection_dialog(self, container_id):
        """Show dialog to select customer for packing list"""
        try:
            # Get unique customers in this container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            customers = list(set(b.get('nama_customer', 'Unknown') for b in container_barang if b.get('nama_customer')))
            
            if not customers:
                messagebox.showwarning("Peringatan", "Tidak ada customer di container ini!")
                return
            
            if len(customers) == 1:
                # Only one customer, print directly
                self.print_customer_packing_list(container_id, customers[0])
                return
            
            # Multiple customers, show selection dialog
            selection_window = tk.Toplevel()
            selection_window.title("Pilih Customer")
            selection_window.geometry("400x300")
            selection_window.configure(bg='#ecf0f1')
            selection_window.transient()
            selection_window.grab_set()
            
            # Header
            header = tk.Label(
                selection_window,
                text="📋 PILIH CUSTOMER UNTUK PACKING LIST",
                font=('Arial', 14, 'bold'),
                bg='#e67e22',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
            
            # Instructions
            tk.Label(
                selection_window,
                text="Pilih customer yang akan dibuatkan packing list:",
                font=('Arial', 11),
                bg='#ecf0f1'
            ).pack(pady=10)
            
            # Customer list
            list_frame = tk.Frame(selection_window, bg='#ecf0f1')
            list_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            customer_listbox = tk.Listbox(list_frame, font=('Arial', 10), height=8)
            
            # Add "All Customers" option
            customer_listbox.insert(tk.END, "📊 ALL CUSTOMERS")
            
            # Add individual customers
            for customer in sorted(customers):
                customer_listbox.insert(tk.END, f"👤 {customer}")
            
            # Scrollbar for listbox
            scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=customer_listbox.yview)
            customer_listbox.configure(yscrollcommand=scrollbar.set)
            
            customer_listbox.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Buttons
            btn_frame = tk.Frame(selection_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', padx=20, pady=10)
            
            def print_selected():
                selection = customer_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Peringatan", "Pilih customer terlebih dahulu!")
                    return
                
                selected_text = customer_listbox.get(selection[0])
                
                if selected_text.startswith("📊 ALL CUSTOMERS"):
                    # Print for all customers
                    self.print_customer_packing_list(container_id, None)
                else:
                    # Print for specific customer
                    customer_name = selected_text.replace("👤 ", "")
                    self.print_customer_packing_list(container_id, customer_name)
                
                selection_window.destroy()
            
            tk.Button(
                btn_frame,
                text="📄 Print Packing List",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=20,
                pady=8,
                command=print_selected
            ).pack(side='left')
            
            tk.Button(
                btn_frame,
                text="❌ Batal",
                font=('Arial', 12, 'bold'),
                bg='#e74c3c',
                fg='white',
                padx=20,
                pady=8,
                command=selection_window.destroy
            ).pack(side='right')
            
            # Center window
            selection_window.update_idletasks()
            x = (selection_window.winfo_screenwidth() // 2) - (200)
            y = (selection_window.winfo_screenheight() // 2) - (150)
            selection_window.geometry(f"400x300+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat dialog selection: {str(e)}")