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
        self.window.geometry("1400x800")  # Lebih besar untuk accommodate barang
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
        self.container_tree.heading('Items', text='Jumlah Barang')  # New column
        
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
            command=self.add_barang_to_container
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
                                                columns=('ID', 'Customer', 'Nama', 'Dimensi', 'Volume', 'Berat', 'Tanggal'),
                                                show='headings', height=12)
        
        self.container_barang_tree.heading('ID', text='ID')
        self.container_barang_tree.heading('Customer', text='Customer')
        self.container_barang_tree.heading('Nama', text='Nama Barang')
        self.container_barang_tree.heading('Dimensi', text='P×L×T (cm)')
        self.container_barang_tree.heading('Volume', text='Volume (m³)')
        self.container_barang_tree.heading('Berat', text='Berat (ton)')
        self.container_barang_tree.heading('Tanggal', text='Ditambahkan')
        
        self.container_barang_tree.column('ID', width=40)
        self.container_barang_tree.column('Customer', width=100)
        self.container_barang_tree.column('Nama', width=130)
        self.container_barang_tree.column('Dimensi', width=80)
        self.container_barang_tree.column('Volume', width=70)
        self.container_barang_tree.column('Berat', width=70)
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
            
            # Get barang that are already in containers
            barang_in_containers = set()
            containers = self.db.get_all_containers()
            for container in containers:
                container_barang = self.db.get_barang_in_container(container['container_id'])
                for barang in container_barang:
                    barang_in_containers.add(barang['barang_id'])
            
            # Show only available barang
            for barang in all_barang:
                if barang['barang_id'] not in barang_in_containers:
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
            container_barang = self.db.get_barang_in_container(container_id)
            
            for barang in container_barang:
                # Format dimensions
                dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
                
                # Format date
                assigned_date = barang.get('assigned_at', '')[:10] if barang.get('assigned_at') else '-'
                
                self.container_barang_tree.insert('', tk.END, values=(
                    barang['barang_id'],
                    barang['nama_customer'],
                    barang['nama_barang'],
                    dimensi,
                    barang.get('m3_barang', '-'),
                    barang.get('ton_barang', '-'),
                    assigned_date
                ))
        except Exception as e:
            print(f"Error loading container barang: {e}")
            messagebox.showerror("Error", f"Gagal memuat barang dalam container: {str(e)}")
    
    def add_barang_to_container(self):
        """Add selected barang to selected container"""
        # Check if container is selected
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        # Check if barang is selected
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang yang akan ditambahkan ke container!")
            return
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            for item in selection:
                barang_id = self.available_tree.item(item)['values'][0]
                
                # Add barang to container
                success = self.db.assign_barang_to_container(barang_id, container_id)
                
                if not success:
                    messagebox.showwarning("Peringatan", f"Barang ID {barang_id} sudah ada dalam container ini!")
                    continue
            
            messagebox.showinfo("Sukses", f"{len(selection)} barang berhasil ditambahkan ke container!")
            
            # Refresh displays
            self.load_available_barang()
            self.load_container_barang(container_id)
            self.load_containers()  # Refresh container list to update item count
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus barang dari container: {str(e)}")
    
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
                selected_items.append({
                    'id': barang_id,
                    'nama': nama_barang,
                    'customer': customer
                })
            
            # Confirm removal with details
            if len(selected_items) == 1:
                item = selected_items[0]
                confirm_msg = f"Hapus barang dari container?\n\n" + \
                            f"Barang: {item['nama']}\n" + \
                            f"Customer: {item['customer']}\n\n" + \
                            f"Barang akan dikembalikan ke daftar barang tersedia."
            else:
                confirm_msg = f"Hapus {len(selected_items)} barang dari container?\n\n"
                for i, item in enumerate(selected_items[:3], 1):  # Show max 3 items
                    confirm_msg += f"{i}. {item['nama']} ({item['customer']})\n"
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
            
            # Get barang in container
            container_barang = self.db.get_barang_in_container(container_id)
            
            # Calculate totals
            total_volume = sum(float(b.get('m3_barang', 0) or 0) for b in container_barang)
            total_weight = sum(float(b.get('ton_barang', 0) or 0) for b in container_barang)
            total_colli = sum(int(b.get('col_barang', 0) or 0) for b in container_barang)
            
            # Group by customer
            customer_summary = {}
            for barang in container_barang:
                customer = barang['nama_customer']
                if customer not in customer_summary:
                    customer_summary[customer] = {
                        'count': 0,
                        'volume': 0,
                        'weight': 0,
                        'colli': 0
                    }
                customer_summary[customer]['count'] += 1
                customer_summary[customer]['volume'] += float(barang.get('m3_barang', 0) or 0)
                customer_summary[customer]['weight'] += float(barang.get('ton_barang', 0) or 0)
                customer_summary[customer]['colli'] += int(barang.get('col_barang', 0) or 0)
            
            self.show_container_summary_dialog(container, container_barang, customer_summary, 
                                             total_volume, total_weight, total_colli)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat summary container: {str(e)}")
    
    def show_container_summary_dialog(self, container, barang_list, customer_summary, total_volume, total_weight, total_colli):
        """Show container summary in a dialog"""
        summary_window = tk.Toplevel(self.window)
        summary_window.title(f"📊 Summary Container - {container.get('container', 'N/A')}")
        summary_window.geometry("900x700")
        summary_window.configure(bg='#ecf0f1')
        summary_window.transient(self.window)
        summary_window.grab_set()
        
        # Center window
        summary_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (900 // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (700 // 2)
        summary_window.geometry(f"900x700+{x}+{y}")
        
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
        
        info_text = f"""
Container: {container.get('container', '-')}
Feeder: {container.get('feeder', '-')}
Destination: {container.get('destination', '-')}
Party: {container.get('party', '-')}
ETD Sub: {container.get('etd_sub', '-')}
CLS: {container.get('cls', '-')}
Open: {container.get('open', '-')}
Full: {container.get('full', '-')}
Seal: {container.get('seal', '-')}
Ref JOA: {container.get('ref_joa', '-')}
        """
        
        tk.Label(info_frame, text=info_text.strip(), font=('Arial', 10), bg='#ffffff', justify='left').pack(padx=20, pady=10)
        
        # Summary stats
        stats_frame = tk.Frame(overview_frame, bg='#ffffff', relief='solid', bd=1)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(stats_frame, text="📊 STATISTIK MUATAN", font=('Arial', 14, 'bold'), bg='#ffffff').pack(pady=10)
        
        stats_text = f"""
Total Barang: {len(barang_list)} items
Total Volume: {total_volume:.3f} m³
Total Berat: {total_weight:.3f} ton
Total Colli: {total_colli} kemasan
Jumlah Customer: {len(customer_summary)}
        """
        
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
        customer_summary_tree.heading('Colli', text='Colli')
        
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
        
        # Tab 3: Detailed Items
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
        
        # Add items data
        for barang in barang_list:
            dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
            added_date = barang.get('assigned_at', '')[:10] if barang.get('assigned_at') else '-'
            
            items_detail_tree.insert('', tk.END, values=(
                barang['barang_id'],
                barang['nama_customer'],
                barang['nama_barang'],
                barang.get('jenis_barang', '-'),
                dimensi,
                barang.get('m3_barang', '-'),
                barang.get('ton_barang', '-'),
                barang.get('col_barang', '-'),
                added_date
            ))
        
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
            messagebox.showerror("Error", f"Gagal menambahkan container: {str(e)}")
    
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