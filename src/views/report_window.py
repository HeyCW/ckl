import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.utils.helpers import setup_window_restore_behavior

class ReportsWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_window()
    
    def create_window(self):
        """Create reports window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📋 Laporan Data")

        # Calculate responsive window size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Use 80% of screen width and 75% of screen height (better for 1366x768)
        window_width = min(int(screen_width * 0.80), 1200)
        window_height = min(int(screen_height * 0.75), 700)

        # Minimum size for usability
        window_width = max(window_width, 900)
        window_height = max(window_height, 500)

        self.window.geometry(f"{window_width}x{window_height}")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()

        # Setup window restore behavior (fix minimize/restore issue)
        setup_window_restore_behavior(self.window)

        # Store window size for center_window
        self.window_width = window_width
        self.window_height = window_height

        # Center window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.window,
            text="📋 LAPORAN SEMUA DATA",
            font=('Arial', 18, 'bold'),
            bg='#9b59b6',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Customer tab
        customer_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(customer_frame, text='👥 Customer')
        self.create_customer_report(customer_frame)
        
        # Barang tab
        barang_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(barang_frame, text='📦 Barang')
        self.create_barang_report(barang_frame)
        
        # Container tab
        container_frame = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(container_frame, text='🚢 Container')
        self.create_container_report(container_frame)
        
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
    
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width // 2) - (self.window_width // 2)
        y = parent_y + (parent_height // 2) - (self.window_height // 2)

        self.window.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
    
    def create_customer_report(self, parent):
        """Create customer report tab"""
        # Title
        tk.Label(parent, text="📊 LAPORAN CUSTOMER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        # Treeview
        tree_frame = tk.Frame(parent, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Nama', 'Alamat', 'Jumlah_Barang'), show='headings')
        
        tree.heading('ID', text='ID')
        tree.heading('Nama', text='Nama Customer')
        tree.heading('Alamat', text='Alamat')
        tree.heading('Jumlah_Barang', text='Jumlah Barang')
        
        tree.column('ID', width=50)
        tree.column('Nama', width=200)
        tree.column('Alamat', width=300)
        tree.column('Jumlah_Barang', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load data
        customers = self.db.get_all_customers()
        for customer in customers:
            barang_count = len(self.db.get_barang_by_customer(customer['customer_id']))
            tree.insert('', tk.END, values=(
                customer['customer_id'],
                customer['nama_customer'],
                customer['alamat_customer'] or '-',
                barang_count
            ))
    
    def create_barang_report(self, parent):
        """Create barang report tab"""
        # Title
        tk.Label(parent, text="📊 LAPORAN BARANG", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        # Treeview
        tree_frame = tk.Frame(parent, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Customer', 'Nama', 'Dimensi', 'Volume', 'Berat', 'Colli', 'Harga'), show='headings')
        
        tree.heading('ID', text='ID')
        tree.heading('Customer', text='Customer')
        tree.heading('Nama', text='Nama Barang')
        tree.heading('Dimensi', text='P×L×T (cm)')
        tree.heading('Volume', text='Volume (m³)')
        tree.heading('Berat', text='Berat (ton)')
        tree.heading('Colli', text='Colli')
        tree.heading('Harga', text='Harga (Rp)')
        
        tree.column('ID', width=40)
        tree.column('Customer', width=120)
        tree.column('Nama', width=150)
        tree.column('Dimensi', width=100)
        tree.column('Volume', width=80)
        tree.column('Berat', width=80)
        tree.column('Colli', width=60)
        tree.column('Harga', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load data
        barang_list = self.db.get_all_barang()
        for barang in barang_list:
            dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
            harga = f"Rp {barang.get('harga_satuan', 0):,.0f}" if barang.get('harga_satuan') else '-'
            
            tree.insert('', tk.END, values=(
                barang['barang_id'],
                barang['nama_customer'],
                barang['nama_barang'],
                dimensi,
                barang.get('m3_barang', '-'),
                barang.get('ton_barang', '-'),
                barang.get('col_barang', '-'),
                harga
            ))
    
    def create_container_report(self, parent):
        """Create container report tab"""
        # Title
        tk.Label(parent, text="📊 LAPORAN CONTAINER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        # Treeview
        tree_frame = tk.Frame(parent, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Feeder', 'Party', 'Container', 'Destination', 'ETD_Sub', 'CLS', 'Open', 'Full', 'Seal', 'Ref_JOA'), show='headings')
        
        tree.heading('ID', text='ID')
        tree.heading('Feeder', text='Feeder')
        tree.heading('Party', text='Party')
        tree.heading('Container', text='Container')
        tree.heading('Destination', text='Destination')
        tree.heading('ETD_Sub', text='ETD Sub')
        tree.heading('CLS', text='CLS')
        tree.heading('Open', text='Open')
        tree.heading('Full', text='Full')
        tree.heading('Seal', text='Seal')
        tree.heading('Ref_JOA', text='Ref JOA')
        
        tree.column('ID', width=40)
        tree.column('Feeder', width=100)
        tree.column('Party', width=80)
        tree.column('Container', width=100)
        tree.column('Destination', width=80)
        tree.column('ETD_Sub', width=80)
        tree.column('CLS', width=80)
        tree.column('Open', width=80)
        tree.column('Full', width=80)
        tree.column('Seal', width=80)
        tree.column('Ref_JOA', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load data
        containers = self.db.get_all_containers()
        for container in containers:
            tree.insert('', tk.END, values=(
                container['container_id'],
                container.get('feeder', '-'),
                container.get('party', '-'),
                container.get('container', '-'),
                container.get('destination', '-'),
                container.get('etd_sub', '-'),
                container.get('cls', '-'),
                container.get('open', '-'),
                container.get('full', '-'),
                container.get('seal', '-'),
                container.get('ref_joa', '-')
            ))