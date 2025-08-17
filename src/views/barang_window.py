import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from src.models.database import AppDatabase
import re
from PIL import Image, ImageTk

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
        
        try:
            # Load dan resize image
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            
            # Set sebagai window icon
            self.window.iconphoto(False, icon_photo)
            
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")
        
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
        """Create barang list tab with search, update, delete functionality"""
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
        
        # Search/Filter Frame
        search_frame = tk.Frame(list_container, bg='#ffffff', relief='solid', bd=1)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search label
        search_label = tk.Label(
            search_frame,
            text="🔍 Filter & Pencarian:",
            font=('Arial', 12, 'bold'),
            fg='#2c3e50',
            bg='#ffffff'
        )
        search_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Search controls frame
        search_controls = tk.Frame(search_frame, bg='#ffffff')
        search_controls.pack(fill='x', padx=10, pady=(0, 10))
        
        # Search by name
        tk.Label(search_controls, text="Nama Barang:", font=('Arial', 10), bg='#ffffff').pack(side='left')
        self.search_name_var = tk.StringVar()
        self.search_name_var.trace('w', self.on_search_change)
        search_name_entry = tk.Entry(search_controls, textvariable=self.search_name_var, font=('Arial', 10), width=20)
        search_name_entry.pack(side='left', padx=(5, 15))
        
        # Filter by customer
        tk.Label(search_controls, text="Customer:", font=('Arial', 10), bg='#ffffff').pack(side='left')
        self.filter_customer_var = tk.StringVar()
        self.filter_customer_var.trace('w', self.on_search_change)
        self.filter_customer_combo = ttk.Combobox(
            search_controls, 
            textvariable=self.filter_customer_var, 
            font=('Arial', 10), 
            width=18,
            state='readonly'
        )
        self.filter_customer_combo.pack(side='left', padx=(5, 15))
        
        # Clear search button
        clear_search_btn = tk.Button(
            search_controls,
            text="❌ Clear",
            font=('Arial', 9),
            bg='#e67e22',
            fg='white',
            padx=10,
            pady=2,
            command=self.clear_search
        )
        clear_search_btn.pack(side='left', padx=5)
        
        # Action buttons frame
        action_frame = tk.Frame(list_container, bg='#ecf0f1')
        action_frame.pack(fill='x', pady=(0, 10))
        
        # Update button
        update_btn = tk.Button(
            action_frame,
            text="✏️ Edit Barang",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            command=self.update_barang
        )
        update_btn.pack(side='left', padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(
            action_frame,
            text="🗑️ Hapus Barang",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=8,
            command=self.delete_barang
        )
        delete_btn.pack(side='left', padx=(0, 10))
        
        # Export button
        export_btn = tk.Button(
            action_frame,
            text="📤 Export Excel",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            command=self.export_barang
        )
        export_btn.pack(side='left')
        
        # Info label
        self.info_label = tk.Label(
            action_frame,
            text="💡 Pilih barang dari tabel untuk edit/hapus",
            font=('Arial', 10),
            fg='#7f8c8d',
            bg='#ecf0f1'
        )
        self.info_label.pack(side='right')
        
        # Treeview for barang list with scrollbars
        tree_frame = tk.Frame(list_container, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True)
        
        tree_container = tk.Frame(tree_frame, bg='#ecf0f1')
        tree_container.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_container,
                               columns=('ID', 'Customer', 'Nama', 'Jenis', 'Dimensi', 'Volume', 'Berat', 'Colli', 'Harga/M3', 'Harga/Ton', 'Harga/Col', 'Created'),
                               show='headings', height=12)
        
        # Configure columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Customer', text='Customer')
        self.tree.heading('Nama', text='Nama Barang')
        self.tree.heading('Jenis', text='Jenis Barang')
        self.tree.heading('Dimensi', text='P×L×T (cm)')
        self.tree.heading('Volume', text='Volume (m³)')
        self.tree.heading('Berat', text='Berat (ton)')
        self.tree.heading('Colli', text='Colli')
        self.tree.heading('Harga/M3', text='Harga/M3 (Rp)')
        self.tree.heading('Harga/Ton', text='Harga/Ton (Rp)')
        self.tree.heading('Harga/Col', text='Harga/Col (Rp)')
        self.tree.heading('Created', text='Tanggal Dibuat')
        
        self.tree.column('ID', width=40)
        self.tree.column('Customer', width=120)
        self.tree.column('Nama', width=200)
        self.tree.column('Jenis', width=100)
        self.tree.column('Dimensi', width=100)
        self.tree.column('Volume', width=80)
        self.tree.column('Berat', width=80)
        self.tree.column('Colli', width=60)
        self.tree.column('Harga/M3', width=100)
        self.tree.column('Harga/Ton', width=100)
        self.tree.column('Harga/Col', width=100)
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
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self.update_barang())
        
        # Bind selection change to update info
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Store original data for filtering
        self.original_barang_data = []
        
        # Load existing barang
        self.load_barang()
        self.load_customer_filter()
        
        # Add tab change event to refresh data when switching to this tab
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def load_customer_filter(self):
        """Load customers for filter dropdown"""
        try:
            customers = self.db.get_all_customers()
            customer_names = ['-- Semua Customer --'] + [c['nama_customer'] for c in customers]
            self.filter_customer_combo['values'] = customer_names
            self.filter_customer_combo.set('-- Semua Customer --')
        except Exception as e:
            print(f"Error loading customer filter: {e}")
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        self.filter_barang()
    
    def clear_search(self):
        """Clear all search filters"""
        self.search_name_var.set('')
        self.filter_customer_var.set('-- Semua Customer --')
        self.filter_barang()
    
    def filter_barang(self):
        """Filter barang based on search criteria with fuzzy matching"""
        # Clear current display
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get search criteria
        search_name = self.search_name_var.get().strip()
        filter_customer = self.filter_customer_var.get()
        
        print(f"Search name {search_name}")
        
        # Filter data
        filtered_data = []
        
        print(f"Filtering data with {len(self.original_barang_data)} items")
        
        for barang in self.original_barang_data:
            # Check name filter with flexible matching
            if search_name:
                nama_barang = barang['nama_barang'].lower()
                search_terms = search_name.lower().split()
                
                print(f"search terms {search_terms}")
                
                # Check if any search term matches (partial matching)
                match_found = False
                for term in search_terms:
                    # Create regex pattern for flexible matching
                    # Allow for minor typos and partial matches
                    pattern = '.*'.join(re.escape(char) for char in term)
                    print(f"pattern: {pattern}")
                    if re.search(pattern, nama_barang, re.IGNORECASE):
                        match_found = True
                        break
                    
                    # Also check direct substring match
                    if term in nama_barang:
                        match_found = True
                        break
                
                if not match_found:
                    continue
                
            # Check customer filter
            if filter_customer and filter_customer != '-- Semua Customer --':
                if barang['nama_customer'] != filter_customer:
                    continue
            
            filtered_data.append(barang)
        
        # Display filtered data
        for barang in filtered_data:
            # Format dimensions
            dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
            
            # Format currency
            harga_m3 = f"Rp {barang.get('harga_m3', 0):,.0f}" if barang.get('harga_m3') else '-'
            harga_ton = f"Rp {barang.get('harga_ton', 0):,.0f}" if barang.get('harga_ton') else '-'
            harga_col = f"Rp {barang.get('harga_col', 0):,.0f}" if barang.get('harga_col') else '-'
            
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
                harga_m3,
                harga_ton,
                harga_col,
                created_date
            ))
        
        # Update info label
        total_count = len(self.original_barang_data)
        filtered_count = len(filtered_data)
        if total_count != filtered_count:
            self.info_label.config(text=f"📊 Menampilkan {filtered_count} dari {total_count} barang")
        else:
            self.info_label.config(text="💡 Pilih barang dari tabel untuk edit/hapus")

    def update_barang(self):
        """Update selected barang"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang yang akan diedit dari tabel!")
            return
        
        # Get selected item data
        item = self.tree.item(selection[0])
        barang_id = item['values'][0]
        
        # Find full barang data
        selected_barang = None
        for barang in self.original_barang_data:
            if barang['barang_id'] == barang_id:
                selected_barang = barang
                break
        print(f"Selected barang: {selected_barang}")

        if not selected_barang:
            messagebox.showerror("Error", "Data barang tidak ditemukan!")
            return
        
        # Open update dialog
        self.open_update_dialog(selected_barang)

    def save_changes(self, updated_barang):
        try:
            print(f"Updated data: {updated_barang}")
            self.db.update_barang(updated_barang)
            messagebox.showinfo("Sukses", "Data barang berhasil disimpan!")
            self.load_barang()
        except Exception as e:
            print(f"Error saat menyimpan data: {e}")
            messagebox.showerror("Error", f"Gagal menyimpan data barang!\nError: {str(e)}")
    
    def open_update_dialog(self, barang_data):
        """Open dialog to update barang data"""
        # Create update window
        update_window = tk.Toplevel(self.window)
        update_window.title(f"✏️ Edit Barang - {barang_data['nama_barang']}")
        update_window.geometry("600x700")
        update_window.configure(bg='#ecf0f1')
        update_window.transient(self.window)
        update_window.grab_set()
        
        # Center window
        update_window.update_idletasks()
        x = (update_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (update_window.winfo_screenheight() // 2) - (700 // 2)
        update_window.geometry(f"600x700+{x}+{y}")
        
        # Header
        header = tk.Label(
            update_window,
            text="✏️ EDIT DATA BARANG",
            font=('Arial', 16, 'bold'),
            bg='#3498db',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Form frame
        form_frame = tk.Frame(update_window, bg='#ecf0f1')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create form fields (similar to manual input but pre-filled)
        # Customer (read-only)
        tk.Label(form_frame, text="Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        customer_label = tk.Label(
            form_frame, 
            text=barang_data['nama_customer'], 
            font=('Arial', 11),
            bg='#ffffff',
            relief='solid',
            bd=1,
            padx=5,
            pady=5
        )
        customer_label.pack(fill='x', pady=(5, 10))
        
        # Nama Barang
        tk.Label(form_frame, text="Nama Barang:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        nama_barang_var = tk.StringVar(value=barang_data['nama_barang'])
        nama_barang_entry = tk.Entry(form_frame, textvariable=nama_barang_var, font=('Arial', 11))
        nama_barang_entry.pack(fill='x', pady=(5, 10))
        
        tk.Label(form_frame, text="Jenis Barang:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        jenis_barang_var = tk.StringVar(value=barang_data['jenis_barang'])
        jenis_barang_entry = tk.Entry(form_frame, textvariable=jenis_barang_var, font=('Arial', 11))
        jenis_barang_entry.pack(fill='x', pady=(5, 10))

        # Dimensions
        dim_frame = tk.Frame(form_frame, bg='#ecf0f1')
        dim_frame.pack(fill='x', pady=10)
        
        tk.Label(dim_frame, text="Panjang (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        panjang_var = tk.StringVar(value=str(barang_data.get('panjang_barang', '') or ''))
        panjang_entry = tk.Entry(dim_frame, textvariable=panjang_var, font=('Arial', 10), width=10)
        panjang_entry.pack(side='left', padx=(5, 20))
        
        tk.Label(dim_frame, text="Lebar (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        lebar_var = tk.StringVar(value=str(barang_data.get('lebar_barang', '') or ''))
        lebar_entry = tk.Entry(dim_frame, textvariable=lebar_var, font=('Arial', 10), width=10)
        lebar_entry.pack(side='left', padx=(5, 20))
        
        tk.Label(dim_frame, text="Tinggi (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        tinggi_var = tk.StringVar(value=str(barang_data.get('tinggi_barang', '') or ''))
        tinggi_entry = tk.Entry(dim_frame, textvariable=tinggi_var, font=('Arial', 10), width=10)
        tinggi_entry.pack(side='left', padx=5)
        
        # Other fields
        other_frame = tk.Frame(form_frame, bg='#ecf0f1')
        other_frame.pack(fill='x', pady=10)
        
        tk.Label(other_frame, text="Volume (m³):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        m3_var = tk.StringVar(value=str(barang_data.get('m3_barang', '') or ''))
        m3_entry = tk.Entry(other_frame, textvariable=m3_var, font=('Arial', 10), width=10)
        m3_entry.pack(side='left', padx=(5, 20))
        
        tk.Label(other_frame, text="Berat (ton):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        ton_var = tk.StringVar(value=str(barang_data.get('ton_barang', '') or ''))
        ton_entry = tk.Entry(other_frame, textvariable=ton_var, font=('Arial', 10), width=10)
        ton_entry.pack(side='left', padx=(5, 20))
        
        tk.Label(other_frame, text="Colli:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        col_var = tk.StringVar(value=str(barang_data.get('col_barang', '') or ''))
        col_entry = tk.Entry(other_frame, textvariable=col_var, font=('Arial', 10), width=10)
        col_entry.pack(side='left', padx=5)
        
        # Pricing fields
        price_frame = tk.Frame(form_frame, bg='#ecf0f1')
        price_frame.pack(fill='x', pady=10)
        
        tk.Label(price_frame, text="Harga Satuan:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 5))
        
        # Harga M3
        harga_m3_frame = tk.Frame(price_frame, bg='#ecf0f1')
        harga_m3_frame.pack(fill='x', pady=2)
        tk.Label(harga_m3_frame, text="Harga/m³ (Rp):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        harga_m3_var = tk.StringVar(value=str(barang_data.get('harga_m3', '') or ''))
        harga_m3_entry = tk.Entry(harga_m3_frame, textvariable=harga_m3_var, font=('Arial', 10), width=20)
        harga_m3_entry.pack(side='left', padx=(5, 0))
        
        # Harga Ton
        harga_ton_frame = tk.Frame(price_frame, bg='#ecf0f1')
        harga_ton_frame.pack(fill='x', pady=2)
        tk.Label(harga_ton_frame, text="Harga/ton (Rp):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        harga_ton_var = tk.StringVar(value=str(barang_data.get('harga_ton', '') or ''))
        harga_ton_entry = tk.Entry(harga_ton_frame, textvariable=harga_ton_var, font=('Arial', 10), width=20)
        harga_ton_entry.pack(side='left', padx=(5, 0))
        
        # Harga Col
        harga_col_frame = tk.Frame(price_frame, bg='#ecf0f1')
        harga_col_frame.pack(fill='x', pady=2)
        tk.Label(harga_col_frame, text="Harga/colli (Rp):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        harga_col_var = tk.StringVar(value=str(barang_data.get('harga_col', '') or ''))
        harga_col_entry = tk.Entry(harga_col_frame, textvariable=harga_col_var, font=('Arial', 10), width=20)
        harga_col_entry.pack(side='left', padx=(5, 0))
        
        def validate_update_form():
            """Validate update form data"""
            
            # 1. Nama Barang wajib
            if not nama_barang_var.get().strip():
                messagebox.showwarning("Peringatan", "Nama Barang tidak boleh kosong.")
                nama_barang_entry.focus()
                return False
            
            # 2. Validasi format angka untuk dimensi (jika diisi)
            try:
                if panjang_var.get().strip():
                    val = float(panjang_var.get())
                    if val <= 0:
                        raise ValueError("Panjang harus lebih besar dari 0")
                
                if lebar_var.get().strip():
                    val = float(lebar_var.get())
                    if val <= 0:
                        raise ValueError("Lebar harus lebih besar dari 0")
                
                if tinggi_var.get().strip():
                    val = float(tinggi_var.get())
                    if val <= 0:
                        raise ValueError("Tinggi harus lebih besar dari 0")
                        
            except ValueError as e:
                messagebox.showwarning("Format Tidak Valid", f"Dimensi tidak valid: {str(e)}")
                return False
            
            # 3. Validasi volume, berat, colli (jika diisi)
            try:
                if m3_var.get().strip():
                    val = float(m3_var.get())
                    if val <= 0:
                        raise ValueError("Volume harus lebih besar dari 0")
                
                if ton_var.get().strip():
                    val = float(ton_var.get())
                    if val <= 0:
                        raise ValueError("Berat harus lebih besar dari 0")
                
                if col_var.get().strip():
                    val = int(float(col_var.get()))
                    if val <= 0:
                        raise ValueError("Colli harus lebih besar dari 0")
                        
            except ValueError as e:
                messagebox.showwarning("Format Tidak Valid", f"Volume/Berat/Colli tidak valid: {str(e)}")
                return False
            
            # 4. Validasi harga - minimal salah satu harus diisi
            harga_m3 = harga_m3_var.get().strip()
            harga_ton = harga_ton_var.get().strip()
            harga_col = harga_col_var.get().strip()
            
            if not harga_m3 and not harga_ton and not harga_col:
                messagebox.showwarning(
                    "Peringatan", 
                    "Minimal salah satu metode pricing harus diisi!\n\n" +
                    "💰 Pilihan pricing:\n" +
                    "• Harga per m³ (untuk volume)\n" +
                    "• Harga per ton (untuk berat)\n" +
                    "• Harga per colli (untuk jumlah kemasan)"
                )
                harga_m3_entry.focus()
                return False
            
            # 5. Validasi format harga yang diisi
            try:
                if harga_m3:
                    val = float(harga_m3)
                    if val <= 0:
                        raise ValueError("Harga per m³ harus lebih besar dari 0")
                
                if harga_ton:
                    val = float(harga_ton)
                    if val <= 0:
                        raise ValueError("Harga per ton harus lebih besar dari 0")
                
                if harga_col:
                    val = float(harga_col)
                    if val <= 0:
                        raise ValueError("Harga per colli harus lebih besar dari 0")
                        
            except ValueError as e:
                messagebox.showwarning("Format Harga Tidak Valid", str(e))
                return False
            
            return True

        
        
        def on_save():
            """Save updated barang data with validation"""
        
            if not validate_update_form():
                return
            
            updated_barang = {
                'barang_id': barang_data['barang_id'],
                'nama_barang': nama_barang_var.get(),
                'jenis_barang': jenis_barang_var.get(),
                'panjang_barang': panjang_var.get(),
                'lebar_barang': lebar_var.get(),
                'tinggi_barang': tinggi_var.get(),
                'm3_barang': m3_var.get(),
                'ton_barang': ton_var.get(),
                'col_barang': col_var.get(),
                'harga_m3': harga_m3_var.get(),
                'harga_ton': harga_ton_var.get(),
                'harga_col': harga_col_var.get(),
                'updated_at': datetime.datetime.now()
            }
            self.save_changes(updated_barang)
            update_window.destroy()  

        

        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=30)
        
        # Tambahkan tombol Save
        btn_save = tk.Button(btn_frame, text="Save", bg="#2ecc71", fg="white", padx=20, pady=5, command=lambda: on_save())
        btn_save.pack(side="right", padx=10)

        # (opsional) tambahin tombol Cancel
        btn_cancel = tk.Button(btn_frame, text="Cancel", bg="#e74c3c", fg="white", padx=20, pady=5, command= lambda: update_window.destroy())
        btn_cancel.pack(side="right")
        
    def on_tree_select(self, event):
        """Handle tree selection change"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            barang_id = item['values'][0]
            nama_barang = item['values'][2]
            self.info_label.config(text=f"✅ Terpilih: {nama_barang} (ID: {barang_id})")
        else:
            self.info_label.config(text="💡 Pilih barang dari tabel untuk edit/hapus")
    
    def delete_barang(self):
        """Delete selected barang"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang yang akan dihapus dari tabel!")
            return
        
        # Get selected item data
        item = self.tree.item(selection[0])
        barang_id = item['values'][0]
        nama_barang = item['values'][2]
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Konfirmasi Hapus", 
            f"Yakin ingin menghapus barang?\n\n" +
            f"ID: {barang_id}\n" +
            f"Nama: {nama_barang}\n\n" +
            f"⚠️ Aksi ini tidak dapat dibatalkan!"
        ):
            return
        
        try:
            # Delete from database
            self.db.delete_barang(barang_id)
            
            messagebox.showinfo("Sukses", f"Barang '{nama_barang}' berhasil dihapus!")
            
            # Refresh data
            self.load_barang()
            if self.refresh_callback:
                self.refresh_callback()
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus barang:\n{str(e)}")
    
    def export_barang(self):
        """Export barang data to Excel"""
        try:
            if not self.original_barang_data:
                messagebox.showwarning("Peringatan", "Tidak ada data barang untuk diekspor!")
                return
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                parent=self.window,
                title="Export Data Barang ke Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"data_barang_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not filename:
                return
            
            # Prepare data for export
            export_data = []
            for barang in self.original_barang_data:
                export_data.append({
                    'ID': barang['barang_id'],
                    'Customer': barang['nama_customer'],
                    'Nama Barang': barang['nama_barang'],
                    'Panjang (cm)': barang.get('panjang_barang', ''),
                    'Lebar (cm)': barang.get('lebar_barang', ''),
                    'Tinggi (cm)': barang.get('tinggi_barang', ''),
                    'Volume (m³)': barang.get('m3_barang', ''),
                    'Berat (ton)': barang.get('ton_barang', ''),
                    'Colli': barang.get('col_barang', ''),
                    'Harga/M3 (Rp)': barang.get('harga_m3', ''),
                    'Harga/Ton (Rp)': barang.get('harga_ton', ''),
                    'Harga/Col (Rp)': barang.get('harga_col', ''),
                    'Tanggal Dibuat': barang.get('created_at', '')
                })
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data Barang')
                
                # Format the Excel file
                workbook = writer.book
                worksheet = writer.sheets['Data Barang']
                
                # Style headers
                from openpyxl.styles import Font, PatternFill, Alignment
                
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="27AE60", end_color="27AE60", fill_type="solid")
                
                for col_num, column_title in enumerate(df.columns, 1):
                    cell = worksheet.cell(row=1, column=col_num)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            messagebox.showinfo(
                "Export Berhasil",
                f"Data barang berhasil diekspor ke:\n{filename}\n\n" +
                f"📊 Total: {len(export_data)} barang"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export data:\n{str(e)}")

    def show_error_details(self, errors, customer_not_found_list, success_count, total_count):
        """Show detailed error modal with proper horizontal scrolling"""
        error_window = tk.Toplevel(self.window)
        error_window.title("📊 Detail Error Upload")
        error_window.geometry("1200x700")  # ✅ Lebih lebar lagi
        error_window.configure(bg='#ecf0f1')
        error_window.transient(self.window)
        error_window.grab_set()
        
        # Center the error window
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (1200 // 2)
        y = (error_window.winfo_screenheight() // 2) - (700 // 2)
        error_window.geometry(f"1200x700+{x}+{y}")
        
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
        
        # Tab 1: Processing Errors with PROPER scrolling
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
            
            # ✅ Main frame untuk treeview
            error_main_frame = tk.Frame(error_frame, bg='#ecf0f1')
            error_main_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # ✅ Create treeview dengan scrollbar yang benar
            error_tree = ttk.Treeview(error_main_frame, 
                                    columns=('No', 'Nama Barang', 'Customer', 'Error'), 
                                    show='headings', height=12)
            
            # Configure headers
            error_tree.heading('No', text='No')
            error_tree.heading('Nama Barang', text='Nama Barang')
            error_tree.heading('Customer', text='Customer')  
            error_tree.heading('Error', text='Detail Error')
            
            # ✅ Column widths yang lebih reasonable
            error_tree.column('No', width=50, minwidth=40, stretch=False)
            error_tree.column('Nama Barang', width=200, minwidth=150, stretch=False)
            error_tree.column('Customer', width=150, minwidth=120, stretch=False)
            error_tree.column('Error', width=600, minwidth=300, stretch=True)
            
            # Create scrollbars
            error_v_scroll = ttk.Scrollbar(error_main_frame, orient='vertical', command=error_tree.yview)
            error_h_scroll = ttk.Scrollbar(error_main_frame, orient='horizontal', command=error_tree.xview)
            
            # Configure treeview scrollbars
            error_tree.configure(yscrollcommand=error_v_scroll.set, xscrollcommand=error_h_scroll.set)
            
            # ✅ GRID LAYOUT untuk scrollbar yang proper
            error_tree.grid(row=0, column=0, sticky='nsew')
            error_v_scroll.grid(row=0, column=1, sticky='ns')
            error_h_scroll.grid(row=1, column=0, sticky='ew')
            
            # ✅ Configure grid weights
            error_main_frame.grid_rowconfigure(0, weight=1)
            error_main_frame.grid_columnconfigure(0, weight=1)
            
            # Add error data
            for i, error_info in enumerate(errors, 1):
                error_tree.insert('', tk.END, values=(
                    i,
                    error_info.get('nama_barang', 'N/A'),
                    error_info.get('customer', 'N/A'),
                    error_info.get('error', 'Unknown error')  # ✅ Error message bisa panjang
                ))
        
        # Tab 2: Customer Not Found dengan scrolling yang sama
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
            
            # ✅ Customer treeview dengan grid layout
            customer_main_frame = tk.Frame(customer_frame, bg='#ecf0f1')
            customer_main_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            customer_tree = ttk.Treeview(customer_main_frame, 
                                    columns=('No', 'Nama Barang', 'Customer yang Dicari'), 
                                    show='headings', height=12)
            
            customer_tree.heading('No', text='No')
            customer_tree.heading('Nama Barang', text='Nama Barang')
            customer_tree.heading('Customer yang Dicari', text='Customer yang Dicari')
            
            customer_tree.column('No', width=50, minwidth=40, stretch=False)
            customer_tree.column('Nama Barang', width=300, minwidth=200, stretch=False)
            customer_tree.column('Customer yang Dicari', width=300, minwidth=200, stretch=True)
            
            # Scrollbars
            customer_v_scroll = ttk.Scrollbar(customer_main_frame, orient='vertical', command=customer_tree.yview)
            customer_h_scroll = ttk.Scrollbar(customer_main_frame, orient='horizontal', command=customer_tree.xview)
            customer_tree.configure(yscrollcommand=customer_v_scroll.set, xscrollcommand=customer_h_scroll.set)
            
            # ✅ Grid layout
            customer_tree.grid(row=0, column=0, sticky='nsew')
            customer_v_scroll.grid(row=0, column=1, sticky='ns')
            customer_h_scroll.grid(row=1, column=0, sticky='ew')
            
            customer_main_frame.grid_rowconfigure(0, weight=1)
            customer_main_frame.grid_columnconfigure(0, weight=1)
            
            # Add customer not found data
            for i, customer_info in enumerate(customer_not_found_list, 1):
                customer_tree.insert('', tk.END, values=(
                    i,
                    customer_info.get('nama_barang', 'N/A'),
                    customer_info.get('customer', 'N/A')
                ))
            
            # Instruction
            instruction_frame = tk.Frame(customer_frame, bg='#fff3cd', relief='solid', bd=1)
            instruction_frame.pack(fill='x', padx=10, pady=10)
            
            instruction_text = tk.Label(
                instruction_frame,
                text="💡 Solusi: Tambahkan customer yang belum terdaftar melalui menu Customer, " +
                    "kemudian upload ulang file Excel ini.",
                font=('Arial', 10),
                fg='#856404',
                bg='#fff3cd',
                wraplength=1000,
                justify='left',
                padx=15,
                pady=10
            )
            instruction_text.pack()
        
        # Tab 3: Tips (sama seperti sebelumnya)
        tips_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(tips_frame, text='💡 Tips Upload')
        
        # ... (kode tips sama seperti sebelumnya)
        
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
            
            # Enhanced column mapping for barang data with better matching logic
            column_mapping = {
                'customer': ['customer', 'nama customer', 'client'],
                'jenis_barang': ['jenis barang', 'jenis_barang', 'kategori', 'category', 'type'],
                'nama_barang': ['nama barang', 'nama_barang', 'barang', 'product', 'nama'],
                'panjang': ['p', 'panjang', 'length'],
                'lebar': ['l', 'lebar', 'width'], 
                'tinggi': ['t', 'tinggi', 'height'],
                'm3': ['m3', 'volume', 'vol'],
                'ton': ['ton', 'berat', 'weight'],
                'colli': ['colli', 'col', 'kemasan', 'package'],
                'harga_m3': ['harga/m3', 'harga per m3', 'harga_m3', 'price_m3'],
                'harga_ton': ['harga/ton', 'harga per ton', 'harga_ton', 'price_ton'],
                'harga_coll': ['harga/col', 'harga per coll', 'harga_coll', 'price_coll', 'harga/colli'],
                'harga': ['harga', 'price']  # Generic price field as fallback
            }
            
            # Improved column finding algorithm - find exact matches first, then partial matches
            found_columns = {}
            used_columns = set()  # Track which Excel columns are already used
            
            # First pass: Look for exact matches (highest priority)
            for field, possible_names in column_mapping.items():
                best_match = None
                best_score = 0
                
                for col in df.columns:
                    if col in used_columns:
                        continue
                        
                    col_lower = col.lower().strip()
                    
                    # Calculate match score
                    for possible_name in possible_names:
                        if col_lower == possible_name:  # Exact match
                            best_match = col
                            best_score = 100
                            break
                        elif possible_name in col_lower:  # Partial match
                            # Prefer shorter matches and those that start with the pattern
                            score = len(possible_name) / len(col_lower) * 50
                            if col_lower.startswith(possible_name):
                                score += 25
                            if score > best_score:
                                best_match = col
                                best_score = score
                
                if best_match and best_score >= 25:  # Minimum threshold for acceptance
                    found_columns[field] = best_match
                    used_columns.add(best_match)
                    print(f"🎯 Mapped '{field}' to '{best_match}' (score: {best_score})")
            
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

                print(f"Previewing row: {row.name}")
                print(f"Customer: {customer}, Nama Barang: {nama_barang}")
                print(f"Jenis Barang: {jenis_barang}, Panjang: {panjang}, Lebar: {lebar}, Tinggi: {tinggi}")
                print(f"Volume (m3): {m3}, Tonase: {ton}, Colli: {colli}")
                print(f"Harga/m3: {harga_m3}, Harga/Ton: {harga_ton}, Harga/Colli: {harga_coll}")

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
    
    def validate_excel_row(self, row_data, column_mapping, existing_customers, row_index):
        """Validate single row from Excel data"""
        errors = []
        
        try:
            # 1. Validasi Customer
            customer_name = str(row_data.get(column_mapping.get('customer', ''), '')).strip()
            if not customer_name:
                errors.append("Customer tidak boleh kosong")
            elif customer_name.upper() not in existing_customers:
                errors.append(f"Customer '{customer_name}' tidak ditemukan di database")
            
            # 2. Validasi Nama Barang
            nama_barang = str(row_data.get(column_mapping.get('nama_barang', ''), '')).strip()
            if not nama_barang:
                errors.append("Nama Barang tidak boleh kosong")
            
            # 3. Validasi Dimensi (jika ada)
            for field in ['panjang', 'lebar', 'tinggi']:
                if field in column_mapping:
                    value = row_data.get(column_mapping[field])
                    if pd.notna(value) and value != '':
                        try:
                            float_val = float(str(value).replace(',', ''))
                            if float_val <= 0:
                                errors.append(f"{field.title()} harus lebih besar dari 0")
                        except (ValueError, TypeError):
                            errors.append(f"Format {field} tidak valid: '{value}'")
            
            # 4. Validasi Volume, Berat, Colli
            for field, field_name in [('m3', 'Volume'), ('ton', 'Berat'), ('colli', 'Colli')]:
                if field in column_mapping:
                    value = row_data.get(column_mapping[field])
                    if pd.notna(value) and value != '':
                        try:
                            if field == 'colli':
                                int_val = int(float(str(value)))
                                if int_val <= 0:
                                    errors.append(f"{field_name} harus lebih besar dari 0")
                            else:
                                float_val = float(str(value).replace(',', ''))
                                if float_val <= 0:
                                    errors.append(f"{field_name} harus lebih besar dari 0")
                        except (ValueError, TypeError):
                            errors.append(f"Format {field_name} tidak valid: '{value}'")
            
            # 5. Validasi Harga (minimal salah satu harus ada)
            harga_fields = ['harga_m3', 'harga_ton', 'harga_coll']
            has_price = False
            
            for field in harga_fields:
                if field in column_mapping:
                    value = row_data.get(column_mapping[field])
                    if pd.notna(value) and str(value).strip():
                        try:
                            price = float(str(value).replace(',', ''))
                            if price > 0:
                                has_price = True
                            else:
                                errors.append(f"Harga {field.replace('harga_', '')} harus lebih besar dari 0")
                        except (ValueError, TypeError):
                            errors.append(f"Format harga {field.replace('harga_', '')} tidak valid: '{value}'")
            
            if not has_price:
                errors.append("Minimal salah satu harga (m³/ton/colli) harus diisi")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'customer_name': customer_name,
                'nama_barang': nama_barang
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validasi: {str(e)}"],
                'customer_name': '',
                'nama_barang': ''
            }

    def upload_excel_data(self):
        """Upload Excel data with validation"""
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
            
            validation_errors = []
            customer_not_found_list = []
            valid_data_for_upload = []
            
            for idx, (_, row) in enumerate(valid_rows.iterrows()):
                validation_result = self.validate_excel_row(
                    row, column_mapping, existing_customers, idx + 2
                )
                
                if validation_result['valid']:
                    valid_data_for_upload.append((idx, row))
                else:
                    # Pisahkan error berdasarkan jenis
                    customer_errors = [e for e in validation_result['errors'] if 'tidak ditemukan' in e]
                    other_errors = [e for e in validation_result['errors'] if 'tidak ditemukan' not in e]
                    
                    if customer_errors:
                        customer_not_found_list.append({
                            'nama_barang': validation_result['nama_barang'],
                            'customer': validation_result['customer_name'],
                            'row_number': idx + 2
                        })
                    
                    if other_errors:
                        validation_errors.append({
                            'nama_barang': validation_result['nama_barang'],
                            'customer': validation_result['customer_name'],
                            'error': '; '.join(other_errors),
                            'row_number': idx + 2
                        })
            
            # Jika ada error validasi, tampilkan dan stop
            if validation_errors or customer_not_found_list:
                error_msg = f"Ditemukan {len(validation_errors + customer_not_found_list)} error validasi!\n\n"
                error_msg += "Perbaiki error berikut sebelum upload:\n"
                
                if not messagebox.askyesno(
                    "Error Validasi", 
                    error_msg + "Lanjutkan untuk melihat detail error?"
                ):
                    return
                
                # Tampilkan detail error
                self.show_error_details(
                    validation_errors, 
                    customer_not_found_list, 
                    0,  # success_count = 0 karena belum upload
                    len(valid_rows)
                )
                return
            
            # Confirm upload jika semua data valid
            if not messagebox.askyesno(
                "Konfirmasi Upload", 
                f"Semua data valid!\n\nUpload {len(valid_data_for_upload)} barang ke database?"
            ):
                return
            
            # ✅ UPLOAD DATA YANG SUDAH TERVALIDASI
            success_count = 0
            upload_errors = []  # Error saat proses database
            
            for idx, (original_idx, row) in enumerate(valid_data_for_upload):
                try:
                    customer_name = str(row[column_mapping['customer']]).strip()
                    customer_id = existing_customers[customer_name.upper()]
                    nama_barang = str(row[column_mapping['nama_barang']]).strip()
                    
                    # ✅ Extract semua field data seperti kode asli
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
                    harga_m3 = get_safe_value('harga_m3', 'float')
                    harga_ton = get_safe_value('harga_ton', 'float')
                    harga_coll = get_safe_value('harga_coll', 'float')

                    print(f"Processing row {original_idx + 1}: {nama_barang} - Customer: {customer_name}")
                    print(f"  Jenis: {jenis_barang}, Panjang: {panjang}, Lebar: {lebar}, Tinggi: {tinggi}")
                    print(f"  M3: {m3}, Ton: {ton}, Colli: {colli}")
                    print(f"  Harga/m3: {harga_m3}, Harga/Ton: {harga_ton}, Harga/Colli: {harga_coll}")
                    
                    # ✅ Create barang dengan parameter lengkap
                    barang_id = self.db.create_barang(
                        customer_id=customer_id,
                        nama_barang=nama_barang,
                        jenis_barang=jenis_barang,
                        panjang_barang=panjang,
                        lebar_barang=lebar,
                        tinggi_barang=tinggi,
                        m3_barang=m3,
                        ton_barang=ton,
                        col_barang=colli,
                        harga_m3=harga_m3,
                        harga_ton=harga_ton,
                        harga_col=harga_coll
                    )
                    
                    success_count += 1
                    print(f"✅ Barang created successfully with ID: {barang_id}")
                    
                except Exception as e:
                    error_detail = str(e)
                    print(f"💥 Error creating barang '{nama_barang}': {error_detail}")
                    
                    upload_errors.append({
                        'nama_barang': nama_barang,
                        'customer': customer_name,
                        'error': f"Database error: {error_detail}",
                        'row_number': original_idx + 2
                    })
            
            # Show results
            if upload_errors:
                self.show_error_details(upload_errors, [], success_count, len(valid_data_for_upload))
            else:
                messagebox.showinfo(
                    "Upload Berhasil! 🎉", 
                    f"Semua data berhasil diupload!\n\n" +
                    f"✅ Total berhasil: {success_count} barang"
                )
            
            # Refresh dan cleanup
            self.load_barang()
            if self.refresh_callback:
                self.refresh_callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal upload data:\n{str(e)}")
    
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
        
        if not self.validated_barang():
            return 
        
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
            
            barang_id = self.db.create_barang(
                customer_id=customer_id,
                nama_barang=nama_barang,
                jenis_barang=jenis_barang,
                panjang_barang=panjang,
                lebar_barang=lebar,
                tinggi_barang=tinggi,
                m3_barang=m3,
                ton_barang=ton,
                col_barang=col,
                harga_m3=harga_m3,
                harga_ton=harga_ton,
                harga_col=harga_coll,
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
    
    def validated_barang(self):
            # Validate input fields for barang
            if not self.customer_var.get():
                messagebox.showwarning("Peringatan", "Pilih Customer terlebih dahulu.")
                return False
            if not self.jenis_barang_entry.get():
                messagebox.showwarning("Peringatan", "Jenis Barang tidak boleh kosong.")
                return False
            if not self.barang_entry.get():
                messagebox.showwarning("Peringatan", "Nama Barang tidak boleh kosong.")
                return False
            if not self.panjang_entry.get() or not self.lebar_entry.get() or not self.tinggi_entry.get():
                messagebox.showwarning("Peringatan", "Dimensi Barang tidak boleh kosong.")
                return False
            if not self.m3_entry.get() or not self.ton_entry.get() or not self.col_entry.get():
                messagebox.showwarning("Peringatan", "Volume dan Berat Barang tidak boleh kosong.")
                return False
            
            harga_m3 = self.harga_m3_entry.get().strip()
            harga_ton = self.harga_ton_entry.get().strip()
            harga_col = self.harga_coll_entry.get().strip()
            
            if not harga_m3 and not harga_ton and not harga_col:
                messagebox.showwarning(
                    "Peringatan", 
                    "Minimal salah satu metode pricing harus diisi!\n\n" +
                    "💰 Pilihan pricing:\n" +
                    "• Harga per m³ (untuk volume)\n" +
                    "• Harga per ton (untuk berat)\n" +
                    "• Harga per colli (untuk jumlah kemasan)"
                )
                self.harga_m3_entry.focus()
                return False
            return True
    
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
            self.original_barang_data = barang_list  # Store original data for filtering
            print(f"📊 Found {len(barang_list)} barang in database")
            
            for barang in barang_list:
                # Format dimensions
                dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
                
                # Format currency
                harga_m3 = f"Rp {barang.get('harga_m3', 0):,.0f}" if barang.get('harga_m3') else '-'
                harga_ton = f"Rp {barang.get('harga_ton', 0):,.0f}" if barang.get('harga_ton') else '-'
                harga_col = f"Rp {barang.get('harga_col', 0):,.0f}" if barang.get('harga_col') else '-'

                # Format date
                created_date = barang.get('created_at', '')[:10] if barang.get('created_at') else '-'
                
                self.tree.insert('', tk.END, values=(
                    barang['barang_id'],
                    barang['nama_customer'],
                    barang['nama_barang'],
                    barang['jenis_barang'],
                    dimensi,
                    barang.get('m3_barang', '-'),
                    barang.get('ton_barang', '-'),
                    barang.get('col_barang', '-'),
                    harga_m3,
                    harga_ton,
                    harga_col,
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