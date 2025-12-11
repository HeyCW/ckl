import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.utils.helpers import format_ton, setup_window_restore_behavior

class CustomerOrdersWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.selected_customer_id = None
        self.selected_container_id = None
        self.create_window()

    def create_window(self):
        """Create the main window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📊 Customer Orders Management")
        self.window.configure(bg="#ecf0f1")

        # Setup window restore behavior (fix minimize/restore issue)
        setup_window_restore_behavior(self.window)

        # Responsive window sizing
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Window size: 85% of screen
        width = int(screen_width * 0.85)
        height = int(screen_height * 0.85)

        # Center position
        x_pos = int((screen_width - width) / 2)
        y_pos = int((screen_height - height) / 2)

        self.window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

        # Responsive minimum size
        min_width = max(1000, int(screen_width * 0.6))
        min_height = max(600, int(screen_height * 0.5))
        self.window.minsize(min_width, min_height)

        # Allow resizing
        self.window.resizable(True, True)

        # Responsive scaling
        scale = max(0.8, min(screen_width / 1920, 1.2))

        # Fonts
        font_title = ("Arial", max(16, int(18 * scale)), "bold")
        font_header = ("Arial", max(12, int(13 * scale)), "bold")
        font_normal = ("Arial", max(10, int(11 * scale)))

        # Header
        header_frame = tk.Frame(self.window, bg="#27ae60")
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="📊 CUSTOMER ORDERS MANAGEMENT",
            font=font_title,
            bg="#27ae60",
            fg="white",
            pady=max(12, int(15 * scale))
        )
        title_label.pack()

        # Main container with 3 panels
        main_container = tk.Frame(self.window, bg="#ecf0f1")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Configure grid weights for responsive layout
        main_container.columnconfigure(0, weight=1, minsize=max(250, int(screen_width * 0.15)))
        main_container.columnconfigure(1, weight=2, minsize=max(350, int(screen_width * 0.25)))
        main_container.columnconfigure(2, weight=3, minsize=max(400, int(screen_width * 0.30)))
        main_container.rowconfigure(0, weight=1)

        # ===== LEFT PANEL - CUSTOMER LIST =====
        customer_frame = ttk.LabelFrame(
            main_container,
            text="👥 Daftar Customer",
            padding="10"
        )
        customer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))

        # Search customer
        search_frame = ttk.Frame(customer_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="🔍 Cari:", font=font_normal).pack(side=tk.LEFT, padx=(0, 5))
        self.customer_search_var = tk.StringVar()
        self.customer_search_var.trace('w', lambda *args: self.filter_customers())
        customer_search = ttk.Entry(search_frame, textvariable=self.customer_search_var)
        customer_search.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Customer listbox
        customer_list_frame = ttk.Frame(customer_frame)
        customer_list_frame.pack(fill=tk.BOTH, expand=True)

        customer_scroll = ttk.Scrollbar(customer_list_frame)
        customer_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.customer_listbox = tk.Listbox(
            customer_list_frame,
            yscrollcommand=customer_scroll.set,
            font=font_normal,
            selectmode=tk.SINGLE
        )
        self.customer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        customer_scroll.config(command=self.customer_listbox.yview)

        self.customer_listbox.bind('<<ListboxSelect>>', self.on_customer_select)

        # Refresh button
        ttk.Button(
            customer_frame,
            text="🔄 Refresh",
            command=self.load_customers
        ).pack(fill=tk.X, pady=(10, 0))

        # ===== MIDDLE PANEL - CONTAINER LIST =====
        container_frame = ttk.LabelFrame(
            main_container,
            text="📦 Container",
            padding="10"
        )
        container_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 8))

        # Container info label
        self.container_info_label = ttk.Label(
            container_frame,
            text="← Pilih customer untuk melihat container",
            font=font_normal,
            foreground="gray"
        )
        self.container_info_label.pack(pady=(0, 10))

        # Container tree
        container_tree_frame = ttk.Frame(container_frame)
        container_tree_frame.pack(fill=tk.BOTH, expand=True)

        container_scroll_y = ttk.Scrollbar(container_tree_frame, orient=tk.VERTICAL)
        container_scroll_x = ttk.Scrollbar(container_tree_frame, orient=tk.HORIZONTAL)

        container_columns = ('container', 'kapal', 'ref_joa', 'party')
        self.container_tree = ttk.Treeview(
            container_tree_frame,
            columns=container_columns,
            show='headings',
            yscrollcommand=container_scroll_y.set,
            xscrollcommand=container_scroll_x.set
        )

        container_scroll_y.config(command=self.container_tree.yview)
        container_scroll_x.config(command=self.container_tree.xview)

        # Configure columns
        self.container_tree.heading('container', text='Container')
        self.container_tree.heading('kapal', text='Kapal')
        self.container_tree.heading('ref_joa', text='REF JOA')
        self.container_tree.heading('party', text='Party')

        # Responsive column widths
        col_width = max(80, int(100 * scale))
        self.container_tree.column('container', width=int(col_width * 1.2), minwidth=90)
        self.container_tree.column('kapal', width=int(col_width * 1.3), minwidth=100)
        self.container_tree.column('ref_joa', width=int(col_width * 1.0), minwidth=80)
        self.container_tree.column('party', width=int(col_width * 0.8), minwidth=60)

        self.container_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        container_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        container_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.container_tree.bind('<<TreeviewSelect>>', self.on_container_select)

        # ===== RIGHT PANEL - BARANG LIST =====
        barang_frame = ttk.LabelFrame(
            main_container,
            text="📋 Detail Barang",
            padding="10"
        )
        barang_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))

        # Barang info label
        self.barang_info_label = ttk.Label(
            barang_frame,
            text="← Pilih container untuk melihat barang",
            font=font_normal,
            foreground="gray"
        )
        self.barang_info_label.pack(pady=(0, 10))

        # Barang tree
        barang_tree_frame = ttk.Frame(barang_frame)
        barang_tree_frame.pack(fill=tk.BOTH, expand=True)

        barang_scroll_y = ttk.Scrollbar(barang_tree_frame, orient=tk.VERTICAL)
        barang_scroll_x = ttk.Scrollbar(barang_tree_frame, orient=tk.HORIZONTAL)

        barang_columns = ('nama_barang', 'colli', 'm3', 'ton', 'harga')
        self.barang_tree = ttk.Treeview(
            barang_tree_frame,
            columns=barang_columns,
            show='headings',
            yscrollcommand=barang_scroll_y.set,
            xscrollcommand=barang_scroll_x.set
        )

        barang_scroll_y.config(command=self.barang_tree.yview)
        barang_scroll_x.config(command=self.barang_tree.xview)

        # Configure columns
        self.barang_tree.heading('nama_barang', text='Nama Barang')
        self.barang_tree.heading('colli', text='Colli')
        self.barang_tree.heading('m3', text='M³')
        self.barang_tree.heading('ton', text='Ton')
        self.barang_tree.heading('harga', text='Harga')

        # Responsive column widths
        self.barang_tree.column('nama_barang', width=int(col_width * 2.0), minwidth=150, anchor=tk.W)
        self.barang_tree.column('colli', width=int(col_width * 0.7), minwidth=60, anchor=tk.CENTER)
        self.barang_tree.column('m3', width=int(col_width * 0.8), minwidth=70, anchor=tk.E)
        self.barang_tree.column('ton', width=int(col_width * 0.8), minwidth=70, anchor=tk.E)
        self.barang_tree.column('harga', width=int(col_width * 1.2), minwidth=100, anchor=tk.E)

        self.barang_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barang_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        barang_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Summary frame at bottom of barang panel
        summary_frame = ttk.Frame(barang_frame)
        summary_frame.pack(fill=tk.X, pady=(10, 0))

        self.summary_label = ttk.Label(
            summary_frame,
            text="Total: 0 item | Rp 0",
            font=font_header,
            foreground="#27ae60"
        )
        self.summary_label.pack()

        # Load initial data
        self.load_customers()

    def load_customers(self):
        """Load all customers who have orders (have barang)"""
        try:
            query = """
                SELECT DISTINCT
                    c.customer_id,
                    c.nama_customer,
                    COUNT(DISTINCT b.barang_id) as total_barang,
                    COUNT(DISTINCT cont.container_id) as total_container
                FROM customers c
                INNER JOIN barang b ON b.pengirim = c.customer_id
                INNER JOIN detail_container dc ON dc.barang_id = b.barang_id
                INNER JOIN containers cont ON cont.container_id = dc.container_id
                GROUP BY c.customer_id, c.nama_customer
                ORDER BY c.nama_customer
            """

            customers = self.db.execute(query)

            # Store full customer data
            self.customer_data = {}

            self.customer_listbox.delete(0, tk.END)

            for row in customers:
                customer_id = row['customer_id']
                customer_name = row['nama_customer']
                total_barang = row['total_barang']
                total_container = row['total_container']

                display_text = f"{customer_name} ({total_container} container, {total_barang} item)"

                self.customer_data[display_text] = {
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'total_barang': total_barang,
                    'total_container': total_container
                }

                self.customer_listbox.insert(tk.END, display_text)

            print(f"✅ Loaded {len(customers)} customers with orders")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data customer:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def filter_customers(self):
        """Filter customer list based on search"""
        search_text = self.customer_search_var.get().lower()

        self.customer_listbox.delete(0, tk.END)

        for display_text, data in self.customer_data.items():
            if search_text in display_text.lower():
                self.customer_listbox.insert(tk.END, display_text)

    def on_customer_select(self, event):
        """Handle customer selection"""
        selection = self.customer_listbox.curselection()
        if not selection:
            return

        selected_text = self.customer_listbox.get(selection[0])
        customer_data = self.customer_data.get(selected_text)

        if not customer_data:
            return

        self.selected_customer_id = customer_data['customer_id']
        customer_name = customer_data['customer_name']

        # Update info label
        self.container_info_label.config(
            text=f"📦 Container milik: {customer_name}",
            foreground="#2c3e50"
        )

        # Load containers for this customer
        self.load_containers(self.selected_customer_id)

        # Clear barang tree
        for item in self.barang_tree.get_children():
            self.barang_tree.delete(item)

        self.barang_info_label.config(
            text="← Pilih container untuk melihat barang",
            foreground="gray"
        )
        self.summary_label.config(text="Total: 0 item | Rp 0")

    def load_containers(self, customer_id):
        """Load containers for selected customer"""
        try:
            # Clear existing data
            for item in self.container_tree.get_children():
                self.container_tree.delete(item)

            query = """
                SELECT DISTINCT
                    cont.container_id,
                    cont.container,
                    k.feeder as kapal_name,
                    cont.ref_joa,
                    cont.party
                FROM containers cont
                LEFT JOIN kapals k ON k.kapal_id = cont.kapal_id
                INNER JOIN detail_container dc ON dc.container_id = cont.container_id
                INNER JOIN barang b ON b.barang_id = dc.barang_id
                WHERE b.pengirim = ?
                ORDER BY cont.container
            """

            containers = self.db.execute(query, (customer_id,))

            for row in containers:
                self.container_tree.insert('', 'end', values=(
                    row['container'] or '-',
                    row['kapal_name'] or '-',
                    row['ref_joa'] or '-',
                    row['party'] or '-'
                ), tags=(row['container_id'],))

            print(f"✅ Loaded {len(containers)} containers for customer {customer_id}")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data container:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def on_container_select(self, event):
        """Handle container selection"""
        selection = self.container_tree.selection()
        if not selection:
            return

        # Get container_id from tags
        item = selection[0]
        tags = self.container_tree.item(item, 'tags')

        if not tags:
            return

        self.selected_container_id = tags[0]
        container_name = self.container_tree.item(item, 'values')[0]

        # Update info label
        self.barang_info_label.config(
            text=f"📋 Barang dalam container: {container_name}",
            foreground="#2c3e50"
        )

        # Load barang for this container
        self.load_barang(self.selected_container_id)

    def load_barang(self, container_id):
        """Load barang for selected container"""
        try:
            # Clear existing data
            for item in self.barang_tree.get_children():
                self.barang_tree.delete(item)

            query = """
                SELECT
                    b.nama_barang,
                    dc.colli_amount,
                    b.m3_barang,
                    b.ton_barang,
                    dc.total_harga
                FROM barang b
                INNER JOIN detail_container dc ON dc.barang_id = b.barang_id
                WHERE dc.container_id = ?
                ORDER BY b.nama_barang
            """

            barangs = self.db.execute(query, (container_id,))

            total_items = 0
            total_harga = 0

            for row in barangs:
                nama = row['nama_barang'] or '-'
                colli = row['colli_amount'] or 0
                m3 = row['m3_barang'] or 0
                ton = row['ton_barang'] or 0
                harga = row['total_harga'] or 0

                # Calculate totals
                total_items += 1
                total_harga += harga

                # Format values
                m3_display = f"{m3:.4f}" if m3 > 0 else "-"
                ton_display = format_ton(ton) if ton > 0 else "-"
                harga_display = f"Rp {harga:,.0f}" if harga > 0 else "-"

                self.barang_tree.insert('', 'end', values=(
                    nama,
                    colli,
                    m3_display,
                    ton_display,
                    harga_display
                ))

            # Update summary
            self.summary_label.config(
                text=f"Total: {total_items} item | Rp {total_harga:,.0f}"
            )

            print(f"✅ Loaded {len(barangs)} barang for container {container_id}")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data barang:\n{str(e)}")
            import traceback
            traceback.print_exc()
