
import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.utils.print_handler import PrintHandler
from datetime import datetime
import sqlite3

class ContainerWindow:
    def __init__(self, parent, db, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.print_handler = PrintHandler(db) 
        self.create_window()
        self.load_kapals()

    def load_kapals(self):
        """Load kapal options from the database"""
        try:
            kapals = self.db.execute("SELECT feeder FROM kapals")
            print(f"Loaded kapals: {kapals}")
            kapals = [k[0] for k in kapals]
            self.kapal_combo['values'] = kapals
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

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
        
        # Kapal (Dropdown)
        tk.Label(row1_frame, text="Kapal:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.kapal_var = tk.StringVar()
        self.kapal_combo = ttk.Combobox(
            row1_frame,
            textvariable=self.kapal_var,
            font=('Arial', 10),
            width=15,
        )
        
        self.kapal_combo.pack(side='left', padx=5)

        # Container
        tk.Label(row1_frame, text="Container:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.container_entry = tk.Entry(row1_frame, font=('Arial', 10), width=15)
        self.container_entry.pack(side='left', padx=(5, 20))
        
        # Seal
        tk.Label(row1_frame, text="Seal:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.seal_entry = tk.Entry(row1_frame, font=('Arial', 10), width=15)
        self.seal_entry.pack(side='left', padx=(5, 20))
        
        # Ref JOA
        tk.Label(row1_frame, text="Ref JOA:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.ref_joa_entry = tk.Entry(row1_frame, font=('Arial', 10), width=15)
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
            padx=10,
            pady=5,
            command=self.add_container
        )
        add_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Bersihkan",
            font=('Arial', 12, 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=10,
            pady=5,
            command=self.clear_form
        )
        clear_btn.pack(side='left', padx=(0, 10))
        
        edit_btn = tk.Button(
            btn_frame,
            text="✏️ Edit Container",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=10,
            pady=5,
            command=self.edit_container
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Hapus Container",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=10,
            pady=5,
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
                                         columns=('ID', 'Kapal', 'Container', 'Ref JOA','Items'), 
                                         show='headings', height=8)
        
        self.container_tree.heading('ID', text='ID')
        self.container_tree.heading('Kapal', text='Kapal')
        self.container_tree.heading('Container', text='Container')
        self.container_tree.heading('Ref JOA', text='Ref JOA')
        self.container_tree.heading('Items', text='Jumlah Barang')
        
        self.container_tree.column('ID', width=40)
        self.container_tree.column('Kapal', width=120)
        self.container_tree.column('Container', width=120)
        self.container_tree.column('Ref JOA', width=100)
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
        
        # ADD PRINT BUTTONS HERE
        self.add_print_buttons_to_container_tab(parent)
        
        
    def add_print_buttons_to_container_tab(self, parent):
        """Add print buttons to container tab"""
        print_frame = tk.Frame(parent, bg='#ecf0f1')
        print_frame.pack(fill='x', padx=20, pady=10)
        
        # Separator
        separator = tk.Frame(print_frame, height=2, bg='#34495e')
        separator.pack(fill='x', pady=(0, 10))
        
        tk.Label(print_frame, text="📄 PRINT DOCUMENTS", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 10))
        
        btn_frame = tk.Frame(print_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x')
        
        # Print Invoice Container button
        print_invoice_btn = tk.Button(
            btn_frame,
            text="🧾 Print Invoice Container",
            font=('Arial', 11, 'bold'),
            bg='#8e44ad',
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_container_invoice
        )
        print_invoice_btn.pack(side='left', padx=(0, 10))
        
        # Print Customer Packing List button
        print_packing_btn = tk.Button(
            btn_frame,
            text="📋 Print Customer Packing List",
            font=('Arial', 11, 'bold'),
            bg='#2980b9',
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_customer_packing_list
        )
        print_packing_btn.pack(side='left', padx=(0, 10))
    
    def print_selected_container_invoice(self):
        """Print invoice for selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih container yang akan diprint invoicenya!")
            return
        
        item = self.container_tree.item(selection[0])
        container_id = item['values'][0]
        container_name = item['values'][3]  # Container column
        
        # Confirm print
        if messagebox.askyesno("Konfirmasi Print", f"Print Invoice untuk Container '{container_name}'?"):
            self.print_handler.print_container_invoice(container_id)

    def print_selected_customer_packing_list(self):
        """Print customer packing list for selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih container yang akan diprint packing listnya!")
            return
        
        item = self.container_tree.item(selection[0])
        container_id = item['values'][0]
        container_name = item['values'][3]  # Container column
        
        # Show customer selection dialog
        self.print_handler.show_sender_receiver_selection_dialog(container_id)
    
    def create_container_barang_tab(self, parent):
        """Create container-barang management tab with pricing and sender/receiver selection"""
        # Container selection frame
        selection_frame = tk.Frame(parent, bg='#ecf0f1')
        selection_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(selection_frame, text="📦 Kelola Barang dalam Container", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 10))
        
        # Container selection
        container_select_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        container_select_frame.pack(fill='x', pady=10)
        
        # Search and Add frame (jadi grid 2 kolom)
        search_add_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        search_add_frame.pack(fill='x', pady=15)

        # === KIRI ===
        left_frame = tk.Frame(search_add_frame, bg='#ecf0f1')
        left_frame.grid(row=0, column=0, sticky='nw', padx=(10, 100))

        # Container selection
        container_select_frame = tk.Frame(left_frame, bg='#ecf0f1')
        container_select_frame.pack(fill='x', pady=5)

        tk.Label(container_select_frame, text="Pilih Container:").pack(side='left')
        self.selected_container_var = tk.StringVar()
        self.container_combo = ttk.Combobox(container_select_frame, 
                                            textvariable=self.selected_container_var, 
                                            width=40, state='readonly')
        self.container_combo.pack(side='left', padx=(5, 20))
        self.load_container_combo()
        self.container_combo.bind('<<ComboboxSelected>>', self.on_container_select)

        # Sender selection
        sender_frame = tk.Frame(left_frame, bg='#ecf0f1')
        sender_frame.pack(fill='x', pady=5)

        tk.Label(sender_frame, text="📤 Pilih Pengirim:").pack(side='left')
        self.sender_search_var = tk.StringVar()
        self.sender_search_combo = ttk.Combobox(sender_frame, 
                                                textvariable=self.sender_search_var, 
                                                width=25)
        self.sender_search_combo.pack(side='left', padx=(5, 20))

        # Receiver selection
        receiver_frame = tk.Frame(left_frame, bg='#ecf0f1')
        receiver_frame.pack(fill='x', pady=5)

        tk.Label(receiver_frame, text="📥 Pilih Penerima:").pack(side='left')
        self.receiver_search_var = tk.StringVar()
        self.receiver_search_combo = ttk.Combobox(receiver_frame, 
                                                textvariable=self.receiver_search_var,
                                                width=25)
        self.receiver_search_combo.pack(side='left', padx=(5, 20))

        # Colli input
        colli_frame = tk.Frame(left_frame, bg='#ecf0f1')
        colli_frame.pack(fill='x', pady=5)

        tk.Label(colli_frame, text="📦 Jumlah Colli:").pack(side='left')
        self.colli_var = tk.StringVar(value="1")
        self.colli_entry = tk.Entry(colli_frame, textvariable=self.colli_var, width=8)
        self.colli_entry.pack(side='left', padx=(5, 10))

        # === KANAN ===
        delivery_cost_frame = tk.Frame(search_add_frame, bg='#ecf0f1')
        delivery_cost_frame.grid(row=0, column=1, sticky='ne', padx=10)

        tk.Label(delivery_cost_frame, text="🚚 Biaya Pengantaran:", 
                font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#e67e22').pack(anchor='w', pady=(0, 5))

        # Row 1: Deskripsi biaya
        desc_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        desc_row.pack(fill='x', pady=2)
        tk.Label(desc_row, text="Deskripsi:").pack(side='left')
        self.delivery_desc_var = tk.StringVar()
        self.delivery_desc_entry = tk.Entry(desc_row, textvariable=self.delivery_desc_var, width=40)
        self.delivery_desc_entry.pack(side='left', padx=(5, 20))

        # Row 2: Biaya
        cost_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        cost_row.pack(fill='x', pady=2)
        tk.Label(cost_row, text="Biaya (Rp):").pack(side='left')
        self.delivery_cost_var = tk.StringVar(value="0")
        self.delivery_cost_entry = tk.Entry(cost_row, textvariable=self.delivery_cost_var, width=15)
        self.delivery_cost_entry.pack(side='left', padx=(5, 10))

        add_delivery_btn = tk.Button(cost_row, text="➕ Tambah Biaya", bg='#e67e22', fg='white',
                                    padx=15, pady=5, command=self.add_delivery_cost)
        add_delivery_btn.pack(side='left', padx=(10, 0))

        # Row 3: Lokasi
        destination_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        destination_row.pack(fill='x', pady=2)
        tk.Label(destination_row, text="Lokasi:").pack(side='left')

        self.delivery_destination_var = tk.StringVar()
        self.delivery_destination_combo = ttk.Combobox(destination_row, 
                                                    textvariable=self.delivery_destination_var,
                                                    width=37, state="readonly")
        self.delivery_destination_combo.pack(side='left', padx=(5, 20))
        
        
        self.load_customers()
        
        # Actions frame
        actions_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        actions_frame.pack(fill='x', pady=10)
        
        # Add barang to container with pricing
        add_barang_btn = tk.Button(
            actions_frame,
            text="💰 Tambah Barang + Harga ke Container",
            font=('Arial', 8, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=10,
            pady=5,
            command=self.add_selected_barang_to_container
        )
        add_barang_btn.pack(side='left', padx=(0, 10))
        
        # Remove barang from container
        remove_barang_btn = tk.Button(
            actions_frame,
            text="➖ Hapus Barang dari Container",
            font=('Arial', 8, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=10,
            pady=5,
            command=self.remove_barang_from_container
        )
        remove_barang_btn.pack(side='left', padx=(0, 10))
        
        # Edit price button
        edit_price_btn = tk.Button(
            actions_frame,
            text="✏️ Edit Harga",
            font=('Arial', 8, 'bold'),
            bg='#f39c12',
            fg='white',
            padx=10,
            pady=5,
            command=self.edit_barang_price_in_container
        )
        edit_price_btn.pack(side='left', padx=(0, 10))
        
        # === TAMBAHAN: Tombol kelola biaya pengantaran ===
        manage_delivery_btn = tk.Button(
            actions_frame,
            text="🚚 Kelola Biaya Pengantaran",
            font=('Arial', 8, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=10,
            pady=5,
            command=self.manage_delivery_costs
        )
        manage_delivery_btn.pack(side='left', padx=(0, 10))
        
        # View container summary
        summary_btn = tk.Button(
            actions_frame,
            text="📊 Lihat Summary Container",
            font=('Arial', 8, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=10,
            pady=5,
            command=self.view_container_summary
        )
        summary_btn.pack(side='left', padx=(0, 10))
        
        # Clear selection button
        clear_selection_btn = tk.Button(
            actions_frame,
            text="🗑️ Bersihkan Pilihan",
            font=('Arial', 8, 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=10,
            pady=5,
            command=self.clear_selection
        )
        clear_selection_btn.pack(side='left', padx=(0, 10))
        
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
                                        columns=('ID', 'Pengirim', 'Penerima', 'Nama', 'Dimensi', 'Volume', 'Berat'),
                                        show='headings', height=12)
        
        self.available_tree.heading('ID', text='ID')
        self.available_tree.heading('Pengirim', text='Pengirim')
        self.available_tree.heading('Penerima', text='Penerima')
        self.available_tree.heading('Nama', text='Nama Barang')
        self.available_tree.heading('Dimensi', text='P×L×T (cm)')
        self.available_tree.heading('Volume', text='Volume (m³)')
        self.available_tree.heading('Berat', text='Berat (ton)')
        
        self.available_tree.column('ID', width=40)
        self.available_tree.column('Pengirim', width=90)
        self.available_tree.column('Penerima', width=90)
        self.available_tree.column('Nama', width=130)
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
        
        # Right side - Barang in selected container (WITH PRICING)
        right_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.container_label = tk.Label(right_frame, text="📦 Barang dalam Container", font=('Arial', 12, 'bold'), bg='#ffffff')
        self.container_label.pack(pady=10)
        
        # Container barang tree WITH PRICING COLUMNS
        container_tree_frame = tk.Frame(right_frame)
        container_tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.container_barang_tree = ttk.Treeview(container_tree_frame,
                                                columns=('Pengirim', 'Penerima', 'Nama', 'Jenis', 'Satuan', 'Door','Dimensi', 'Volume', 'Berat', 'Colli', 'Harga_Unit', 'Total_Harga', 'Tanggal'),
                                                show='headings', height=12)
        
        self.container_barang_tree.heading('Pengirim', text='Pengirim')
        self.container_barang_tree.heading('Penerima', text='Penerima')
        self.container_barang_tree.heading('Nama', text='Nama Barang')
        self.container_barang_tree.heading('Jenis', text='Jenis Barang')
        self.container_barang_tree.heading('Satuan', text='Satuan')
        self.container_barang_tree.heading('Door', text='Door Type')
        self.container_barang_tree.heading('Dimensi', text='P×L×T (cm)')
        self.container_barang_tree.heading('Volume', text='Volume (m³)')
        self.container_barang_tree.heading('Berat', text='Berat (ton)')
        self.container_barang_tree.heading('Colli', text='Colli')
        self.container_barang_tree.heading('Harga_Unit', text='Harga/Unit')
        self.container_barang_tree.heading('Total_Harga', text='Total Harga')
        self.container_barang_tree.heading('Tanggal', text='Ditambahkan')
        
        self.container_barang_tree.column('Pengirim', width=70)
        self.container_barang_tree.column('Penerima', width=70)
        self.container_barang_tree.column('Nama', width=90)
        self.container_barang_tree.column('Jenis', width=80)
        self.container_barang_tree.column('Satuan', width=60)
        self.container_barang_tree.column('Door', width=80)
        self.container_barang_tree.column('Dimensi', width=65)
        self.container_barang_tree.column('Volume', width=45)
        self.container_barang_tree.column('Berat', width=45)
        self.container_barang_tree.column('Colli', width=40)
        self.container_barang_tree.column('Harga_Unit', width=75)
        self.container_barang_tree.column('Total_Harga', width=85)
        self.container_barang_tree.column('Tanggal', width=65)
        
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

    # === FUNGSI-FUNGSI TAMBAHAN UNTUK BIAYA PENGANTARAN ===
    
    def load_destinations(self, event=None):
        try:
            print("load_destinations dipanggil")
            # Cek apakah ada container yang dipilih
            if hasattr(self, 'selected_container_var') and self.selected_container_var.get():
                container_text = self.selected_container_var.get()
                container_parts = container_text.split(" ")
                if len(container_parts) > 0:
                    # Ambil bagian terakhir sebagai ID (format: "ID - Container Name (Destination)")
                    container_id = container_parts[0]  # Ambil ID dari awal string
                    print(f"Loading destinations for container ID: {container_id}")
                    
                    # Pastikan container_id tidak kosong dan valid
                    if container_id and container_id.strip() and container_id.isdigit():
                        # Ambil data container berdasarkan ID
                        container_data = self.db.get_container_by_id(int(container_id))
                        print(f"Container data: {container_data}")
                        
                        if container_data:
                            # Cek apakah container_data memiliki destination
                            destination = None
                            if hasattr(container_data, 'get'):
                                destination = container_data.get('destination', '')
                            elif isinstance(container_data, dict):
                                destination = container_data.get('destination', '')
                            else:
                                # Jika object lain, coba akses attribut
                                destination = getattr(container_data, 'destination', '')
                            
                            print(f"Destination found: {destination}")
                            
                            if destination and str(destination).strip():
                                # Set dropdown values: Surabaya dan destination dari container
                                self.delivery_destination_combo['values'] = ['Surabaya', str(destination)]
                                print(f"Set values: ['Surabaya', '{destination}']")
                            else:
                                # Jika destination kosong
                                self.delivery_destination_combo['values'] = ['Surabaya']
                                print("Destination kosong, set values: ['Surabaya']")
                            
                            # Set default ke Surabaya
                            self.delivery_destination_combo.set('Surabaya')
                        else:
                            # Jika container tidak ditemukan
                            self.delivery_destination_combo['values'] = ['Surabaya']
                            self.delivery_destination_combo.set('Surabaya')
                            print(f"Container dengan ID {container_id} tidak ditemukan")
                    else:
                        # Jika container_id kosong atau tidak valid
                        self.delivery_destination_combo['values'] = ['Pilih container terlebih dahulu']
                        self.delivery_destination_combo.set('Pilih container terlebih dahulu')
                        print(f"Container ID tidak valid: '{container_id}'")
                else:
                    # Jika tidak bisa parse container text
                    self.delivery_destination_combo['values'] = ['Pilih container terlebih dahulu']
                    self.delivery_destination_combo.set('Pilih container terlebih dahulu')
                    print("Tidak bisa parse container text")
            else:
                # Jika belum ada container yang dipilih
                self.delivery_destination_combo['values'] = ['Pilih container terlebih dahulu']
                self.delivery_destination_combo.set('Pilih container terlebih dahulu')
                print("Belum ada container yang dipilih")
                
        except Exception as e:
            print(f"Error loading destinations: {e}")
            import traceback
            traceback.print_exc()
            # Fallback jika ada error
            self.delivery_destination_combo['values'] = ['Surabaya']
            self.delivery_destination_combo.set('Surabaya')
            
        
    def format_currency_input(self, event=None):
        """Format currency input untuk rupiah"""
        try:
            # Ambil nilai dari entry
            value = self.delivery_cost_var.get().replace(',', '').replace('Rp', '').strip()
            if value and value.replace('.', '').isdigit():
                # Format sebagai currency
                formatted = f"{int(float(value)):,}".replace(',', '.')
                # Set kembali ke entry tanpa memicu event lagi
                current_pos = self.delivery_cost_entry.index(tk.INSERT)
                self.delivery_cost_var.set(formatted)
                self.delivery_cost_entry.icursor(min(current_pos, len(formatted)))
        except:
            pass

    def add_delivery_cost(self):
        """Tambah biaya pengantaran ke container yang dipilih"""
        container_id = self.get_selected_container_id()
        if not container_id:
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        deskripsi = self.delivery_desc_var.get().strip()
        biaya_str = self.delivery_cost_var.get().replace('.', '').replace(',', '').strip()
        lokasi = self.delivery_destination_var.get().strip()
        
        # Check jika masih placeholder text
        if not deskripsi or deskripsi == "Contoh: Biaya pickup/delivery, Bongkar muat, dll":
            messagebox.showwarning("Peringatan", "Masukkan deskripsi biaya pengantaran!")
            return
        
        try:
            biaya = float(biaya_str) if biaya_str else 0
            if biaya <= 0:
                messagebox.showwarning("Peringatan", "Masukkan nominal biaya yang valid!")
                return
        except:
            messagebox.showwarning("Peringatan", "Format biaya tidak valid!")
            return
        
        try:
            # Simpan ke database dengan tipe pengantaran
            self.db.execute("""
                INSERT INTO container_delivery_costs (container_id, delivery, description, cost, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (container_id, lokasi, deskripsi, biaya, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Clear form dan reset placeholder
            self.delivery_desc_var.set('')
            self.delivery_desc_entry.delete(0, tk.END)
            self.delivery_desc_entry.insert(0, "Contoh: Biaya pickup/delivery, Bongkar muat, dll")
            self.delivery_desc_entry.config(fg='grey')
            self.delivery_cost_var.set('0')
            self.delivery_destination_combo.set('Surabaya')
            
            messagebox.showinfo("Sukses", f"Biaya {lokasi}: '{deskripsi}' sebesar Rp {biaya:,.0f} berhasil ditambahkan!")
            
            # Refresh container summary jika ada
            if hasattr(self, 'summary_window') and self.summary_window.winfo_exists():
                self.view_container_summary()
                
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal menyimpan biaya pengantaran: {str(e)}")

    def manage_delivery_costs(self):
        """Window untuk mengelola biaya pengantaran container dengan lokasi"""
        container_id = self.get_selected_container_id()
        if not container_id:
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        # Create window
        delivery_window = tk.Toplevel(self.window)
        delivery_window.title(f"Kelola Biaya Pengantaran - Container {self.selected_container_var.get()}")
        delivery_window.geometry("1000x600")  # Perbesar untuk kolom lokasi
        delivery_window.configure(bg='#ecf0f1')
        
        # Header
        header_frame = tk.Frame(delivery_window, bg='#e67e22', height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🚚 Kelola Biaya Pengantaran", 
                font=('Arial', 16, 'bold'), bg='#e67e22', fg='white').pack(expand=True)
        
        # Content frame
        content_frame = tk.Frame(delivery_window, bg='#ffffff', relief='solid', bd=1)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Tree untuk menampilkan biaya pengantaran dengan kolom lokasi
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Label
        tk.Label(tree_frame, text="Daftar Biaya Pengantaran:", 
                font=('Arial', 12, 'bold'), bg='#ffffff').pack(anchor='w', pady=(0, 10))
        
        # Treeview dengan kolom lokasi
        columns = ('ID', 'Deskripsi', 'Lokasi', 'Biaya', 'Tanggal')
        delivery_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        delivery_tree.heading('ID', text='ID')
        delivery_tree.heading('Deskripsi', text='Deskripsi')
        delivery_tree.heading('Lokasi', text='Lokasi')
        delivery_tree.heading('Biaya', text='Biaya (Rp)')
        delivery_tree.heading('Tanggal', text='Tanggal Dibuat')
        
        delivery_tree.column('ID', width=50)
        delivery_tree.column('Deskripsi', width=250)
        delivery_tree.column('Lokasi', width=120)  # Kolom lokasi baru
        delivery_tree.column('Biaya', width=120)
        delivery_tree.column('Tanggal', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=delivery_tree.yview)
        delivery_tree.configure(yscrollcommand=scrollbar.set)
        
        delivery_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load data biaya pengantaran dengan lokasi
        def load_delivery_costs():
            for item in delivery_tree.get_children():
                delivery_tree.delete(item)
            
            # Query dengan kolom location
            results = self.db.execute("""
                SELECT id, description, delivery, cost, created_date
                FROM container_delivery_costs 
                WHERE container_id = ?
                ORDER BY created_date DESC
            """, (container_id,))
            
            total_biaya = 0
            for row in results:
                biaya_formatted = f"Rp {row[3]:,.0f}"  # cost di index 3
                delivery_tree.insert('', 'end', values=(
                    row[0],      # id
                    row[1],      # description
                    row[2] or 'Surabaya',  # location (default Surabaya jika NULL)
                    biaya_formatted,  # cost
                    row[4]       # created_date
                ))
                total_biaya += row[3]
            
            # Update total label
            total_label.config(text=f"Total Biaya Pengantaran: Rp {total_biaya:,.0f}")
        
        # Tombol aksi
        action_frame = tk.Frame(content_frame, bg='#ffffff')
        action_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Edit button
        edit_btn = tk.Button(action_frame, text="✏️ Edit Biaya", font=('Arial', 11, 'bold'),
                            bg='#f39c12', fg='white', padx=20, pady=8,
                            command=lambda: edit_delivery_cost(delivery_tree))
        edit_btn.pack(side='left', padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(action_frame, text="🗑️ Hapus Biaya", font=('Arial', 11, 'bold'),
                            bg='#e74c3c', fg='white', padx=20, pady=8,
                            command=lambda: delete_delivery_cost(delivery_tree))
        delete_btn.pack(side='left', padx=(0, 10))
        
        # Total label
        total_label = tk.Label(action_frame, text="Total Biaya: Rp 0", 
                            font=('Arial', 12, 'bold'), bg='#ffffff', fg='#27ae60')
        total_label.pack(side='right')
        
        # Fungsi edit biaya dengan lokasi
        def edit_delivery_cost(tree):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih biaya yang akan diedit!")
                return
            
            item = tree.item(selected[0])
            values = item['values']
            cost_id = values[0]
            current_desc = values[1]
            current_location = values[2]  # Lokasi di index 2
            current_cost = float(values[3].replace('Rp ', '').replace(',', '').replace('.', ''))
            
            # Dialog edit dengan lokasi
            edit_dialog = tk.Toplevel(delivery_window)
            edit_dialog.title("Edit Biaya Pengantaran")
            edit_dialog.geometry("450x300")  # Lebih tinggi untuk field lokasi
            edit_dialog.configure(bg='#ecf0f1')
            edit_dialog.transient(delivery_window)
            edit_dialog.grab_set()
            
            # Center dialog
            edit_dialog.update_idletasks()
            x = delivery_window.winfo_x() + (delivery_window.winfo_width() // 2) - (225)
            y = delivery_window.winfo_y() + (delivery_window.winfo_height() // 2) - (150)
            edit_dialog.geometry(f"450x300+{x}+{y}")
            
            # Form dengan lokasi
            tk.Label(edit_dialog, text="Deskripsi:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(pady=5)
            desc_var = tk.StringVar(value=current_desc)
            tk.Entry(edit_dialog, textvariable=desc_var, font=('Arial', 10), width=40).pack(pady=5)
            
            tk.Label(edit_dialog, text="Lokasi:", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(pady=5)
            location_var = tk.StringVar(value=current_location)
            location_combo = ttk.Combobox(edit_dialog, textvariable=location_var, 
                                        font=('Arial', 10), width=37, state='readonly')
            
            # Set lokasi options berdasarkan container
            try:
                container_data = self.db.get_container_by_id(container_id)
                if container_data:
                    destination = None
                    if hasattr(container_data, 'get'):
                        destination = container_data.get('destination', '')
                    elif isinstance(container_data, dict):
                        destination = container_data.get('destination', '')
                    else:
                        destination = getattr(container_data, 'destination', '')
                    
                    if destination and str(destination).strip():
                        location_combo['values'] = ['Surabaya', str(destination)]
                    else:
                        location_combo['values'] = ['Surabaya']
                else:
                    location_combo['values'] = ['Surabaya']
            except Exception as e:
                print(f"Error loading destinations for edit: {e}")
                location_combo['values'] = ['Surabaya']
            
            location_combo.pack(pady=5)
            
            tk.Label(edit_dialog, text="Biaya (Rp):", font=('Arial', 11, 'bold'), bg='#ecf0f1').pack(pady=5)
            cost_var = tk.StringVar(value=str(int(current_cost)))
            tk.Entry(edit_dialog, textvariable=cost_var, font=('Arial', 10), width=20).pack(pady=5)
            
            def save_edit():
                new_desc = desc_var.get().strip()
                new_location = location_var.get().strip()
                new_cost_str = cost_var.get().replace(',', '').replace('.', '').strip()
                
                if not new_desc or not new_location or not new_cost_str:
                    messagebox.showwarning("Peringatan", "Lengkapi semua field!")
                    return
                
                try:
                    new_cost = float(new_cost_str)
                    self.db.execute("""
                        UPDATE container_delivery_costs 
                        SET description = ?, delivery = ?, cost = ?
                        WHERE id = ?
                    """, (new_desc, new_location, new_cost, cost_id))
                    
                    edit_dialog.destroy()
                    load_delivery_costs()
                    messagebox.showinfo("Sukses", "Biaya pengantaran berhasil diupdate!")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal mengupdate: {str(e)}")
            
            # Buttons
            btn_frame = tk.Frame(edit_dialog, bg='#ecf0f1')
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="💾 Simpan", font=('Arial', 11, 'bold'),
                    bg='#27ae60', fg='white', padx=20, pady=8, command=save_edit).pack(side='left', padx=(0, 10))
            
            tk.Button(btn_frame, text="❌ Batal", font=('Arial', 11, 'bold'),
                    bg='#95a5a6', fg='white', padx=20, pady=8, command=edit_dialog.destroy).pack(side='left')
        
        # Fungsi hapus biaya
        def delete_delivery_cost(tree):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih biaya yang akan dihapus!")
                return
            
            item = tree.item(selected[0])
            cost_id = item['values'][0]
            desc = item['values'][1]
            location = item['values'][2]
            
            if messagebox.askyesno("Konfirmasi", f"Hapus biaya '{desc}' untuk lokasi '{location}'?"):
                try:
                    self.db.execute("DELETE FROM container_delivery_costs WHERE id = ?", (cost_id,))
                    load_delivery_costs()
                    messagebox.showinfo("Sukses", "Biaya pengantaran berhasil dihapus!")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menghapus: {str(e)}")
        
        # Load initial data
        load_delivery_costs()
    
    def get_selected_container_id(self):
        """Helper function untuk mendapatkan ID container yang dipilih"""
        container_text = self.selected_container_var.get()
        if not container_text:
            return None
        
        try:
            # Assuming container text format: "Container_Name (ID: X)"
            container_id = container_text.split('-')[0].split(' ')[0]
            return int(container_id)
        except:
            return None

    def export_container_summary(self, container_id):
        """Export container summary to text file"""
        try:
            from tkinter import filedialog
            
            # Get container name for filename
            container_name = self.selected_container_var.get().replace(' ', '_').replace('/', '_')
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=f"Summary_{container_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if not filename:
                return
            
            # Generate summary content
            cursor = self.conn.cursor()
            
            # Get all data again
            cursor.execute("SELECT * FROM containers WHERE id = ?", (container_id,))
            container_info = cursor.fetchone()
            
            cursor.execute("""
                SELECT cb.*, b.nama_barang, c1.nama as pengirim, c2.nama as penerima,
                    cb.harga_per_unit, cb.colli, cb.total_harga
                FROM container_barang cb
                JOIN barang b ON cb.barang_id = b.id
                JOIN customers c1 ON b.pengirim_id = c1.id
                JOIN customers c2 ON b.penerima_id = c2.id
                WHERE cb.container_id = ?
            """, (container_id,))
            barang_data = cursor.fetchall()
            
            cursor.execute("""
                SELECT description, cost, created_date
                FROM container_delivery_costs 
                WHERE container_id = ?
            """, (container_id,))
            delivery_costs = cursor.fetchall()
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("           SUMMARY CONTAINER BARANG\n")
                f.write("="*60 + "\n\n")
                
                # Container info
                if container_info:
                    f.write(f"Container: {container_info[1]}\n")
                    f.write(f"Tipe: {container_info[2]}\n")
                    f.write(f"Kapasitas: {container_info[3]}m³\n")
                
                f.write(f"Tanggal Export: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-"*60 + "\n\n")
                
                # Barang details
                f.write("DETAIL BARANG:\n")
                f.write("-"*60 + "\n")
                total_barang = 0
                total_colli = 0
                
                for i, row in enumerate(barang_data, 1):
                    pengirim = row[11]
                    penerima = row[12]  
                    nama_barang = row[5]
                    colli = row[14]
                    harga_unit = row[13]
                    total_harga = row[15]
                    
                    f.write(f"{i:2d}. {nama_barang}\n")
                    f.write(f"    Pengirim: {pengirim}\n")
                    f.write(f"    Penerima: {penerima}\n")
                    f.write(f"    Colli: {colli}\n")
                    f.write(f"    Harga/Unit: Rp {harga_unit:,.0f}\n")
                    f.write(f"    Total: Rp {total_harga:,.0f}\n\n")
                    
                    total_barang += total_harga
                    total_colli += colli
                
                # Delivery costs
                f.write("BIAYA PENGANTARAN:\n")
                f.write("-"*60 + "\n")
                total_delivery = 0
                
                if delivery_costs:
                    for i, (desc, cost, date) in enumerate(delivery_costs, 1):
                        f.write(f"{i:2d}. {desc}\n")
                        f.write(f"    Biaya: Rp {cost:,.0f}\n")
                        f.write(f"    Tanggal: {date}\n\n")
                        total_delivery += cost
                else:
                    f.write("Tidak ada biaya pengantaran\n\n")
                
                # Summary
                f.write("="*60 + "\n")
                f.write("RINGKASAN:\n")
                f.write("="*60 + "\n")
                f.write(f"Total Colli           : {total_colli:>15,}\n")
                f.write(f"Total Nilai Barang    : Rp {total_barang:>12,.0f}\n")  
                f.write(f"Total Biaya Antar     : Rp {total_delivery:>12,.0f}\n")
                f.write("-"*60 + "\n")
                f.write(f"GRAND TOTAL           : Rp {total_barang + total_delivery:>12,.0f}\n")
                f.write("="*60 + "\n")
            
            messagebox.showinfo("Sukses", f"Summary berhasil di-export ke:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export summary: {str(e)}")
            
    def filter_senders(self, event=None):
        """Filter sender combobox based on typed text"""
        try:
            typed = self.sender_search_var.get().lower()
            
            if not typed:
                # Reload all customers if nothing typed
                customers = self.db.execute("SELECT customer_id, nama_customer FROM customers ORDER BY customer_id")
                customer_list = [f"{customer[0]} - {customer[1]}" for customer in customers]
                self.sender_search_combo['values'] = customer_list
                return
                
            # Get all customer values and filter
            all_customers = list(self.sender_search_combo['values'])
            filtered = [customer for customer in all_customers if typed in customer.lower()]
            self.sender_search_combo['values'] = filtered
            
        except Exception as e:
            print(f"Error filtering senders: {e}")
        
    def filter_receivers(self, event=None):
        """Filter receiver combobox based on typed text"""
        try:
            typed = self.receiver_search_var.get().lower()
            
            if not typed:
                # Reload all customers if nothing typed
                customers = self.db.execute("SELECT customer_id, nama_customer FROM customers ORDER BY customer_id")
                customer_list = [f"{customer[0]} - {customer[1]}" for customer in customers]
                self.receiver_search_combo['values'] = customer_list
                return
                
            # Get all customer values and filter
            all_customers = list(self.receiver_search_combo['values'])
            filtered = [customer for customer in all_customers if typed in customer.lower()]
            self.receiver_search_combo['values'] = filtered
            
        except Exception as e:
            print(f"Error filtering receivers: {e}")

    def on_sender_receiver_select(self, event=None):
        """Handle selection of sender or receiver to load available barang"""
        sender = self.sender_search_var.get() if self.sender_search_var.get() != "" else None
        receiver = self.receiver_search_var.get() if self.receiver_search_var.get() != "" else None
        
        print(f"Sender/Receiver selection changed - Sender: {sender}, Receiver: {receiver}")
        
        # Call the updated method with both parameters
        self.load_customer_barang_tree(sender, receiver)

    def show_sender_receiver_summary_dialog(self, container, summary_data):
        """Show container summary dialog with sender/receiver breakdown"""
        try:
            summary_window = tk.Toplevel(self.window)
            summary_window.title(f"Summary Container - {container.get('container', 'N/A')}")
            summary_window.geometry("900x600")
            summary_window.transient(self.window)
            summary_window.grab_set()
            
            # Center window
            summary_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (450)
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (300)
            summary_window.geometry(f"900x600+{x}+{y}")
            
            # Header
            header = tk.Label(
                summary_window,
                text=f"📊 SUMMARY CONTAINER: {container.get('container', 'N/A')}",
                font=('Arial', 16, 'bold'),
                bg='#e67e22',
                fg='white',
                pady=15
            )
            header.pack(fill='x')
            
            # Container info
            info_frame = tk.Frame(summary_window, bg='#ecf0f1', relief='solid', bd=1)
            info_frame.pack(fill='x', padx=20, pady=10)
            
            
            
            tk.Label(info_frame, text=f"📦 Container: {container.get('container', 'N/A')}", 
                    font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            details_frame = tk.Frame(info_frame, bg='#ecf0f1')
            details_frame.pack(pady=(0, 10))
            
            tk.Label(details_frame, text=f"Feeder: {container.get('feeder', 'N/A')}", 
                    font=('Arial', 11), bg='#ecf0f1').pack(side='left', padx=20)
            tk.Label(details_frame, text=f"Destination: {container.get('destination', 'N/A')}", 
                    font=('Arial', 11), bg='#ecf0f1').pack(side='left', padx=20)
            tk.Label(details_frame, text=f"ETD: {container.get('etd_sub', 'N/A')}", 
                    font=('Arial', 11), bg='#ecf0f1').pack(side='left', padx=20)
            
            # Summary by sender-receiver
            tk.Label(summary_window, text="📊 Ringkasan per Pengirim-Penerima", 
                    font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w', padx=20, pady=(10, 5))
            
            # Summary tree
            tree_frame = tk.Frame(summary_window)
            tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            summary_tree = ttk.Treeview(tree_frame,
                                    columns=('Pengirim', 'Penerima', 'Items', 'Colli', 'Volume', 'Berat', 'Total_Harga'),
                                    show='headings', height=15)
            
            summary_tree.heading('Pengirim', text='Pengirim')
            summary_tree.heading('Penerima', text='Penerima')
            summary_tree.heading('Items', text='Jumlah Item')
            summary_tree.heading('Colli', text='Total Colli')
            summary_tree.heading('Volume', text='Volume (m³)')
            summary_tree.heading('Berat', text='Berat (ton)')
            summary_tree.heading('Total_Harga', text='Total Harga')
            
            summary_tree.column('Pengirim', width=120)
            summary_tree.column('Penerima', width=120)
            summary_tree.column('Items', width=80)
            summary_tree.column('Colli', width=80)
            summary_tree.column('Volume', width=80)
            summary_tree.column('Berat', width=80)
            summary_tree.column('Total_Harga', width=120)
            
            # Scrollbars
            v_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=summary_tree.yview)
            h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal', command=summary_tree.xview)
            summary_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            summary_tree.grid(row=0, column=0, sticky='nsew')
            v_scroll.grid(row=0, column=1, sticky='ns')
            h_scroll.grid(row=1, column=0, sticky='ew')
            
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            # Populate data and calculate totals
            grand_total_items = 0
            grand_total_colli = 0
            grand_total_volume = 0
            grand_total_berat = 0
            grand_total_harga = 0
            
            for row in summary_data:
                pengirim, penerima, items, colli, volume, berat, harga = row
                
                grand_total_items += items or 0
                grand_total_colli += colli or 0
                grand_total_volume += volume or 0
                grand_total_berat += berat or 0
                grand_total_harga += harga or 0
                
                summary_tree.insert('', 'end', values=(
                    pengirim or "N/A",
                    penerima or "N/A",
                    items or 0,
                    colli or 0,
                    f"{volume:.3f}" if volume else "0.000",
                    f"{berat:.3f}" if berat else "0.000",
                    f"Rp {harga:,.0f}" if harga else "Rp 0"
                ))
            
            # Add grand total row
            summary_tree.insert('', 'end', values=(
                "TOTAL",
                "",
                grand_total_items,
                grand_total_colli,
                f"{grand_total_volume:.3f}",
                f"{grand_total_berat:.3f}",
                f"Rp {grand_total_harga:,.0f}"
            ), tags=('total',))
            
            # Style total row
            summary_tree.tag_configure('total', background='#3498db', foreground='white')
            
            # Close button
            tk.Button(summary_window, text="Tutup", command=summary_window.destroy,
                    bg='#95a5a6', fg='white', font=('Arial', 12, 'bold'), 
                    padx=30, pady=8).pack(pady=20)
            
        except Exception as e:
            print(f"Error creating sender/receiver summary dialog: {e}")
            messagebox.showerror("Error", f"Gagal menampilkan summary: {e}")

    def create_pricing_dialog(self, selected_items, colli_amount):
        """Create dialog for pricing input with auto-price selection using Treeview table"""
        pricing_window = tk.Toplevel(self.window)
        pricing_window.title("💰 Set Harga Barang")
        pricing_window.geometry("1300x800")
        pricing_window.configure(bg='#ecf0f1')
        pricing_window.transient(self.window)
        pricing_window.grab_set()
        
        # Center window
        self._center_window(pricing_window, 1300, 800)
        
        # Initialize pricing data storage
        pricing_data_store = {}
        
        # CREATE MAIN SCROLLABLE CANVAS FOR ENTIRE DIALOG
        main_canvas = tk.Canvas(pricing_window, bg='#ecf0f1')
        main_scrollbar = ttk.Scrollbar(pricing_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ecf0f1')
        
        # Configure scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_mousewheel_linux(event):
            if event.num == 4:
                main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                main_canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel events
        main_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        main_canvas.bind("<Button-4>", _on_mousewheel_linux)  # Linux
        main_canvas.bind("<Button-5>", _on_mousewheel_linux)  # Linux
        
        # Update canvas scroll region when frame size changes
        def _on_canvas_configure(event):
            # Update scroll region
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            # Make sure canvas window width follows canvas width
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)
        
        main_canvas.bind('<Configure>', _on_canvas_configure)
        
        # NOW USE scrollable_frame AS PARENT INSTEAD OF pricing_window
        parent_frame = scrollable_frame
        
        # Create header
        self._create_pricing_header(parent_frame, colli_amount)
        
        # Create control buttons (Auto Fill & Quick Fill) - Create early for reference
        controls_frame = self._create_pricing_controls_placeholder(parent_frame, pricing_data_store)
        
        # Create main pricing table - FIXED HEIGHT untuk tidak terlalu tinggi
        table_frame, pricing_tree = self._create_pricing_table_compact(parent_frame, selected_items, colli_amount, pricing_data_store)
        
        # Setup pricing controls with tree reference
        self._setup_pricing_controls_with_tree(controls_frame, pricing_tree, pricing_data_store)
        
        # Create action buttons
        result = {'confirmed': False, 'pricing_data': {}}
        self._create_pricing_actions(parent_frame, pricing_window, pricing_tree, pricing_data_store, selected_items, colli_amount, result)
        
        # Update canvas scroll region after all widgets are added
        pricing_window.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Focus on canvas to enable mouse wheel
        main_canvas.focus_set()
        
        # Wait for dialog to close
        pricing_window.wait_window()
        
        return result if result['confirmed'] else None

    def _create_pricing_controls_placeholder(self, parent, pricing_data_store):
        """Create placeholder for pricing controls - will be setup later"""
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill='x', padx=25, pady=10)
        
        # Step 1: Select Satuan (Base Unit)
        satuan_frame = tk.LabelFrame(controls_frame, text="📏 Step 1: Pilih Satuan Dasar", 
                                    font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        satuan_frame.pack(fill='x', pady=(0, 10))
        
        satuan_inner = tk.Frame(satuan_frame, bg='#ecf0f1')
        satuan_inner.pack(fill='x', padx=15, pady=8)
        
        # Step 2: Select Door/Package Type
        door_frame = tk.LabelFrame(controls_frame, text="📦 Step 2: Pilih Tipe Door/Package", 
                                font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        door_frame.pack(fill='x', pady=(0, 10))
        
        door_inner = tk.Frame(door_frame, bg='#ecf0f1')
        door_inner.pack(fill='x', padx=15, pady=8)
        
        # Step 3: Generated Combinations + Manual
        result_frame = tk.LabelFrame(controls_frame, text="🚀 Step 3: Apply Kombinasi atau Manual", 
                                    font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        result_frame.pack(fill='x')
        
        result_inner = tk.Frame(result_frame, bg='#ecf0f1')
        result_inner.pack(fill='x', padx=15, pady=8)
        
        # Manual section with input field and quick buttons
        manual_inner = tk.Frame(result_frame, bg='#ecf0f1')
        manual_inner.pack(fill='x', padx=15, pady=(0, 8))
        
        tk.Label(manual_inner, text="⚡ Quick Manual:", 
                font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left', padx=(0, 10))
        
        # Custom amount input
        custom_frame = tk.Frame(manual_inner, bg='#ecf0f1')
        custom_frame.pack(side='left', padx=(0, 15))
        
        tk.Label(custom_frame, text="💰 Custom:", 
                font=('Arial', 9, 'bold'), bg='#ecf0f1').pack(side='left')
        
        custom_var = tk.StringVar()
        custom_entry = tk.Entry(custom_frame, textvariable=custom_var, 
                            font=('Arial', 9), width=10)
        custom_entry.pack(side='left', padx=(5, 5))
        
        # Store reference for later setup
        return {
            'controls_frame': controls_frame,
            'satuan_frame': satuan_inner, 
            'door_frame': door_inner, 
            'result_frame': result_inner,
            'manual_frame': manual_inner,
            'custom_var': custom_var,
            'custom_entry': custom_entry
        }

    def _create_pricing_table_compact(self, parent, selected_items, colli_amount, pricing_data_store):
        """Create compact pricing table that fits in scrollable dialog"""
        table_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        table_frame.pack(fill='x', padx=25, pady=15)  # Changed from fill='both' expand=True
        
        # Table title
        title_frame = tk.Frame(table_frame, bg='#34495e')
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text="📋 DAFTAR BARANG DAN HARGA", 
                font=('Arial', 14, 'bold'), bg='#34495e', fg='white', pady=10).pack()
        
        # Create Treeview with Frame container - FIXED HEIGHT
        tree_frame = tk.Frame(table_frame, bg='#ffffff', height=300)  # Fixed height
        tree_frame.pack(fill='x', padx=10, pady=10)
        tree_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Create Treeview with smaller height
        columns = ('nama_barang', 'pengirim', 'penerima', 'auto_pricing', 'harga_unit', 'total_harga')
        pricing_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)  # Reduced height from 15 to 10
        
        # Define headings and column widths - SMALLER COLUMNS
        column_config = {
            'nama_barang': ('Nama Barang', 150),  # Reduced from 180
            'pengirim': ('Pengirim', 100),        # Reduced from 120
            'penerima': ('Penerima', 100),        # Reduced from 120
            'auto_pricing': ('Auto Pricing', 110), # Reduced from 120
            'harga_unit': ('Harga/Unit', 100),    # Reduced from 120
            'total_harga': ('Total Harga', 120),  # Reduced from 140
        }
        
        for col, (heading, width) in column_config.items():
            pricing_tree.heading(col, text=heading)
            pricing_tree.column(col, width=width, anchor='w' if col in ['nama_barang', 'pengirim', 'penerima'] else 'center')
        
        # Create scrollbars for table
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=pricing_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=pricing_tree.xview)
        
        # Configure scrollbars
        pricing_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack with proper scrollbar layout
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        pricing_tree.pack(side='left', fill='both', expand=True)
        
        # Get barang details and populate table
        barang_details = self._get_barang_details(selected_items)
        self._populate_pricing_table(pricing_tree, selected_items, barang_details, colli_amount, pricing_data_store)
        
        # Setup table editing
        self._setup_table_editing(pricing_tree, pricing_data_store, colli_amount)
        
        return table_frame, pricing_tree

    def _setup_pricing_controls_with_tree(self, controls_frame, pricing_tree, pricing_data_store):
        """Setup pricing controls after tree is created"""
        
        # Setup custom amount input
        def apply_custom_amount():
            try:
                amount_str = controls_frame['custom_var'].get().strip()
                if not amount_str:
                    messagebox.showwarning("Input Error", "Masukkan nilai harga!")
                    return
                    
                amount = float(amount_str.replace(',', '').replace('.', ''))
                if amount >= 0:
                    print(f"Applying custom amount: {amount}")
                    self._quick_fill_manual(pricing_tree, pricing_data_store, amount)
                    controls_frame['custom_var'].set("")  # Clear after apply
                    messagebox.showinfo("Berhasil", f"Harga manual Rp {amount:,.0f} telah diterapkan ke semua barang!")
                else:
                    messagebox.showwarning("Input Error", "Masukkan angka positif!")
            except ValueError:
                messagebox.showwarning("Input Error", "Masukkan angka yang valid!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menerapkan harga: {str(e)}")
        
        # Create apply button
        custom_btn = tk.Button(
            controls_frame['custom_entry'].master,
            text="✓ Apply",
            font=('Arial', 8, 'bold'),
            bg='#34495e',
            fg='white',
            padx=8,
            pady=3,
            relief='flat',
            cursor='hand2',
            command=apply_custom_amount
        )
        custom_btn.pack(side='left', padx=(0, 5))
        
        # Bind Enter key to apply
        controls_frame['custom_entry'].bind('<Return>', lambda e: apply_custom_amount())
        controls_frame['custom_entry'].bind('<KP_Enter>', lambda e: apply_custom_amount())
        
        # Manual quick fill buttons
        quick_amounts = [50000, 100000, 150000, 200000, 250000, 300000]
        for amount in quick_amounts:
            btn = tk.Button(
                controls_frame['manual_frame'],
                text=f"{amount//1000}K",
                font=('Arial', 9),
                bg='#95a5a6',
                fg='white',
                padx=10,
                pady=5,
                relief='flat',
                cursor='hand2',
                command=lambda a=amount: self._quick_fill_manual(pricing_tree, pricing_data_store, a)
            )
            btn.pack(side='left', padx=2)
        
        # Setup combination controls
        self._setup_pricing_controls(controls_frame, pricing_tree, pricing_data_store)

    def _center_window(self, window, width, height):
        """Center window on parent"""
        window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (width // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_pricing_header(self, parent, colli_amount):
        """Create header section"""
        header = tk.Label(
            parent,
            text="💰 SET HARGA BARANG",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='white',
            pady=20
        )
        header.pack(fill='x')
        
        info_frame = tk.Frame(parent, bg='#ecf0f1')
        info_frame.pack(fill='x', padx=25, pady=15)
        
        info_label = tk.Label(
            info_frame,
            text=f"📦 Jumlah Colli per barang: {colli_amount}  |  💡 Klik dua kali pada cell untuk edit",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        info_label.pack(anchor='w')

    def _create_pricing_controls(self, parent, pricing_data_store, pricing_tree):
        """Create auto fill and quick fill controls with combination system"""
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill='x', padx=25, pady=10)
        
        # Step 1: Select Satuan (Base Unit)
        satuan_frame = tk.LabelFrame(controls_frame, text="📏 Step 1: Pilih Satuan Dasar", 
                                    font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        satuan_frame.pack(fill='x', pady=(0, 10))
        
        satuan_inner = tk.Frame(satuan_frame, bg='#ecf0f1')
        satuan_inner.pack(fill='x', padx=15, pady=8)
        
        # Step 2: Select Door/Package Type
        door_frame = tk.LabelFrame(controls_frame, text="📦 Step 2: Pilih Tipe Door/Package", 
                                font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        door_frame.pack(fill='x', pady=(0, 10))
        
        door_inner = tk.Frame(door_frame, bg='#ecf0f1')
        door_inner.pack(fill='x', padx=15, pady=8)
        
        # Step 3: Generated Combinations + Manual
        result_frame = tk.LabelFrame(controls_frame, text="🚀 Step 3: Apply Kombinasi atau Manual", 
                                    font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        result_frame.pack(fill='x')
        
        result_inner = tk.Frame(result_frame, bg='#ecf0f1')
        result_inner.pack(fill='x', padx=15, pady=8)
        
        # Manual section with input field and quick buttons
        manual_inner = tk.Frame(result_frame, bg='#ecf0f1')
        manual_inner.pack(fill='x', padx=15, pady=(0, 8))
        
        tk.Label(manual_inner, text="⚡ Quick Manual:", 
                font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left', padx=(0, 10))
        
        # Custom amount input
        custom_frame = tk.Frame(manual_inner, bg='#ecf0f1')
        custom_frame.pack(side='left', padx=(0, 15))
        
        tk.Label(custom_frame, text="💰 Custom:", 
                font=('Arial', 9, 'bold'), bg='#ecf0f1').pack(side='left')
        
        custom_var = tk.StringVar()
        custom_entry = tk.Entry(custom_frame, textvariable=custom_var, 
                            font=('Arial', 9), width=10)
        custom_entry.pack(side='left', padx=(5, 5))
        
        def apply_custom_amount():
            try:
                amount_str = custom_var.get().strip()
                if not amount_str:
                    messagebox.showwarning("Input Error", "Masukkan nilai harga!")
                    return
                    
                amount = float(amount_str.replace(',', '').replace('.', ''))
                if amount >= 0:
                    # FIX: Gunakan pricing_tree yang sudah dibuat, bukan parent
                    print(f"Applying custom amount: {amount}")
                    self._quick_fill_manual(pricing_tree, pricing_data_store, amount)
                    custom_var.set("")  # Clear after apply
                    messagebox.showinfo("Berhasil", f"Harga manual Rp {amount:,.0f} telah diterapkan ke semua barang!")
                else:
                    messagebox.showwarning("Input Error", "Masukkan angka positif!")
            except ValueError:
                messagebox.showwarning("Input Error", "Masukkan angka yang valid!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menerapkan harga: {str(e)}")
        
        custom_btn = tk.Button(
            custom_frame,
            text="✓ Apply",
            font=('Arial', 8, 'bold'),
            bg='#34495e',
            fg='white',
            padx=8,
            pady=3,
            relief='flat',
            cursor='hand2',
            command=apply_custom_amount
        )
        custom_btn.pack(side='left', padx=(0, 5))
        
        # Bind Enter key to apply - BOTH regular and numpad enter
        custom_entry.bind('<Return>', lambda e: apply_custom_amount())
        custom_entry.bind('<KP_Enter>', lambda e: apply_custom_amount())
        
        # Manual quick fill buttons
        quick_amounts = [50000, 100000, 150000, 200000, 250000, 300000]
        for amount in quick_amounts:
            btn = tk.Button(
                manual_inner,
                text=f"{amount//1000}K",
                font=('Arial', 9),
                bg='#95a5a6',
                fg='white',
                padx=10,
                pady=5,
                relief='flat',
                cursor='hand2',
                # FIX: Gunakan pricing_tree sebagai parameter pertama
                command=lambda a=amount: self._quick_fill_manual(pricing_tree, pricing_data_store, a)
            )
            btn.pack(side='left', padx=2)
        
        return {
            'satuan_frame': satuan_inner, 
            'door_frame': door_inner, 
            'result_frame': result_inner,
            'manual_frame': manual_inner,
            'custom_var': custom_var,
            'custom_entry': custom_entry
        }

    def _create_pricing_table(self, parent, selected_items, colli_amount, pricing_data_store):
        """Create main pricing table using Treeview - FIXED SCROLLABLE LAYOUT"""
        table_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        table_frame.pack(fill='both', expand=True, padx=25, pady=15)
        
        # Table title
        title_frame = tk.Frame(table_frame, bg='#34495e')
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text="📋 DAFTAR BARANG DAN HARGA", 
                font=('Arial', 14, 'bold'), bg='#34495e', fg='white', pady=10).pack()
        
        # Create Treeview with Frame container
        tree_frame = tk.Frame(table_frame, bg='#ffffff')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Treeview
        columns = ('nama_barang', 'pengirim', 'penerima', 'auto_pricing', 'harga_unit', 'total_harga')
        pricing_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings and column widths
        column_config = {
            'nama_barang': ('Nama Barang', 180),
            'pengirim': ('Pengirim', 120),
            'penerima': ('Penerima', 120),
            'auto_pricing': ('Auto Pricing', 120),
            'harga_unit': ('Harga/Unit', 120),
            'total_harga': ('Total Harga', 140),
        }
        
        for col, (heading, width) in column_config.items():
            pricing_tree.heading(col, text=heading)
            pricing_tree.column(col, width=width, anchor='w' if col in ['nama_barang', 'pengirim', 'penerima'] else 'center')
        
        # FIXED: Use pack layout consistently for scrollbars
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=pricing_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=pricing_tree.xview)
        
        # Configure scrollbars
        pricing_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack with proper scrollbar layout
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        pricing_tree.pack(side='left', fill='both', expand=True)
        
        # Get barang details and populate table
        barang_details = self._get_barang_details(selected_items)
        self._populate_pricing_table(pricing_tree, selected_items, barang_details, colli_amount, pricing_data_store)
        
        # Setup table editing
        self._setup_table_editing(pricing_tree, pricing_data_store, colli_amount)
        
        return table_frame, pricing_tree

    def _get_barang_details(self, selected_items):
        """Get detailed barang data for pricing options"""
        barang_details = {}
        for item in selected_items:
            try:
                barang_data = self.db.execute_one("""
                    SELECT b.*, r.nama_customer AS receiver_name, s.nama_customer AS sender_name
                    FROM barang b
                    JOIN customers r ON b.penerima = r.customer_id
                    JOIN customers s ON b.pengirim = s.customer_id
                    WHERE b.barang_id = ?
                """, (item['id'],))
                
                if barang_data:
                    barang_details[item['id']] = dict(barang_data)
            except Exception as e:
                print(f"Error getting barang details for {item['id']}: {e}")
                barang_details[item['id']] = {}
        
        return barang_details

    def _populate_pricing_table(self, tree, selected_items, barang_details, colli_amount, pricing_data_store):
        """Populate the pricing table with data"""
        for item in selected_items:
            barang_detail = barang_details.get(item['id'], {})
            
            # Extract pricing data for combinations
            pricing_info = {
                # Combination fields
                'harga_m3_pp': barang_detail.get('m3_pp', 0) or 0,
                'harga_m3_pd': barang_detail.get('m3_pd', 0) or 0,
                'harga_m3_dd': barang_detail.get('m3_dd', 0) or 0,
                'harga_ton_pp': barang_detail.get('ton_pp', 0) or 0,
                'harga_ton_pd': barang_detail.get('ton_pd', 0) or 0,
                'harga_ton_dd': barang_detail.get('ton_dd', 0) or 0,
                'harga_colli_pp': barang_detail.get('col_pp', 0) or 0,
                'harga_colli_pd': barang_detail.get('col_pd', 0) or 0,
                'harga_colli_dd': barang_detail.get('col_dd', 0) or 0,
                # Base measurements
                'm3_barang': barang_detail.get('m3_barang', 0) or 0,
                'ton_barang': barang_detail.get('ton_barang', 0) or 0
            }
            
            # Store data for calculations
            pricing_data_store[item['id']] = {
                'item': item,
                'pricing_info': pricing_info,
                'current_method': 'Manual',
                'current_price': 0,
                'colli_amount': colli_amount
            }
            
            # Insert into tree
            tree.insert('', tk.END, iid=item['id'], values=(
                item['name'],
                item.get('sender', ''),
                item.get('receiver', ''),
                'Manual',
                '0',
                '0'
            ), tags=('row',))
        
        # Configure row styling
        tree.tag_configure('row', background='#f8f9fa')
        tree.tag_configure('selected', background='#e3f2fd')

    def _setup_table_editing(self, tree, pricing_data_store, colli_amount):
        """Setup double-click editing for table cells"""
        def on_double_click(event):
            item_id = tree.selection()[0] if tree.selection() else None
            if not item_id:
                return
            
            # Get clicked column
            region = tree.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            column = tree.identify_column(event.x, event.y)
            
            # Only allow editing for auto_pricing and harga_unit columns
            if column == '#4':  # auto_pricing column
                self._edit_auto_pricing(tree, item_id, pricing_data_store, colli_amount)
            elif column == '#5':  # harga_unit column
                self._edit_harga_unit(tree, item_id, pricing_data_store, colli_amount)
        
        tree.bind('<Double-1>', on_double_click)

    def _edit_auto_pricing(self, tree, item_id, pricing_data_store, colli_amount):
        """Edit auto pricing method"""
        # Get current position
        bbox = tree.bbox(item_id, 'auto_pricing')
        if not bbox:
            return
        
        # Create combobox
        combo_var = tk.StringVar(value=pricing_data_store[item_id]['current_method'])
        combo = ttk.Combobox(tree, textvariable=combo_var, 
                            values=['Manual', 'Harga/m³', 'Harga/ton', 'Harga/colli'],
                            state='readonly')
        
        combo.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        combo.focus_set()
        
        def on_combo_change(event=None):
            new_method = combo_var.get()
            pricing_data_store[item_id]['current_method'] = new_method
            
            # Auto-set price based on method
            new_price = self._calculate_auto_price(item_id, new_method, pricing_data_store)
            pricing_data_store[item_id]['current_price'] = new_price
            
            # Update tree
            tree.set(item_id, 'auto_pricing', new_method)
            tree.set(item_id, 'harga_unit', f"{new_price:,.0f}")
            
            # Calculate total
            total = self._calculate_total_price(item_id, pricing_data_store, colli_amount)
            tree.set(item_id, 'total_harga', f"Rp {total:,.0f}")
            
            combo.destroy()
        
        def on_combo_escape(event):
            combo.destroy()
        
        combo.bind('<<ComboboxSelected>>', on_combo_change)
        combo.bind('<Return>', on_combo_change)
        combo.bind('<Escape>', on_combo_escape)
        combo.bind('<FocusOut>', lambda e: combo.destroy())

    def _edit_harga_unit(self, tree, item_id, pricing_data_store, colli_amount):
        """Edit harga unit"""
        bbox = tree.bbox(item_id, 'harga_unit')
        if not bbox:
            return
        
        # Create entry
        entry_var = tk.StringVar(value=str(int(pricing_data_store[item_id]['current_price'])))
        entry = tk.Entry(tree, textvariable=entry_var)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        def on_entry_confirm(event=None):
            try:
                new_price = float(entry_var.get().replace(',', ''))
                pricing_data_store[item_id]['current_price'] = new_price
                pricing_data_store[item_id]['current_method'] = 'Manual'
                
                # Update tree
                tree.set(item_id, 'harga_unit', f"{new_price:,.0f}")
                tree.set(item_id, 'auto_pricing', 'Manual')
                
                # Calculate total
                total = self._calculate_total_price(item_id, pricing_data_store, colli_amount)
                tree.set(item_id, 'total_harga', f"Rp {total:,.0f}")
                
            except ValueError:
                pass  # Invalid input, ignore
            
            entry.destroy()
        
        def on_entry_escape(event):
            entry.destroy()
        
        entry.bind('<Return>', on_entry_confirm)
        entry.bind('<Escape>', on_entry_escape)
        entry.bind('<FocusOut>', lambda e: on_entry_confirm())

    def _calculate_auto_price(self, item_id, method, pricing_data_store):
        """Calculate automatic price based on combination method"""

        barang_pricing = pricing_data_store[item_id]['pricing_info']

        print("Barang pricing info:", barang_pricing)

        # Handle combination methods
        if method == 'Harga/m3_pp' and barang_pricing['harga_m3_pp'] > 0:
            return barang_pricing['harga_m3_pp']
        elif method == 'Harga/m3_pd' and barang_pricing['harga_m3_pd'] > 0:
            return barang_pricing['harga_m3_pd']
        elif method == 'Harga/m3_dd' and barang_pricing['harga_m3_dd'] > 0:
            return barang_pricing['harga_m3_dd']
        elif method == 'Harga/ton_pp' and barang_pricing['harga_ton_pp'] > 0:
            return barang_pricing['harga_ton_pp']
        elif method == 'Harga/ton_pd' and barang_pricing['harga_ton_pd'] > 0:
            return barang_pricing['harga_ton_pd']
        elif method == 'Harga/ton_dd' and barang_pricing['harga_ton_dd'] > 0:
            return barang_pricing['harga_ton_dd']
        elif method == 'Harga/colli_pp' and barang_pricing['harga_colli_pp'] > 0:
            return barang_pricing['harga_colli_pp']
        elif method == 'Harga/colli_pd' and barang_pricing['harga_colli_pd'] > 0:
            return barang_pricing['harga_colli_pd']
        elif method == 'Harga/colli_dd' and barang_pricing['harga_colli_dd'] > 0:
            return barang_pricing['harga_colli_dd']
        else:
            return 0

    def _calculate_total_price(self, item_id, pricing_data_store, colli_amount):
        """Calculate total price for an item with combination methods"""
        data = pricing_data_store[item_id]
        method = data['current_method']
        price = data['current_price']
        pricing_info = data['pricing_info']
        
        print(f"Calculating total for item {item_id} with method {method}, price {price}, colli {colli_amount}")
        print("Pricing Info:", pricing_info)

        # Parse combination methods
        if method.startswith('Harga/m3_'):
            # m3-based combinations: price × m3_barang × colli × package_multiplier
            base_total = price * pricing_info['m3_barang'] * colli_amount

            return base_total

        elif method.startswith('Harga/ton_'):
            # ton-based combinations: price × ton_barang × colli × package_multiplier
            base_total = price * pricing_info['ton_barang'] * colli_amount

            return base_total

        elif method.startswith('Harga/colli_'):
            # colli-based combinations: price × colli × package_multiplier
            base_total = price * colli_amount

            return base_total

                
        elif method == 'Manual':
            # Manual: price × colli
            return price * colli_amount
        else:
            return 0

    def _setup_pricing_controls(self, controls_frame, tree, pricing_data_store):
        """Setup combination pricing controls with 2-step selection"""
        
        # State variables for combination
        selected_satuan = tk.StringVar()
        selected_door = tk.StringVar()
        
        # Step 1: Satuan selection buttons  
        satuan_types = [
            ("m³", "m3", '#3498db'),
            ("ton", "ton", '#e74c3c'), 
            ("colli", "colli", '#27ae60')
        ]
        
        def select_satuan(satuan_key):
            selected_satuan.set(satuan_key)
            self._update_combination_buttons(controls_frame['result_frame'], 
                                        selected_satuan.get(), selected_door.get(), 
                                        tree, pricing_data_store)
            # Update button colors to show selection
            for btn in satuan_buttons:
                if btn['text'] == satuan_key:
                    btn.configure(relief='sunken', borderwidth=3)
                else:
                    btn.configure(relief='flat', borderwidth=1)
        
        satuan_buttons = []
        for label, key, color in satuan_types:
            btn = tk.Button(
                controls_frame['satuan_frame'],
                text=label,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg='white',
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=lambda k=key: select_satuan(k)
            )
            btn.pack(side='left', padx=5)
            satuan_buttons.append(btn)
        
        # Step 2: Door/Package selection buttons
        door_types = [
            ("PP", "pp", '#9b59b6'),     # Per Pcs
            ("PD", "pd", '#f39c12'),     # Per Dozen  
            ("DD", "dd", '#16a085')      # Per Double Dozen
        ]
        
        def select_door(door_key):
            selected_door.set(door_key)
            self._update_combination_buttons(controls_frame['result_frame'], 
                                        selected_satuan.get(), selected_door.get(), 
                                        tree, pricing_data_store)
            # Update button colors to show selection
            for btn in door_buttons:
                if btn['text'] == door_key.upper():
                    btn.configure(relief='sunken', borderwidth=3)
                else:
                    btn.configure(relief='flat', borderwidth=1)
        
        door_buttons = []
        for label, key, color in door_types:
            btn = tk.Button(
                controls_frame['door_frame'],
                text=label,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg='white',
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=lambda k=key: select_door(k)
            )
            btn.pack(side='left', padx=5)
            door_buttons.append(btn)

    def _update_combination_buttons(self, result_frame, satuan, door, tree, pricing_data_store):
        """Update combination buttons based on selection"""
        # Clear existing buttons
        for widget in result_frame.winfo_children():
            widget.destroy()
        
        if not satuan or not door:
            tk.Label(result_frame, text="👆 Pilih Satuan dan Door/Package untuk melihat kombinasi", 
                    font=('Arial', 10), bg='#ecf0f1', fg='#7f8c8d').pack(pady=10)
            return
        
        # Create info label
        info_text = f"🎯 Kombinasi: {satuan.upper()} × {door.upper()}"
        tk.Label(result_frame, text=info_text, 
                font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=(5, 10))
        
        # Create combination button
        combination_method = f"Harga/{satuan}_{door}"
        combination_text = f"{satuan.upper()}_{door.upper()}"
        
        btn = tk.Button(
            result_frame,
            text=f"🚀 Apply {combination_text}",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=lambda: self._auto_fill_all(tree, pricing_data_store, combination_method)
        )
        btn.pack(pady=5)

    def _auto_fill_all(self, tree, pricing_data_store, method):
        """Auto fill all items with selected pricing method"""
        updated_count = 0
        try:
            for item_id in pricing_data_store.keys():
                if tree.exists(item_id):
                    pricing_data_store[item_id]['current_method'] = method
                    
                    # Calculate new price
                    new_price = self._calculate_auto_price(item_id, method, pricing_data_store)
                    pricing_data_store[item_id]['current_price'] = new_price
                    
                    # Update tree
                    tree.set(item_id, 'auto_pricing', method)
                    tree.set(item_id, 'harga_unit', f"{new_price:,.0f}")

                    # Calculate total
                    colli_amount = pricing_data_store[item_id]['colli_amount']
                    total = self._calculate_total_price(item_id, pricing_data_store, colli_amount)
                    tree.set(item_id, 'total_harga', f"Rp {total:,.0f}")
                    
                    updated_count += 1
            
            print(f"Auto fill completed: {updated_count} items updated with method {method}")
            messagebox.showinfo("Berhasil", f"Metode {method} telah diterapkan ke {updated_count} barang!")
            
        except Exception as e:
            print(f"Error in _auto_fill_all: {str(e)}")
            messagebox.showerror("Error", f"Gagal menerapkan auto fill: {str(e)}")

    def _quick_fill_manual(self, tree, pricing_data_store, amount):
        """Quick fill all items with manual amount - FIXED"""
        updated_count = 0
        try:
            print(f"Starting quick fill manual with amount: {amount}")
            print(f"Items in pricing_data_store: {list(pricing_data_store.keys())}")
            
            for item_id in pricing_data_store.keys():
                # Pastikan item_id ada di tree
                if tree.exists(item_id):
                    # Update data store
                    pricing_data_store[item_id]['current_method'] = 'Manual'
                    pricing_data_store[item_id]['current_price'] = amount
                    
                    # Update tree display
                    tree.set(item_id, 'auto_pricing', 'Manual')
                    tree.set(item_id, 'harga_unit', f"{amount:,.0f}")
                    
                    # Calculate total
                    colli_amount = pricing_data_store[item_id]['colli_amount']
                    total = self._calculate_total_price(item_id, pricing_data_store, colli_amount)
                    tree.set(item_id, 'total_harga', f"Rp {total:,.0f}")
                    
                    updated_count += 1
                    print(f"Updated item {item_id}: price={amount}, total={total}")
                else:
                    print(f"WARNING: Item {item_id} not found in tree")
            
            print(f"Manual fill completed: {updated_count} items updated")
            
            if updated_count > 0:
                messagebox.showinfo("Berhasil", f"Harga manual Rp {amount:,.0f} telah diterapkan ke {updated_count} barang!")
            else:
                messagebox.showwarning("Peringatan", "Tidak ada barang yang berhasil diupdate!")
            
        except Exception as e:
            print(f"Error in _quick_fill_manual: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal mengisi harga manual: {str(e)}")

    def _create_pricing_actions(self, parent_frame, pricing_window, tree, pricing_data_store, selected_items, colli_amount, result):
        """Create action buttons - FIXED: Pass pricing_window reference"""
        btn_frame = tk.Frame(parent_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', padx=25, pady=20)
        
        # Action buttons
        action_frame = tk.Frame(btn_frame, bg='#ecf0f1')
        action_frame.pack()
        
        def confirm_pricing():
            try:
                pricing_data = {}
                total_amount = 0
                
                for item_id, data in pricing_data_store.items():
                    if tree.exists(item_id):
                        price = data['current_price']
                        method = data['current_method']
                        total = self._calculate_total_price(item_id, pricing_data_store, colli_amount)
                        
                        pricing_data[item_id] = {
                            'harga_per_unit': price,
                            'total_harga': total,
                            'metode_pricing': method
                        }
                        total_amount += total
                
                if not pricing_data:
                    messagebox.showwarning("Peringatan", "Tidak ada data pricing yang valid!")
                    return
                
                # Confirmation dialog
                if self._confirm_pricing_dialog(selected_items, colli_amount, total_amount, pricing_data):
                    result['confirmed'] = True
                    result['pricing_data'] = pricing_data
                    print(f"Pricing confirmed with {len(pricing_data)} items, total: {total_amount}")
                    # FIX: Use pricing_window instead of parent
                    pricing_window.destroy()
                    
            except Exception as e:
                print(f"Error in confirm_pricing: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        def cancel_pricing():
            print("Pricing canceled by user")
            # FIX: Use pricing_window instead of parent
            pricing_window.destroy()
        
        
        
        tk.Button(
            action_frame,
            text="✅ Konfirmasi & Tambah",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=confirm_pricing
        ).pack(side='left', padx=(0, 15))
        
        tk.Button(
            action_frame,
            text="❌ Batal",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=cancel_pricing
        ).pack(side='left')

    def _confirm_pricing_dialog(self, selected_items, colli_amount, total_amount, pricing_data):
        """Show confirmation dialog with pricing summary"""
        confirm_msg = f"Konfirmasi penambahan barang dengan harga:\n\n"
        confirm_msg += f"📊 RINGKASAN:\n"
        confirm_msg += f"• Total {len(selected_items)} barang\n"
        confirm_msg += f"• Colli per barang: {colli_amount}\n"
        confirm_msg += f"• Total nilai: Rp {total_amount:,.0f}\n\n"
        
        # Add detail for each item (max 5 items to avoid dialog being too long)
        confirm_msg += f"📋 DETAIL BARANG:\n"
        for i, (item_id, pricing_detail) in enumerate(pricing_data.items()):
            if i >= 5:  # Show max 5 items
                remaining = len(pricing_data) - 5
                confirm_msg += f"... dan {remaining} barang lainnya\n"
                break
            
            item_name = next((item['name'] for item in selected_items if item['id'] == item_id), f"ID:{item_id}")
            harga_unit = pricing_detail['harga_per_unit']
            total_harga = pricing_detail['total_harga']
            metode = pricing_detail['metode_pricing']
            
            confirm_msg += f"• {item_name}\n"
            confirm_msg += f"  Metode: {metode} | Unit: Rp {harga_unit:,.0f} | Total: Rp {total_harga:,.0f}\n"
        
        confirm_msg += f"\n🚀 Lanjutkan proses?"
        
        return messagebox.askyesno("Konfirmasi Harga", confirm_msg)


    def create_edit_pricing_dialog(self, selected_items, container_id):
        """Create scrollable dialog for editing existing prices with auto-price options using Treeview"""
        pricing_window = tk.Toplevel(self.window)
        pricing_window.title("✏️ Edit Harga Barang")
        pricing_window.geometry("1300x800")
        pricing_window.configure(bg='#ecf0f1')
        pricing_window.transient(self.window)
        pricing_window.grab_set()
        
        # Center window
        pricing_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (650)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (400)
        pricing_window.geometry(f"1300x800+{x}+{y}")
        
        # CREATE MAIN SCROLLABLE CANVAS FOR ENTIRE DIALOG
        main_canvas = tk.Canvas(pricing_window, bg='#ecf0f1')
        main_scrollbar = ttk.Scrollbar(pricing_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ecf0f1')
        
        # Configure scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_mousewheel_linux(event):
            if event.num == 4:
                main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                main_canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel events
        main_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        main_canvas.bind("<Button-4>", _on_mousewheel_linux)  # Linux
        main_canvas.bind("<Button-5>", _on_mousewheel_linux)  # Linux
        
        # Update canvas scroll region when frame size changes
        def _on_canvas_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)
        
        main_canvas.bind('<Configure>', _on_canvas_configure)
        
        # NOW USE scrollable_frame AS PARENT
        parent_frame = scrollable_frame
        
        # Initialize pricing data storage
        pricing_data_store = {}
        
        # Header
        header = tk.Label(
            parent_frame,
            text="✏️ EDIT HARGA BARANG",
            font=('Arial', 18, 'bold'),
            bg='#f39c12',
            fg='white',
            pady=20
        )
        header.pack(fill='x')
        
        # Info frame
        info_frame = tk.Frame(parent_frame, bg='#ecf0f1')
        info_frame.pack(fill='x', padx=25, pady=15)
        
        info_label = tk.Label(
            info_frame,
            text=f"📝 Mengedit harga untuk {len(selected_items)} barang | 💡 Klik dua kali pada cell untuk edit | 🔄 Gunakan kombinasi satuan + door",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        info_label.pack(anchor='w')
        
        # Create combination controls
        controls_frame = self._create_edit_pricing_controls(parent_frame, pricing_data_store)
        
        # Create main pricing table
        table_frame, pricing_tree = self._create_edit_pricing_table(parent_frame, selected_items, pricing_data_store)
        
        # Setup combination controls with tree reference
        self._setup_edit_pricing_controls(controls_frame, pricing_tree, pricing_data_store)
        
        # Create action buttons
        result = {'confirmed': False, 'pricing_data': {}}
        self._create_edit_pricing_actions(parent_frame, pricing_window, pricing_tree, pricing_data_store, selected_items, result)
        
        # Update canvas scroll region after all widgets are added
        pricing_window.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Focus on canvas to enable mouse wheel
        main_canvas.focus_set()
        
        # Wait for dialog to close
        pricing_window.wait_window()
        
        return result if result['confirmed'] else None

    def _create_edit_pricing_controls(self, parent, pricing_data_store):
        """Create combination pricing controls for edit dialog"""
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill='x', padx=25, pady=10)
        
        # Step 1: Select Satuan (Base Unit)
        satuan_frame = tk.LabelFrame(controls_frame, text="📏 Step 1: Pilih Satuan Dasar", 
                                    font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        satuan_frame.pack(fill='x', pady=(0, 10))
        
        satuan_inner = tk.Frame(satuan_frame, bg='#ecf0f1')
        satuan_inner.pack(fill='x', padx=15, pady=8)
        
        # Step 2: Select Door/Package Type
        door_frame = tk.LabelFrame(controls_frame, text="📦 Step 2: Pilih Tipe Door/Package", 
                                font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        door_frame.pack(fill='x', pady=(0, 10))
        
        door_inner = tk.Frame(door_frame, bg='#ecf0f1')
        door_inner.pack(fill='x', padx=15, pady=8)
        
        # Step 3: Generated Combinations + Manual
        result_frame = tk.LabelFrame(controls_frame, text="🚀 Step 3: Apply Kombinasi atau Manual", 
                                    font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        result_frame.pack(fill='x')
        
        result_inner = tk.Frame(result_frame, bg='#ecf0f1')
        result_inner.pack(fill='x', padx=15, pady=8)
        
        # Manual section with input field and quick buttons
        manual_inner = tk.Frame(result_frame, bg='#ecf0f1')
        manual_inner.pack(fill='x', padx=15, pady=(0, 8))
        
        tk.Label(manual_inner, text="⚡ Quick Manual:", 
                font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left', padx=(0, 10))
        
        # Custom amount input
        custom_frame = tk.Frame(manual_inner, bg='#ecf0f1')
        custom_frame.pack(side='left', padx=(0, 15))
        
        tk.Label(custom_frame, text="💰 Custom:", 
                font=('Arial', 9, 'bold'), bg='#ecf0f1').pack(side='left')
        
        custom_var = tk.StringVar()
        custom_entry = tk.Entry(custom_frame, textvariable=custom_var, 
                            font=('Arial', 9), width=10)
        custom_entry.pack(side='left', padx=(5, 5))
        
        return {
            'controls_frame': controls_frame,
            'satuan_frame': satuan_inner, 
            'door_frame': door_inner, 
            'result_frame': result_inner,
            'manual_frame': manual_inner,
            'custom_var': custom_var,
            'custom_entry': custom_entry
        }

    def _create_edit_pricing_table(self, parent, selected_items, pricing_data_store):
        """Create edit pricing table using Treeview"""
        table_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        table_frame.pack(fill='x', padx=25, pady=15)
        
        # Table title
        title_frame = tk.Frame(table_frame, bg='#34495e')
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text="📋 EDIT DAFTAR BARANG DAN HARGA", 
                font=('Arial', 14, 'bold'), bg='#34495e', fg='white', pady=10).pack()
        
        # Create Treeview with Frame container
        tree_frame = tk.Frame(table_frame, bg='#ffffff', height=300)
        tree_frame.pack(fill='x', padx=10, pady=10)
        tree_frame.pack_propagate(False)  # Fixed height
        
        # Create Treeview
        columns = ('nama_barang', 'colli', 'harga_lama', 'auto_pricing', 'harga_baru', 'total_baru')
        pricing_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Define headings and column widths
        column_config = {
            'nama_barang': ('Nama Barang', 180),
            'colli': ('Colli', 80),
            'harga_lama': ('Harga Lama', 120),
            'auto_pricing': ('Auto Pricing', 120),
            'harga_baru': ('Harga Baru', 120),
            'total_baru': ('Total Baru', 140)
        }
        
        for col, (heading, width) in column_config.items():
            pricing_tree.heading(col, text=heading)
            pricing_tree.column(col, width=width, anchor='w' if col in ['nama_barang'] else 'center')
        
        # Create scrollbars for table
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=pricing_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=pricing_tree.xview)
        
        # Configure scrollbars
        pricing_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack with proper scrollbar layout
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        pricing_tree.pack(side='left', fill='both', expand=True)
        
        # Get barang details and populate table
        barang_details = self._get_edit_barang_details(selected_items)
        self._populate_edit_pricing_table(pricing_tree, selected_items, barang_details, pricing_data_store)
        
        # Setup table editing
        self._setup_edit_table_editing(pricing_tree, pricing_data_store)
        
        return table_frame, pricing_tree

    def _get_edit_barang_details(self, selected_items):
        """Get detailed barang data for edit pricing options"""
        barang_details = {}
        for item in selected_items:
            try:
                barang_data = self.db.execute_one("""
                    SELECT b.*, s.nama_customer AS sender_name, r.nama_customer AS receiver_name
                    FROM barang b 
                    JOIN customers s ON b.pengirim = s.customer_id
                    JOIN customers r ON b.penerima = r.customer_id
                    WHERE b.barang_id = ?
                """, (item['id'],))
                
                if barang_data:
                    barang_details[item['id']] = dict(barang_data)
            except Exception as e:
                print(f"Error getting barang details for {item['id']}: {e}")
                barang_details[item['id']] = {}
        
        return barang_details

    def _populate_edit_pricing_table(self, tree, selected_items, barang_details, pricing_data_store):
        """Populate the edit pricing table with current data"""
        for item in selected_items:
            barang_detail = barang_details.get(item['id'], {})
            
            # Extract pricing data for combinations
            pricing_info = {
                # Combination fields
                'harga_m3_pp': barang_detail.get('m3_pp', 0) or 0,
                'harga_m3_pd': barang_detail.get('m3_pd', 0) or 0,
                'harga_m3_dd': barang_detail.get('m3_dd', 0) or 0,
                'harga_ton_pp': barang_detail.get('ton_pp', 0) or 0,
                'harga_ton_pd': barang_detail.get('ton_pd', 0) or 0,
                'harga_ton_dd': barang_detail.get('ton_dd', 0) or 0,
                'harga_colli_pp': barang_detail.get('col_pp', 0) or 0,
                'harga_colli_pd': barang_detail.get('col_pd', 0) or 0,
                'harga_colli_dd': barang_detail.get('col_dd', 0) or 0,
                # Base measurements
                'm3_barang': barang_detail.get('m3_barang', 0) or 0,
                'ton_barang': barang_detail.get('ton_barang', 0) or 0
            }
            
            # Get current price from item data
            current_price = float(str(item.get('current_harga', 0)).replace(',', ''))
            colli = int(item.get('colli', 1))
            
            # Store data for calculations
            pricing_data_store[item['id']] = {
                'item': item,
                'pricing_info': pricing_info,
                'current_method': 'Manual',
                'current_price': current_price,
                'original_price': current_price,
                'colli_amount': colli
            }
            
            # Calculate initial total
            total_baru = current_price * colli
            
            # Insert into tree
            tree.insert('', tk.END, iid=item['id'], values=(
                item['name'],
                str(colli),
                f"{current_price:,.0f}",
                'Manual',
                f"{current_price:,.0f}",
                f"Rp {total_baru:,.0f}",
            ), tags=('row',))
        
        # Configure row styling
        tree.tag_configure('row', background='#f8f9fa')
        tree.tag_configure('selected', background='#e3f2fd')

    def _setup_edit_table_editing(self, tree, pricing_data_store):
        """Setup double-click editing for edit table cells"""
        def on_double_click(event):
            item_id = tree.selection()[0] if tree.selection() else None
            if not item_id:
                return
            
            # Get clicked column
            region = tree.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            column = tree.identify_column(event.x, event.y)
            
            print("Column: ", column)
            
            # Allow editing for auto_pricing and harga_baru columns
            if column == '#4':  # auto_pricing column
                self._edit_auto_pricing_edit(tree, item_id, pricing_data_store)
            elif column == '#5':  # harga_baru column
                self._edit_harga_baru_edit(tree, item_id, pricing_data_store)
        
        tree.bind('<Double-1>', on_double_click)

    def _edit_auto_pricing_edit(self, tree, item_id, pricing_data_store):
        """Edit auto pricing method for edit dialog"""
        bbox = tree.bbox(item_id, 'auto_pricing')
        if not bbox:
            return
        
        # Create combobox with combination options
        combo_var = tk.StringVar(value=pricing_data_store[item_id]['current_method'])
        combo = ttk.Combobox(tree, textvariable=combo_var, 
                            values=['Manual', 'Harga/m3_pp', 'Harga/m3_pd', 'Harga/m3_dd',
                                'Harga/ton_pp', 'Harga/ton_pd', 'Harga/ton_dd',
                                'Harga/colli_pp', 'Harga/colli_pd', 'Harga/colli_dd'],
                            state='readonly')
        
        combo.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        combo.focus_set()
        
        def on_combo_change(event=None):
            new_method = combo_var.get()
            pricing_data_store[item_id]['current_method'] = new_method
            
            # Auto-set price based on method
            new_price = self._calculate_edit_auto_price(item_id, new_method, pricing_data_store)
            pricing_data_store[item_id]['current_price'] = new_price
            
            # Update tree
            tree.set(item_id, 'auto_pricing', new_method)
            tree.set(item_id, 'harga_baru', f"{new_price:,.0f}")
            
            # Calculate total
            colli = pricing_data_store[item_id]['colli_amount']
            total = new_price * colli
            tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
            
            combo.destroy()
        
        combo.bind('<<ComboboxSelected>>', on_combo_change)
        combo.bind('<Return>', on_combo_change)
        combo.bind('<Escape>', lambda e: combo.destroy())
        combo.bind('<FocusOut>', lambda e: combo.destroy())

    def _edit_harga_baru_edit(self, tree, item_id, pricing_data_store):
        """Edit harga baru for edit dialog"""
        bbox = tree.bbox(item_id, 'harga_baru')
        if not bbox:
            return
        
        # Create entry
        entry_var = tk.StringVar(value=str(int(pricing_data_store[item_id]['current_price'])))
        entry = tk.Entry(tree, textvariable=entry_var)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        def on_entry_confirm(event=None):
            try:
                new_price = float(entry_var.get().replace(',', ''))
                pricing_data_store[item_id]['current_price'] = new_price
                pricing_data_store[item_id]['current_method'] = 'Manual'
                
                # Update tree
                tree.set(item_id, 'harga_baru', f"{new_price:,.0f}")
                tree.set(item_id, 'auto_pricing', 'Manual')
                
                # Calculate total
                colli = pricing_data_store[item_id]['colli_amount']
                total = new_price * colli
                tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
                
            except ValueError:
                pass  # Invalid input, ignore
            
            entry.destroy()
        
        entry.bind('<Return>', on_entry_confirm)
        entry.bind('<Escape>', lambda e: entry.destroy())
        entry.bind('<FocusOut>', lambda e: on_entry_confirm())

    def _calculate_edit_auto_price(self, item_id, method, pricing_data_store):
        """Calculate automatic price for edit dialog based on combination method"""
        pricing_info = pricing_data_store[item_id]['pricing_info']
        
        # Handle combination methods
        if method == 'Harga/m3_pp' and pricing_info['harga_m3_pp'] > 0:
            return pricing_info['harga_m3_pp']
        elif method == 'Harga/m3_pd' and pricing_info['harga_m3_pd'] > 0:
            return pricing_info['harga_m3_pd']
        elif method == 'Harga/m3_dd' and pricing_info['harga_m3_dd'] > 0:
            return pricing_info['harga_m3_dd']
        elif method == 'Harga/ton_pp' and pricing_info['harga_ton_pp'] > 0:
            return pricing_info['harga_ton_pp']
        elif method == 'Harga/ton_pd' and pricing_info['harga_ton_pd'] > 0:
            return pricing_info['harga_ton_pd']
        elif method == 'Harga/ton_dd' and pricing_info['harga_ton_dd'] > 0:
            return pricing_info['harga_ton_dd']
        elif method == 'Harga/colli_pp' and pricing_info['harga_colli_pp'] > 0:
            return pricing_info['harga_colli_pp']
        elif method == 'Harga/colli_pd' and pricing_info['harga_colli_pd'] > 0:
            return pricing_info['harga_colli_pd']
        elif method == 'Harga/colli_dd' and pricing_info['harga_colli_dd'] > 0:
            return pricing_info['harga_colli_dd']
        else:
            # Return original price if no valid combination found
            return pricing_data_store[item_id]['original_price']

    def _setup_edit_pricing_controls(self, controls_frame, pricing_tree, pricing_data_store):
        """Setup combination pricing controls for edit dialog"""
        
        # State variables for combination
        selected_satuan = tk.StringVar()
        selected_door = tk.StringVar()
        
        # Step 1: Satuan selection buttons  
        satuan_types = [
            ("m³", "m3", '#3498db'),
            ("ton", "ton", '#e74c3c'), 
            ("colli", "colli", '#27ae60')
        ]
        
        def select_satuan(satuan_key):
            selected_satuan.set(satuan_key)
            self._update_edit_combination_buttons(controls_frame['result_frame'], 
                                            selected_satuan.get(), selected_door.get(), 
                                            pricing_tree, pricing_data_store)
            # Update button colors
            for btn in satuan_buttons:
                if btn['text'] == satuan_key:
                    btn.configure(relief='sunken', borderwidth=3)
                else:
                    btn.configure(relief='flat', borderwidth=1)
        
        satuan_buttons = []
        for label, key, color in satuan_types:
            btn = tk.Button(
                controls_frame['satuan_frame'],
                text=label,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg='white',
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=lambda k=key: select_satuan(k)
            )
            btn.pack(side='left', padx=5)
            satuan_buttons.append(btn)
        
        # Step 2: Door/Package selection buttons
        door_types = [
            ("PP", "pp", '#9b59b6'),     # Per Pcs
            ("PD", "pd", '#f39c12'),     # Per Dozen  
            ("DD", "dd", '#16a085')      # Per Double Dozen
        ]
        
        def select_door(door_key):
            selected_door.set(door_key)
            self._update_edit_combination_buttons(controls_frame['result_frame'], 
                                            selected_satuan.get(), selected_door.get(), 
                                            pricing_tree, pricing_data_store)
            # Update button colors
            for btn in door_buttons:
                if btn['text'] == door_key.upper():
                    btn.configure(relief='sunken', borderwidth=3)
                else:
                    btn.configure(relief='flat', borderwidth=1)
        
        door_buttons = []
        for label, key, color in door_types:
            btn = tk.Button(
                controls_frame['door_frame'],
                text=label,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg='white',
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=lambda k=key: select_door(k)
            )
            btn.pack(side='left', padx=5)
            door_buttons.append(btn)
        
        # Setup custom amount input
        def apply_custom_amount():
            try:
                amount_str = controls_frame['custom_var'].get().strip()
                if not amount_str:
                    messagebox.showwarning("Input Error", "Masukkan nilai harga!")
                    return
                    
                amount = float(amount_str.replace(',', '').replace('.', ''))
                if amount >= 0:
                    self._edit_quick_fill_manual(pricing_tree, pricing_data_store, amount)
                    controls_frame['custom_var'].set("")
                    messagebox.showinfo("Berhasil", f"Harga manual Rp {amount:,.0f} telah diterapkan ke semua barang!")
                else:
                    messagebox.showwarning("Input Error", "Masukkan angka positif!")
            except ValueError:
                messagebox.showwarning("Input Error", "Masukkan angka yang valid!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menerapkan harga: {str(e)}")
        
        # Create apply button
        custom_btn = tk.Button(
            controls_frame['custom_entry'].master,
            text="✓ Apply",
            font=('Arial', 8, 'bold'),
            bg='#34495e',
            fg='white',
            padx=8,
            pady=3,
            relief='flat',
            cursor='hand2',
            command=apply_custom_amount
        )
        custom_btn.pack(side='left', padx=(0, 5))
        
        # Bind Enter key
        controls_frame['custom_entry'].bind('<Return>', lambda e: apply_custom_amount())
        controls_frame['custom_entry'].bind('<KP_Enter>', lambda e: apply_custom_amount())
        
        # Manual quick fill buttons
        quick_amounts = [50000, 100000, 150000, 200000, 250000, 300000]
        for amount in quick_amounts:
            btn = tk.Button(
                controls_frame['manual_frame'],
                text=f"{amount//1000}K",
                font=('Arial', 9),
                bg='#95a5a6',
                fg='white',
                padx=10,
                pady=5,
                relief='flat',
                cursor='hand2',
                command=lambda a=amount: self._edit_quick_fill_manual(pricing_tree, pricing_data_store, a)
            )
            btn.pack(side='left', padx=2)

    def _update_edit_combination_buttons(self, result_frame, satuan, door, pricing_tree, pricing_data_store):
        """Update combination buttons for edit dialog"""
        # Clear existing buttons
        for widget in result_frame.winfo_children():
            widget.destroy()
        
        if not satuan or not door:
            tk.Label(result_frame, text="👆 Pilih Satuan dan Door/Package untuk melihat kombinasi", 
                    font=('Arial', 10), bg='#ecf0f1', fg='#7f8c8d').pack(pady=10)
            return
        
        # Create info label
        info_text = f"🎯 Kombinasi: {satuan.upper()} × {door.upper()}"
        tk.Label(result_frame, text=info_text, 
                font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=(5, 10))
        
        # Create combination button
        combination_method = f"Harga/{satuan}_{door}"
        combination_text = f"{satuan.upper()}_{door.upper()}"
        
        btn = tk.Button(
            result_frame,
            text=f"🚀 Apply {combination_text}",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=lambda: self._edit_auto_fill_all(pricing_tree, pricing_data_store, combination_method)
        )
        btn.pack(pady=5)

    def _edit_auto_fill_all(self, pricing_tree, pricing_data_store, method):
        """Auto fill all items with selected pricing method for edit dialog"""
        updated_count = 0
        try:
            for item_id in pricing_data_store.keys():
                if pricing_tree.exists(item_id):
                    pricing_data_store[item_id]['current_method'] = method
                    
                    # Calculate new price
                    new_price = self._calculate_edit_auto_price(item_id, method, pricing_data_store)
                    pricing_data_store[item_id]['current_price'] = new_price
                    
                    # Update tree
                    pricing_tree.set(item_id, 'auto_pricing', method)
                    pricing_tree.set(item_id, 'harga_baru', f"{new_price:,.0f}")
                    
                    # Calculate total
                    colli = pricing_data_store[item_id]['colli_amount']
                    total = self._calculate_total_price(item_id, pricing_data_store, colli_amount=colli)
                    pricing_tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
                    
                    updated_count += 1
            
            print(f"Edit auto fill completed: {updated_count} items updated with method {method}")
            messagebox.showinfo("Berhasil", f"Metode {method} telah diterapkan ke {updated_count} barang!")
            
        except Exception as e:
            print(f"Error in _edit_auto_fill_all: {str(e)}")
            messagebox.showerror("Error", f"Gagal menerapkan auto fill: {str(e)}")

    def _edit_quick_fill_manual(self, pricing_tree, pricing_data_store, amount):
        """Quick fill all items with manual amount for edit dialog"""
        updated_count = 0
        try:
            print(f"Starting edit quick fill manual with amount: {amount}")
            
            for item_id in pricing_data_store.keys():
                if pricing_tree.exists(item_id):
                    # Update data store
                    pricing_data_store[item_id]['current_method'] = 'Manual'
                    pricing_data_store[item_id]['current_price'] = amount
                    
                    # Update tree display
                    pricing_tree.set(item_id, 'auto_pricing', 'Manual')
                    pricing_tree.set(item_id, 'harga_baru', f"{amount:,.0f}")
                    
                    # Calculate total
                    colli = pricing_data_store[item_id]['colli_amount']
                    total = amount * colli
                    pricing_tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
                    
                    updated_count += 1
                    print(f"Updated edit item {item_id}: price={amount}, total={total}")
                else:
                    print(f"WARNING: Edit item {item_id} not found in tree")
            
            print(f"Edit manual fill completed: {updated_count} items updated")
            
        except Exception as e:
            print(f"Error in _edit_quick_fill_manual: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal mengisi harga manual: {str(e)}")

    def _create_edit_pricing_actions(self, parent_frame, pricing_window, pricing_tree, pricing_data_store, selected_items, result):
        """Create action buttons for edit pricing dialog"""
        btn_frame = tk.Frame(parent_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', padx=25, pady=20)
        
        # Action buttons
        action_frame = tk.Frame(btn_frame, bg='#ecf0f1')
        action_frame.pack()
        
        def confirm_edit():
            try:
                pricing_data = {}
                total_amount = 0
                changed_items = []
                
                for item_id, data in pricing_data_store.items():
                    if pricing_tree.exists(item_id):
                        current_price = data['current_price']
                        original_price = data['original_price']
                        method = data['current_method']
                        colli = data['colli_amount']
                        total = current_price * colli
                        
                        pricing_data[item_id] = {
                            'harga_per_unit': current_price,
                            'total_harga': total,
                            'metode_pricing': method,
                            'original_price': original_price,
                            'price_changed': current_price != original_price
                        }
                        total_amount += total
                        
                        if current_price != original_price:
                            changed_items.append({
                                'id': item_id,
                                'name': data['item']['name'],
                                'old_price': original_price,
                                'new_price': current_price,
                                'method': method
                            })
                
                if not pricing_data:
                    messagebox.showwarning("Peringatan", "Tidak ada data pricing yang valid!")
                    return
                
                if not changed_items:
                    messagebox.showinfo("Info", "Tidak ada perubahan harga yang perlu disimpan!")
                    return
                
                # Enhanced confirmation dialog
                confirm_msg = f"Konfirmasi perubahan harga:\n\n"
                confirm_msg += f"📊 RINGKASAN PERUBAHAN:\n"
                confirm_msg += f"• Total barang: {len(selected_items)}\n"
                confirm_msg += f"• Barang yang berubah: {len(changed_items)}\n"
                confirm_msg += f"• Total nilai baru: Rp {total_amount:,.0f}\n\n"
                
                # Show detailed changes (max 5 items)
                confirm_msg += f"📋 DETAIL PERUBAHAN:\n"
                for i, item in enumerate(changed_items[:5]):
                    confirm_msg += f"• {item['name'][:30]}{'...' if len(item['name']) > 30 else ''}\n"
                    confirm_msg += f"  Lama: Rp {item['old_price']:,.0f} → Baru: Rp {item['new_price']:,.0f} ({item['method']})\n"
                
                if len(changed_items) > 5:
                    remaining = len(changed_items) - 5
                    confirm_msg += f"... dan {remaining} perubahan lainnya\n"
                
                confirm_msg += f"\n🚀 Simpan perubahan?"
                
                if messagebox.askyesno("Konfirmasi Edit Harga", confirm_msg):
                    result['confirmed'] = True
                    result['pricing_data'] = pricing_data
                    result['changed_count'] = len(changed_items)
                    print(f"Edit pricing confirmed with {len(changed_items)} changes, total: {total_amount}")
                    pricing_window.destroy()
                    
            except Exception as e:
                print(f"Error in confirm_edit: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        def cancel_edit():
            print("Edit pricing canceled by user")
            pricing_window.destroy()
        
        def reset_all_prices():
            """Reset all prices to original values"""
            try:
                reset_count = 0
                for item_id, data in pricing_data_store.items():
                    if pricing_tree.exists(item_id):
                        original_price = data['original_price']
                        
                        # Reset to original values
                        data['current_method'] = 'Manual'
                        data['current_price'] = original_price
                        
                        # Update tree
                        pricing_tree.set(item_id, 'auto_pricing', 'Manual')
                        pricing_tree.set(item_id, 'harga_baru', f"{original_price:,.0f}")
                        
                        # Calculate total
                        colli = data['colli_amount']
                        total = original_price * colli
                        pricing_tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
                        
                        reset_count += 1
                
                messagebox.showinfo("Reset", f"Berhasil mereset {reset_count} barang ke harga asli!")
                
            except Exception as e:
                print(f"Error in reset_all_prices: {str(e)}")
                messagebox.showerror("Error", f"Gagal mereset harga: {str(e)}")
        
        
        tk.Button(
            action_frame,
            text="🔄 Reset Semua",
            font=('Arial', 10, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=reset_all_prices
        ).pack(side='left', padx=(0, 10))
        
        
        tk.Button(
            action_frame,
            text="✅ Simpan Perubahan",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=confirm_edit
        ).pack(side='left', padx=(0, 15))
        
        tk.Button(
            action_frame,
            text="❌ Batal",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=cancel_edit
        ).pack(side='left')
    
    def edit_barang_price_in_container(self):
        """Edit price of selected barang in container"""
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        selection = self.container_barang_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang yang akan diedit harganya!")
            return
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            # Get selected barang details
            selected_items = []
            for item in selection:
                values = self.container_barang_tree.item(item)['values']
                # Find barang_id from database based on customer and nama_barang
                pengirim = values[0]  # Customer column
                penerima = values[1]  # Nama barang column
                nama_barang = values[2]  # Nama barang column
                current_harga = values[7] if len(values) > 6 else "0"  # Current price
                current_total = values[8] if len(values) > 7 else "0"  # Current total
                colli = values[6]  # Colli column
                
                # Get barang_id from database
                barang_data = self.db.execute("""
                    SELECT b.barang_id FROM barang b 
                    JOIN customers s ON b.pengirim = s.customer_id
                    JOIN customers r ON b.penerima = r.customer_id
                    WHERE s.nama_customer = ? AND r.nama_customer = ? AND b.nama_barang = ?
                """, (pengirim, penerima, nama_barang))

                if barang_data:
                    barang_id = barang_data[0][0]
                    selected_items.append({
                        'id': barang_id,
                        'name': nama_barang,
                        'pengirim': pengirim,
                        'penerima': penerima,
                        'current_harga': current_harga,
                        'current_total': current_total,
                        'colli': colli
                    })
            
            if not selected_items:
                messagebox.showerror("Error", "Tidak dapat menemukan data barang yang dipilih!")
                return
            
            # Create edit pricing dialog
            edit_result = self.create_edit_pricing_dialog(selected_items, container_id)
            
            if edit_result and edit_result['confirmed']:
                # Update prices in database
                success_count = 0
                error_count = 0
                
                for barang_id, price_data in edit_result['pricing_data'].items():
                    try:
                        # Update price in detail_container table
                        self.db.execute("""
                            UPDATE detail_container 
                            SET harga_per_unit = ?, total_harga = ? 
                            WHERE barang_id = ? AND container_id = ?
                        """, (
                            price_data['harga_per_unit'], 
                            price_data['total_harga'], 
                            barang_id, 
                            container_id
                        ))
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        print(f"❌ Error updating price for barang {barang_id}: {e}")
                
                # Show result
                if success_count > 0:
                    messagebox.showinfo("Sukses", f"✅ Berhasil mengupdate harga {success_count} barang!")
                    self.load_container_barang(container_id)  # Refresh display
                
                if error_count > 0:
                    messagebox.showwarning("Peringatan", f"❌ {error_count} barang gagal diupdate.")
            
        except Exception as e:
            print(f"Error in edit_barang_price_in_container: {e}")
            messagebox.showerror("Error", f"Gagal mengedit harga: {str(e)}")
    
    def load_customers(self):
        """Load all customers for search dropdown"""
        try:
            # Get unique customers from barang table
            customers = self.db.get_all_customers()
            customer_list = [row['nama_customer'] for row in customers if row['nama_customer']]
            self.sender_search_combo['values'] = customer_list
            self.receiver_search_combo['values'] = customer_list
        except Exception as e:
            print(f"Error loading customers: {e}")
    
    def load_customer_barang_tree(self, sender_name=None, receiver_name=None):
        """Load barang based on sender and/or receiver selection"""
        try:
            # Clear existing items
            for item in self.available_tree.get_children():
                self.available_tree.delete(item)
        
            # Get all barang first
            all_barang = self.db.get_all_barang()
        
            # Show barang based on selection criteria
            filtered_barang_count = 0
            for barang in all_barang:
                try:
                    # Safe way to get values from sqlite3.Row object
                    def safe_get(row, key, default='-'):
                        try:
                            return row[key] if row[key] is not None else default
                        except (KeyError, IndexError):
                            return default
                
                    barang_id = safe_get(barang, 'barang_id', 0)
                    
                    # Get sender and receiver info from barang
                    # Adjust these field names based on your actual database schema
                    barang_sender_id = safe_get(barang, 'pengirim', '')  # or pengirim field
                    barang_sender = self.db.get_customer_by_id(barang_sender_id)['nama_customer'] if barang_sender_id else '-'
                    barang_receiver_id = safe_get(barang, 'penerima', '')     # receiver field name
                    barang_receiver = self.db.get_customer_by_id(barang_receiver_id)['nama_customer'] if barang_receiver_id else '-'
                    
                    print(f"Barang ID: {barang_id}, Sender: {barang_sender}, Receiver: {barang_receiver}")
                    
                    # Filter logic: show barang that match criteria
                    show_barang = True
                    
                    if sender_name and receiver_name:
                        # Both selected: must match both sender AND receiver
                        show_barang = (barang_sender == sender_name and barang_receiver == receiver_name)
                    elif sender_name:
                        # Only sender selected: must match sender
                        show_barang = (barang_sender == sender_name)
                    elif receiver_name:
                        # Only receiver selected: must match receiver
                        show_barang = (barang_receiver == receiver_name)
                    # If neither selected, show all barang (show_barang remains True)
                    
                    if show_barang:
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
                            barang_sender,    # Pengirim column
                            barang_receiver,  # Penerima column
                            nama_barang,      # Nama column
                            dimensi,          # Dimensi column
                            m3_barang,        # Volume column
                            ton_barang        # Berat column
                        ))
                        filtered_barang_count += 1
                    
                except Exception as row_error:
                    print(f"Error processing barang row: {row_error}")
                    continue
        
            # Create descriptive message
            criteria = []
            if sender_name:
                criteria.append(f"Pengirim: {sender_name}")
            if receiver_name:
                criteria.append(f"Penerima: {receiver_name}")
            
            criteria_text = " & ".join(criteria) if criteria else "Semua barang"
            print(f"✅ Loaded {filtered_barang_count} barang dengan kriteria: {criteria_text}")
        
        except Exception as e:
            print(f"❌ Error loading barang tree: {e}")
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
                    pengirim_id = safe_get(barang, 'pengirim', '')
                    penerima_id = safe_get(barang, 'penerima', '')
                    pengirim_name = self.db.get_customer_by_id(pengirim_id)['nama_customer'] if pengirim_id else '-'
                    penerima_name = self.db.get_customer_by_id(penerima_id)['nama_customer'] if penerima_id else '-'
                    nama_barang = safe_get(barang, 'nama_barang', '-')
                    m3_barang = safe_get(barang, 'm3_barang', '-')
                    ton_barang = safe_get(barang, 'ton_barang', '-')

                    print(f"Barang ID: {barang_id}, Pengirim: {pengirim_name}, Penerima: {penerima_name}, Nama Barang: {nama_barang}, kubikasi: {m3_barang}")

                    self.available_tree.insert('', tk.END, values=(
                        barang_id,
                        pengirim_name,
                        penerima_name,
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
        self.selected_container_var.set("")
        self.sender_search_var.set("")
        self.receiver_search_var.set("")
        self.colli_var.set("1")
        self.load_available_barang()
        self.load_container_barang(None)
    
    def add_selected_barang_to_container(self):
        """Add selected barang from treeview to container with pricing"""
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
                # Based on your treeview structure: ID, Pengirim, Penerima, Nama, Dimensi, Volume, Berat
                barang_id = values[0]      # ID column
                barang_sender = values[1]  # Pengirim column
                barang_receiver = values[2] # Penerima column
                barang_name = values[3]    # Nama barang column
                
                # Validate sender/receiver selection if any is selected
                sender_selected = self.sender_search_var.get()
                receiver_selected = self.receiver_search_var.get()
                
                validation_error = False
                error_message = ""
                
                # Check sender validation
                if sender_selected and barang_sender != sender_selected:
                    error_message += f"Pengirim '{barang_sender}' tidak sesuai dengan pilihan '{sender_selected}'. "
                    validation_error = True
                
                # Check receiver validation
                if receiver_selected and barang_receiver != receiver_selected:
                    error_message += f"Penerima '{barang_receiver}' tidak sesuai dengan pilihan '{receiver_selected}'. "
                    validation_error = True
                
                if validation_error:
                    messagebox.showwarning(
                        "Peringatan", 
                        f"Barang '{barang_name}': {error_message.strip()}"
                    )
                    continue
                
                selected_items.append({
                    'id': barang_id,
                    'name': barang_name,
                    'sender': barang_sender,
                    'receiver': barang_receiver
                })
            
            if not selected_items:
                messagebox.showwarning("Peringatan", "Tidak ada barang yang valid untuk ditambahkan!")
                return
            
            # Show pricing dialog
            pricing_result = self.create_pricing_dialog(selected_items, colli_amount)
            
            if not pricing_result:
                return  # User cancelled
            
            # Add barang to container with pricing
            success_count = 0
            error_count = 0
            success_details = []
            error_details = []
            
            for item in selected_items:
                try:
                    barang_id = item['id']
                    price_data = pricing_result['pricing_data'].get(barang_id, {'harga_per_unit': 0, 'total_harga': 0})
                    print("price data: ", price_data)
                    # Add barang to container with pricing
                    success = self.db.assign_barang_to_container_with_pricing(
                        barang_id, 
                        container_id, 
                        price_data['metode_pricing'].split('_')[0].split('/')[1] if 'metode_pricing' in price_data else 'manual',
                        price_data['metode_pricing'].split('_')[1] if 'metode_pricing' in price_data else 'manual',
                        colli_amount,
                        price_data['harga_per_unit'],
                        price_data['total_harga']
                    )
                    
                    if success:
                        success_count += 1
                        success_details.append(f"✅ {item['name']} (ID: {barang_id})")
                        print(f"✅ Added barang {barang_id} ({item['name']}) to container {container_id} with price {price_data['harga_per_unit']}")
                    else:
                        error_count += 1
                        error_details.append(f"❌ {item['name']} (ID: {barang_id}) - Database operation failed")
                        
                except Exception as e:
                    error_count += 1
                    error_details.append(f"❌ {item['name']} (ID: {item['id']}) - {str(e)}")
                    print(f"❌ Error adding barang {item['id']} ({item['name']}): {e}")
            
            # Show detailed result message
            result_msg = ""
            if success_count > 0:
                result_msg += f"🎉 Berhasil menambahkan {success_count} barang ke container!\n"
                result_msg += f"Setiap barang ditambahkan dengan {colli_amount} colli.\n\n"
                result_msg += "Detail berhasil:\n" + "\n".join(success_details[:5])  # Show max 5 items
                if len(success_details) > 5:
                    result_msg += f"\n... dan {len(success_details) - 5} barang lainnya"
            
            if error_count > 0:
                result_msg += f"\n\n❌ {error_count} barang gagal ditambahkan:\n"
                result_msg += "\n".join(error_details[:3])  # Show max 3 error details
                if len(error_details) > 3:
                    result_msg += f"\n... dan {len(error_details) - 3} error lainnya"
            
            # Show appropriate message box
            if success_count > 0 and error_count == 0:
                messagebox.showinfo("Berhasil!", result_msg)
            elif success_count > 0 and error_count > 0:
                messagebox.showwarning("Sebagian Berhasil", result_msg)
            else:
                messagebox.showerror("Gagal", result_msg)
            
            # Clear selections and refresh displays only if there were successful additions
            if success_count > 0:
                # Clear selections
                # self.clear_selection()
                
                # Refresh displays based on current sender/receiver filter
                sender = self.sender_search_var.get() if self.sender_search_var.get() != "" else None
                receiver = self.receiver_search_var.get() if self.receiver_search_var.get() != "" else None
                
                # Refresh available barang list with current filters
                self.load_customer_barang_tree(sender, receiver)
                    
                # Refresh container barang list
                self.load_container_barang(container_id)
                
                # Refresh other lists
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
        self.load_destinations()
        selection = self.selected_container_var.get()
        if selection:
            container_id = int(selection.split(' - ')[0])
            self.load_container_barang(container_id)
            
            # Update label
            container_info = selection.split(' - ', 1)[1] if ' - ' in selection else selection
            self.container_label.config(text=f"📦 Barang dalam Container: {container_info}")
    
    def load_container_barang(self, container_id):
        """Load barang in specific container with pricing"""
        try:
            # Clear existing items
            for item in self.container_barang_tree.get_children():
                self.container_barang_tree.delete(item)
            
            # Load barang in container with pricing
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
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
                    pengirim = safe_get(barang, 'sender_name', '')
                    penerima = safe_get(barang, 'receiver_name', '')
                    nama_barang = safe_get(barang, 'nama_barang', '-')
                    jenis_barang = safe_get(barang, 'jenis_barang', '-')
                    m3_barang = safe_get(barang, 'm3_barang', '-')
                    ton_barang = safe_get(barang, 'ton_barang', '-')
                    satuan = safe_get(barang, 'satuan', '-')
                    door_type = safe_get(barang, 'door_type', '-')
                    colli_amount = safe_get(barang, 'colli_amount', 1)
                    harga_per_unit = safe_get(barang, 'harga_per_unit', 0)
                    total_harga = safe_get(barang, 'total_harga', 0)
                    
                    # Format pricing display
                    harga_display = f"{float(harga_per_unit):,.0f}" if str(harga_per_unit).replace('.', '').isdigit() else harga_per_unit
                    total_display = f"{float(total_harga):,.0f}" if str(total_harga).replace('.', '').isdigit() else total_harga

                    self.container_barang_tree.insert('', tk.END, values=(
                        pengirim,
                        penerima,
                        nama_barang,
                        jenis_barang,
                        satuan,
                        door_type,
                        dimensi,
                        m3_barang,
                        ton_barang,
                        colli_amount,
                        harga_display,
                        total_display,
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
                pengirim = values[0]     # Customer column
                penerima = values[1]     # Receiver column
                nama_barang = values[2]  # Nama barang column
                colli = values[6]        # Colli column
                harga_unit = values[7]   # Harga per unit
                total_harga = values[8]  # Total harga

                # Get barang_id from database
                barang_data = self.db.execute("""
                    SELECT b.barang_id FROM barang b 
                    JOIN customers r ON b.penerima = r.customer_id
                    JOIN customers s ON b.pengirim = s.customer_id
                    WHERE r.nama_customer = ? AND s.nama_customer = ? AND b.nama_barang = ?
                """, (penerima, pengirim, nama_barang))

                if barang_data:
                    barang_id = barang_data[0][0]
                    selected_items.append({
                        'id': barang_id,
                        'nama': nama_barang,
                        'pengirim': pengirim,
                        'penerima': penerima,
                        'colli': colli,
                        'harga_unit': harga_unit,
                        'total_harga': total_harga,
                        'assigned_at': values[9]  # Assigned at timestamp
                    })
            
            # Confirm removal with details including pricing
            if len(selected_items) == 1:
                item = selected_items[0]
                confirm_msg = f"Hapus barang dari container?\n\n" + \
                            f"Barang: {item['nama']}\n" + \
                            f"Pengirim: {item['pengirim']}\n" + \
                            f"Penerima: {item['penerima']}\n" + \
                            f"Colli: {item['colli']}\n" + \
                            f"Harga/Unit: Rp {item['harga_unit']}\n" + \
                            f"Total Harga: Rp {item['total_harga']}\n\n" + \
                            f"Barang akan dikembalikan ke daftar barang tersedia."
            else:
                total_nilai = 0
                confirm_msg = f"Hapus {len(selected_items)} barang dari container?\n\n"
                for i, item in enumerate(selected_items[:3], 1):  # Show max 3 items
                    confirm_msg += f"{i}. {item['nama']} ({item['customer']}) - {item['colli']} colli - Rp {item['total_harga']}\n"
                    try:
                        total_nilai += float(str(item['total_harga']).replace(',', ''))
                    except:
                        pass
                if len(selected_items) > 3:
                    confirm_msg += f"... dan {len(selected_items) - 3} barang lainnya\n"
                confirm_msg += f"\nTotal nilai yang akan dihapus: Rp {total_nilai:,.0f}\n"
                confirm_msg += f"Semua barang akan dikembalikan ke daftar barang tersedia."
            
            if not messagebox.askyesno("Konfirmasi Hapus", confirm_msg):
                return
            
            # Remove barang from container
            success_count = 0
            error_count = 0
            
            for item in selected_items:

                print("Items to remove:")
                print(f" - {item['nama']} (Pengirim: {item['pengirim']}, Penerima: {item['penerima']}, Colli: {item['colli']}, Harga/Unit: Rp {item['harga_unit']}, Total Harga: Rp {item['total_harga']}, Assigned At: {item['assigned_at']})")

                try:
                    # Remove from detail_container table
                    result = self.db.execute(
                        "DELETE FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at = ?",
                        (item['id'], container_id, item['assigned_at'])
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
        """View detailed summary of selected container including pricing"""
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
            
            # Get barang in container with colli and pricing
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
            # Safe way to get values from sqlite3.Row object
            def safe_get(row, key, default=0):
                try:
                    value = row[key]
                    return value if value is not None else default
                except (KeyError, IndexError):
                    return default
            
            # Calculate totals including pricing
            total_volume = 0
            total_weight = 0
            total_colli = 0
            total_nilai = 0
            
            for b in container_barang:
                try:
                    m3_value = safe_get(b, 'm3_barang', 0)
                    total_volume += float(m3_value) if m3_value not in [None, '', '-'] else 0
                    
                    ton_value = safe_get(b, 'ton_barang', 0)
                    total_weight += float(ton_value) if ton_value not in [None, '', '-'] else 0
                    
                    colli_value = safe_get(b, 'colli_amount', 0)
                    total_colli += int(colli_value) if colli_value not in [None, '', '-'] else 0
                    
                    # Calculate total pricing
                    total_harga_value = safe_get(b, 'total_harga', 0)
                    total_nilai += float(total_harga_value) if total_harga_value not in [None, '', '-'] else 0
                    
                except (ValueError, TypeError) as ve:
                    print(f"Error calculating totals for barang: {ve}")
                    continue
            
            # Group by customer with pricing
            customer_summary = {}
            for barang in container_barang:
                try:
                    customer = safe_get(barang, 'nama_customer', 'Unknown Customer')
                    
                    if customer not in customer_summary:
                        customer_summary[customer] = {
                            'count': 0,
                            'volume': 0,
                            'weight': 0,
                            'colli': 0,
                            'nilai': 0
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
                    
                    try:
                        nilai_value = safe_get(barang, 'total_harga', 0)
                        customer_summary[customer]['nilai'] += float(nilai_value) if nilai_value not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                        
                except Exception as customer_error:
                    print(f"Error processing customer summary for barang: {customer_error}")
                    continue
            
            self.show_container_summary_dialog_with_pricing(container, container_barang, customer_summary, 
                                            total_volume, total_weight, total_colli, total_nilai)
            
        except Exception as e:
            print(f"Error in view_container_summary: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal membuat summary container: {str(e)}")

    def show_container_summary_dialog_with_pricing(self, container, barang_list, customer_summary, total_volume, total_weight, total_colli, total_nilai):
        """Show container summary in a dialog with pricing information"""
        try:
            summary_window = tk.Toplevel(self.window)
            summary_window.title(f"📊 Summary Container - {container.get('container', 'N/A') if hasattr(container, 'get') else container['container'] if 'container' in container else 'N/A'}")
            summary_window.geometry("1000x750")
            summary_window.configure(bg='#ecf0f1')
            summary_window.transient(self.window)
            summary_window.grab_set()
            
            # Center window
            summary_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (500)
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (375)
            summary_window.geometry(f"1000x750+{x}+{y}")
            
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
            
            # Tab 1: Overview with Pricing
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
            
            # Summary stats with pricing
            stats_frame = tk.Frame(overview_frame, bg='#ffffff', relief='solid', bd=1)
            stats_frame.pack(fill='x', padx=10, pady=10)
            
            tk.Label(stats_frame, text="📊 STATISTIK MUATAN & NILAI", font=('Arial', 14, 'bold'), bg='#ffffff').pack(pady=10)
            
            stats_lines = [
                f"Total Barang: {len(barang_list)} items",
                f"Total Volume: {total_volume:.3f} m³", 
                f"Total Berat: {total_weight:.3f} ton",
                f"Total Colli: {total_colli} kemasan",
                f"Total Nilai: Rp {total_nilai:,.0f}",  # NEW PRICING INFO
                f"Jumlah Customer: {len(customer_summary)}"
            ]
            stats_text = "\n".join(stats_lines)
            
            tk.Label(stats_frame, text=stats_text.strip(), font=('Arial', 12, 'bold'), bg='#ffffff', justify='left').pack(padx=20, pady=10)
            
            # Tab 2: Customer Summary with Pricing
            customer_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(customer_frame, text='👥 Per Customer')
            
            tk.Label(customer_frame, text="👥 RINGKASAN PER CUSTOMER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            # Customer summary tree with pricing
            customer_tree_container = tk.Frame(customer_frame, bg='#ecf0f1')
            customer_tree_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            customer_summary_tree = ttk.Treeview(customer_tree_container,
                                            columns=('Customer', 'Items', 'Volume', 'Weight', 'Colli', 'Nilai'),
                                            show='headings', height=15)
            
            customer_summary_tree.heading('Customer', text='Customer')
            customer_summary_tree.heading('Items', text='Jumlah Barang')
            customer_summary_tree.heading('Volume', text='Volume (m³)')
            customer_summary_tree.heading('Weight', text='Berat (ton)')
            customer_summary_tree.heading('Colli', text='Total Colli')
            customer_summary_tree.heading('Nilai', text='Total Nilai (Rp)')
            
            customer_summary_tree.column('Customer', width=180)
            customer_summary_tree.column('Items', width=100)
            customer_summary_tree.column('Volume', width=100)
            customer_summary_tree.column('Weight', width=100)
            customer_summary_tree.column('Colli', width=100)
            customer_summary_tree.column('Nilai', width=150)
            
            # Add customer data with pricing
            for customer, data in customer_summary.items():
                customer_summary_tree.insert('', tk.END, values=(
                    customer,
                    data['count'],
                    f"{data['volume']:.3f}",
                    f"{data['weight']:.3f}",
                    data['colli'],
                    f"{data['nilai']:,.0f}"
                ))
            
            # Scrollbar for customer tree
            customer_v_scroll = ttk.Scrollbar(customer_tree_container, orient='vertical', command=customer_summary_tree.yview)
            customer_summary_tree.configure(yscrollcommand=customer_v_scroll.set)
            
            customer_summary_tree.pack(side='left', fill='both', expand=True)
            customer_v_scroll.pack(side='right', fill='y')
            
            # Tab 3: Detailed Items with Pricing
            items_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(items_frame, text='📦 Detail Barang')
            
            tk.Label(items_frame, text="📦 DETAIL SEMUA BARANG DENGAN HARGA", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            # Items detail tree with pricing
            items_tree_container = tk.Frame(items_frame, bg='#ecf0f1')
            items_tree_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            items_detail_tree = ttk.Treeview(items_tree_container,
                                        columns=('Customer', 'Nama', 'Jenis', 'Dimensi', 'Volume', 'Weight', 'Colli', 'Harga_Unit', 'Total_Harga', 'Added'),
                                        show='headings', height=15)
            
            items_detail_tree.heading('Customer', text='Customer')
            items_detail_tree.heading('Nama', text='Nama Barang')
            items_detail_tree.heading('Jenis', text='Jenis')
            items_detail_tree.heading('Dimensi', text='P×L×T (cm)')
            items_detail_tree.heading('Volume', text='Volume (m³)')
            items_detail_tree.heading('Weight', text='Berat (ton)')
            items_detail_tree.heading('Colli', text='Colli')
            items_detail_tree.heading('Harga_Unit', text='Harga/Unit')
            items_detail_tree.heading('Total_Harga', text='Total Harga')
            items_detail_tree.heading('Added', text='Ditambahkan')
            
            items_detail_tree.column('Customer', width=90)
            items_detail_tree.column('Nama', width=120)
            items_detail_tree.column('Jenis', width=80)
            items_detail_tree.column('Dimensi', width=70)
            items_detail_tree.column('Volume', width=60)
            items_detail_tree.column('Weight', width=60)
            items_detail_tree.column('Colli', width=50)
            items_detail_tree.column('Harga_Unit', width=80)
            items_detail_tree.column('Total_Harga', width=90)
            items_detail_tree.column('Added', width=70)
            
            # Add items data with safe access including pricing
            def safe_barang_get(barang, key, default='-'):
                try:
                    value = barang[key]
                    return value if value is not None else default
                except (KeyError, IndexError):
                    return default
            
            # Add items data with pricing
            for barang in barang_list:
                try:
                    panjang = safe_barang_get(barang, 'panjang_barang', '-')
                    lebar = safe_barang_get(barang, 'lebar_barang', '-')
                    tinggi = safe_barang_get(barang, 'tinggi_barang', '-')
                    dimensi = f"{panjang}×{lebar}×{tinggi}"
                    
                    assigned_at = safe_barang_get(barang, 'assigned_at', '')
                    added_date = assigned_at[:10] if assigned_at and len(str(assigned_at)) >= 10 else '-'
                    
                    # Format pricing for display
                    harga_unit = safe_barang_get(barang, 'harga_per_unit', 0)
                    total_harga = safe_barang_get(barang, 'total_harga', 0)
                    
                    harga_unit_display = f"{float(harga_unit):,.0f}" if str(harga_unit).replace('.', '').isdigit() else str(harga_unit)
                    total_harga_display = f"{float(total_harga):,.0f}" if str(total_harga).replace('.', '').isdigit() else str(total_harga)
                    
                    items_detail_tree.insert('', tk.END, values=(
                        safe_barang_get(barang, 'nama_customer', '-'),
                        safe_barang_get(barang, 'nama_barang', '-'),
                        safe_barang_get(barang, 'jenis_barang', '-'),
                        dimensi,
                        safe_barang_get(barang, 'm3_barang', '-'),
                        safe_barang_get(barang, 'ton_barang', '-'),
                        safe_barang_get(barang, 'colli_amount', '-'),
                        harga_unit_display,
                        total_harga_display,
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
        try:
            self.db.execute_insert(
                "INSERT INTO containers (kapal_feeder, container, seal, ref_joa) VALUES (?, ?, ?, ?)", 
                (
                    self.kapal_var.get(),
                    self.container_entry.get(),
                    self.seal_entry.get(),
                    self.ref_joa_entry.get()
                )
            )

            # Jika berhasil, refresh form & combo
            self.clear_form()
            self.load_containers()
            self.load_container_combo()  # Refresh combo
            
            if self.refresh_callback:
                self.refresh_callback()

        except sqlite3.Error as e:
            # Tampilkan pesan error ke user
            messagebox.showerror("Database Error", f"Gagal menambahkan container:\n{str(e)}")

            
    def edit_container(self):
        """Edit selected container - opens dialog"""
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
        
        # Open edit dialog
        self.show_edit_container_dialog(container_id, container)

    def show_edit_container_dialog(self, container_id, container):
        """Show container edit dialog with only feeder, container, seal, ref_joa"""
        try:
            edit_window = tk.Toplevel(self.window)
            edit_window.title(f"✏️ Edit Container - ID: {container_id}")
            edit_window.geometry("600x400")
            edit_window.configure(bg='#ecf0f1')
            edit_window.transient(self.window)
            edit_window.grab_set()

            # Center dialog
            edit_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - 300
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - 200
            edit_window.geometry(f"600x400+{x}+{y}")

            # Helper
            def safe_get(value):
                return str(value) if value is not None else ""

            # Header
            tk.Label(
                edit_window,
                text=f"✏️ EDIT CONTAINER - ID: {container_id}",
                font=('Arial', 16, 'bold'),
                bg='#3498db',
                fg='white',
                pady=15
            ).pack(fill='x')

            # Form frame
            form_frame = tk.Frame(edit_window, bg='#ffffff', relief='solid', bd=1)
            form_frame.pack(fill='both', expand=True, padx=20, pady=20)

            # Dictionary to store entry widgets
            entries = {}

            # Fields to show
            fields = [
                ('Feeder', 'kapal_feeder'),
                ('Container', 'container'),
                ('Seal', 'seal'),
                ('Ref JOA', 'ref_joa')
            ]

            for label_text, field_name in fields:
                row = tk.Frame(form_frame, bg='#ffffff')
                row.pack(fill='x', pady=8, padx=20)

                tk.Label(row, text=f"{label_text}:", font=('Arial', 11, 'bold'), bg='#ffffff', width=15, anchor='w').pack(side='left')
                entry = tk.Entry(row, font=('Arial', 11), width=30)
                entry.pack(side='left', padx=(10, 0))

                # Fill current value
                if isinstance(container, dict):
                    entry.insert(0, safe_get(container.get(field_name)))
                else:
                    entry.insert(0, safe_get(getattr(container, field_name, "")))

                entries[field_name] = entry

            # Buttons
            btn_frame = tk.Frame(edit_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', pady=15, padx=20)

            # Save function
            def save_container():
                try:
                    if not messagebox.askyesno("Konfirmasi Update", f"Simpan perubahan untuk container ID {container_id}?"):
                        return

                    self.db.execute("""
                        UPDATE containers SET 
                        kapal_feeder = ?, container = ?, seal = ?, ref_joa = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE container_id = ?
                    """, (
                        entries['kapal_feeder'].get().strip(),
                        entries['container'].get().strip(),
                        entries['seal'].get().strip(),
                        entries['ref_joa'].get().strip(),
                        container_id
                    ))

                    messagebox.showinfo("Sukses", "✅ Container berhasil diupdate!")
                    self.load_containers()
                    self.load_container_combo()
                    if self.refresh_callback:
                        self.refresh_callback()
                    edit_window.destroy()

                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menyimpan perubahan: {str(e)}")

            tk.Button(btn_frame, text="💾 Simpan Perubahan", bg='#27ae60', fg='white',
                    font=('Arial', 12, 'bold'), padx=20, pady=10, command=save_container).pack(side='left', padx=(0,10))

            tk.Button(btn_frame, text="❌ Tutup", bg='#e74c3c', fg='white',
                    font=('Arial', 12, 'bold'), padx=20, pady=10, command=edit_window.destroy).pack(side='right')

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat dialog edit: {str(e)}")

    def is_valid_date_format(self, date_string):
        """Validate date format YYYY-MM-DD"""
        if not date_string:
            return True  # Empty is valid
        
        try:
            from datetime import datetime
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
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
        self.container_entry.delete(0, tk.END)
        self.seal_entry.delete(0, tk.END)
        self.ref_joa_entry.delete(0, tk.END)
        
        # Clear editing state
        if hasattr(self, 'editing_container_id'):
            delattr(self, 'editing_container_id')
        
    
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
                    container.get('kapal_feeder', '-'),
                    container.get('container', '-'),
                    container.get('ref_joa', '-'),
                    f"{item_count} items"  # Show item count
                ))
        except Exception as e:
            print(f"Error loading containers: {e}")
            messagebox.showerror("Error", f"Gagal memuat daftar container: {str(e)}")
