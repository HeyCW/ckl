import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase

class ContainerWindow:
    def __init__(self, parent, db, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.create_window()
    
    def create_window(self):
        """Create container management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("🚢 Data Container")
        self.window.geometry("1400x800")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.window,
            text="🚢 KELOLA DATA CONTAINER & BARANG",
            font=('Arial', 18, 'bold'),
            bg='#e67e22',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tab 1: Container Management
        container_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(container_frame, text='🚢 Container')
        self.create_container_tab(container_frame)
        
        # Tab 2: Container-Barang Management
        container_barang_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(container_barang_frame, text='📦 Barang dalam Container')
        self.create_container_barang_tab(container_barang_frame)
        
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
    
    def create_container_tab(self, parent):
        """Create container management tab"""
        # Form frame
        form_frame = tk.Frame(parent, bg='#ecf0f1')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Instructions
        instruction_label = tk.Label(
            form_frame,
            text="🚢 Tambah Container Baru",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        )
        instruction_label.pack(pady=(0, 20))
        
        # Row 1
        row1_frame = tk.Frame(form_frame, bg='#ecf0f1')
        row1_frame.pack(fill='x', pady=5)
        
        # Feeder
        tk.Label(row1_frame, text="Feeder:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.feeder_entry = tk.Entry(row1_frame, font=('Arial', 10), width=15)
        self.feeder_entry.pack(side='left', padx=(5, 20))
        
        # Party
        tk.Label(row1_frame, text="Party:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.party_entry = tk.Entry(row1_frame, font=('Arial', 10), width=15)
        self.party_entry.pack(side='left', padx=(5, 20))
        
        # Destination
        tk.Label(row1_frame, text="Destination:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.destination_entry = tk.Entry(row1_frame, font=('Arial', 10), width=15)
        self.destination_entry.pack(side='left', padx=5)
        
        # Row 2 - Dates
        row2_frame = tk.Frame(form_frame, bg='#ecf0f1')
        row2_frame.pack(fill='x', pady=10)
        
        # ETD Sub
        tk.Label(row2_frame, text="ETD Sub:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.etd_sub_entry = tk.Entry(row2_frame, font=('Arial', 10), width=12)
        self.etd_sub_entry.pack(side='left', padx=(5, 15))
        tk.Label(row2_frame, text="(YYYY-MM-DD)", font=('Arial', 8), fg='gray', bg='#ecf0f1').pack(side='left', padx=(0, 15))
        
        # CLS
        tk.Label(row2_frame, text="CLS:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.cls_entry = tk.Entry(row2_frame, font=('Arial', 10), width=12)
        self.cls_entry.pack(side='left', padx=(5, 15))
        tk.Label(row2_frame, text="(YYYY-MM-DD)", font=('Arial', 8), fg='gray', bg='#ecf0f1').pack(side='left')
        
        # Row 3 - More dates
        row3_frame = tk.Frame(form_frame, bg='#ecf0f1')
        row3_frame.pack(fill='x', pady=5)
        
        # Open
        tk.Label(row3_frame, text="Open:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.open_entry = tk.Entry(row3_frame, font=('Arial', 10), width=12)
        self.open_entry.pack(side='left', padx=(5, 15))
        tk.Label(row3_frame, text="(YYYY-MM-DD)", font=('Arial', 8), fg='gray', bg='#ecf0f1').pack(side='left', padx=(0, 15))
        
        # Full
        tk.Label(row3_frame, text="Full:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.full_entry = tk.Entry(row3_frame, font=('Arial', 10), width=12)
        self.full_entry.pack(side='left', padx=(5, 15))
        tk.Label(row3_frame, text="(YYYY-MM-DD)", font=('Arial', 8), fg='gray', bg='#ecf0f1').pack(side='left')
        
        # Row 4 - Container details
        row4_frame = tk.Frame(form_frame, bg='#ecf0f1')
        row4_frame.pack(fill='x', pady=10)
        
        # Container
        tk.Label(row4_frame, text="Container:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.container_entry = tk.Entry(row4_frame, font=('Arial', 10), width=15)
        self.container_entry.pack(side='left', padx=(5, 20))
        
        # Seal
        tk.Label(row4_frame, text="Seal:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.seal_entry = tk.Entry(row4_frame, font=('Arial', 10), width=15)
        self.seal_entry.pack(side='left', padx=(5, 20))
        
        # Ref JOA
        tk.Label(row4_frame, text="Ref JOA:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.ref_joa_entry = tk.Entry(row4_frame, font=('Arial', 10), width=15)
        self.ref_joa_entry.pack(side='left', padx=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=15)
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Tambah Container",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=10,
            command=self.add_container
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
        clear_btn.pack(side='left', padx=(0, 10))
        
        edit_btn = tk.Button(
            btn_frame,
            text="✏️ Edit Container",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            command=self.edit_container
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Hapus Container",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            command=self.delete_container
        )
        delete_btn.pack(side='left')
        
        # Container list
        list_frame = tk.Frame(parent, bg='#ecf0f1')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(list_frame, text="📋 DAFTAR CONTAINER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        # Treeview for container list
        tree_frame = tk.Frame(list_frame, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        container_tree_container = tk.Frame(tree_frame, bg='#ecf0f1')
        container_tree_container.pack(fill='both', expand=True)
        
        self.container_tree = ttk.Treeview(container_tree_container, 
                                         columns=('ID', 'Feeder', 'Party', 'Container', 'Destination', 'ETD_Sub', 'CLS', 'Items'), 
                                         show='headings', height=8)
        
        self.container_tree.heading('ID', text='ID')
        self.container_tree.heading('Feeder', text='Feeder')
        self.container_tree.heading('Party', text='Party')
        self.container_tree.heading('Container', text='Container')
        self.container_tree.heading('Destination', text='Destination')
        self.container_tree.heading('ETD_Sub', text='ETD Sub')
        self.container_tree.heading('CLS', text='CLS')
        self.container_tree.heading('Items', text='Jumlah Barang')
        
        self.container_tree.column('ID', width=40)
        self.container_tree.column('Feeder', width=120)
        self.container_tree.column('Party', width=100)
        self.container_tree.column('Container', width=120)
        self.container_tree.column('Destination', width=100)
        self.container_tree.column('ETD_Sub', width=80)
        self.container_tree.column('CLS', width=80)
        self.container_tree.column('Items', width=100)
        
        # Scrollbars
        container_v_scrollbar = ttk.Scrollbar(container_tree_container, orient='vertical', command=self.container_tree.yview)
        container_h_scrollbar = ttk.Scrollbar(container_tree_container, orient='horizontal', command=self.container_tree.xview)
        self.container_tree.configure(yscrollcommand=container_v_scrollbar.set, xscrollcommand=container_h_scrollbar.set)
        
        self.container_tree.grid(row=0, column=0, sticky='nsew')
        container_v_scrollbar.grid(row=0, column=1, sticky='ns')
        container_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        container_tree_container.grid_rowconfigure(0, weight=1)
        container_tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to view container details
        self.container_tree.bind('<Double-1>', self.view_container_details)
        
        # Load existing containers
        self.load_containers()
        
        # Focus on feeder entry
        self.feeder_entry.focus()
    
    def create_container_barang_tab(self, parent):
        """Create container-barang management tab"""
        # Container selection frame
        selection_frame = tk.Frame(parent, bg='#ecf0f1')
        selection_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(selection_frame, text="📦 Kelola Barang dalam Container", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 10))
        
        # Container selection
        container_select_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        container_select_frame.pack(fill='x', pady=10)
        
        tk.Label(container_select_frame, text="Pilih Container:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(side='left')
        self.selected_container_var = tk.StringVar()
        self.container_combo = ttk.Combobox(container_select_frame, textvariable=self.selected_container_var, 
                                          font=('Arial', 11), width=40, state='readonly')
        self.container_combo.pack(side='left', padx=(5, 20))
        
        # Load containers into combobox
        self.load_container_combo()
        
        # Bind container selection
        self.container_combo.bind('<<ComboboxSelected>>', self.on_container_select)
        
        # Search and Add frame
        search_add_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        search_add_frame.pack(fill='x', pady=15)
        
        # Customer search
        customer_frame = tk.Frame(search_add_frame, bg='#ecf0f1')
        customer_frame.pack(fill='x', pady=5)
        
        tk.Label(customer_frame, text="🔍 Pilih Customer:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(side='left')
        self.customer_search_var = tk.StringVar()
        self.customer_search_combo = ttk.Combobox(customer_frame, textvariable=self.customer_search_var,
                                                font=('Arial', 10), width=25)
        self.customer_search_combo.pack(side='left', padx=(5, 20))
        
        # Colli input
        tk.Label(customer_frame, text="Jumlah Colli:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(side='left')
        self.colli_var = tk.StringVar(value="1")
        self.colli_entry = tk.Entry(customer_frame, textvariable=self.colli_var, font=('Arial', 10), width=8)
        self.colli_entry.pack(side='left', padx=(5, 10))
        
        # Bind customer selection to load barang
        self.customer_search_combo.bind('<<ComboboxSelected>>', self.on_customer_select)
        self.customer_search_combo.bind('<KeyRelease>', self.filter_customers)
        
        # Load customers
        self.load_customers()
        
        # Actions frame
        actions_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        actions_frame.pack(fill='x', pady=10)
        
        # Add barang to container
        add_barang_btn = tk.Button(
            actions_frame,
            text="➕ Tambah Barang ke Container",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            command=self.add_selected_barang_to_container
        )
        add_barang_btn.pack(side='left', padx=(0, 10))
        
        # Remove barang from container
        remove_barang_btn = tk.Button(
            actions_frame,
            text="➖ Hapus Barang dari Container",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=8,
            command=self.remove_barang_from_container
        )
        remove_barang_btn.pack(side='left', padx=(0, 10))
        
        # View container summary
        summary_btn = tk.Button(
            actions_frame,
            text="📊 Lihat Summary Container",
            font=('Arial', 12, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=8,
            command=self.view_container_summary
        )
        summary_btn.pack(side='left')
        
        # Clear selection button
        clear_selection_btn = tk.Button(
            actions_frame,
            text="🗑️ Bersihkan Pilihan",
            font=('Arial', 12, 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8,
            command=self.clear_selection
        )
        clear_selection_btn.pack(side='right')
        
        # Content frame with two sections
        content_frame = tk.Frame(parent, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Left side - Available barang
        left_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="📋 Barang Tersedia", font=('Arial', 12, 'bold'), bg='#ffffff').pack(pady=10)
        
        # Available barang tree
        available_tree_container = tk.Frame(left_frame)
        available_tree_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.available_tree = ttk.Treeview(available_tree_container,
                                         columns=('ID', 'Customer', 'Nama', 'Dimensi', 'Volume', 'Berat'),
                                         show='headings', height=12)
        
        self.available_tree.heading('ID', text='ID')
        self.available_tree.heading('Customer', text='Customer')
        self.available_tree.heading('Nama', text='Nama Barang')
        self.available_tree.heading('Dimensi', text='P×L×T (cm)')
        self.available_tree.heading('Volume', text='Volume (m³)')
        self.available_tree.heading('Berat', text='Berat (ton)')
        
        self.available_tree.column('ID', width=40)
        self.available_tree.column('Customer', width=100)
        self.available_tree.column('Nama', width=150)
        self.available_tree.column('Dimensi', width=80)
        self.available_tree.column('Volume', width=70)
        self.available_tree.column('Berat', width=70)
        
        # Scrollbars for available tree
        available_v_scroll = ttk.Scrollbar(available_tree_container, orient='vertical', command=self.available_tree.yview)
        available_h_scroll = ttk.Scrollbar(available_tree_container, orient='horizontal', command=self.available_tree.xview)
        self.available_tree.configure(yscrollcommand=available_v_scroll.set, xscrollcommand=available_h_scroll.set)
        
        self.available_tree.grid(row=0, column=0, sticky='nsew')
        available_v_scroll.grid(row=0, column=1, sticky='ns')
        available_h_scroll.grid(row=1, column=0, sticky='ew')
        
        available_tree_container.grid_rowconfigure(0, weight=1)
        available_tree_container.grid_columnconfigure(0, weight=1)
        
        # Right side - Barang in selected container
        right_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.container_label = tk.Label(right_frame, text="📦 Barang dalam Container", font=('Arial', 12, 'bold'), bg='#ffffff')
        self.container_label.pack(pady=10)
        
        # Container barang tree
        container_tree_frame = tk.Frame(right_frame)
        container_tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.container_barang_tree = ttk.Treeview(container_tree_frame,
                                                columns=('Customer', 'Nama', 'Dimensi', 'Volume', 'Berat', 'Colli', 'Tanggal'),
                                                show='headings', height=12)
        
        self.container_barang_tree.heading('Customer', text='Customer')
        self.container_barang_tree.heading('Nama', text='Nama Barang')
        self.container_barang_tree.heading('Dimensi', text='P×L×T (cm)')
        self.container_barang_tree.heading('Volume', text='Volume (m³)')
        self.container_barang_tree.heading('Berat', text='Berat (ton)')
        self.container_barang_tree.heading('Colli', text='Colli')
        self.container_barang_tree.heading('Tanggal', text='Ditambahkan')
        
        self.container_barang_tree.column('Customer', width=90)
        self.container_barang_tree.column('Nama', width=120)
        self.container_barang_tree.column('Dimensi', width=80)
        self.container_barang_tree.column('Volume', width=60)
        self.container_barang_tree.column('Berat', width=60)
        self.container_barang_tree.column('Colli', width=50)
        self.container_barang_tree.column('Tanggal', width=80)
        
        # Scrollbars for container barang tree
        container_barang_v_scroll = ttk.Scrollbar(container_tree_frame, orient='vertical', command=self.container_barang_tree.yview)
        container_barang_h_scroll = ttk.Scrollbar(container_tree_frame, orient='horizontal', command=self.container_barang_tree.xview)
        self.container_barang_tree.configure(yscrollcommand=container_barang_v_scroll.set, xscrollcommand=container_barang_h_scroll.set)
        
        self.container_barang_tree.grid(row=0, column=0, sticky='nsew')
        container_barang_v_scroll.grid(row=0, column=1, sticky='ns')
        container_barang_h_scroll.grid(row=1, column=0, sticky='ew')
        
        container_tree_frame.grid_rowconfigure(0, weight=1)
        container_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial data
        self.load_available_barang()
    
    def load_customers(self):
        """Load all customers for search dropdown"""
        try:
            # Get unique customers from barang table
            customers = self.db.execute("SELECT DISTINCT c.nama_customer FROM barang b JOIN customers c ON b.customer_id = c.customer_id ORDER BY c.nama_customer")
            customer_list = [row[0] for row in customers if row[0]]
            self.customer_search_combo['values'] = customer_list
        except Exception as e:
            print(f"Error loading customers: {e}")
    
    def filter_customers(self, event=None):
        """Filter customers based on typing"""
        try:
            typed = self.customer_search_var.get().lower()
            if not typed:
                # Show all customers if nothing typed
                customers = self.db.execute("SELECT DISTINCT c.nama_customer FROM barang b JOIN customers c ON b.customer_id = c.customer_id ORDER BY c.nama_customer")
                customer_list = [row[0] for row in customers if row[0]]
            else:
                # Filter customers containing the typed text
                customers = self.db.execute(
                    "SELECT DISTINCT c.nama_customer FROM barang b JOIN customers c ON b.customer_id = c.customer_id WHERE LOWER(c.nama_customer) LIKE ? ORDER BY c.nama_customer",
                    (f"%{typed}%",)
                )
                customer_list = [row[0] for row in customers if row[0]]
            
            self.customer_search_combo['values'] = customer_list
        except Exception as e:
            print(f"Error filtering customers: {e}")
    
    def on_customer_select(self, event=None):
        """Handle customer selection to load their barang"""
        customer = self.customer_search_var.get()
        print(f"Customer selected: '{customer}'") 
        if customer:
            # Filter treeview to show only this customer's barang
            self.load_customer_barang_tree(customer)
        else:
            # Reset tabel ke semua barang hanya jika customer dikosongkan
            self.load_available_barang()

    def load_customer_barang_tree(self, customer_name):
        """Load barang for specific customer in the left tree"""
        try:
            # Clear existing items
            for item in self.available_tree.get_children():
                self.available_tree.delete(item)
            
            # Get all barang first
            all_barang = self.db.get_all_barang()
            
            # Show only this customer's available barang
            customer_barang_count = 0
            for barang in all_barang:
                try:
                    # Safe way to get values from sqlite3.Row object
                    def safe_get(row, key, default='-'):
                        try:
                            return row[key] if row[key] is not None else default
                        except (KeyError, IndexError):
                            return default
                    
                    barang_id = safe_get(barang, 'barang_id', 0)
                    nama_customer = safe_get(barang, 'nama_customer', '')

                    print(f"Nama Customer: {nama_customer}")
                        
                    # Show only barang from selected customer
                    if nama_customer == customer_name:
                        # Format dimensions
                        panjang = safe_get(barang, 'panjang_barang', '-')
                        lebar = safe_get(barang, 'lebar_barang', '-')
                        tinggi = safe_get(barang, 'tinggi_barang', '-')
                        dimensi = f"{panjang}×{lebar}×{tinggi}"
                        
                        # Get values safely
                        nama_barang = safe_get(barang, 'nama_barang', '-')
                        m3_barang = safe_get(barang, 'm3_barang', '-')
                        ton_barang = safe_get(barang, 'ton_barang', '-')
                        
                        self.available_tree.insert('', tk.END, values=(
                            barang_id,
                            nama_customer,
                            nama_barang,
                            dimensi,
                            m3_barang,
                            ton_barang
                        ))
                        customer_barang_count += 1
                        
                except Exception as row_error:
                    print(f"Error processing customer barang row: {row_error}")
                    continue
            
            print(f"✅ Loaded {customer_barang_count} available barang for customer '{customer_name}' in tree")
            
        except Exception as e:
            print(f"❌ Error loading customer barang tree: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to all barang
            self.load_available_barang()
            
    def load_available_barang(self):
        """Load available barang (not in any container)"""
        try:
            # Clear existing items
            for item in self.available_tree.get_children():
                self.available_tree.delete(item)
            
            # Get all barang
            all_barang = self.db.get_all_barang()
            
            
            # Show only available barang (not in any container)
            available_count = 0
            for barang in all_barang:
                try:
                    # Safe way to get values from sqlite3.Row object
                    def safe_get(row, key, default='-'):
                        try:
                            return row[key] if row[key] is not None else default
                        except (KeyError, IndexError):
                            return default
                    
                    barang_id = safe_get(barang, 'barang_id', 0)
                    
                    # Format dimensions
                    panjang = safe_get(barang, 'panjang_barang', '-')
                    lebar = safe_get(barang, 'lebar_barang', '-')
                    tinggi = safe_get(barang, 'tinggi_barang', '-')
                    dimensi = f"{panjang}×{lebar}×{tinggi}"
                    
                    # Get values safely
                    nama_customer = safe_get(barang, 'nama_customer', '-')
                    nama_barang = safe_get(barang, 'nama_barang', '-')
                    m3_barang = safe_get(barang, 'm3_barang', '-')
                    ton_barang = safe_get(barang, 'ton_barang', '-')
                    
                    self.available_tree.insert('', tk.END, values=(
                        barang_id,
                        nama_customer,
                        nama_barang,
                        dimensi,
                        m3_barang,
                        ton_barang
                    ))
                    available_count += 1
                        
                except Exception as row_error:
                    print(f"Error processing available barang row: {row_error}")
                    continue
            
            print(f"✅ Loaded {available_count} available barang in tree")
            
        except Exception as e:
            print(f"Error loading available barang: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal memuat daftar barang: {str(e)}")
            
    def clear_selection(self):
        """Clear customer and barang selection"""
        self.customer_search_var.set("")
        self.colli_var.set("1")
        self.load_available_barang()
    
    def add_selected_barang_to_container(self):
        """Add selected barang from treeview to container"""
        # Validate container selection
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        # Validate barang selection from treeview
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang dari daftar barang tersedia!")
            return
        
        # Validate colli
        try:
            colli_amount = int(self.colli_var.get())
            if colli_amount <= 0:
                messagebox.showwarning("Peringatan", "Jumlah colli harus lebih dari 0!")
                return
        except ValueError:
            messagebox.showwarning("Peringatan", "Jumlah colli harus berupa angka!")
            return
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            # Get selected barang from treeview
            selected_items = []
            for item in selection:
                values = self.available_tree.item(item)['values']
                barang_id = values[0]  # ID column
                barang_customer = values[1]  # Customer column
                barang_name = values[2]  # Nama barang column
                
                # If customer is selected, verify customer matches
                if self.customer_search_var.get() and barang_customer != self.customer_search_var.get():
                    messagebox.showwarning(
                        "Peringatan", 
                        f"Barang '{barang_name}' milik customer '{barang_customer}' " +
                        f"tidak sesuai dengan customer yang dipilih '{self.customer_search_var.get()}'!"
                    )
                    continue
                
                selected_items.append({
                    'id': barang_id,
                    'name': barang_name,
                    'customer': barang_customer
                })
            
            if not selected_items:
                messagebox.showwarning("Peringatan", "Tidak ada barang yang valid untuk ditambahkan!")
                return
            
            # Confirm addition
            if len(selected_items) == 1:
                item = selected_items[0]
                confirm_msg = f"Tambah barang ke container?\n\n" + \
                            f"Customer: {item['customer']}\n" + \
                            f"Barang: {item['name']}\n" + \
                            f"Jumlah Colli: {colli_amount}\n" + \
                            f"Container: {self.selected_container_var.get().split(' - ', 1)[1]}"
            else:
                confirm_msg = f"Tambah {len(selected_items)} barang ke container?\n\n" + \
                            f"Jumlah Colli per barang: {colli_amount}\n" + \
                            f"Container: {self.selected_container_var.get().split(' - ', 1)[1]}\n\n" + \
                            f"Barang yang akan ditambahkan:\n"
                
                for i, item in enumerate(selected_items[:5], 1):  # Show max 5 items
                    confirm_msg += f"{i}. {item['name']} ({item['customer']})\n"
                if len(selected_items) > 5:
                    confirm_msg += f"... dan {len(selected_items) - 5} barang lainnya"
            
            if not messagebox.askyesno("Konfirmasi", confirm_msg):
                return
            
            # Add barang to container
            success_count = 0
            error_count = 0
            
            for item in selected_items:
                try:
                    # Add barang to container with colli amount
                    success = self.db.assign_barang_to_container_with_colli(item['id'], container_id, colli_amount)
                    
                    if success:
                        success_count += 1
                        print(f"✅ Added barang {item['id']} ({item['name']}) to container {container_id}")
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error adding barang {item['id']} ({item['name']}): {e}")
            
            # Show result message
            result_msg = ""
            if success_count > 0:
                result_msg += f"✅ Berhasil menambahkan {success_count} barang ke container!\n"
            if error_count > 0:
                result_msg += f"❌ {error_count} barang gagal ditambahkan.\n"
            
            if success_count > 0:
                result_msg += f"\nSetiap barang ditambahkan dengan {colli_amount} colli."
                messagebox.showinfo("Hasil", result_msg)
            else:
                messagebox.showerror("Error", result_msg)
            
            # Clear selections and refresh displays only if there were successful additions
            if success_count > 0:
                self.clear_selection()
                
                # Refresh displays based on current customer filter
                if self.customer_search_var.get():
                    self.load_customer_barang_tree(self.customer_search_var.get())
                else:
                    self.load_available_barang()
                    
                self.load_container_barang(container_id)
                self.load_containers()  # Refresh container list to update item count
                self.load_customers()   # Refresh customer list
            
        except ValueError as ve:
            messagebox.showerror("Error", f"Format data tidak valid: {str(ve)}")
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Error in add_selected_barang_to_container: {error_detail}")
            messagebox.showerror("Error", f"Gagal menambah barang ke container: {str(e)}")
            
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (1400 // 2)
        y = parent_y + (parent_height // 2) - (800 // 2)
        
        self.window.geometry(f"1400x800+{x}+{y}")
    
    def load_container_combo(self):
        """Load containers into combobox"""
        try:
            containers = self.db.get_all_containers()
            container_list = []
            for c in containers:
                container_text = f"{c['container_id']} - {c.get('container', 'No Container')} ({c.get('destination', 'No Dest')})"
                container_list.append(container_text)
            
            self.container_combo['values'] = container_list
        except Exception as e:
            print(f"Error loading container combo: {e}")
    
    def on_container_select(self, event=None):
        """Handle container selection"""
        selection = self.selected_container_var.get()
        if selection:
            container_id = int(selection.split(' - ')[0])
            self.load_container_barang(container_id)
            
            # Update label
            container_info = selection.split(' - ', 1)[1] if ' - ' in selection else selection
            self.container_label.config(text=f"📦 Barang dalam Container: {container_info}")
    
    def load_available_barang(self):
        """Load available barang (not in any container)"""
        try:
            # Clear existing items
            for item in self.available_tree.get_children():
                self.available_tree.delete(item)
            
            # Get all barang
            all_barang = self.db.get_all_barang()
            
            # Show only available barang
            for barang in all_barang:
                    # Format dimensions
                    dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
                    
                    self.available_tree.insert('', tk.END, values=(
                        barang['barang_id'],
                        barang['nama_customer'],
                        barang['nama_barang'],
                        dimensi,
                        barang.get('m3_barang', '-'),
                        barang.get('ton_barang', '-')
                    ))
        except Exception as e:
            print(f"Error loading available barang: {e}")
            messagebox.showerror("Error", f"Gagal memuat daftar barang: {str(e)}")
    
    def load_container_barang(self, container_id):
        """Load barang in specific container"""
        try:
            # Clear existing items
            for item in self.container_barang_tree.get_children():
                self.container_barang_tree.delete(item)
            
            # Load barang in container
            container_barang = self.db.get_barang_in_container_with_colli(container_id)
            
            for barang in container_barang:
                try:
                    # Safe way to get values from sqlite3.Row object
                    def safe_get(row, key, default='-'):
                        try:
                            return row[key] if row[key] is not None else default
                        except (KeyError, IndexError):
                            return default
                    
                    # Format dimensions
                    panjang = safe_get(barang, 'panjang_barang', '-')
                    lebar = safe_get(barang, 'lebar_barang', '-')
                    tinggi = safe_get(barang, 'tinggi_barang', '-')
                    dimensi = f"{panjang}×{lebar}×{tinggi}"
                    
                    assigned_at = safe_get(barang, 'assigned_at', '')
                    
                    # Get values safely
                    barang_id = safe_get(barang, 'barang_id', 0)
                    nama_customer = safe_get(barang, 'nama_customer', '-')
                    nama_barang = safe_get(barang, 'nama_barang', '-')
                    m3_barang = safe_get(barang, 'm3_barang', '-')
                    ton_barang = safe_get(barang, 'ton_barang', '-')
                    colli_amount = safe_get(barang, 'colli_amount', 1)

                    print(f"Debug - Processed date: '{assigned_at}' for barang {barang_id}")  # Debug

                    self.container_barang_tree.insert('', tk.END, values=(
                        nama_customer,
                        nama_barang,
                        dimensi,
                        m3_barang,
                        ton_barang,
                        colli_amount,
                        assigned_at
                    ))
                    
                except Exception as row_error:
                    print(f"Error processing barang row: {row_error}")
                    print(f"Barang data: {dict(barang) if hasattr(barang, 'keys') else barang}")
                    continue
                    
        except Exception as e:
            print(f"Error loading container barang: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal memuat barang dalam container: {str(e)}")
            
                
    def remove_barang_from_container(self):
        """Remove selected barang from container"""
        # Check if container is selected
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        # Check if barang is selected
        selection = self.container_barang_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang yang akan dihapus dari container!")
            return
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            # Get selected barang details for confirmation
            selected_items = []
            for item in selection:
                values = self.container_barang_tree.item(item)['values']
                barang_id = values[0]
                nama_barang = values[2]  # Nama barang column
                customer = values[1]     # Customer column
                colli = values[6]        # Colli column
                selected_items.append({
                    'id': barang_id,
                    'nama': nama_barang,
                    'customer': customer,
                    'colli': colli
                })
            
            # Confirm removal with details
            if len(selected_items) == 1:
                item = selected_items[0]
                confirm_msg = f"Hapus barang dari container?\n\n" + \
                            f"Barang: {item['nama']}\n" + \
                            f"Customer: {item['customer']}\n" + \
                            f"Colli: {item['colli']}\n\n" + \
                            f"Barang akan dikembalikan ke daftar barang tersedia."
            else:
                confirm_msg = f"Hapus {len(selected_items)} barang dari container?\n\n"
                for i, item in enumerate(selected_items[:3], 1):  # Show max 3 items
                    confirm_msg += f"{i}. {item['nama']} ({item['customer']}) - {item['colli']} colli\n"
                if len(selected_items) > 3:
                    confirm_msg += f"... dan {len(selected_items) - 3} barang lainnya\n"
                confirm_msg += f"\nSemua barang akan dikembalikan ke daftar barang tersedia."
            
            if not messagebox.askyesno("Konfirmasi Hapus", confirm_msg):
                return
            
            # Remove barang from container
            success_count = 0
            error_count = 0
            
            for item in selected_items:
                try:
                    # Remove from detail_container table
                    result = self.db.execute(
                        "DELETE FROM detail_container WHERE barang_id = ? AND container_id = ?", 
                        (item['id'], container_id)
                    )
                    success_count += 1
                    print(f"✅ Removed barang {item['id']} from container {container_id}")
                    
                except Exception as e:
                    error_count += 1
                    print(f"❌ Failed to remove barang {item['id']}: {e}")
            
            # Show result message
            if error_count == 0:
                messagebox.showinfo(
                    "Sukses", 
                    f"✅ {success_count} barang berhasil dihapus dari container!\n\n" +
                    f"Barang telah dikembalikan ke daftar barang tersedia."
                )
            else:
                messagebox.showwarning(
                    "Sebagian Berhasil",
                    f"✅ Berhasil: {success_count} barang\n" +
                    f"❌ Gagal: {error_count} barang\n\n" +
                    f"Periksa log untuk detail error."
                )
            
            # Refresh displays
            self.load_available_barang()           # Refresh available barang (will show removed items)
            self.load_container_barang(container_id)  # Refresh container barang list
            self.load_containers()                 # Refresh container list to update item count
            self.load_container_combo()            # Refresh container combo
            self.load_customers()                  # Refresh customer list
            
            # Call refresh callback if provided
            if self.refresh_callback:
                self.refresh_callback()
            
            print(f"🔄 Displays refreshed after removing {success_count} barang from container {container_id}")
            
        except ValueError as ve:
            messagebox.showerror("Error", f"Format container ID tidak valid: {str(ve)}")
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Error in remove_barang_from_container: {error_detail}")
            messagebox.showerror("Error", f"Gagal menghapus barang dari container!\n\nError: {str(e)}")
    
    def view_container_summary(self):
        """View detailed summary of selected container"""
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            # Get container details
            container = self.db.get_container_by_id(container_id)
            if not container:
                messagebox.showerror("Error", "Container tidak ditemukan!")
                return
            
            # Get barang in container with colli
            container_barang = self.db.get_barang_in_container_with_colli(container_id)
            
            # Safe way to get values from sqlite3.Row object
            def safe_get(row, key, default=0):
                try:
                    value = row[key]
                    return value if value is not None else default
                except (KeyError, IndexError):
                    return default
            
            # Calculate totals
            total_volume = 0
            total_weight = 0
            total_colli = 0
            
            for b in container_barang:
                try:
                    m3_value = safe_get(b, 'm3_barang', 0)
                    total_volume += float(m3_value) if m3_value not in [None, '', '-'] else 0
                    
                    ton_value = safe_get(b, 'ton_barang', 0)
                    total_weight += float(ton_value) if ton_value not in [None, '', '-'] else 0
                    
                    colli_value = safe_get(b, 'colli_amount', 0)
                    total_colli += int(colli_value) if colli_value not in [None, '', '-'] else 0
                except (ValueError, TypeError) as ve:
                    print(f"Error calculating totals for barang: {ve}")
                    continue
            
            # Group by customer
            customer_summary = {}
            for barang in container_barang:
                try:
                    customer = safe_get(barang, 'nama_customer', 'Unknown Customer')
                    
                    if customer not in customer_summary:
                        customer_summary[customer] = {
                            'count': 0,
                            'volume': 0,
                            'weight': 0,
                            'colli': 0
                        }
                    
                    customer_summary[customer]['count'] += 1
                    
                    # Safe calculation for customer summary
                    try:
                        m3_value = safe_get(barang, 'm3_barang', 0)
                        customer_summary[customer]['volume'] += float(m3_value) if m3_value not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        ton_value = safe_get(barang, 'ton_barang', 0)
                        customer_summary[customer]['weight'] += float(ton_value) if ton_value not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        colli_value = safe_get(barang, 'colli_amount', 0)
                        customer_summary[customer]['colli'] += int(colli_value) if colli_value not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                        
                except Exception as customer_error:
                    print(f"Error processing customer summary for barang: {customer_error}")
                    continue
            
            self.show_container_summary_dialog(container, container_barang, customer_summary, 
                                            total_volume, total_weight, total_colli)
            
        except Exception as e:
            print(f"Error in view_container_summary: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal membuat summary container: {str(e)}")

    def show_container_summary_dialog(self, container, barang_list, customer_summary, total_volume, total_weight, total_colli):
        """Show container summary in a dialog"""
        try:
            summary_window = tk.Toplevel(self.window)
            summary_window.title(f"📊 Summary Container - {container.get('container', 'N/A') if hasattr(container, 'get') else container['container'] if 'container' in container else 'N/A'}")
            summary_window.geometry("900x700")
            summary_window.configure(bg='#ecf0f1')
            summary_window.transient(self.window)
            summary_window.grab_set()
            
            # Center window
            summary_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (900 // 2)
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (700 // 2)
            summary_window.geometry(f"900x700+{x}+{y}")
            
            # Safe way to get container values
            def safe_container_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return container.get(key, default)
                    else:
                        return container[key] if key in container else default
                except:
                    return default
            
            container_name = safe_container_get('container', 'N/A')
            
            # Header
            header = tk.Label(
                summary_window,
                text=f"📊 SUMMARY CONTAINER: {container_name}",
                font=('Arial', 16, 'bold'),
                bg='#e67e22',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
            
            # Create notebook for summary tabs
            summary_notebook = ttk.Notebook(summary_window)
            summary_notebook.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Tab 1: Overview
            overview_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(overview_frame, text='📋 Overview')
            
            # Container info
            info_frame = tk.Frame(overview_frame, bg='#ffffff', relief='solid', bd=1)
            info_frame.pack(fill='x', padx=10, pady=10)
            
            tk.Label(info_frame, text="🚢 INFORMASI CONTAINER", font=('Arial', 14, 'bold'), bg='#ffffff').pack(pady=10)
            
            info_lines = [
                f"Container: {safe_container_get('container')}",
                f"Feeder: {safe_container_get('feeder')}",
                f"Destination: {safe_container_get('destination')}",
                f"Party: {safe_container_get('party')}",
                f"ETD Sub: {safe_container_get('etd_sub')}",
                f"CLS: {safe_container_get('cls')}",
                f"Open: {safe_container_get('open')}",
                f"Full: {safe_container_get('full')}",
                f"Seal: {safe_container_get('seal')}",
                f"Ref JOA: {safe_container_get('ref_joa')}"
            ]
            info_text = "\n".join(info_lines)
            
            tk.Label(info_frame, text=info_text.strip(), font=('Arial', 10), bg='#ffffff', justify='left').pack(padx=20, pady=10)
            
            # Summary stats
            stats_frame = tk.Frame(overview_frame, bg='#ffffff', relief='solid', bd=1)
            stats_frame.pack(fill='x', padx=10, pady=10)
            
            tk.Label(stats_frame, text="📊 STATISTIK MUATAN", font=('Arial', 14, 'bold'), bg='#ffffff').pack(pady=10)
            
            stats_lines = [
                f"Total Barang: {len(barang_list)} items",
                f"Total Volume: {total_volume:.3f} m³", 
                f"Total Berat: {total_weight:.3f} ton",
                f"Total Colli: {total_colli} kemasan",
                f"Jumlah Customer: {len(customer_summary)}"
            ]
            stats_text = "\n".join(stats_lines)
            
            tk.Label(stats_frame, text=stats_text.strip(), font=('Arial', 12, 'bold'), bg='#ffffff', justify='left').pack(padx=20, pady=10)
            
            # Tab 2: Customer Summary
            customer_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(customer_frame, text='👥 Per Customer')
            
            tk.Label(customer_frame, text="👥 RINGKASAN PER CUSTOMER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            # Customer summary tree
            customer_tree_container = tk.Frame(customer_frame, bg='#ecf0f1')
            customer_tree_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            customer_summary_tree = ttk.Treeview(customer_tree_container,
                                            columns=('Customer', 'Items', 'Volume', 'Weight', 'Colli'),
                                            show='headings', height=15)
            
            customer_summary_tree.heading('Customer', text='Customer')
            customer_summary_tree.heading('Items', text='Jumlah Barang')
            customer_summary_tree.heading('Volume', text='Volume (m³)')
            customer_summary_tree.heading('Weight', text='Berat (ton)')
            customer_summary_tree.heading('Colli', text='Total Colli')
            
            customer_summary_tree.column('Customer', width=200)
            customer_summary_tree.column('Items', width=120)
            customer_summary_tree.column('Volume', width=120)
            customer_summary_tree.column('Weight', width=120)
            customer_summary_tree.column('Colli', width=120)
            
            # Add customer data
            for customer, data in customer_summary.items():
                customer_summary_tree.insert('', tk.END, values=(
                    customer,
                    data['count'],
                    f"{data['volume']:.3f}",
                    f"{data['weight']:.3f}",
                    data['colli']
                ))
            
            # Scrollbar for customer tree
            customer_v_scroll = ttk.Scrollbar(customer_tree_container, orient='vertical', command=customer_summary_tree.yview)
            customer_summary_tree.configure(yscrollcommand=customer_v_scroll.set)
            
            customer_summary_tree.pack(side='left', fill='both', expand=True)
            customer_v_scroll.pack(side='right', fill='y')
            
            # Tab 3: Detailed Items (simplified for safety)
            items_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(items_frame, text='📦 Detail Barang')
            
            tk.Label(items_frame, text="📦 DETAIL SEMUA BARANG", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            # Items detail tree
            items_tree_container = tk.Frame(items_frame, bg='#ecf0f1')
            items_tree_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            items_detail_tree = ttk.Treeview(items_tree_container,
                                        columns=('ID', 'Customer', 'Nama', 'Jenis', 'Dimensi', 'Volume', 'Weight', 'Colli', 'Added'),
                                        show='headings', height=15)
            
            items_detail_tree.heading('ID', text='ID')
            items_detail_tree.heading('Customer', text='Customer')
            items_detail_tree.heading('Nama', text='Nama Barang')
            items_detail_tree.heading('Jenis', text='Jenis')
            items_detail_tree.heading('Dimensi', text='P×L×T (cm)')
            items_detail_tree.heading('Volume', text='Volume (m³)')
            items_detail_tree.heading('Weight', text='Berat (ton)')
            items_detail_tree.heading('Colli', text='Colli')
            items_detail_tree.heading('Added', text='Ditambahkan')
            
            items_detail_tree.column('ID', width=40)
            items_detail_tree.column('Customer', width=100)
            items_detail_tree.column('Nama', width=150)
            items_detail_tree.column('Jenis', width=100)
            items_detail_tree.column('Dimensi', width=80)
            items_detail_tree.column('Volume', width=80)
            items_detail_tree.column('Weight', width=80)
            items_detail_tree.column('Colli', width=60)
            items_detail_tree.column('Added', width=80)
            
            # Add items data with safe access
            def safe_barang_get(barang, key, default='-'):
                try:
                    value = barang[key]
                    return value if value is not None else default
                except (KeyError, IndexError):
                    return default
            
            # Add items data
            for barang in barang_list:
                try:
                    panjang = safe_barang_get(barang, 'panjang_barang', '-')
                    lebar = safe_barang_get(barang, 'lebar_barang', '-')
                    tinggi = safe_barang_get(barang, 'tinggi_barang', '-')
                    dimensi = f"{panjang}×{lebar}×{tinggi}"
                    
                    assigned_at = safe_barang_get(barang, 'assigned_at', '')
                    added_date = assigned_at[:10] if assigned_at and len(str(assigned_at)) >= 10 else '-'
                    
                    items_detail_tree.insert('', tk.END, values=(
                        safe_barang_get(barang, 'barang_id', '-'),
                        safe_barang_get(barang, 'nama_customer', '-'),
                        safe_barang_get(barang, 'nama_barang', '-'),
                        safe_barang_get(barang, 'jenis_barang', '-'),
                        dimensi,
                        safe_barang_get(barang, 'm3_barang', '-'),
                        safe_barang_get(barang, 'ton_barang', '-'),
                        safe_barang_get(barang, 'colli_amount', '-'),
                        added_date
                    ))
                except Exception as item_error:
                    print(f"Error adding item to detail tree: {item_error}")
                    continue
            
            # Scrollbars for items tree
            items_v_scroll = ttk.Scrollbar(items_tree_container, orient='vertical', command=items_detail_tree.yview)
            items_h_scroll = ttk.Scrollbar(items_tree_container, orient='horizontal', command=items_detail_tree.xview)
            items_detail_tree.configure(yscrollcommand=items_v_scroll.set, xscrollcommand=items_h_scroll.set)
            
            items_detail_tree.grid(row=0, column=0, sticky='nsew')
            items_v_scroll.grid(row=0, column=1, sticky='ns')
            items_h_scroll.grid(row=1, column=0, sticky='ew')
            
            items_tree_container.grid_rowconfigure(0, weight=1)
            items_tree_container.grid_columnconfigure(0, weight=1)
            
            # Close button
            close_btn = tk.Button(
                summary_window,
                text="✅ Tutup",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=30,
                pady=10,
                command=summary_window.destroy
            )
            close_btn.pack(pady=10)
            
        except Exception as dialog_error:
            print(f"Error creating summary dialog: {dialog_error}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal membuat dialog summary: {str(dialog_error)}")
            
    def view_container_details(self, event):
        """View container details on double-click"""
        selection = self.container_tree.selection()
        if selection:
            item = self.container_tree.item(selection[0])
            container_id = item['values'][0]
            
            # Switch to container-barang tab and select this container
            self.notebook.select(1)
            
            # Find and select the container in combo
            for i, value in enumerate(self.container_combo['values']):
                if value.startswith(str(container_id)):
                    self.container_combo.current(i)
                    self.on_container_select()
                    break
    
    def add_container(self):
        """Add new container"""
        try:
            # Check if we're editing an existing container
            if hasattr(self, 'editing_container_id'):
                # Update existing container
                container_id = self.editing_container_id
                self.db.execute("""
                    UPDATE containers SET 
                    feeder = ?, etd_sub = ?, party = ?, cls = ?, open = ?, full = ?,
                    destination = ?, container = ?, seal = ?, ref_joa = ?
                    WHERE container_id = ?
                """, (
                    self.feeder_entry.get().strip() or None,
                    self.etd_sub_entry.get().strip() or None,
                    self.party_entry.get().strip() or None,
                    self.cls_entry.get().strip() or None,
                    self.open_entry.get().strip() or None,
                    self.full_entry.get().strip() or None,
                    self.destination_entry.get().strip() or None,
                    self.container_entry.get().strip() or None,
                    self.seal_entry.get().strip() or None,
                    self.ref_joa_entry.get().strip() or None,
                    container_id
                ))
                messagebox.showinfo("Sukses", f"Container ID {container_id} berhasil diupdate!")
            else:
                # Create new container
                container_id = self.db.create_container(
                    feeder=self.feeder_entry.get().strip() or None,
                    etd_sub=self.etd_sub_entry.get().strip() or None,
                    party=self.party_entry.get().strip() or None,
                    cls=self.cls_entry.get().strip() or None,
                    open_date=self.open_entry.get().strip() or None,
                    full=self.full_entry.get().strip() or None,
                    destination=self.destination_entry.get().strip() or None,
                    container=self.container_entry.get().strip() or None,
                    seal=self.seal_entry.get().strip() or None,
                    ref_joa=self.ref_joa_entry.get().strip() or None
                )
                messagebox.showinfo("Sukses", f"Container berhasil ditambahkan dengan ID: {container_id}")
            
            self.clear_form()
            self.load_containers()
            self.load_container_combo()  # Refresh combo
            
            if self.refresh_callback:
                self.refresh_callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan container: {str(e)}")
    
    def edit_container(self):
        """Edit selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih container yang akan diedit!")
            return
        
        item = self.container_tree.item(selection[0])
        container_id = item['values'][0]
        
        # Get container data
        container = self.db.get_container_by_id(container_id)
        if not container:
            messagebox.showerror("Error", "Container tidak ditemukan!")
            return
        
        # Fill form with existing data
        self.feeder_entry.delete(0, tk.END)
        self.feeder_entry.insert(0, container.get('feeder', ''))
        
        self.etd_sub_entry.delete(0, tk.END)
        self.etd_sub_entry.insert(0, container.get('etd_sub', ''))
        
        self.party_entry.delete(0, tk.END)
        self.party_entry.insert(0, container.get('party', ''))
        
        self.cls_entry.delete(0, tk.END)
        self.cls_entry.insert(0, container.get('cls', ''))
        
        self.open_entry.delete(0, tk.END)
        self.open_entry.insert(0, container.get('open', ''))
        
        self.full_entry.delete(0, tk.END)
        self.full_entry.insert(0, container.get('full', ''))
        
        self.destination_entry.delete(0, tk.END)
        self.destination_entry.insert(0, container.get('destination', ''))
        
        self.container_entry.delete(0, tk.END)
        self.container_entry.insert(0, container.get('container', ''))
        
        self.seal_entry.delete(0, tk.END)
        self.seal_entry.insert(0, container.get('seal', ''))
        
        self.ref_joa_entry.delete(0, tk.END)
        self.ref_joa_entry.insert(0, container.get('ref_joa', ''))
        
        # Store container_id for update
        self.editing_container_id = container_id
        
        messagebox.showinfo("Info", f"Data container ID {container_id} dimuat. Edit data lalu klik 'Tambah Container' untuk menyimpan.")
    
    def delete_container(self):
        """Delete selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih container yang akan dihapus!")
            return
        
        item = self.container_tree.item(selection[0])
        container_id = item['values'][0]
        container_name = item['values'][3]  # Container column
        
        # Check if container has barang
        container_barang = self.db.get_barang_in_container(container_id)
        if container_barang:
            if not messagebox.askyesno(
                "Konfirmasi Hapus",
                f"Container '{container_name}' berisi {len(container_barang)} barang.\n\n" +
                "Menghapus container akan mengeluarkan semua barang dari container.\n" +
                "Yakin ingin melanjutkan?"
            ):
                return
        else:
            if not messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus container '{container_name}'?"):
                return
        
        try:
            # Remove all barang from container first
            self.db.execute("DELETE FROM detail_container WHERE container_id = ?", (container_id,))
            
            # Delete container
            self.db.execute("DELETE FROM containers WHERE container_id = ?", (container_id,))
            
            messagebox.showinfo("Sukses", f"Container '{container_name}' berhasil dihapus!")
            
            self.load_containers()
            self.load_container_combo()
            self.load_available_barang()  # Refresh available barang
            self.load_customers()  # Refresh customers
            
            if self.refresh_callback:
                self.refresh_callback()
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus container: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.feeder_entry.delete(0, tk.END)
        self.etd_sub_entry.delete(0, tk.END)
        self.party_entry.delete(0, tk.END)
        self.cls_entry.delete(0, tk.END)
        self.open_entry.delete(0, tk.END)
        self.full_entry.delete(0, tk.END)
        self.destination_entry.delete(0, tk.END)
        self.container_entry.delete(0, tk.END)
        self.seal_entry.delete(0, tk.END)
        self.ref_joa_entry.delete(0, tk.END)
        
        # Clear editing state
        if hasattr(self, 'editing_container_id'):
            delattr(self, 'editing_container_id')
        
        self.feeder_entry.focus()
    
    def load_containers(self):
        """Load containers into treeview with item count"""
        try:
            # Clear existing items
            for item in self.container_tree.get_children():
                self.container_tree.delete(item)
            
            # Load containers from database
            containers = self.db.get_all_containers()
            for container in containers:
                # Count barang in this container
                container_barang = self.db.get_barang_in_container(container['container_id'])
                item_count = len(container_barang)
                
                self.container_tree.insert('', tk.END, values=(
                    container['container_id'],
                    container.get('feeder', '-'),
                    container.get('party', '-'),
                    container.get('container', '-'),
                    container.get('destination', '-'),
                    container.get('etd_sub', '-'),
                    container.get('cls', '-'),
                    f"{item_count} items"  # Show item count
                ))
        except Exception as e:
            print(f"Error loading containers: {e}")
            messagebox.showerror("Error", f"Gagal memuat daftar container: {str(e)}")

if __name__ == "__main__":
    try:
        from src.models.database import AppDatabase
        
        # Create test database
        db = AppDatabase("test_container.db")
        
        # Create root window
        root = tk.Tk()
        root.title("Test Container Window")
        root.geometry("400x300")
        
        def open_container_window():
            ContainerWindow(root, db)
        
        # Test button
        test_btn = tk.Button(
            root,
            text="Open Container Window",
            font=('Arial', 14),
            command=open_container_window,
            padx=20,
            pady=10
        )
        test_btn.pack(expand=True)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()