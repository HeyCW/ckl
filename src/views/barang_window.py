import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from src.models.database import AppDatabase

class BarangWindow:
    def __init__(self, parent, db, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.create_window()
    
    def create_window(self):
        """Create barang management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📦 Data Barang")
        self.window.geometry("1200x800")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.window,
            text="📦 KELOLA DATA BARANG",
            font=('Arial', 18, 'bold'),
            bg='#27ae60',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tab 1: Manual Input
        manual_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(manual_frame, text='✍️ Input Manual')
        self.create_manual_tab(manual_frame)
        
        # Tab 2: Excel Upload
        excel_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(excel_frame, text='📊 Upload Excel')
        self.create_excel_tab(excel_frame)
        
        # Tab 3: Barang List
        list_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(list_frame, text='📋 Daftar Barang')
        self.create_list_tab(list_frame)
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="❌ Tutup",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=10,
            command=self.window.destroy
        )
        close_btn.pack(pady=10)
    
    def create_manual_tab(self, parent):
        """Create manual input tab"""
        # Form frame
        form_frame = tk.Frame(parent, bg='#ecf0f1')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Instructions
        instruction_label = tk.Label(
            form_frame,
            text="📝 Tambah Barang Satu per Satu",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        )
        instruction_label.pack(pady=(0, 20))
        
        # Customer selection
        tk.Label(form_frame, text="Pilih Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(form_frame, textvariable=self.customer_var, font=('Arial', 11), width=47, state='readonly')
        self.customer_combo.pack(fill='x', pady=(5, 10))
        
        # Load customers into combobox
        self.load_customer_combo()
        
        # Jenis Barang
        tk.Label(form_frame, text="Jenis Barang:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.jenis_barang_entry = tk.Entry(form_frame, font=('Arial', 12), width=50)
        self.jenis_barang_entry.pack(fill='x', pady=(5, 10))
        
        # Barang name
        tk.Label(form_frame, text="Nama Barang:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.barang_entry = tk.Entry(form_frame, font=('Arial', 12), width=50)
        self.barang_entry.pack(fill='x', pady=(5, 10))
        
        # Dimensions frame
        dim_frame = tk.Frame(form_frame, bg='#ecf0f1')
        dim_frame.pack(fill='x', pady=10)
        
        # Panjang
        tk.Label(dim_frame, text="Panjang (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.panjang_entry = tk.Entry(dim_frame, font=('Arial', 10), width=10)
        self.panjang_entry.pack(side='left', padx=(5, 20))
        
        # Lebar
        tk.Label(dim_frame, text="Lebar (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.lebar_entry = tk.Entry(dim_frame, font=('Arial', 10), width=10)
        self.lebar_entry.pack(side='left', padx=(5, 20))
        
        # Tinggi
        tk.Label(dim_frame, text="Tinggi (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.tinggi_entry = tk.Entry(dim_frame, font=('Arial', 10), width=10)
        self.tinggi_entry.pack(side='left', padx=5)
        
        # Other fields frame
        other_frame = tk.Frame(form_frame, bg='#ecf0f1')
        other_frame.pack(fill='x', pady=10)
        
        # M3
        tk.Label(other_frame, text="Volume (m³):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.m3_entry = tk.Entry(other_frame, font=('Arial', 10), width=10)
        self.m3_entry.pack(side='left', padx=(5, 20))
        
        # Ton
        tk.Label(other_frame, text="Berat (ton):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.ton_entry = tk.Entry(other_frame, font=('Arial', 10), width=10)
        self.ton_entry.pack(side='left', padx=(5, 20))
        
        # Colli
        tk.Label(other_frame, text="Colli:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.col_entry = tk.Entry(other_frame, font=('Arial', 10), width=10)
        self.col_entry.pack(side='left', padx=5)
        
        # Price frame with multiple pricing options
        price_frame = tk.Frame(form_frame, bg='#ecf0f1')
        price_frame.pack(fill='x', pady=10)
        
        tk.Label(price_frame, text="Harga Satuan:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 5))
        
        # Pricing options sub-frame
        pricing_subframe = tk.Frame(price_frame, bg='#ecf0f1')
        pricing_subframe.pack(fill='x')
        
        # Harga per m3
        harga_m3_frame = tk.Frame(pricing_subframe, bg='#ecf0f1')
        harga_m3_frame.pack(fill='x', pady=2)
        tk.Label(harga_m3_frame, text="Harga/m³ (Rp):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.harga_m3_entry = tk.Entry(harga_m3_frame, font=('Arial', 10), width=20)
        self.harga_m3_entry.pack(side='left', padx=(5, 0))
        
        # Harga per ton
        harga_ton_frame = tk.Frame(pricing_subframe, bg='#ecf0f1')
        harga_ton_frame.pack(fill='x', pady=2)
        tk.Label(harga_ton_frame, text="Harga/ton (Rp):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.harga_ton_entry = tk.Entry(harga_ton_frame, font=('Arial', 10), width=20)
        self.harga_ton_entry.pack(side='left', padx=(5, 0))
        
        # Harga per colli
        harga_coll_frame = tk.Frame(pricing_subframe, bg='#ecf0f1')
        harga_coll_frame.pack(fill='x', pady=2)
        tk.Label(harga_coll_frame, text="Harga/colli (Rp):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.harga_coll_entry = tk.Entry(harga_coll_frame, font=('Arial', 10), width=20)
        self.harga_coll_entry.pack(side='left', padx=(5, 0))
        
        # Note
        note_label = tk.Label(
            price_frame,
            text="💡 Isi salah satu metode pricing atau lebih",
            font=('Arial', 9),
            fg='#7f8c8d',
            bg='#ecf0f1'
        )
        note_label.pack(anchor='w', pady=(5, 0))
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=20)
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Tambah Barang",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            command=self.add_barang
        )
        add_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Bersihkan",
            font=('Arial', 12, 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=10,
            command=self.clear_form
        )
        clear_btn.pack(side='left')
        
        # Focus on customer combo
        self.customer_combo.focus()
    
    def create_excel_tab(self, parent):
        """Create Excel upload tab"""
        # Main container
        main_container = tk.Frame(parent, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Instructions
        instruction_frame = tk.Frame(main_container, bg='#ffffff', relief='solid', bd=1)
        instruction_frame.pack(fill='x', pady=(0, 20))
        
        instruction_title = tk.Label(
            instruction_frame,
            text="📊 Upload Data Barang dari Excel",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50',
            bg='#ffffff'
        )
        instruction_title.pack(pady=(10, 5))
        
        instruction_text = tk.Label(
            instruction_frame,
            text="Format Excel yang dibutuhkan:\n\n" +
                 "• Customer: Nama customer yang sudah terdaftar (WAJIB)\n" +
                 "• Nama Barang: Nama produk/barang (WAJIB)\n" +
                 "• Jenis Barang: Kategori barang (opsional)\n" +
                 "• P, L, T: Panjang, Lebar, Tinggi (cm)\n" +
                 "• M3: Volume (m³), Ton: Berat (ton), Colli: Jumlah kemasan\n" +
                 "• Harga/m3, Harga/ton, Harga/coll: Harga satuan per metode\n\n" +
                 "Pastikan customer sudah terdaftar di sistem!",
            font=('Arial', 10),
            fg='#34495e',
            bg='#ffffff',
            justify='left'
        )
        instruction_text.pack(pady=(0, 10), padx=20)
        
        # File selection
        file_frame = tk.Frame(main_container, bg='#ecf0f1')
        file_frame.pack(fill='x', pady=10)
        
        tk.Label(file_frame, text="Pilih File Excel:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        file_input_frame = tk.Frame(file_frame, bg='#ecf0f1')
        file_input_frame.pack(fill='x', pady=(5, 0))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_input_frame, textvariable=self.file_path_var, font=('Arial', 11), state='readonly')
        self.file_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        browse_btn = tk.Button(
            file_input_frame,
            text="📁 Browse",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            command=self.browse_file
        )
        browse_btn.pack(side='right', padx=(5, 0))
        
        # Preview area
        preview_frame = tk.Frame(main_container, bg='#ecf0f1')
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(preview_frame, text="📋 Preview Data:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        # Preview treeview with horizontal scroll
        preview_tree_frame = tk.Frame(preview_frame, bg='#ecf0f1')
        preview_tree_frame.pack(fill='x', pady=5)
        
        preview_container = tk.Frame(preview_tree_frame, bg='#ecf0f1')
        preview_container.pack(fill='both', expand=True)
        
        self.preview_tree = ttk.Treeview(preview_container, 
                                       columns=('Customer', 'Jenis', 'Nama', 'P', 'L', 'T', 'M3', 'Ton', 'Colli', 'Harga/m3', 'Harga/ton', 'Harga/coll'), 
                                       show='headings', height=6)
        
        # Configure columns
        headers = {
            'Customer': 'Customer',
            'Jenis': 'Jenis Barang', 
            'Nama': 'Nama Barang',
            'P': 'P(cm)',
            'L': 'L(cm)', 
            'T': 'T(cm)',
            'M3': 'M3',
            'Ton': 'Ton',
            'Colli': 'Colli',
            'Harga/m3': 'Harga/m3',
            'Harga/ton': 'Harga/ton',
            'Harga/coll': 'Harga/coll'
        }
        
        for col_id, header_text in headers.items():
            self.preview_tree.heading(col_id, text=header_text)
        
        # Configure column widths
        column_widths = {
            'Customer': 120,
            'Jenis': 100,
            'Nama': 180,
            'P': 50,
            'L': 50,
            'T': 50,
            'M3': 70,
            'Ton': 70,
            'Colli': 60,
            'Harga/m3': 100,
            'Harga/ton': 100,
            'Harga/coll': 100
        }
        
        for col_id, width in column_widths.items():
            self.preview_tree.column(col_id, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(preview_container, orient='vertical', command=self.preview_tree.yview)
        h_scrollbar = ttk.Scrollbar(preview_container, orient='horizontal', command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.preview_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # Upload buttons
        upload_btn_frame = tk.Frame(main_container, bg='#ecf0f1')
        upload_btn_frame.pack(fill='x', pady=15)
        
        self.upload_btn = tk.Button(
            upload_btn_frame,
            text="⬆️ Upload ke Database",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=15,
            command=self.upload_excel_data,
            state='disabled'
        )
        self.upload_btn.pack(side='left', padx=(0, 15))
        
        download_template_btn = tk.Button(
            upload_btn_frame,
            text="📥 Download Template",
            font=('Arial', 14, 'bold'),
            bg='#f39c12',
            fg='white',
            padx=30,
            pady=15,
            command=self.download_template
        )
        download_template_btn.pack(side='left')
        
        # Status label
        self.status_label = tk.Label(
            main_container,
            text="",
            font=('Arial', 11),
            fg='#e74c3c',
            bg='#ecf0f1',
            wraplength=1000,
            justify='left'
        )
        self.status_label.pack(pady=10, fill='x')
    
    def create_list_tab(self, parent):
        """Create barang list tab"""
        # Container
        list_container = tk.Frame(parent, bg='#ecf0f1')
        list_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(list_container, bg='#ecf0f1')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="📋 DAFTAR BARANG", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(side='left')
        
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            command=self.load_barang
        )
        refresh_btn.pack(side='right')
        
        # Treeview for barang list with scrollbars
        tree_frame = tk.Frame(list_container, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True)
        
        tree_container = tk.Frame(tree_frame, bg='#ecf0f1')
        tree_container.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_container, 
                               columns=('ID', 'Customer', 'Nama', 'Dimensi', 'Volume', 'Berat', 'Colli', 'Harga', 'Created'), 
                               show='headings', height=15)
        
        # Configure columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Customer', text='Customer')
        self.tree.heading('Nama', text='Nama Barang')
        self.tree.heading('Dimensi', text='P×L×T (cm)')
        self.tree.heading('Volume', text='Volume (m³)')
        self.tree.heading('Berat', text='Berat (ton)')
        self.tree.heading('Colli', text='Colli')
        self.tree.heading('Harga', text='Harga (Rp)')
        self.tree.heading('Created', text='Tanggal Dibuat')
        
        self.tree.column('ID', width=40)
        self.tree.column('Customer', width=120)
        self.tree.column('Nama', width=200)
        self.tree.column('Dimensi', width=100)
        self.tree.column('Volume', width=80)
        self.tree.column('Berat', width=80)
        self.tree.column('Colli', width=60)
        self.tree.column('Harga', width=100)
        self.tree.column('Created', width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Load existing barang
        self.load_barang()
        
        # Add tab change event to refresh data when switching to this tab
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def show_error_details(self, errors, customer_not_found_list, success_count, total_count):
        """Show detailed error modal with specific error information"""
        error_window = tk.Toplevel(self.window)
        error_window.title("📊 Detail Error Upload")
        error_window.geometry("800x600")
        error_window.configure(bg='#ecf0f1')
        error_window.transient(self.window)
        error_window.grab_set()
        
        # Center the error window
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (error_window.winfo_screenheight() // 2) - (600 // 2)
        error_window.geometry(f"800x600+{x}+{y}")
        
        # Header
        header = tk.Label(
            error_window,
            text="📊 DETAIL HASIL UPLOAD",
            font=('Arial', 16, 'bold'),
            bg='#e74c3c',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Summary frame
        summary_frame = tk.Frame(error_window, bg='#ffffff', relief='solid', bd=1)
        summary_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        summary_text = f"""📈 RINGKASAN UPLOAD:
        
✅ Berhasil: {success_count} dari {total_count} barang
❌ Gagal: {len(errors)} barang  
⚠️ Customer tidak ditemukan: {len(customer_not_found_list)} barang
        
📋 Total diproses: {total_count} baris data"""
        
        summary_label = tk.Label(
            summary_frame,
            text=summary_text,
            font=('Arial', 12),
            fg='#2c3e50',
            bg='#ffffff',
            justify='left',
            padx=20,
            pady=15
        )
        summary_label.pack(fill='x')
        
        # Create notebook for error details
        notebook = ttk.Notebook(error_window)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: Processing Errors
        if errors:
            error_frame = tk.Frame(notebook, bg='#ecf0f1')
            notebook.add(error_frame, text=f'❌ Error Processing ({len(errors)})')
            
            error_label = tk.Label(
                error_frame,
                text="Barang yang gagal diproses karena error teknis:",
                font=('Arial', 12, 'bold'),
                fg='#e74c3c',
                bg='#ecf0f1'
            )
            error_label.pack(anchor='w', padx=10, pady=(10, 5))
            
            # Error treeview
            error_tree_frame = tk.Frame(error_frame, bg='#ecf0f1')
            error_tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            error_tree = ttk.Treeview(error_tree_frame, 
                                    columns=('No', 'Nama Barang', 'Customer', 'Error'), 
                                    show='headings', height=15)
            
            error_tree.heading('No', text='No')
            error_tree.heading('Nama Barang', text='Nama Barang')
            error_tree.heading('Customer', text='Customer')
            error_tree.heading('Error', text='Detail Error')
            
            error_tree.column('No', width=40)
            error_tree.column('Nama Barang', width=200)
            error_tree.column('Customer', width=150)
            error_tree.column('Error', width=300)
            
            # Add error data
            for i, error_info in enumerate(errors, 1):
                error_tree.insert('', tk.END, values=(
                    i,
                    error_info.get('nama_barang', 'N/A'),
                    error_info.get('customer', 'N/A'),
                    error_info.get('error', 'Unknown error')
                ))
            
            # Scrollbars for error tree
            error_v_scrollbar = ttk.Scrollbar(error_tree_frame, orient='vertical', command=error_tree.yview)
            error_h_scrollbar = ttk.Scrollbar(error_tree_frame, orient='horizontal', command=error_tree.xview)
            error_tree.configure(yscrollcommand=error_v_scrollbar.set, xscrollcommand=error_h_scrollbar.set)
            
            error_tree.pack(side='left', fill='both', expand=True)
            error_v_scrollbar.pack(side='right', fill='y')
            error_h_scrollbar.pack(side='bottom', fill='x')
        
        # Tab 2: Customer Not Found
        if customer_not_found_list:
            customer_frame = tk.Frame(notebook, bg='#ecf0f1')
            notebook.add(customer_frame, text=f'⚠️ Customer Tidak Ditemukan ({len(customer_not_found_list)})')
            
            customer_label = tk.Label(
                customer_frame,
                text="Barang yang gagal karena customer belum terdaftar di sistem:",
                font=('Arial', 12, 'bold'),
                fg='#f39c12',
                bg='#ecf0f1'
            )
            customer_label.pack(anchor='w', padx=10, pady=(10, 5))
            
            # Customer not found treeview
            customer_tree_frame = tk.Frame(customer_frame, bg='#ecf0f1')
            customer_tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            customer_tree = ttk.Treeview(customer_tree_frame, 
                                       columns=('No', 'Nama Barang', 'Customer yang Dicari'), 
                                       show='headings', height=15)
            
            customer_tree.heading('No', text='No')
            customer_tree.heading('Nama Barang', text='Nama Barang')
            customer_tree.heading('Customer yang Dicari', text='Customer yang Dicari')
            
            customer_tree.column('No', width=40)
            customer_tree.column('Nama Barang', width=300)
            customer_tree.column('Customer yang Dicari', width=250)
            
            # Add customer not found data
            for i, customer_info in enumerate(customer_not_found_list, 1):
                customer_tree.insert('', tk.END, values=(
                    i,
                    customer_info.get('nama_barang', 'N/A'),
                    customer_info.get('customer', 'N/A')
                ))
            
            # Scrollbars for customer tree
            customer_v_scrollbar = ttk.Scrollbar(customer_tree_frame, orient='vertical', command=customer_tree.yview)
            customer_h_scrollbar = ttk.Scrollbar(customer_tree_frame, orient='horizontal', command=customer_tree.xview)
            customer_tree.configure(yscrollcommand=customer_v_scrollbar.set, xscrollcommand=customer_h_scrollbar.set)
            
            customer_tree.pack(side='left', fill='both', expand=True)
            customer_v_scrollbar.pack(side='right', fill='y')
            customer_h_scrollbar.pack(side='bottom', fill='x')
            
            # Add instruction for customer not found
            instruction_frame = tk.Frame(customer_frame, bg='#fff3cd', relief='solid', bd=1)
            instruction_frame.pack(fill='x', padx=10, pady=10)
            
            instruction_text = tk.Label(
                instruction_frame,
                text="💡 Solusi: Tambahkan customer yang belum terdaftar melalui menu Customer, " +
                     "kemudian upload ulang file Excel ini.",
                font=('Arial', 10),
                fg='#856404',
                bg='#fff3cd',
                wraplength=700,
                justify='left',
                padx=15,
                pady=10
            )
            instruction_text.pack()
        
        # Tab 3: Upload Tips
        tips_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(tips_frame, text='💡 Tips Upload')
        
        tips_text = """
📋 TIPS UNTUK UPLOAD YANG SUKSES:

1. 🔍 Pastikan Format Excel Benar:
   • Gunakan template yang sudah disediakan
   • Kolom 'Customer' dan 'Nama Barang' wajib diisi
   • Format angka menggunakan titik (.) untuk desimal

2. 👥 Customer Management:
   • Pastikan semua customer sudah terdaftar di sistem
   • Nama customer di Excel harus persis sama dengan di sistem
   • Gunakan menu Customer untuk menambah customer baru

3. 📊 Data Quality:
   • Hindari sel kosong pada kolom wajib
   • Gunakan format angka yang konsisten
   • Periksa kembali data sebelum upload

4. 🚨 Mengatasi Error:
   • Perbaiki baris yang error sesuai detail di tab Error
   • Tambahkan customer yang belum ada
   • Upload ulang file yang sudah diperbaiki

5. 💾 Backup Data:
   • Simpan file Excel asli sebagai backup
   • Export data yang sudah ada sebelum upload besar
        """
        
        tips_label = tk.Label(
            tips_frame,
            text=tips_text,
            font=('Arial', 11),
            fg='#2c3e50',
            bg='#ecf0f1',
            justify='left',
            padx=20,
            pady=20
        )
        tips_label.pack(fill='both', expand=True)
        
        # Close button
        close_btn = tk.Button(
            error_window,
            text="✅ Tutup",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=40,
            pady=15,
            command=error_window.destroy
        )
        close_btn.pack(pady=20)
    
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (1200 // 2)
        y = parent_y + (parent_height // 2) - (800 // 2)
        
        self.window.geometry(f"1200x800+{x}+{y}")
    
    def load_customer_combo(self):
        """Load customers into combobox"""
        customers = self.db.get_all_customers()
        customer_list = [f"{c['customer_id']} - {c['nama_customer']}" for c in customers]
        self.customer_combo['values'] = customer_list
    
    def browse_file(self):
        """Browse for Excel file"""
        file_types = [
            ('Excel files', '*.xlsx *.xls'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Pilih File Excel",
            filetypes=file_types,
            parent=self.window
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.preview_excel_file(filename)
    
    def preview_excel_file(self, filename):
        """Preview Excel file content with enhanced field mapping"""
        try:
            self.status_label.config(text="📄 Membaca file Excel...", fg='#3498db')
            
            # Clear previous preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Read Excel file
            df = pd.read_excel(filename, engine='openpyxl')
            print(f"📋 Columns found: {list(df.columns)}")
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            
            # Enhanced column mapping for barang data
            column_mapping = {
                'customer': ['customer', 'nama customer', 'client'],
                'jenis_barang': ['jenis barang', 'jenis_barang', 'kategori', 'category', 'type'],
                'nama_barang': ['nama barang', 'nama_barang', 'barang', 'product', 'nama'],
                'panjang': ['p', 'panjang', 'length'],
                'lebar': ['l', 'lebar', 'width'], 
                'tinggi': ['t', 'tinggi', 'height'],
                'm3': ['m3', 'volume', 'vol'],
                'ton': ['ton', 'berat', 'weight'],
                'colli': ['colli', 'coll', 'kemasan', 'package'],
                'harga_m3': ['harga/m3', 'harga per m3', 'harga_m3', 'price_m3'],
                'harga_ton': ['harga/ton', 'harga per ton', 'harga_ton', 'price_ton'],
                'harga_coll': ['harga/coll', 'harga per coll', 'harga_coll', 'price_coll', 'harga/colli'],
                'harga': ['harga', 'price']  # Generic price field as fallback
            }
            
            # Find columns
            found_columns = {}
            for field, possible_names in column_mapping.items():
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if any(name in col_lower for name in possible_names):
                        found_columns[field] = col
                        break
            
            print(f"🎯 Found columns mapping: {found_columns}")
            
            # Check required columns
            required_fields = ['customer', 'nama_barang']
            missing_fields = [field for field in required_fields if field not in found_columns]
            
            if missing_fields:
                available_cols = ', '.join(df.columns.tolist())
                self.status_label.config(
                    text=f"❌ Kolom wajib tidak ditemukan: {missing_fields}\n\nKolom tersedia: {available_cols}", 
                    fg='#e74c3c'
                )
                self.upload_btn.config(state='disabled')
                return
            
            # Preview data
            valid_rows = df.dropna(subset=[found_columns['customer'], found_columns['nama_barang']])
            preview_data = valid_rows.head(50)
            
            # Get existing customers for validation
            existing_customers = {c['nama_customer'].upper(): c['customer_id'] for c in self.db.get_all_customers()}
            
            preview_count = 0
            for _, row in preview_data.iterrows():
                customer = str(row[found_columns['customer']]).strip()
                nama_barang = str(row[found_columns['nama_barang']]).strip()
                
                # Get other fields with better handling
                def get_field_value(field_name, default=''):
                    if field_name in found_columns:
                        value = row.get(found_columns[field_name], default)
                        if pd.isna(value) or str(value).strip().lower() in ['nan', 'none', '']:
                            return ''
                        return str(value).strip()
                    return default
                
                jenis_barang = get_field_value('jenis_barang')
                panjang = get_field_value('panjang')
                lebar = get_field_value('lebar') 
                tinggi = get_field_value('tinggi')
                m3 = get_field_value('m3')
                ton = get_field_value('ton')
                colli = get_field_value('colli')
                harga_m3 = get_field_value('harga_m3')
                harga_ton = get_field_value('harga_ton')
                harga_coll = get_field_value('harga_coll')
                
                # If specific price fields not found, try generic harga
                if not any([harga_m3, harga_ton, harga_coll]):
                    generic_harga = get_field_value('harga')
                    if generic_harga:
                        harga_m3 = generic_harga  # Default to m3 pricing
                
                if customer and nama_barang:
                    # Check if customer exists
                    customer_status = "✅" if customer.upper() in existing_customers else "❌"
                    display_customer = f"{customer_status} {customer}"
                    
                    # Format currency values
                    def format_currency(value):
                        if value and str(value).strip():
                            try:
                                return f"{float(value):,.0f}"
                            except:
                                return value
                        return ''
                    
                    self.preview_tree.insert('', tk.END, values=(
                        display_customer, 
                        jenis_barang,
                        nama_barang, 
                        panjang, 
                        lebar, 
                        tinggi, 
                        m3, 
                        ton,
                        colli,
                        format_currency(harga_m3),
                        format_currency(harga_ton), 
                        format_currency(harga_coll)
                    ))
                    preview_count += 1
            
            # Store column mapping for upload
            self.column_mapping = found_columns
            
            # Create status message with found columns
            found_fields = list(found_columns.keys())
            optional_fields = [f for f in found_fields if f not in required_fields]
            
            status_msg = f"✅ File berhasil dibaca: {preview_count} baris data\n"
            status_msg += f"📋 Kolom wajib: {', '.join([found_columns[f] for f in required_fields])}\n"
            if optional_fields:
                status_msg += f"📊 Kolom opsional: {', '.join([found_columns[f] for f in optional_fields])}\n"
            status_msg += f"⚠️ Pastikan customer dengan tanda ❌ sudah terdaftar di sistem!"
            
            self.status_label.config(text=status_msg, fg='#27ae60')
            self.upload_btn.config(state='normal')
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Preview error: {error_detail}")
            
            self.status_label.config(
                text=f"❌ Error membaca file: {str(e)}", 
                fg='#e74c3c'
            )
            self.upload_btn.config(state='disabled')
    
    def upload_excel_data(self):
        """Upload Excel data to database with enhanced error handling and detailed modal"""
        filename = self.file_path_var.get()
        if not filename:
            messagebox.showerror("Error", "Pilih file Excel terlebih dahulu!")
            return
        
        try:
            print(f"🔄 Starting enhanced barang upload from file: {filename}")
            
            # Read Excel file
            df = pd.read_excel(filename, engine='openpyxl')
            df.columns = df.columns.astype(str).str.strip()
            
            # Use stored column mapping
            column_mapping = getattr(self, 'column_mapping', {})
            
            # Get existing customers
            existing_customers = {c['nama_customer'].upper(): c['customer_id'] for c in self.db.get_all_customers()}
            
            # Filter valid data
            valid_rows = df.dropna(subset=[column_mapping['customer'], column_mapping['nama_barang']])
            
            if len(valid_rows) == 0:
                messagebox.showerror("Error", "Tidak ada data valid untuk diupload!")
                return
            
            # Show data preview and pricing strategy confirmation
            pricing_methods = []
            has_harga_m3 = 'harga_m3' in column_mapping
            has_harga_ton = 'harga_ton' in column_mapping  
            has_harga_coll = 'harga_coll' in column_mapping
            has_generic_harga = 'harga' in column_mapping
            
            if has_harga_m3:
                pricing_methods.append("Harga per m³")
            if has_harga_ton:
                pricing_methods.append("Harga per ton")
            if has_harga_coll:
                pricing_methods.append("Harga per colli")
            if has_generic_harga and not pricing_methods:
                pricing_methods.append("Harga umum")
            
            pricing_info = "Metode pricing yang ditemukan:\n• " + "\n• ".join(pricing_methods) if pricing_methods else "Tidak ada kolom harga ditemukan"
            
            # Confirm upload
            confirm_msg = f"Upload {len(valid_rows)} barang ke database?\n\n{pricing_info}\n\nKolom yang akan diproses:\n"
            for field, col_name in column_mapping.items():
                confirm_msg += f"• {field}: {col_name}\n"
            
            if not messagebox.askyesno("Konfirmasi Upload", confirm_msg):
                return
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.window)
            progress_window.title("Upload Progress")
            progress_window.geometry("600x250")
            progress_window.transient(self.window)
            progress_window.grab_set()
            
            progress_label = tk.Label(progress_window, text="Memulai upload...", font=('Arial', 12))
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, length=500, mode='determinate')
            progress_bar.pack(pady=10)
            progress_bar['maximum'] = len(valid_rows)
            
            detail_label = tk.Label(progress_window, text="", font=('Arial', 10), fg='#666')
            detail_label.pack(pady=5)
            
            status_text = tk.Text(progress_window, height=6, width=70, font=('Arial', 9))
            status_text.pack(pady=10, padx=20, fill='both', expand=True)
            
            def log_status(message):
                status_text.insert(tk.END, message + "\n")
                status_text.see(tk.END)
                progress_window.update()
            
            # Initialize tracking variables
            success_count = 0
            errors = []  # List to store detailed error information
            customer_not_found_list = []  # List to store customer not found details
            
            log_status("🚀 Memulai proses upload barang...")
            
            for idx, (_, row) in enumerate(valid_rows.iterrows()):
                try:
                    customer_name = str(row[column_mapping['customer']]).strip()
                    nama_barang = str(row[column_mapping['nama_barang']]).strip()
                    
                    # Find customer ID
                    customer_id = existing_customers.get(customer_name.upper())
                    
                    if not customer_id:
                        log_status(f"❌ Customer tidak ditemukan: {customer_name}")
                        customer_not_found_list.append({
                            'nama_barang': nama_barang,
                            'customer': customer_name,
                            'row_number': idx + 2  # +2 because Excel is 1-indexed and has header
                        })
                        continue
                    
                    # Get all field values with enhanced handling
                    def get_safe_value(field_name, value_type='str'):
                        if field_name not in column_mapping:
                            return None
                        
                        value = row.get(column_mapping[field_name])
                        if pd.isna(value) or str(value).strip() == '':
                            return None
                        
                        try:
                            if value_type == 'float':
                                # Handle comma separated numbers (Indonesian format)
                                if isinstance(value, str):
                                    value = value.replace(',', '')
                                return float(str(value).strip())
                            elif value_type == 'int':
                                return int(float(str(value).strip()))
                            else:
                                return str(value).strip()
                        except Exception as ve:
                            raise ValueError(f"Format {field_name} tidak valid: '{value}' - {str(ve)}")
                    
                    # Get all fields
                    jenis_barang = get_safe_value('jenis_barang')
                    panjang = get_safe_value('panjang', 'float')
                    lebar = get_safe_value('lebar', 'float')
                    tinggi = get_safe_value('tinggi', 'float')
                    m3 = get_safe_value('m3', 'float')
                    ton = get_safe_value('ton', 'float')
                    colli = get_safe_value('colli', 'int')
                    
                    # Handle pricing - priority order: specific pricing > generic harga
                    harga_satuan = None
                    pricing_method = None
                    
                    if has_harga_m3:
                        harga_m3 = get_safe_value('harga_m3', 'float')
                        if harga_m3:
                            harga_satuan = harga_m3
                            pricing_method = "per m³"
                    
                    if not harga_satuan and has_harga_ton:
                        harga_ton = get_safe_value('harga_ton', 'float')
                        if harga_ton:
                            harga_satuan = harga_ton
                            pricing_method = "per ton"
                    
                    if not harga_satuan and has_harga_coll:
                        harga_coll = get_safe_value('harga_coll', 'float')
                        if harga_coll:
                            harga_satuan = harga_coll
                            pricing_method = "per colli"
                    
                    if not harga_satuan and has_generic_harga:
                        generic_harga = get_safe_value('harga', 'float')
                        if generic_harga:
                            harga_satuan = generic_harga
                            pricing_method = "umum"
                    
                    # Create barang with extended data
                    # Include jenis_barang in nama_barang if available
                    full_nama_barang = nama_barang
                    if jenis_barang:
                        full_nama_barang = f"[{jenis_barang}] {nama_barang}"
                    
                    barang_id = self.db.create_barang(
                        customer_id=customer_id,
                        nama_barang=full_nama_barang,
                        panjang_barang=panjang,
                        lebar_barang=lebar,
                        tinggi_barang=tinggi,
                        m3_barang=m3,
                        ton_barang=ton,
                        col_barang=colli,
                        harga_satuan=harga_satuan
                    )
                    
                    pricing_info = f" ({pricing_method})" if pricing_method else ""
                    log_status(f"✅ {success_count+1}. {nama_barang} - {customer_name}{pricing_info}")
                    success_count += 1
                
                except Exception as e:
                    error_detail = str(e)
                    error_msg = f"❌ Error pada '{nama_barang}': {error_detail}"
                    log_status(error_msg)
                    print(f"💥 Error adding barang '{nama_barang}': {error_detail}")
                    
                    # Store detailed error information
                    errors.append({
                        'nama_barang': nama_barang,
                        'customer': customer_name,
                        'error': error_detail,
                        'row_number': idx + 2  # +2 because Excel is 1-indexed and has header
                    })
                
                # Update progress
                progress_bar['value'] = idx + 1
                progress_label.config(text=f"Processing {idx + 1} of {len(valid_rows)}")
                detail_label.config(text=f"{nama_barang[:50]}...")
                progress_window.update()
            
            # Final summary
            total_processed = len(valid_rows)
            error_count = len(errors)
            customer_not_found_count = len(customer_not_found_list)
            
            log_status(f"\n🎉 Upload selesai!")
            log_status(f"✅ Berhasil: {success_count} barang")
            if customer_not_found_count > 0:
                log_status(f"⚠️ Customer tidak ditemukan: {customer_not_found_count}")
            if error_count > 0:
                log_status(f"❌ Error: {error_count}")
            
            # Keep progress window open for user to review
            close_btn = tk.Button(
                progress_window,
                text="✅ Tutup",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=30,
                pady=10,
                command=progress_window.destroy
            )
            close_btn.pack(pady=10)
            
            # Show detailed error modal if there are errors or customer issues
            if errors or customer_not_found_list:
                self.show_error_details(errors, customer_not_found_list, success_count, total_processed)
            else:
                # Show success message if everything went well
                messagebox.showinfo(
                    "Upload Berhasil! 🎉", 
                    f"Semua data berhasil diupload!\n\n" +
                    f"✅ Total berhasil: {success_count} barang\n" +
                    f"📊 Total diproses: {total_processed} baris data"
                )
            
            # Refresh display and switch to list tab
            self.load_barang()
            if self.refresh_callback:
                self.refresh_callback()
            
            # Switch to barang list tab
            self.notebook.select(2)
            
            # Clear file selection
            self.file_path_var.set("")
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            self.upload_btn.config(state='disabled')
            self.status_label.config(text="")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Upload error: {error_detail}")
            
            # Show critical error dialog
            error_msg = f"Terjadi error kritik saat upload:\n\n{str(e)}\n\nDetail teknis:\n{error_detail}"
            messagebox.showerror("Error Kritik", error_msg)
    
    def download_template(self):
        """Download Excel template for barang with enhanced fields"""
        try:
            print("📥 Creating enhanced barang template...")
            
            # Get existing customers for template
            customers = self.db.get_all_customers()
            if not customers:
                messagebox.showwarning("Warning", "Belum ada customer yang terdaftar!\nTambahkan customer terlebih dahulu.")
                return
            
            # Create enhanced sample data with all required fields
            template_data = {
                'Customer': [
                    customers[0]['nama_customer'] if customers else 'ANEKA PLASTIK',
                    customers[1]['nama_customer'] if len(customers) > 1 else 'ASIA VARIASI', 
                    customers[2]['nama_customer'] if len(customers) > 2 else 'ABADI KERAMIK',
                    customers[0]['nama_customer'] if customers else 'ANEKA PLASTIK'
                ],
                'Jenis Barang': [
                    'Bahan Baku',
                    'Makanan',
                    'Kemasan',
                    'Peralatan'
                ],
                'Nama Barang': [
                    'D ZAAN COKLAT BUBUK 25 KG',
                    'ABON JAMBU 15KG', 
                    'ABON PIALA, STEREOFOM BULAT',
                    'MIXER INDUSTRIAL 50L'
                ],
                'P': [77, 33, 134, 120],  # Panjang (cm)
                'L': [18, 28, 27, 80],    # Lebar (cm)
                'T': [38, 33, 72, 150],   # Tinggi (cm)
                'M3': [0.053, 0.030, 0.260, 1.44],  # Volume
                'Ton': [0.025, 0.015, 0.050, 0.500], # Berat
                'Colli': [1, 1, 50, 1],   # Jumlah colli
                'Harga/m3': [2830189, 6666667, 288462, 694444],    # Harga per m3
                'Harga/ton': [6000000, 13333333, 1500000, 2000000], # Harga per ton
                'Harga/coll': [150000, 200000, 75000, 1000000]     # Harga per colli
            }
            
            df = pd.DataFrame(template_data)
            print("✅ Enhanced template data created")
            
            # Save file
            filename = filedialog.asksaveasfilename(
                parent=self.window,
                title="Simpan Template Excel Barang",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile="template_barang_lengkap.xlsx"
            )
            
            if filename:
                print(f"💾 Saving enhanced template to: {filename}")
                
                # Create Excel with styling and instructions
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Main data sheet
                    df.to_excel(writer, index=False, sheet_name='Data Barang')
                    
                    # Create instructions sheet
                    instructions_data = {
                        'Kolom': [
                            'Customer',
                            'Jenis Barang', 
                            'Nama Barang',
                            'P (Panjang)',
                            'L (Lebar)',
                            'T (Tinggi)',
                            'M3 (Volume)',
                            'Ton (Berat)',
                            'Colli',
                            'Harga/m3',
                            'Harga/ton',
                            'Harga/coll'
                        ],
                        'Keterangan': [
                            'Nama customer yang sudah terdaftar di sistem (WAJIB)',
                            'Kategori/jenis barang (opsional)',
                            'Nama lengkap barang/produk (WAJIB)',
                            'Panjang barang dalam cm (opsional)',
                            'Lebar barang dalam cm (opsional)',
                            'Tinggi barang dalam cm (opsional)',
                            'Volume barang dalam meter kubik (opsional)',
                            'Berat barang dalam ton (opsional)',
                            'Jumlah colli/kemasan (opsional)',
                            'Harga per meter kubik dalam Rupiah (opsional)',
                            'Harga per ton dalam Rupiah (opsional)',
                            'Harga per colli dalam Rupiah (opsional)'
                        ],
                        'Contoh': [
                            'ANEKA PLASTIK',
                            'Bahan Baku / Makanan / Kemasan',
                            'D ZAAN COKLAT BUBUK 25 KG',
                            '77',
                            '18', 
                            '38',
                            '0.053',
                            '0.025',
                            '1',
                            '2830189',
                            '6000000',
                            '150000'
                        ]
                    }
                    
                    instructions_df = pd.DataFrame(instructions_data)
                    instructions_df.to_excel(writer, index=False, sheet_name='Petunjuk')
                    
                    # Get workbook and worksheets
                    workbook = writer.book
                    data_worksheet = writer.sheets['Data Barang']
                    instructions_worksheet = writer.sheets['Petunjuk']
                    
                    # Style headers
                    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                    
                    # Header styling
                    header_font = Font(bold=True, color="FFFFFF")
                    header_fill = PatternFill(start_color="27AE60", end_color="27AE60", fill_type="solid")
                    center_alignment = Alignment(horizontal="center", vertical="center")
                    
                    # Border
                    thin_border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )
                    
                    # Style data sheet headers
                    for col_num, column_title in enumerate(df.columns, 1):
                        cell = data_worksheet.cell(row=1, column=col_num)
                        cell.font = header_font
                        cell.fill = header_fill
                        cell.alignment = center_alignment
                        cell.border = thin_border
                    
                    # Style instructions sheet headers
                    instructions_header_fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
                    for col_num, column_title in enumerate(instructions_df.columns, 1):
                        cell = instructions_worksheet.cell(row=1, column=col_num)
                        cell.font = header_font
                        cell.fill = instructions_header_fill
                        cell.alignment = center_alignment
                        cell.border = thin_border
                    
                    # Auto-adjust column widths for both sheets
                    for worksheet in [data_worksheet, instructions_worksheet]:
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 3, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    # Add some formatting to data cells
                    for row in data_worksheet.iter_rows(min_row=2, max_row=len(df)+1):
                        for cell in row:
                            cell.border = thin_border
                            cell.alignment = Alignment(vertical="center")
                    
                    # Format currency columns in data sheet
                    currency_columns = ['Harga/m3', 'Harga/ton', 'Harga/coll']
                    for col_name in currency_columns:
                        if col_name in df.columns:
                            col_idx = list(df.columns).index(col_name) + 1
                            for row in range(2, len(df) + 2):
                                cell = data_worksheet.cell(row=row, column=col_idx)
                                cell.number_format = '#,##0'
                
                print("✅ Enhanced template saved successfully")
                messagebox.showinfo(
                    "Sukses", 
                    f"Template lengkap berhasil disimpan:\n{filename}\n\n" +
                    "Template berisi:\n" +
                    "• Sheet 'Data Barang' - contoh data dengan semua kolom\n" +
                    "• Sheet 'Petunjuk' - penjelasan setiap kolom\n" +
                    "• Harga/m3, Harga/ton, Harga/coll untuk berbagai metode pricing\n" +
                    "• Kolom Jenis Barang untuk kategorisasi\n\n" +
                    "Pastikan customer sudah terdaftar di sistem sebelum upload!"
                )
            else:
                print("❌ Save cancelled by user")
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Template download error: {error_detail}")
            
            messagebox.showerror("Error", f"Gagal membuat template:\n\nError: {str(e)}")
    
    def add_barang(self):
        """Add new barang manually with enhanced pricing"""
        customer_text = self.customer_var.get()
        if not customer_text:
            messagebox.showerror("Error", "Pilih customer terlebih dahulu!")
            self.customer_combo.focus()
            return
        
        customer_id = int(customer_text.split(' - ')[0])
        jenis_barang = self.jenis_barang_entry.get().strip()
        nama_barang = self.barang_entry.get().strip()
        
        if not nama_barang:
            messagebox.showerror("Error", "Nama barang harus diisi!")
            self.barang_entry.focus()
            return
        
        try:
            # Get numeric values
            panjang = float(self.panjang_entry.get()) if self.panjang_entry.get() else None
            lebar = float(self.lebar_entry.get()) if self.lebar_entry.get() else None
            tinggi = float(self.tinggi_entry.get()) if self.tinggi_entry.get() else None
            m3 = float(self.m3_entry.get()) if self.m3_entry.get() else None
            ton = float(self.ton_entry.get()) if self.ton_entry.get() else None
            col = int(self.col_entry.get()) if self.col_entry.get() else None
            
            # Get pricing information - priority: m3 > ton > coll
            harga_satuan = None
            pricing_method = None
            
            harga_m3 = float(self.harga_m3_entry.get()) if self.harga_m3_entry.get() else None
            harga_ton = float(self.harga_ton_entry.get()) if self.harga_ton_entry.get() else None
            harga_coll = float(self.harga_coll_entry.get()) if self.harga_coll_entry.get() else None
            
            if harga_m3:
                harga_satuan = harga_m3
                pricing_method = "per m³"
            elif harga_ton:
                harga_satuan = harga_ton
                pricing_method = "per ton"
            elif harga_coll:
                harga_satuan = harga_coll
                pricing_method = "per colli"
            
            # Include jenis_barang in nama_barang if provided
            full_nama_barang = nama_barang
            if jenis_barang:
                full_nama_barang = f"[{jenis_barang}] {nama_barang}"
            
            barang_id = self.db.create_barang(
                customer_id=customer_id,
                nama_barang=full_nama_barang,
                panjang_barang=panjang,
                lebar_barang=lebar,
                tinggi_barang=tinggi,
                m3_barang=m3,
                ton_barang=ton,
                col_barang=col,
                harga_satuan=harga_satuan
            )
            
            pricing_info = f" dengan harga {pricing_method}" if pricing_method else ""
            messagebox.showinfo("Sukses", f"Barang berhasil ditambahkan dengan ID: {barang_id}{pricing_info}")
            self.clear_form()
            
            # Refresh and switch to list tab
            self.load_barang()
            if self.refresh_callback:
                self.refresh_callback()
            
            self.notebook.select(2)  # Switch to list tab
            
        except ValueError:
            messagebox.showerror("Error", "Pastikan format angka benar!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan barang: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.customer_var.set('')
        self.jenis_barang_entry.delete(0, tk.END)
        self.barang_entry.delete(0, tk.END)
        self.panjang_entry.delete(0, tk.END)
        self.lebar_entry.delete(0, tk.END)
        self.tinggi_entry.delete(0, tk.END)
        self.m3_entry.delete(0, tk.END)
        self.ton_entry.delete(0, tk.END)
        self.col_entry.delete(0, tk.END)
        self.harga_m3_entry.delete(0, tk.END)
        self.harga_ton_entry.delete(0, tk.END)
        self.harga_coll_entry.delete(0, tk.END)
        self.customer_combo.focus()
    
    def load_barang(self):
        """Load barang into treeview"""
        try:
            print("🔄 Loading barang from database...")
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load barang from database
            barang_list = self.db.get_all_barang()
            print(f"📊 Found {len(barang_list)} barang in database")
            
            for barang in barang_list:
                # Format dimensions
                dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
                
                # Format currency
                harga = f"Rp {barang.get('harga_satuan', 0):,.0f}" if barang.get('harga_satuan') else '-'
                
                # Format date
                created_date = barang.get('created_at', '')[:10] if barang.get('created_at') else '-'
                
                self.tree.insert('', tk.END, values=(
                    barang['barang_id'],
                    barang['nama_customer'],
                    barang['nama_barang'],
                    dimensi,
                    barang.get('m3_barang', '-'),
                    barang.get('ton_barang', '-'),
                    barang.get('col_barang', '-'),
                    harga,
                    created_date
                ))
            
            print("✅ Barang list loaded successfully")
            
        except Exception as e:
            print(f"💥 Error loading barang: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal memuat daftar barang: {str(e)}")
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # If switching to barang list tab, refresh the data
        if "Daftar Barang" in tab_text:
            self.load_barang()
            print("Tab changed to Barang List - data refreshed")