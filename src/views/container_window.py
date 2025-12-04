import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.utils.print_handler import PrintHandler
from datetime import datetime
import sqlite3
from PIL import Image, ImageTk
from tkcalendar import DateEntry

from src.widget.paginated_tree_view import PaginatedTreeView
from src.utils.helpers import format_ton

class ContainerWindow:
    def __init__(self, parent, db, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.print_handler = PrintHandler(db)
        self.create_window()
        self.load_kapals()
    
    # ============ RESPONSIVE METHODS (TAMBAHKAN DI AWAL CLASS) ============
    
    def get_scale_factor(self):
        """Calculate scale factor based on screen size"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Base scale on 1920x1080 as reference
        width_scale = screen_width / 1920
        height_scale = screen_height / 1080
        
        # Use average and clamp between 0.7 and 1.2
        scale = (width_scale + height_scale) / 2
        return max(0.7, min(1.2, scale))
    
    def scaled_font(self, base_size):
        """Return scaled font size"""
        scale = self.get_scale_factor()
        return max(8, int(base_size * scale))

    def make_button_keyboard_accessible(self, button):
        """Make button accessible via Tab and Enter keys"""
        button.config(takefocus=True)

        def on_enter_or_space(event):
            button.invoke()
            return 'break'  # Prevent default behavior

        button.bind('<Return>', on_enter_or_space)
        button.bind('<space>', on_enter_or_space)
        return button

    def on_window_resize(self, event):
        """Handle window resize to adjust column widths"""
        if hasattr(self, 'container_tree') and event.widget == self.window:
            try:
                window_width = self.window.winfo_width()
                available_width = window_width - 100
                
                # Adjust container tree columns
                self.container_tree.column('ID', width=int(available_width * 0.04))
                self.container_tree.column('Kapal', width=int(available_width * 0.18))
                self.container_tree.column('Party', width=int(available_width * 0.15))
                self.container_tree.column('Container', width=int(available_width * 0.18))
                self.container_tree.column('Seal', width=int(available_width * 0.12))
                self.container_tree.column('Ref JOA', width=int(available_width * 0.15))
                self.container_tree.column('Items', width=int(available_width * 0.12))
            except:
                pass


    def parse_party(self, party_text):
        """Parse party text untuk mengidentifikasi container type (20', 21', 40'HC)"""
        import re

        if not party_text or party_text == '-':
            return (0, 0, 0, '-', '-')

        count_20 = 0
        count_21 = 0
        count_40 = 0

        # Pattern untuk container type yang exact match (case insensitive)
        party_upper = party_text.strip().upper()

        # Deteksi single container type
        if party_upper == "20'" or party_upper == "20":
            count_20 = 1
        elif party_upper == "21'" or party_upper == "21":
            count_21 = 1
        elif party_upper in ("40'HC", "40HC", "40'", "40"):
            count_40 = 1

        # Pattern untuk "3X40", "5x40", "3x40'", dll
        matches_40 = re.findall(r"(\d+)\s*[xX]\s*40['\"]?", party_text, re.IGNORECASE)
        if matches_40:
            count_40 = sum(int(m) for m in matches_40)

        # Pattern untuk "2X20", "4x20", "2x20'", dll
        matches_20 = re.findall(r"(\d+)\s*[xX]\s*20['\"]?", party_text)
        if matches_20:
            count_20 = sum(int(m) for m in matches_20)

        # Pattern untuk "2X21", "4x21", "2x21'", dll
        matches_21 = re.findall(r"(\d+)\s*[xX]\s*21['\"]?", party_text)
        if matches_21:
            count_21 = sum(int(m) for m in matches_21)

        # Build display text
        parts = []
        if count_20 > 0:
            parts.append(f"{count_20} X 20'")
        if count_21 > 0:
            parts.append(f"{count_21} X 21'")
        if count_40 > 0:
            parts.append(f"{count_40} X 40'HC")

        if parts:
            total = count_20 + count_21 + count_40
            # Format lengkap dengan total untuk display di header
            display_full = " + ".join(parts) + f" (Total: {total} container{'s' if total > 1 else ''})"
            # Format singkat untuk kolom UNIT (tanpa total)
            display_short = " + ".join(parts)
        else:
            display_full = party_text  # Fallback ke text asli jika tidak bisa di-parse
            display_short = party_text

        return (count_20, count_21, count_40, display_full, display_short)

    def load_kapals(self):
        """Load kapal options from the database - Format: Feeder"""
        try:
            # Query hanya ambil kapal_id dan feeder
            kapals = self.db.execute("""
                SELECT DISTINCT k.feeder
                FROM kapals k 
                ORDER BY k.feeder
            """)
            print(f"[DEBUG] Loaded {len(kapals)} kapals from DB")
            
            # Format sederhana: hanya nama feeder
            kapal_options = []
            for k in kapals:
                feeder = k[0]
                display_text = f"{feeder}"
                kapal_options.append(display_text)
            
            # Simpan nilai saat ini sebelum update
            current_value = self.kapal_combo.get()
            
            # Update dropdown values
            self.kapal_combo['values'] = kapal_options
            
            # Restore nilai jika masih valid
            if current_value and current_value in kapal_options:
                self.kapal_combo.set(current_value)
            
            print(f"[DEBUG] Kapal combo updated with {len(kapal_options)} items")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load kapals: {e}")
            messagebox.showerror("Database Error", f"Gagal memuat daftar kapal:\n{str(e)}")
            return False
    
    
    def filter_kapal_dropdown(self):
        """Filter dropdown kapal berdasarkan text yang diketik (autocomplete)"""
        try:
            typed_text = self.kapal_combo.get().strip()
            
            # Jika kosong, refresh dan tampilkan semua
            if not typed_text:
                self.refresh_kapal_dropdown()
                return
            
            # Ambil semua distinct feeder
            kapals = self.db.execute("""
                SELECT DISTINCT k.feeder
                FROM kapals k 
                ORDER BY k.feeder
            """)
            
            # Filter yang match dengan input user
            filtered_options = []
            typed_lower = typed_text.lower()
            
            for k in kapals:
                feeder = k[0]
                if typed_lower in feeder.lower():
                    filtered_options.append(feeder)
            
            # Update dropdown dengan hasil filter
            self.kapal_combo['values'] = filtered_options
            
            # PENTING: Buka dropdown untuk menampilkan hasil
            if filtered_options:
                try:
                    self.kapal_combo.event_generate('<Down>')
                except:
                    pass
            
            print(f"[DEBUG] Filter found {len(filtered_options)} matches for '{typed_text}'")
            
        except Exception as e:
            print(f"[ERROR] Filter kapal dropdown: {e}")
        
    
    def refresh_kapal_dropdown(self):
        """Refresh kapal dropdown dengan feedback visual"""
        print("[DEBUG] Refreshing kapal dropdown...")
        
        # Simpan posisi cursor saat ini
        current_position = self.kapal_combo.index(tk.INSERT) if self.kapal_combo.get() else 0
        
        # Load data kapal terbaru
        success = self.load_kapals()
        
        # Restore cursor position jika ada text
        if self.kapal_combo.get():
            try:
                self.kapal_combo.icursor(current_position)
            except:
                pass
        
        # Visual feedback (optional - bisa dimatikan jika mengganggu)
        # if success:
        #     # Flash effect
        #     original_bg = self.kapal_combo.cget('background')
        #     self.kapal_combo.configure(background='#2ecc71')
        #     self.kapal_combo.after(200, lambda: self.kapal_combo.configure(background=original_bg))
        
        return success
    
    def on_tab_changed(self, event):
        """Event handler ketika tab berubah - refresh data"""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        print(f"[DEBUG] Tab changed to: {tab_text}")
        
        # Refresh kapal dropdown saat tab Container aktif
        if "Container" in tab_text:
            self.refresh_kapal_dropdown()
            self.load_containers()

    def create_window(self):
        """Create container management window with responsive design"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("🚢 Data Container")
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Adaptive window size
        window_width = min(int(screen_width * 0.85), 1400)
        window_height = min(int(screen_height * 0.90), 1000)
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Resizable
        self.window.minsize(1000, 700)
        self.window.resizable(True, True)
        
        try:
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.window.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")
        
        self.center_window()
        
        # Header with responsive font
        header = tk.Label(
            self.window,
            text="🚢 KELOLA DATA CONTAINER & BARANG",
            font=('Arial', self.scaled_font(18), 'bold'),
            bg='#e67e22',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Bind tab change event untuk auto-refresh
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Tab 1: Container Management
        container_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(container_frame, text='🚢 Container')
        self.create_container_tab(container_frame)
        
        # Tab 2: Container-Barang Management
        container_barang_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(container_barang_frame, text='📦 Barang dalam Container')
        self.create_container_barang_tab(container_barang_frame)
        
        # Close button with responsive font
        close_btn = tk.Button(
            self.window,
            text="❌ Tutup",
            font=('Arial', self.scaled_font(12), 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=10,
            command=self.window.destroy
        )
        close_btn.pack(pady=10)
        
        # Bind resize event
        self.window.bind('<Configure>', self.on_window_resize)

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
        
        # ============================================
        # BARIS 1: Kapal | ETD | Container
        # ============================================
        row1_frame = tk.Frame(form_frame, bg='#ecf0f1')
        row1_frame.pack(fill='x', pady=5)
        
        # Kapal (Dropdown)
        tk.Label(
            row1_frame, 
            text="Kapal:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1',
            width=10,
            anchor='w'
        ).pack(side='left', padx=(0, 5))
        
        self.kapal_var = tk.StringVar()
        self.kapal_combo = ttk.Combobox(
            row1_frame,
            textvariable=self.kapal_var,
            font=('Arial', 10),
            width=22,
            state='normal'
        )
        self.kapal_combo.pack(side='left', padx=(0, 20))
        
        # Bind event untuk auto-refresh dan auto-filter
        self.kapal_combo.bind('<FocusIn>', lambda e: self.refresh_kapal_dropdown())
        self.kapal_combo.bind('<KeyRelease>', self.on_kapal_keyrelease)
        
        tk.Label(
            row1_frame, 
            text="ETD:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1',
            width=10,
            anchor='w'
        ).pack(side='left', padx=(0, 5))

        # Frame untuk ETD DateEntry
        etd_container = tk.Frame(row1_frame, bg='#ecf0f1')
        etd_container.pack(side='left', padx=(0, 20))


        # ✅ DateEntry dengan format Indonesia (DD/MM/YYYY)
        self.etd_entry = DateEntry(
            etd_container,
            font=('Arial', 10),
            width=12,
            background='#e67e22',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/MM/yyyy',  # ✅ FORMAT INDONESIA!
            locale='id_ID'  # ✅ LOCALE INDONESIA (opsional)
        )
        self.etd_entry.pack(side='left')

        # Set nilai default ke hari ini
        self.etd_entry.set_date(datetime.now().date())

        # Hint format (opsional)
        tk.Label(
            etd_container,
            text="(klik untuk pilih)",
            font=('Arial', 8),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(side='left', padx=(5, 0))
                
        # Container
        tk.Label(
            row1_frame, 
            text="Container:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1',
            width=10,
            anchor='w'
        ).pack(side='left', padx=(0, 5))
        
        self.container_entry = tk.Entry(row1_frame, font=('Arial', 10), width=22)
        self.container_entry.pack(side='left')
        
        # ============================================
        # BARIS 2: Seal | Party | Ref JOA
        # ============================================
        row2_frame = tk.Frame(form_frame, bg='#ecf0f1')
        row2_frame.pack(fill='x', pady=5)
        
        # Seal
        tk.Label(
            row2_frame, 
            text="Seal:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1',
            width=10,
            anchor='w'
        ).pack(side='left', padx=(0, 5))
        
        self.seal_entry = tk.Entry(row2_frame, font=('Arial', 10), width=22)
        self.seal_entry.pack(side='left', padx=(0, 20))
        
        # Party
        tk.Label(
            row2_frame, 
            text="Party:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1',
            width=10,
            anchor='w'
        ).pack(side='left', padx=(0, 5))
        
        party_options = ["20'", "21'", "40'HC"]
        self.party_entry = ttk.Combobox(row2_frame, values=party_options, state='readonly', font=('Arial', 10), width=17)
        self.party_entry.pack(side='left', padx=(0, 20))
        self.party_entry.set('')  # allow empty selection by default
        
        # Ref JOA
        tk.Label(
            row2_frame, 
            text="Ref JOA:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1',
            width=10,
            anchor='w'
        ).pack(side='left', padx=(0, 5))
        
        self.ref_joa_entry = tk.Entry(row2_frame, font=('Arial', 10), width=22)
        self.ref_joa_entry.pack(side='left')
        
        # ============================================
        # BUTTONS - AKSI CONTAINER
        # ============================================
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=15)
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Tambah Container",
            font=('Arial', 10, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=15,
            pady=8,
            command=self.add_container
        )
        self.make_button_keyboard_accessible(add_btn)
        add_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Bersihkan",
            font=('Arial', 10, 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=8,
            command=self.clear_form
        )
        self.make_button_keyboard_accessible(clear_btn)
        clear_btn.pack(side='left', padx=(0, 10))
        
        edit_btn = tk.Button(
            btn_frame,
            text="✏️ Edit Container",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8,
            command=self.edit_container
        )
        self.make_button_keyboard_accessible(edit_btn)
        edit_btn.pack(side='left', padx=(0, 10))
        
        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Hapus Container",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=15,
            pady=8,
            command=self.delete_container
        )
        self.make_button_keyboard_accessible(delete_btn)
        delete_btn.pack(side='left', padx=(0, 10))
        
        summary_btn = tk.Button(
            btn_frame,
            text="📊 Lihat Summary",
            font=('Arial', 10, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=8,
            command=self.view_selected_container_summary
        )
        self.make_button_keyboard_accessible(summary_btn)
        summary_btn.pack(side='left')
        
        # ============================================
        # CONTAINER LIST
        # ============================================
        list_frame = tk.Frame(parent, bg='#ecf0f1')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(
            list_frame, 
            text="📋 DAFTAR CONTAINER", 
            font=('Arial', 14, 'bold'), 
            bg='#ecf0f1'
        ).pack(anchor='w')
        
        # Treeview for container list
        tree_frame = tk.Frame(list_frame, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        container_tree_container = tk.Frame(tree_frame, bg='#ecf0f1')
        container_tree_container.pack(fill='both', expand=True)
        
        # Container columns
        container_columns = ('ID', 'Kapal', 'ETD', 'Party', 'Container', 'Seal', 'Ref JOA', 'Items')

        # Create PaginatedTreeView
        self.container_tree = PaginatedTreeView(
            parent=container_tree_container,
            columns=container_columns,
            show='headings',
            height=8,
            items_per_page=10
        )

        # Configure headings
        self.container_tree.heading('ID', text='ID')
        self.container_tree.heading('Kapal', text='Kapal')
        self.container_tree.heading('ETD', text='ETD')
        self.container_tree.heading('Party', text='Party')
        self.container_tree.heading('Container', text='Container')
        self.container_tree.heading('Seal', text='Seal')
        self.container_tree.heading('Ref JOA', text='Ref JOA')
        self.container_tree.heading('Items', text='Jumlah Barang')

        # Configure columns
        self.container_tree.column('ID', width=40)
        self.container_tree.column('Kapal', width=130)
        self.container_tree.column('ETD', width=100)
        self.container_tree.column('Party', width=100)
        self.container_tree.column('Container', width=130)
        self.container_tree.column('Seal', width=90)
        self.container_tree.column('Ref JOA', width=110)
        self.container_tree.column('Items', width=100)

        # Pack PaginatedTreeView
        self.container_tree.pack(fill='both', expand=True)

        # Bind double-click to view container details
        self.container_tree.bind('<Double-1>', self.view_container_details)
        
        # Load existing containers
        self.load_containers()
        
        # ============================================
        # PRINT BUTTONS SECTION
        # ============================================
        self.add_print_buttons_to_container_tab(parent)
        
    
    def on_kapal_keyrelease(self, event=None):
        """Handle ketika user mengetik di dropdown kapal"""
        # Abaikan tombol navigasi
        if event and event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab'):
            return
        
        # Panggil filter dengan delay kecil untuk performa
        if hasattr(self, '_filter_timer'):
            self.window.after_cancel(self._filter_timer)
        
        self._filter_timer = self.window.after(300, self.filter_kapal_dropdown)
        
    
    def add_print_buttons_to_container_tab(self, parent):
        """Add print buttons to container tab"""
        print_frame = tk.Frame(parent, bg='#ecf0f1')
        print_frame.pack(fill='x', padx=20, pady=10)
        
        # Separator
        separator = tk.Frame(print_frame, height=2, bg='#34495e')
        separator.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            print_frame, 
            text="📄 PRINT DOCUMENTS", 
            font=('Arial', 12, 'bold'), 
            bg='#ecf0f1'
        ).pack(anchor='w', pady=(0, 10))
        
        btn_frame = tk.Frame(print_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x')
        
        # Print Invoice Container button
        print_invoice_btn = tk.Button(
            btn_frame,
            text="🧾 Print Invoice Container",
            font=('Arial', 10, 'bold'),
            bg="#4bc23b",
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_container_invoice
        )
        self.make_button_keyboard_accessible(print_invoice_btn)
        print_invoice_btn.pack(side='left', padx=(0, 10))
        
        # Print Invoice PDF button
        print_invoice_pdf_btn = tk.Button(
            btn_frame,
            text="📄 Invoice PDF",
            font=('Arial', 10, 'bold'),
            bg="#f39c12",  # Orange
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_container_invoice_pdf
        )
        self.make_button_keyboard_accessible(print_invoice_pdf_btn)
        print_invoice_pdf_btn.pack(side='left', padx=(0, 10))
        
        # Print Customer Packing List button
        print_packing_btn = tk.Button(
            btn_frame,
            text="📋 Print Customer Packing List",
            font=('Arial', 10, 'bold'),
            bg="#1b9b0a",
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_customer_packing_list
        )
        self.make_button_keyboard_accessible(print_packing_btn)
        print_packing_btn.pack(side='left', padx=(0, 10))

        # Preview IPL Excel button
        preview_ipl_btn = tk.Button(
            btn_frame,
            text="📊 Preview IPL Excel",
            font=('Arial', 10, 'bold'),
            bg="#3498db",  # Blue
            fg='white',
            padx=20,
            pady=8,
            command=self.preview_selected_ipl_excel
        )
        self.make_button_keyboard_accessible(preview_ipl_btn)
        preview_ipl_btn.pack(side='left', padx=(0, 10))


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
            font=('Arial', 8, 'bold'),
            bg="#4bc23b",
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_container_invoice
        )
        self.make_button_keyboard_accessible(print_invoice_btn)
        print_invoice_btn.pack(side='left', padx=(0, 10))
        
        print_invoice_pdf_btn = tk.Button(
            btn_frame,
            text="📄 Invoice PDF",
            font=('Arial', 8, 'bold'),
            bg="#f39c12",  # Orange
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_container_invoice_pdf
        )
        self.make_button_keyboard_accessible(print_invoice_pdf_btn)
        print_invoice_pdf_btn.pack(side='left', padx=(0, 10))
        
        
        # Print Customer Packing List button
        print_packing_btn = tk.Button(
            btn_frame,
            text="📋 Print Customer Packing List",
            font=('Arial', 8, 'bold'),
            bg="#1b9b0a",
            fg='white',
            padx=20,
            pady=8,
            command=self.print_selected_customer_packing_list
        )
        self.make_button_keyboard_accessible(print_packing_btn)
        print_packing_btn.pack(side='left', padx=(0, 10))

        # Preview IPL Excel button
        preview_ipl_btn = tk.Button(
            btn_frame,
            text="📊 Preview IPL Excel",
            font=('Arial', 8, 'bold'),
            bg="#3498db",  # Blue
            fg='white',
            padx=20,
            pady=8,
            command=self.preview_selected_ipl_excel
        )
        self.make_button_keyboard_accessible(preview_ipl_btn)
        preview_ipl_btn.pack(side='left', padx=(0, 10))

    def print_selected_container_invoice(self):
        """Print invoice for selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih container yang akan diprint invoicenya!")
            return
        
        item = self.container_tree.item(selection[0])
        container_id = item['values'][0]
        container_name = item['values'][4]  # Container column
        
        # Confirm print
        if messagebox.askyesno("Konfirmasi Print", f"Print Invoice untuk Container '{container_name}'?"):
            self.print_handler.print_container_invoice(container_id)

    def print_selected_container_invoice_pdf(self):
        """Print selected container(s) invoice as PDF - supports multiple selection"""
        try:
            selected_items = self.container_tree.selection()
            if not selected_items:
                messagebox.showwarning("Peringatan", "Pilih satu atau lebih container yang akan diprint invoice PDF!")
                return
            
            # Get all selected container IDs
            container_ids = []
            container_names = []
            
            for selected in selected_items:
                item = self.container_tree.item(selected)
                container_id = item['values'][0]  # container_id in first column
                container_name = item['values'][2]  # container name in third column
                container_ids.append(container_id)
                container_names.append(container_name)
            
            # Confirm if multiple containers
            if len(container_ids) > 1:
                confirm_msg = f"Print Invoice PDF untuk {len(container_ids)} container?\n\n"
                confirm_msg += "Container yang dipilih:\n"
                for name in container_names[:5]:  # Show max 5
                    confirm_msg += f"• {name}\n"
                if len(container_names) > 5:
                    confirm_msg += f"... dan {len(container_names) - 5} container lainnya\n"
                
                if not messagebox.askyesno("Konfirmasi Print Multiple", confirm_msg):
                    return
            
            # Call print handler
            if hasattr(self, 'print_handler'):
                self.print_handler.print_container_invoice_pdf(container_ids)
            else:
                messagebox.showerror("Error", "Print handler tidak tersedia!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal print invoice PDF: {str(e)}")
            print(f"Error in print_selected_container_invoice_pdf: {e}")
            
    
    def print_selected_customer_packing_list(self):
        """Print customer packing list for selected container(s) - supports multiple selection"""
        try:
            selected_items = self.container_tree.selection()
            if not selected_items:
                messagebox.showwarning("Peringatan", "Pilih satu atau lebih container yang akan diprint packing list PDF!")
                return
            
            # Get all selected container IDs
            container_ids = []
            container_names = []
            
            for selected in selected_items:
                item = self.container_tree.item(selected)
                container_id = item['values'][0]  # container_id in first column
                container_name = item['values'][2]  # container name in third column
                container_ids.append(container_id)
                container_names.append(container_name)
            
            # Confirm if multiple containers
            if len(container_ids) > 1:
                confirm_msg = f"Print Packing List PDF untuk {len(container_ids)} container?\n\n"
                confirm_msg += "Container yang dipilih:\n"
                for name in container_names[:5]:  # Show max 5
                    confirm_msg += f"• {name}\n"
                if len(container_names) > 5:
                    confirm_msg += f"... dan {len(container_names) - 5} container lainnya\n"
                
                if not messagebox.askyesno("Konfirmasi Print Multiple", confirm_msg):
                    return
            
            # Call print handler - SAME AS INVOICE
            if hasattr(self, 'print_handler'):
                self.print_handler.print_customer_packing_list_pdf(container_ids)
            else:
                messagebox.showerror("Error", "Print handler tidak tersedia!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal print packing list PDF: {str(e)}")
            print(f"Error in print_selected_customer_packing_list: {e}")

    def preview_selected_ipl_excel(self):
        """Preview Invoice Packing List (IPL) Excel for selected container(s)"""
        try:
            selected_items = self.container_tree.selection()
            if not selected_items:
                messagebox.showwarning("Peringatan", "Pilih satu container untuk preview IPL Excel!")
                return

            # Get first selected container only
            item = self.container_tree.item(selected_items[0])
            container_id = item['values'][0]

            # Show preview window
            self.show_ipl_preview_window(container_id)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal preview IPL Excel: {str(e)}")
            print(f"Error in preview_selected_ipl_excel: {e}")

    def show_ipl_preview_window(self, container_id):
        """Show IPL preview in a new window with table format"""
        from datetime import datetime
        import tkinter.ttk as ttk

        try:
            # Get container details
            container = self.db.get_container_by_id(container_id)
            if not container:
                messagebox.showerror("Error", "Container tidak ditemukan!")
                return

            # Get barang in container with pricing
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)

            if not container_barang:
                messagebox.showwarning("Peringatan", "Container kosong, tidak ada data untuk ditampilkan!")
                return

            # Create preview window
            preview_window = tk.Toplevel(self.window)
            preview_window.title(f"Preview IPL - {container.get('container', 'N/A')}")
            preview_window.configure(bg='white')

            # Get screen dimensions
            screen_width = preview_window.winfo_screenwidth()
            screen_height = preview_window.winfo_screenheight()

            # Set window size (80% of screen)
            window_width = int(screen_width * 0.8)
            window_height = int(screen_height * 0.85)

            # Position window at right side of screen to not block main window
            x_position = int(screen_width * 0.15)
            y_position = int(screen_height * 0.05)

            preview_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Make window resizable
            preview_window.resizable(True, True)
            preview_window.minsize(800, 600)  # Minimum size

            # Don't use grab_set() so main window remains accessible
            # preview_window.transient(self.window)  # Commented out to allow independent movement

            # Main container with scrollbar
            main_frame = tk.Frame(preview_window, bg='white')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Canvas with scrollbar
            canvas = tk.Canvas(main_frame, bg='white')
            scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            # Store canvas window id for resizing
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Update scrollregion when content changes
            def update_scrollregion(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))

            # Update canvas window width when canvas is resized
            def on_canvas_resize(event):
                # Make the scrollable_frame match canvas width
                canvas.itemconfig(canvas_window, width=event.width)
                update_scrollregion()

            scrollable_frame.bind("<Configure>", update_scrollregion)
            canvas.bind("<Configure>", on_canvas_resize)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Header Section
            header_frame = tk.Frame(scrollable_frame, bg='white')
            header_frame.pack(fill='x', pady=(0, 20))

            # Title
            title_label = tk.Label(
                header_frame,
                text="INVOICE PACKING LIST",
                font=('Arial', 16, 'bold'),
                bg='white'
            )
            title_label.pack()

            # Company info
            company_label = tk.Label(
                header_frame,
                text="PT. CAHAYA KARUNIA LOGISTIK | Jl Teluk Bone Selatan No 05 | Phone: 031-60166017",
                font=('Arial', 10),
                bg='white'
            )
            company_label.pack(pady=(5, 0))

            # Container Information Section
            info_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', borderwidth=1)
            info_frame.pack(fill='x', pady=(0, 20), padx=20)

            # Safe get function
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return container.get(key, default) or default
                    else:
                        return container[key] if key in container and container[key] else default
                except:
                    return default

            # Format date function
            def format_date(date_value):
                if not date_value or date_value == '-':
                    return '-'
                try:
                    if isinstance(date_value, str) and len(date_value) == 10:
                        date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                        return date_obj.strftime('%d-%m-%Y')
                    return str(date_value)
                except:
                    return str(date_value)

            # Container info data
            container_info = [
                ("Container No", safe_get('container')),
                ("Feeder", safe_get('feeder')),
                ("Destination", safe_get('destination')),
                ("Party", safe_get('party')),
                ("ETD Sub", format_date(safe_get('etd_sub'))),
                ("CLS", format_date(safe_get('cls'))),
                ("Open", format_date(safe_get('open'))),
                ("Full", format_date(safe_get('full'))),
                ("Seal", safe_get('seal')),
                ("Ref JOA", safe_get('ref_joa'))
            ]

            # Display container info in grid (2 columns x 5 rows)
            for i, (label, value) in enumerate(container_info):
                row = i % 5
                col = i // 5

                label_widget = tk.Label(
                    info_frame,
                    text=f"{label}:",
                    font=('Arial', 10, 'bold'),
                    bg='white',
                    anchor='e',
                    width=15
                )
                label_widget.grid(row=row, column=col*2, padx=(10, 5), pady=5, sticky='e')

                value_widget = tk.Label(
                    info_frame,
                    text=str(value),
                    font=('Arial', 10),
                    bg='white',
                    anchor='w',
                    width=20
                )
                value_widget.grid(row=row, column=col*2+1, padx=(0, 10), pady=5, sticky='w')

            # Table Section
            table_frame = tk.Frame(scrollable_frame, bg='white')
            table_frame.pack(fill='both', expand=True, padx=20)

            # Create Treeview
            columns = ('Tgl', 'Pengirim', 'Penerima', 'Nama Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Satuan', 'Door', 'Unit Price', 'Price')

            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

            # Define column widths and headings
            column_widths = {
                'Tgl': 80,
                'Pengirim': 150,
                'Penerima': 150,
                'Nama Barang': 200,
                'Kubikasi': 120,
                'M3': 80,
                'Ton': 80,
                'Col': 60,
                'Satuan': 80,
                'Door': 100,
                'Unit Price': 100,
                'Price': 100
            }

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=column_widths.get(col, 100), anchor='center')

            # Add data to tree
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            total_nilai = 0

            # Get tax information by receiver
            tax_summary = {}
            try:
                receivers = set()
                for barang_row in container_barang:
                    barang = dict(barang_row)
                    receiver = barang.get('receiver_name', '')
                    if receiver:
                        receivers.add(receiver)

                for receiver in receivers:
                    tax_query = """
                        SELECT
                            bt.penerima,
                            AVG(bt.ppn_rate) as avg_ppn_rate,
                            AVG(bt.pph23_rate) as avg_pph_rate,
                            SUM(bt.ppn_amount) as total_ppn_amount,
                            SUM(bt.pph23_amount) as total_pph_amount,
                            SUM(bt.total_nilai_barang) as total_nilai
                        FROM barang_tax bt
                        WHERE bt.container_id = ? AND bt.penerima = ?
                        GROUP BY bt.penerima
                    """
                    result = self.db.execute(tax_query, (container_id, receiver))

                    if result and len(result) > 0:
                        row = result[0]
                        tax_summary[receiver] = {
                            'ppn_rate': (row['avg_ppn_rate'] or 0) * 100,
                            'pph_rate': (row['avg_pph_rate'] or 0) * 100,
                            'ppn_amount': row['total_ppn_amount'] or 0,
                            'pph_amount': row['total_pph_amount'] or 0,
                            'has_tax': True
                        }
                    else:
                        tax_summary[receiver] = {
                            'ppn_rate': 0,
                            'pph_rate': 0,
                            'ppn_amount': 0,
                            'pph_amount': 0,
                            'has_tax': False
                        }
            except Exception as e:
                print(f"Error getting tax info: {e}")

            current_receiver = None
            current_receiver_subtotal = 0
            total_ppn_all = 0
            total_pph_all = 0

            for barang_row in container_barang:
                barang = dict(barang_row)

                def safe_barang_get(key, default='-'):
                    try:
                        value = barang.get(key, default)
                        return value if value not in [None, '', 'NULL', 'null'] else default
                    except Exception:
                        return default

                tanggal = safe_barang_get('tanggal', datetime.now())
                if isinstance(tanggal, str):
                    try:
                        tanggal = datetime.strptime(tanggal, '%Y-%m-%d')
                    except:
                        try:
                            tanggal = datetime.strptime(tanggal, '%Y-%m-%d %H:%M:%S')
                        except:
                            tanggal = datetime.now()

                formatted_date = tanggal.strftime('%d-%b') if isinstance(tanggal, datetime) else '-'

                pengirim = str(safe_barang_get('sender_name', '-'))
                penerima = str(safe_barang_get('receiver_name', '-'))
                nama_barang = str(safe_barang_get('nama_barang', '-'))
                door = str(safe_barang_get('door_type', safe_barang_get('alamat_tujuan', '-')))[:10].upper()

                # Parse numeric values - use correct field names
                p = safe_barang_get('panjang_barang', '-')
                l = safe_barang_get('lebar_barang', '-')
                t = safe_barang_get('tinggi_barang', '-')

                if str(p) != '-':
                    p = str(p).replace(',', '')
                if str(l) != '-':
                    l = str(l).replace(',', '')
                if str(t) != '-':
                    t = str(t).replace(',', '')

                kubikasi_val = f"{p}×{l}×{t}"

                m3 = safe_barang_get('m3_barang', 0)
                ton = safe_barang_get('ton_barang', 0)
                colli = safe_barang_get('colli_amount', 0)
                satuan = str(safe_barang_get('satuan', safe_barang_get('unit', 'pcs')))
                unit_price = safe_barang_get('harga_per_unit', safe_barang_get('unit_price', 0))
                total_harga = safe_barang_get('total_harga', 0)

                # Convert to proper types
                m3_val = float(m3) if m3 not in [None, '', '-'] else 0
                ton_val = float(ton) if ton not in [None, '', '-'] else 0
                colli_val = int(colli) if colli not in [None, '', '-'] else 0
                unit_price_val = float(unit_price) if unit_price not in [None, '', '-'] else 0
                price = float(total_harga) if total_harga not in [None, '', '-'] else 0

                # Calculate totals (m3 and ton multiplied by colli)
                m3_total = m3_val * colli_val if colli_val > 0 else m3_val
                ton_total = ton_val * colli_val if colli_val > 0 else ton_val

                # Check if receiver changed for tax calculation
                if current_receiver != penerima:
                    # Insert tax rows for previous receiver
                    if current_receiver and current_receiver_subtotal > 0:
                        if current_receiver in tax_summary:
                            tax_data = tax_summary[current_receiver]
                            if tax_data['has_tax']:
                                ppn_amount = current_receiver_subtotal * (tax_data['ppn_rate'] / 100)
                                pph_amount = current_receiver_subtotal * (tax_data['pph_rate'] / 100)

                                if tax_data['ppn_rate'] > 0:
                                    tree.insert('', 'end', values=(
                                        '', '', '', f"PPN {tax_data['ppn_rate']:.1f}%", '', '', '', '', '', '', '',
                                        f"{ppn_amount:,.0f}"
                                    ), tags=('tax',))
                                    total_ppn_all += ppn_amount

                                if tax_data['pph_rate'] > 0:
                                    tree.insert('', 'end', values=(
                                        '', '', '', 'PPH 23', '', '', '', '', '', '', '',
                                        f"{-pph_amount:,.0f}"
                                    ), tags=('tax',))
                                    total_pph_all += pph_amount

                    current_receiver = penerima
                    current_receiver_subtotal = 0

                # Add row to tree
                tree.insert('', 'end', values=(
                    formatted_date,
                    pengirim,
                    penerima,
                    nama_barang,
                    kubikasi_val,
                    f"{m3_total:.3f}",
                    f"{ton_total:.3f}",
                    colli_val,
                    satuan,
                    door,
                    f"{unit_price_val:,.0f}",
                    f"{price:,.0f}"
                ))

                # Update totals
                total_m3 += m3_total
                total_ton += ton_total
                total_colli += colli_val
                total_nilai += price
                current_receiver_subtotal += price

            # Insert tax rows for last receiver
            if current_receiver and current_receiver_subtotal > 0:
                if current_receiver in tax_summary:
                    tax_data = tax_summary[current_receiver]
                    if tax_data['has_tax']:
                        ppn_amount = current_receiver_subtotal * (tax_data['ppn_rate'] / 100)
                        pph_amount = current_receiver_subtotal * (tax_data['pph_rate'] / 100)

                        if tax_data['ppn_rate'] > 0:
                            tree.insert('', 'end', values=(
                                '', '', '', f"PPN {tax_data['ppn_rate']:.1f}%", '', '', '', '', '', '', '',
                                f"{ppn_amount:,.0f}"
                            ), tags=('tax',))
                            total_ppn_all += ppn_amount

                        if tax_data['pph_rate'] > 0:
                            tree.insert('', 'end', values=(
                                '', '', '', 'PPH 23', '', '', '', '', '', '', '',
                                f"{-pph_amount:,.0f}"
                            ), tags=('tax',))
                            total_pph_all += pph_amount

            # Style tax rows
            tree.tag_configure('tax', background='#fffacd', font=('Arial', 10, 'italic'))

            # Add scrollbars to tree
            tree_scroll_y = tk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
            tree_scroll_x = tk.Scrollbar(table_frame, orient='horizontal', command=tree.xview)
            tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

            tree.grid(row=0, column=0, sticky='nsew')
            tree_scroll_y.grid(row=0, column=1, sticky='ns')
            tree_scroll_x.grid(row=1, column=0, sticky='ew')

            table_frame.grid_rowconfigure(0, weight=1)
            table_frame.grid_columnconfigure(0, weight=1)

            # Biaya Section - Get delivery costs from database
            try:
                # Query biaya Surabaya
                surabaya_costs = self.db.execute("""
                    SELECT description, cost_description, cost
                    FROM container_delivery_costs
                    WHERE container_id = ? AND delivery = 'Surabaya'
                    ORDER BY id
                """, (container_id,))

                # Query biaya tujuan lain (bukan Surabaya)
                tujuan_costs = self.db.execute("""
                    SELECT delivery, description, cost_description, cost
                    FROM container_delivery_costs
                    WHERE container_id = ? AND delivery != 'Surabaya'
                    ORDER BY delivery, id
                """, (container_id,))

                # Calculate max height needed for tables
                max_rows = max(len(surabaya_costs) if surabaya_costs else 0, 
                             len(tujuan_costs) if tujuan_costs else 0)
                table_height = max(max_rows + 1, 5)  # +1 for total row, minimum 5

                # Create costs frame with grid layout for alignment
                costs_main_frame = tk.Frame(scrollable_frame, bg='white')
                costs_main_frame.pack(fill='both', expand=True, pady=(20, 10), padx=20)

                # Create 2 columns layout using grid with equal stretch
                costs_left_frame = tk.Frame(costs_main_frame, bg='white')
                costs_left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

                costs_right_frame = tk.Frame(costs_main_frame, bg='white')
                costs_right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))

                # Configure grid weights for equal distribution and stretching
                costs_main_frame.grid_rowconfigure(0, weight=1)
                costs_main_frame.grid_columnconfigure(0, weight=1, uniform='costs')
                costs_main_frame.grid_columnconfigure(1, weight=1, uniform='costs')

                # Biaya Surabaya Table
                if surabaya_costs:
                    surabaya_frame = tk.Frame(costs_left_frame, bg='white', relief='solid', borderwidth=1)
                    surabaya_frame.pack(fill='both', expand=True, anchor='n')

                    tk.Label(
                        surabaya_frame,
                        text="BIAYA SURABAYA",
                        font=('Arial', 12, 'bold'),
                        bg='#e8f4f8',
                        fg='#2c3e50'
                    ).pack(fill='x', pady=(5, 0))

                    # Create treeview for Surabaya costs
                    surabaya_tree_frame = tk.Frame(surabaya_frame, bg='white')
                    surabaya_tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

                    surabaya_tree = ttk.Treeview(
                        surabaya_tree_frame,
                        columns=('Deskripsi', 'Keterangan', 'Biaya'),
                        show='headings',
                        height=table_height
                    )

                    surabaya_tree.heading('Deskripsi', text='Deskripsi')
                    surabaya_tree.heading('Keterangan', text='Keterangan')
                    surabaya_tree.heading('Biaya', text='Biaya (Rp)')

                    surabaya_tree.column('Deskripsi', width=200, anchor='w')
                    surabaya_tree.column('Keterangan', width=200, anchor='w')
                    surabaya_tree.column('Biaya', width=120, anchor='e')

                    total_surabaya = 0
                    for cost_row in surabaya_costs:
                        biaya = float(cost_row['cost']) if cost_row['cost'] else 0
                        total_surabaya += biaya
                        surabaya_tree.insert('', 'end', values=(
                            cost_row['description'] or '-',
                            cost_row['cost_description'] or '-',
                            f"{biaya:,.0f}"
                        ))

                    # Add total row
                    surabaya_tree.insert('', 'end', values=(
                        'TOTAL', '', f"{total_surabaya:,.0f}"
                    ), tags=('total',))
                    surabaya_tree.tag_configure('total', background='#ffffcc', font=('Arial', 10, 'bold'))

                    surabaya_scroll_y = ttk.Scrollbar(surabaya_tree_frame, orient='vertical', command=surabaya_tree.yview)
                    surabaya_scroll_x = ttk.Scrollbar(surabaya_tree_frame, orient='horizontal', command=surabaya_tree.xview)
                    surabaya_tree.configure(yscrollcommand=surabaya_scroll_y.set, xscrollcommand=surabaya_scroll_x.set)

                    surabaya_tree.grid(row=0, column=0, sticky='nsew')
                    surabaya_scroll_y.grid(row=0, column=1, sticky='ns')
                    surabaya_scroll_x.grid(row=1, column=0, sticky='ew')

                    surabaya_tree_frame.grid_rowconfigure(0, weight=1)
                    surabaya_tree_frame.grid_columnconfigure(0, weight=1)

                # Biaya Tujuan Table
                if tujuan_costs:
                    # Group by destination
                    tujuan_groups = {}
                    for cost_row in tujuan_costs:
                        dest = cost_row['delivery']
                        if dest not in tujuan_groups:
                            tujuan_groups[dest] = []
                        tujuan_groups[dest].append(cost_row)

                    for destination, costs in tujuan_groups.items():
                        tujuan_frame = tk.Frame(costs_right_frame, bg='white', relief='solid', borderwidth=1)
                        tujuan_frame.pack(fill='both', expand=True, anchor='n', pady=(0, 10))

                        tk.Label(
                            tujuan_frame,
                            text=f"BIAYA {destination.upper()}",
                            font=('Arial', 12, 'bold'),
                            bg='#fff4e6',
                            fg='#2c3e50'
                        ).pack(fill='x', pady=(5, 0))

                        # Create treeview for destination costs
                        tujuan_tree_frame = tk.Frame(tujuan_frame, bg='white')
                        tujuan_tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

                        tujuan_tree = ttk.Treeview(
                            tujuan_tree_frame,
                            columns=('Deskripsi', 'Keterangan', 'Biaya'),
                            show='headings',
                            height=table_height
                        )

                        tujuan_tree.heading('Deskripsi', text='Deskripsi')
                        tujuan_tree.heading('Keterangan', text='Keterangan')
                        tujuan_tree.heading('Biaya', text='Biaya (Rp)')

                        tujuan_tree.column('Deskripsi', width=200, anchor='w')
                        tujuan_tree.column('Keterangan', width=200, anchor='w')
                        tujuan_tree.column('Biaya', width=120, anchor='e')

                        total_tujuan = 0
                        for cost_row in costs:
                            biaya = float(cost_row['cost']) if cost_row['cost'] else 0
                            total_tujuan += biaya
                            tujuan_tree.insert('', 'end', values=(
                                cost_row['description'] or '-',
                                cost_row['cost_description'] or '-',
                                f"{biaya:,.0f}"
                            ))

                        # Add total row
                        tujuan_tree.insert('', 'end', values=(
                            'TOTAL', '', f"{total_tujuan:,.0f}"
                        ), tags=('total',))
                        tujuan_tree.tag_configure('total', background='#ffffcc', font=('Arial', 10, 'bold'))

                        tujuan_scroll_y = ttk.Scrollbar(tujuan_tree_frame, orient='vertical', command=tujuan_tree.yview)
                        tujuan_scroll_x = ttk.Scrollbar(tujuan_tree_frame, orient='horizontal', command=tujuan_tree.xview)
                        tujuan_tree.configure(yscrollcommand=tujuan_scroll_y.set, xscrollcommand=tujuan_scroll_x.set)

                        tujuan_tree.grid(row=0, column=0, sticky='nsew')
                        tujuan_scroll_y.grid(row=0, column=1, sticky='ns')
                        tujuan_scroll_x.grid(row=1, column=0, sticky='ew')

                        tujuan_tree_frame.grid_rowconfigure(0, weight=1)
                        tujuan_tree_frame.grid_columnconfigure(0, weight=1)

            except Exception as e:
                print(f"Error loading delivery costs: {e}")

            # Button Section
            button_frame = tk.Frame(scrollable_frame, bg='white')
            button_frame.pack(pady=20)

            close_btn = tk.Button(
                button_frame,
                text="Tutup",
                font=('Arial', 12, 'bold'),
                bg="#e74c3c",
                fg='white',
                padx=30,
                pady=10,
                command=preview_window.destroy
            )
            close_btn.pack()

            # Pack canvas and scrollbar
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # Bind mousewheel
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # Cleanup on close
            def on_close():
                canvas.unbind_all("<MouseWheel>")
                preview_window.destroy()

            preview_window.protocol("WM_DELETE_WINDOW", on_close)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menampilkan preview: {str(e)}")
            print(f"Error in show_ipl_preview_window: {e}")
            import traceback
            traceback.print_exc()

    def create_container_barang_tab(self, parent):
        """Create container-barang management tab with pricing, sender/receiver selection, and tax management - OPTIMIZED"""

        # Initialize cache dan timer untuk debouncing
        self._cached_barang_data = None
        self._cache_invalid = True
        self._cached_customers = {}
        self.filter_timer = None
        self.filter_delay = 300  # milliseconds

        # === Frame Seleksi (atas) ===
        selection_frame = tk.Frame(parent, bg='#ecf0f1')
        selection_frame.pack(fill='x', padx=20, pady=20)
        tk.Label(selection_frame, text="📦 Kelola Barang dalam Container",
                font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 10))

        # === area search + delivery + tax (grid 3 kolom di baris atas) ===
        search_add_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        search_add_frame.pack(fill='x', pady=10)

        # LEFT: kontrol pemilihan container/pengirim/penerima/colli/tanggal
        left_frame = tk.Frame(search_add_frame, bg='#ecf0f1')
        left_frame.pack(side='left', fill='both', expand=False, padx=(0, 10))

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

        # Sender selection dengan debouncing
        sender_frame = tk.Frame(left_frame, bg='#ecf0f1')
        sender_frame.pack(fill='x', pady=5)
        tk.Label(sender_frame, text="📤 Pilih Pengirim:").pack(side='left')
        self.sender_search_var = tk.StringVar()
        self.sender_search_combo = ttk.Combobox(sender_frame,
                                                textvariable=self.sender_search_var,
                                                width=25)
        self.sender_search_combo.pack(side='left', padx=(5, 20))
        
        # Gunakan debounced filter
        self.sender_search_var.trace('w', self.schedule_filter)
        self.sender_search_combo.bind('<KeyRelease>', self.on_sender_keyrelease)

        # Receiver selection dengan debouncing
        receiver_frame = tk.Frame(left_frame, bg='#ecf0f1')
        receiver_frame.pack(fill='x', pady=5)
        tk.Label(receiver_frame, text="📥 Pilih Penerima:").pack(side='left')
        self.receiver_search_var = tk.StringVar()
        self.receiver_search_combo = ttk.Combobox(receiver_frame,
                                                textvariable=self.receiver_search_var,
                                                width=25)
        self.receiver_search_combo.pack(side='left', padx=(5, 20))
        
        # Gunakan debounced filter
        self.receiver_search_var.trace('w', self.schedule_filter)
        self.receiver_search_combo.bind('<KeyRelease>', self.on_receiver_keyrelease)

        # Barang selection dengan debouncing
        barang_frame = tk.Frame(left_frame, bg='#ecf0f1')
        barang_frame.pack(fill='x', pady=5)
        tk.Label(barang_frame, text="📦 Pilih Barang:").pack(side='left')
        self.barang_search_var = tk.StringVar()
        self.barang_search_combo = ttk.Combobox(barang_frame,
                                                textvariable=self.barang_search_var,
                                                width=25)
        self.barang_search_combo.pack(side='left', padx=(5, 20))

        # Gunakan debounced filter
        self.barang_search_var.trace('w', self.schedule_filter)
        self.barang_search_combo.bind('<KeyRelease>', self.on_barang_keyrelease)

        # Colli input
        colli_frame = tk.Frame(left_frame, bg='#ecf0f1')
        colli_frame.pack(fill='x', pady=5)
        tk.Label(colli_frame, text="📦 Jumlah Colli:").pack(side='left')
        self.colli_var = tk.StringVar(value="1")
        self.colli_entry = tk.Entry(colli_frame, textvariable=self.colli_var, width=8)
        self.colli_entry.pack(side='left', padx=(5, 10))

        # Satuan input
        satuan_frame = tk.Frame(left_frame, bg='#ecf0f1')
        satuan_frame.pack(fill='x', pady=5)
        tk.Label(satuan_frame, text="📏 Satuan:").pack(side='left')
        self.satuan_var = tk.StringVar(value="pcs")
        satuan_options = ["pallet", "koli", "package", "dos", "pcs"]
        self.satuan_combo = ttk.Combobox(satuan_frame, textvariable=self.satuan_var,
                                         values=satuan_options, state='readonly', width=10)
        self.satuan_combo.pack(side='left', padx=(5, 10))

        # ✅ TANGGAL - DATEPICKER DENGAN FORMAT INDONESIA
        tanggal_frame = tk.Frame(left_frame, bg='#ecf0f1')
        tanggal_frame.pack(fill='x', pady=5)

        tk.Label(
            tanggal_frame, 
            text="📅 Tanggal:", 
            font=('Arial', 10, 'bold'), 
            bg='#ecf0f1'
        ).pack(side='left')


        # ✅ DateEntry dengan format Indonesia (DD/MM/YYYY)
        self.tanggal_entry = DateEntry(
            tanggal_frame,
            font=('Arial', 10),
            width=12,
            background='#27ae60',  # Warna hijau (beda dari ETD yang orange)
            foreground='white',
            borderwidth=2,
            date_pattern='dd/MM/yyyy',  # ✅ FORMAT INDONESIA!
            locale='id_ID'
        )
        self.tanggal_entry.pack(side='left', padx=(5, 10))

        # Set nilai default ke hari ini
        self.tanggal_entry.set_date(datetime.now().date())

        # Hint (opsional)
        tk.Label(
            tanggal_frame,
            text="(klik untuk pilih)",
            font=('Arial', 8),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(side='left')

        # MIDDLE: Biaya pengantaran
        delivery_cost_frame = tk.Frame(search_add_frame, bg='#ecf0f1')
        delivery_cost_frame.pack(side='left', fill='both', expand=False, padx=10)

        tk.Label(delivery_cost_frame, text="🚚 Biaya Pengantaran:",
                font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#e67e22').pack(anchor='w', pady=(0, 5))

        desc_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        desc_row.pack(fill='x', pady=2)
        tk.Label(desc_row, text="Title:").pack(side='left')
        self.delivery_desc_var = tk.StringVar()
        self.delivery_desc_combo = ttk.Combobox(desc_row,
                                                textvariable=self.delivery_desc_var,
                                                width=37,
                                                state="normal")
        common_titles = [
            "THC Surabaya", "Freigth", "Bi. LSS", "Seal", "Bi. Cleaning Container",
            "Bi. Ops Stuffing Dalam", "Bi. Ambil Barang", "Bi. Oper Depo",
            "Bi. Kirim Dokumen", "Doe Fee", "Platform Fee", "Bi. Asuransi",
            "PPH 25", "PPH 21", "Pajak", "Trucking Samarinda ke SMA",
            "THC SMD", "Dooring Barang Ringan", "Bi. Dooring Barang Berat",
            "Buruh Harian di depo Samarinda", "Bi. Lolo Empty", "Bi. Ops Samarinda",
            "Bi. Sewa JPT & Adm", "Bi. Forklif Samarinda", "Bi. Lolo", "Rekolasi Samarinda"
        ]
        self.delivery_desc_combo['values'] = common_titles
        self.delivery_desc_combo.pack(side='left', padx=(5, 20))

        cost_desc_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        cost_desc_row.pack(fill='x', pady=2)
        tk.Label(cost_desc_row, text="Description:").pack(side='left')
        self.cost_description_var = tk.StringVar()
        self.cost_description_entry = tk.Entry(cost_desc_row, textvariable=self.cost_description_var, width=40)
        self.cost_description_entry.pack(side='left', padx=(5, 20))

        cost_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        cost_row.pack(fill='x', pady=2)
        tk.Label(cost_row, text="Biaya (Rp):").pack(side='left')
        self.delivery_cost_var = tk.StringVar(value="0")
        self.delivery_cost_entry = tk.Entry(cost_row, textvariable=self.delivery_cost_var, width=15)
        self.delivery_cost_entry.pack(side='left', padx=(5, 10))
        add_delivery_btn = tk.Button(cost_row, text="➕ Tambah Biaya", bg='#e67e22', fg='white',
                                    padx=15, pady=5, command=self.add_delivery_cost)
        self.make_button_keyboard_accessible(add_delivery_btn)
        add_delivery_btn.pack(side='left', padx=(10, 0))

        destination_row = tk.Frame(delivery_cost_frame, bg='#ecf0f1')
        destination_row.pack(fill='x', pady=2)
        tk.Label(destination_row, text="Lokasi:").pack(side='left')
        self.delivery_destination_var = tk.StringVar()
        self.delivery_destination_combo = ttk.Combobox(destination_row,
                                                    textvariable=self.delivery_destination_var,
                                                    width=37, state="readonly")
        self.delivery_destination_combo.pack(side='left', padx=(5, 20))

        # RIGHT-TOP: Ringkasan/Pra-tabel Pajak
        tax_overview_frame = tk.Frame(search_add_frame, bg='#ecf0f1', relief='flat')
        tax_overview_frame.pack(side='right', fill='both', expand=False, padx=(10, 0))

        tax_overview_frame.grid_columnconfigure(0, minsize=1000)

        tk.Label(tax_overview_frame, text="🧾 Daftar Pajak (Ringkasan)",
                font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0, 5))

        tax_tree_container = tk.Frame(tax_overview_frame, bg='#ecf0f1')
        tax_tree_container.pack(fill='both', expand=False)

        tax_columns = ('Jenis_Tax', 'Penerima', 'Jumlah', 'Tanggal')

        self.tax_summary_tree = PaginatedTreeView(
            parent=tax_tree_container,
            columns=tax_columns,
            show='headings',
            height=6,
            items_per_page=5
        )
        self.tax_summary_tree.heading('Jenis_Tax', text='Jenis Pajak')
        self.tax_summary_tree.heading('Penerima', text='Penerima')
        self.tax_summary_tree.heading('Jumlah', text='Jumlah (Rp)')
        self.tax_summary_tree.heading('Tanggal', text='Tanggal')
        self.tax_summary_tree.column('Jenis_Tax', width=120)
        self.tax_summary_tree.column('Penerima', width=120)
        self.tax_summary_tree.column('Jumlah', width=90)
        self.tax_summary_tree.column('Tanggal', width=80)
        self.tax_summary_tree.pack(fill='both', expand=True)

        # === Actions frame (tombol-tombol utama) ===
        actions_frame = tk.Frame(selection_frame, bg='#ecf0f1')
        actions_frame.pack(fill='x', pady=10)

        add_barang_btn = tk.Button(actions_frame, text="💰 Tambah Barang + Harga ke Container",
                                font=('Arial', 7, 'bold'), bg='#27ae60', fg='white',
                                padx=10, pady=5, command=self.add_selected_barang_to_container)
        self.make_button_keyboard_accessible(add_barang_btn)
        add_barang_btn.pack(side='left', padx=(0, 10))

        remove_barang_btn = tk.Button(actions_frame, text="➖ Hapus Barang dari Container",
                                    font=('Arial', 7, 'bold'), bg='#e74c3c', fg='white',
                                    padx=10, pady=5, command=self.remove_barang_from_container)
        self.make_button_keyboard_accessible(remove_barang_btn)
        remove_barang_btn.pack(side='left', padx=(0, 10))

        edit_colli_btn = tk.Button(actions_frame, text="🔢 Edit Colli, Satuan & Tanggal",
                                font=('Arial', 7, 'bold'), bg='#16a085', fg='white',
                                padx=10, pady=5, command=self.edit_barang_colli_in_container)
        self.make_button_keyboard_accessible(edit_colli_btn)
        edit_colli_btn.pack(side='left', padx=(0, 10))

        edit_price_btn = tk.Button(actions_frame, text="✏️ Edit Harga",
                                font=('Arial', 7, 'bold'), bg='#f39c12', fg='white',
                                padx=10, pady=5, command=self.edit_barang_price_in_container)
        self.make_button_keyboard_accessible(edit_price_btn)
        edit_price_btn.pack(side='left', padx=(0, 10))

        manage_delivery_btn = tk.Button(actions_frame, text="🚚 Kelola Biaya Pengantaran",
                                        font=('Arial', 7, 'bold'), bg='#e67e22', fg='white',
                                        padx=10, pady=5, command=self.manage_delivery_costs)
        self.make_button_keyboard_accessible(manage_delivery_btn)
        manage_delivery_btn.pack(side='left', padx=(0, 10))

        summary_btn = tk.Button(actions_frame, text="📊 Lihat Summary Container",
                                font=('Arial', 7, 'bold'), bg='#9b59b6', fg='white',
                                padx=10, pady=5, command=self.view_container_summary)
        self.make_button_keyboard_accessible(summary_btn)
        summary_btn.pack(side='left', padx=(0, 10))

        clear_selection_btn = tk.Button(actions_frame, text="🗑️ Bersihkan Pilihan",
                                        font=('Arial', 7, 'bold'), bg='#95a5a6', fg='white',
                                        padx=10, pady=5, command=self.clear_selection)
        self.make_button_keyboard_accessible(clear_selection_btn)
        clear_selection_btn.pack(side='left', padx=(0, 10))

        # Muat data pelanggan/pengirim/barang
        self.original_pengirim_values = []
        self.original_barang_values = []
        self.load_customers()
        self.load_pengirim()
        self.load_barang()

        # === Content frame bawah: dua panel (left=available, middle=container) ===
        content_frame = tk.Frame(parent, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1, minsize=400)
        content_frame.grid_columnconfigure(1, weight=2, minsize=600) 

        # Left side - Available barang
        left_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 3))

        tk.Label(left_frame, text="📋 Barang Tersedia", font=('Arial', 12, 'bold'), bg='#ffffff').pack(pady=10)
        available_tree_container = tk.Frame(left_frame)
        available_tree_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        columns = ('ID', 'Pengirim', 'Penerima', 'Nama', 'Dimensi', 'Volume', 'Berat')
        self.available_tree = PaginatedTreeView(parent=available_tree_container,
                                                columns=columns, show='headings',
                                                height=8, items_per_page=15)
        self.available_tree.heading('ID', text='ID')
        self.available_tree.heading('Pengirim', text='Pengirim')
        self.available_tree.heading('Penerima', text='Penerima')
        self.available_tree.heading('Nama', text='Nama Barang')
        self.available_tree.heading('Dimensi', text='P×L×T (cm)')
        self.available_tree.heading('Volume', text='Volume (m³)')
        self.available_tree.heading('Berat', text='Berat (ton)')
        self.available_tree.pack(fill='both', expand=True)

        self.load_available_barang()

        # Middle - Barang dalam Container
        middle_frame = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        middle_frame.grid(row=0, column=1, sticky='nsew', padx=(3, 0))

        self.container_label = tk.Label(middle_frame, text="📦 Barang dalam Container",
                                        font=('Arial', 12, 'bold'), bg='#ffffff')
        self.container_label.pack(pady=10)

        # Frame wrapper dengan scrollbar horizontal
        container_tree_frame = tk.Frame(middle_frame)
        container_tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Kolom yang lebih lebar
        container_columns = ('Barang_ID', 'Pengirim', 'Penerima', 'Nama', 'Satuan', 'Door', 'Dimensi',
                    'Volume', 'Berat', 'Colli', 'Harga_Unit', 'Total_Harga', 'Tanggal')

        self.container_barang_tree = PaginatedTreeView(
            parent=container_tree_frame,
            columns=container_columns, 
            show='headings',
            height=8, 
            items_per_page=20
        )
        
        # Configure headings dengan width yang lebih besar
        headers_config = [
            ('Barang_ID', 'ID', 60),
            ('Pengirim', 'Pengirim', 150),
            ('Penerima', 'Penerima', 150),
            ('Nama', 'Nama Barang', 200),
            ('Satuan', 'Satuan', 80),
            ('Door', 'Door Type', 80),
            ('Dimensi', 'P×L×T (cm)', 120),
            ('Volume', 'Volume (m³)', 100),
            ('Berat', 'Berat (ton)', 100),
            ('Colli', 'Colli', 70),
            ('Harga_Unit', 'Harga/Unit', 120),
            ('Total_Harga', 'Total Harga', 130),
            ('Tanggal', 'Ditambahkan', 110)
        ]
        
        for col, text, width in headers_config:
            self.container_barang_tree.heading(col, text=text)
            self.container_barang_tree.column(col, width=width, minwidth=width)
        
        # Pack treeview dengan scrollbar horizontal
        self.container_barang_tree.pack(fill='both', expand=True)

        # Load data container barang jika ada
        if hasattr(self, 'load_container_barang'):
            try:
                self.load_container_barang()
            except Exception:
                pass
    
    # TAMBAHKAN method baru untuk debouncing
    def schedule_filter(self, *args):
        """Schedule filter execution with debouncing"""
        # Cancel previous timer if exists
        if self.filter_timer:
            self.window.after_cancel(self.filter_timer)
        
        # Schedule new filter after delay
        self.filter_timer = self.window.after(self.filter_delay, self.execute_filter)

    def execute_filter(self):
        """Execute the actual filter"""
        sender = self.sender_search_var.get() if self.sender_search_var.get() != "" else None
        receiver = self.receiver_search_var.get() if self.receiver_search_var.get() != "" else None
        barang = self.barang_search_var.get() if self.barang_search_var.get() != "" else None

        print(f"Executing filter - Sender: {sender}, Receiver: {receiver}, Barang: {barang}")
        self.load_customer_barang_tree(sender, receiver, barang)

        self.filter_timer = None

    def on_sender_keyrelease(self, event):
        """Handle sender combobox key release for dropdown filtering"""
        typed = self.sender_search_var.get().lower()
        
        if not hasattr(self, 'original_pengirim_values') or not self.original_pengirim_values:
            self.original_pengirim_values = list(self.sender_search_combo['values'])
        
        if typed == '':
            self.sender_search_combo['values'] = self.original_pengirim_values
        else:
            filtered = [item for item in self.original_pengirim_values 
                    if typed in item.lower()]
            self.sender_search_combo['values'] = filtered

    def on_receiver_keyrelease(self, event):
        """Handle receiver combobox key release for dropdown filtering"""
        typed = self.receiver_search_var.get().lower()

        if not hasattr(self, 'original_receiver_values') or not self.original_receiver_values:
            try:
                customers = self.db.execute("SELECT customer_id, nama_customer FROM customers ORDER BY customer_id")
                self.original_receiver_values = [f"{customer[1]}" for customer in customers]
            except Exception as e:
                print(f"Error loading receivers: {e}")
                self.original_receiver_values = []

        if typed == '':
            self.receiver_search_combo['values'] = self.original_receiver_values
        else:
            filtered = [item for item in self.original_receiver_values
                    if typed in item.lower()]
            self.receiver_search_combo['values'] = filtered

    def on_barang_keyrelease(self, event):
        """Handle barang combobox key release for dropdown filtering"""
        typed = self.barang_search_var.get().lower()

        if not hasattr(self, 'original_barang_values') or not self.original_barang_values:
            try:
                barang_list = self.db.execute("SELECT DISTINCT nama_barang FROM barang ORDER BY nama_barang")
                self.original_barang_values = [barang[0] for barang in barang_list if barang[0]]
            except Exception as e:
                print(f"Error loading barang: {e}")
                self.original_barang_values = []

        if typed == '':
            self.barang_search_combo['values'] = self.original_barang_values
        else:
            filtered = [item for item in self.original_barang_values
                    if typed in item.lower()]
            self.barang_search_combo['values'] = filtered

    # TAMBAHKAN method untuk invalidate cache
    def invalidate_barang_cache(self):
        """Invalidate cached barang data"""
        self._cache_invalid = True
        if hasattr(self, '_cached_customers'):
            self._cached_customers.clear()
    
    
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
    
    def load_tax_summary_tree(self, container_id=None):
        """Load tax summary data into PaginatedTreeView"""
        try:
            # Clear existing data
            self.tax_summary_tree.set_data([])
            
            if not container_id:
                print("No container selected for tax summary")
                return
            
            # Get tax summary data
            tax_data = self.db.get_tax_summary(container_id)
            
            if not tax_data:
                print(f"No tax data found for container {container_id}")
                return
            
            formatted_data = []
            
            for i, record in enumerate(tax_data):
                try:
                    penerima = record[0] if len(record) > 0 else '-'
                    ppn_amount = float(record[1]) if len(record) > 1 and record[1] else 0
                    pph_amount = float(record[2]) if len(record) > 2 and record[2] else 0
                    created_at = str(record[3])[:10] if len(record) > 3 and record[3] else '-'
                    
                    # Add PPN row
                    if ppn_amount > 0:
                        formatted_data.append({
                            'iid': f"ppn_{i}",
                            'values': ('PPN 1.1%', penerima, f"{ppn_amount:,.0f}", created_at)
                        })
                    
                    # Add PPH row  
                    if pph_amount > 0:
                        formatted_data.append({
                            'iid': f"pph_{i}",
                            'values': ('PPH 23 2%', penerima, f"{pph_amount:,.0f}", created_at)
                        })
                        
                except Exception as record_error:
                    print(f"Error processing record {i}: {record_error}")
                    continue
            
            self.tax_summary_tree.set_data(formatted_data)
            print(f"Loaded {len(formatted_data)} tax records for container {container_id}")
            
        except Exception as e:
            print(f"Error loading tax summary: {e}")
            self.tax_summary_tree.set_data([])
           
    def format_currency_input(self, event=None):
        """Format currency input untuk rupiah"""
        try:
            # Ambil nilai dari entry
            value = self.delivery_cost_var.get().replace(',', '').replace('Rp', '').strip()
            # Izinkan angka negatif dengan menghapus tanda minus untuk pengecekan
            check_value = value.replace('-', '').replace('.', '')
            if value and check_value.isdigit():
                # Format sebagai currency (preserve tanda minus jika ada)
                num_value = int(float(value))
                formatted = f"{num_value:,}".replace(',', '.')
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
        if not deskripsi or deskripsi == "":
            messagebox.showwarning("Peringatan", "Masukkan deskripsi biaya pengantaran!")
            return
        
        try:
            biaya = float(biaya_str) if biaya_str else 0
            # Izinkan nilai negatif untuk biaya (misalnya untuk koreksi atau refund)
        except:
            messagebox.showwarning("Peringatan", "Format biaya tidak valid!")
            return
        
        try:
            # Simpan ke database dengan tipe pengantaran
            self.db.execute("""
                INSERT INTO container_delivery_costs (container_id, delivery, description, cost_description,  cost, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (container_id, lokasi, deskripsi, self.cost_description_var.get(), biaya, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Clear form dan reset placeholder
            self.delivery_desc_var.set('')
            self.cost_description_var.set('')
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
        
        try:
            # Load dan resize image
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
        
            # Set sebagai window icon
            delivery_window.iconphoto(False, icon_photo)
            
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")
        
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
        columns = ('ID', 'Deskripsi', 'Lokasi', 'Biaya')
        delivery_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)

        delivery_tree.heading('ID', text='ID')
        delivery_tree.heading('Deskripsi', text='Deskripsi')
        delivery_tree.heading('Lokasi', text='Lokasi')
        delivery_tree.heading('Biaya', text='Biaya (Rp)')
        
        delivery_tree.column('ID', width=50)
        delivery_tree.column('Deskripsi', width=250)
        delivery_tree.column('Lokasi', width=120)
        delivery_tree.column('Biaya', width=120)
        
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
        self.make_button_keyboard_accessible(edit_btn)
        edit_btn.pack(side='left', padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(action_frame, text="🗑️ Hapus Biaya", font=('Arial', 11, 'bold'),
                            bg='#e74c3c', fg='white', padx=20, pady=8,
                            command=lambda: delete_delivery_cost(delivery_tree))
        self.make_button_keyboard_accessible(delete_btn)
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

            save_btn = tk.Button(btn_frame, text="💾 Simpan", font=('Arial', 11, 'bold'),
                    bg='#27ae60', fg='white', padx=20, pady=8, command=save_edit)
            self.make_button_keyboard_accessible(save_btn)
            save_btn.pack(side='left', padx=(0, 10))

            cancel_btn = tk.Button(btn_frame, text="❌ Batal", font=('Arial', 11, 'bold'),
                    bg='#95a5a6', fg='white', padx=20, pady=8, command=edit_dialog.destroy)
            self.make_button_keyboard_accessible(cancel_btn)
            cancel_btn.pack(side='left')
        
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
            

    def on_sender_receiver_select(self, *args):
        """Handle selection of sender or receiver to load available barang"""
        # *args akan menangkap semua argument tambahan dari trace()
        # trace() mengirim: (var_name, index, mode)

        sender = self.sender_search_var.get() if self.sender_search_var.get() != "" else None
        receiver = self.receiver_search_var.get() if self.receiver_search_var.get() != "" else None
        barang = self.barang_search_var.get() if self.barang_search_var.get() != "" else None

        print(f"Sender/Receiver/Barang selection changed - Sender: {sender}, Receiver: {receiver}, Barang: {barang}")

        # Call the updated method with all parameters
        self.load_customer_barang_tree(sender, receiver, barang)

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
            summary_tree.heading('Volume', text='Total Volume (m³)')
            summary_tree.heading('Berat', text='Total Berat (ton)')
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
        self.make_button_keyboard_accessible(custom_btn)
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
        self.make_button_keyboard_accessible(custom_btn)
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
                    SELECT 
                        b.*,
                        COALESCE(s.nama_customer, b.pengirim) AS sender_name,
                        COALESCE(r.nama_customer, b.penerima) AS receiver_name
                    FROM barang b
                    LEFT JOIN customers s 
                        ON (CAST(b.pengirim AS TEXT) = CAST(s.customer_id AS TEXT) OR b.pengirim = s.nama_customer)
                    LEFT JOIN customers r 
                        ON (CAST(b.penerima AS TEXT) = CAST(r.customer_id AS TEXT) OR b.penerima = r.nama_customer)
                    WHERE b.barang_id = ?
                """, (item['id'],))
                
                if barang_data:
                    barang_details[item['id']] = dict(barang_data)
            except Exception as e:
                print(f"Error getting barang details for {item['id']}: {e}")
                barang_details[item['id']] = {}
        
        return barang_details

    def _populate_pricing_table(self, tree, selected_items, barang_details, colli_amount, pricing_data_store):
        """Populate the pricing table with data including tax rows"""
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
                'harga_container_pp': barang_detail.get('container_pp', 0) or 0,
                'harga_container_pd': barang_detail.get('container_pd', 0) or 0,
                'harga_container_dd': barang_detail.get('container_dd', 0) or 0,
                # Container size specific pricing
                'harga_container_20_pp': barang_detail.get('container_20_pp', 0) or 0,
                'harga_container_20_pd': barang_detail.get('container_20_pd', 0) or 0,
                'harga_container_20_dd': barang_detail.get('container_20_dd', 0) or 0,
                'harga_container_21_pp': barang_detail.get('container_21_pp', 0) or 0,
                'harga_container_21_pd': barang_detail.get('container_21_pd', 0) or 0,
                'harga_container_21_dd': barang_detail.get('container_21_dd', 0) or 0,
                'harga_container_40hc_pp': barang_detail.get('container_40hc_pp', 0) or 0,
                'harga_container_40hc_pd': barang_detail.get('container_40hc_pd', 0) or 0,
                'harga_container_40hc_dd': barang_detail.get('container_40hc_dd', 0) or 0,
                # Base measurements
                'm3_barang': barang_detail.get('m3_barang', 0) or 0,
                'ton_barang': barang_detail.get('ton_barang', 0) or 0,
                'container_barang': barang_detail.get('container_barang', 0) or 1,
                # Tax info
                'has_tax': barang_detail.get('pajak', 0) == 1
            }
            
            # Store data for calculations
            pricing_data_store[item['id']] = {
                'item': item,
                'pricing_info': pricing_info,
                'current_method': 'Manual',
                'current_price': 0,
                'colli_amount': colli_amount,
                'has_tax': pricing_info['has_tax']
            }
            
            # Insert main barang row into tree
            tree.insert('', tk.END, iid=item['id'], values=(
                item['name'],
                item.get('sender', ''),
                item.get('receiver', ''),
                'Manual',
                '0',
                '0'
            ), tags=('barang_row',))
            
            # If barang has tax (pajak = 1), add PPN and PPH rows
            if pricing_info['has_tax']:
                # Add PPN row (1.1%)
                ppn_id = f"ppn_{item['id']}"
                tree.insert('', tk.END, iid=ppn_id, values=(
                    f"  └── PPN 1.1% - {item['name']}",
                    item.get('sender', ''),
                    item.get('receiver', ''),
                    'PPN 1.1%',
                    '0',
                    '0'
                ), tags=('tax_row', 'ppn_row'))
                
                # Store PPN data
                pricing_data_store[ppn_id] = {
                    'item': item,
                    'parent_id': item['id'],
                    'tax_type': 'ppn',
                    'tax_rate': 0.011,
                    'current_price': 0,
                    'is_tax_row': True
                }
                
                # Add PPH row (2%)
                pph_id = f"pph_{item['id']}"
                tree.insert('', tk.END, iid=pph_id, values=(
                    f"  └── PPH 23 2% - {item['name']}",
                    item.get('sender', ''),
                    item.get('receiver', ''),
                    'PPH 23 2%',
                    '0',
                    '0'
                ), tags=('tax_row', 'pph_row'))
                
                # Store PPH data
                pricing_data_store[pph_id] = {
                    'item': item,
                    'parent_id': item['id'],
                    'tax_type': 'pph',
                    'tax_rate': 0.02,
                    'current_price': 0,
                    'is_tax_row': True
                }
        
        # Configure row styling
        tree.tag_configure('barang_row', background='#f8f9fa')
        tree.tag_configure('tax_row', background='#fff3cd', foreground='#856404')  # Light yellow for tax
        tree.tag_configure('ppn_row', background='#d1ecf1', foreground='#0c5460')  # Light blue for PPN
        tree.tag_configure('pph_row', background='#f8d7da', foreground='#721c24') 
    
    def _calculate_tax_amounts(self, parent_id, parent_total, pricing_data_store, tree):
        """Calculate and update tax amounts for PPN and PPH rows"""
        ppn_id = f"ppn_{parent_id}"
        pph_id = f"pph_{parent_id}"
        
        # Calculate PPN (1.1%)
        if ppn_id in pricing_data_store:
            ppn_amount = parent_total * 0.011
            pricing_data_store[ppn_id]['current_price'] = ppn_amount
            
            # Update PPN row in tree
            if tree.exists(ppn_id):
                tree.set(ppn_id, 'harga_unit', f"{ppn_amount:,.0f}")
                tree.set(ppn_id, 'total_harga', f"Rp {ppn_amount:,.0f}")
        
        # Calculate PPH (2%)
        if pph_id in pricing_data_store:
            pph_amount = parent_total * 0.02
            pricing_data_store[pph_id]['current_price'] = pph_amount
            
            # Update PPH row in tree
            if tree.exists(pph_id):
                tree.set(pph_id, 'harga_unit', f"{pph_amount:,.0f}")
                tree.set(pph_id, 'total_harga', f"Rp {pph_amount:,.0f}")

    def _calculate_total_price_with_tax(self, item_id, pricing_data_store, colli_amount, tree=None):
        """Calculate total price for an item with combination methods and update tax if needed"""
        data = pricing_data_store[item_id]
        method = data['current_method']
        price = data['current_price']
        pricing_info = data['pricing_info']
        
        print(f"Calculating total for item {item_id} with method {method}, price {price}, colli {colli_amount}")
        print("Pricing Info:", pricing_info)

        # Parse combination methods
        total = 0
        if method.startswith('Harga/m3_'):
            # m3-based combinations: price × m3_barang × colli
            total = price * pricing_info['m3_barang'] * colli_amount
        elif method.startswith('Harga/ton_'):
            # ton-based combinations: price × ton_barang × colli  
            total = price * pricing_info['ton_barang'] * colli_amount
        elif method.startswith('Harga/container'):
            # container-based combinations: price × container_barang × colli
            container_qty = pricing_info.get('container_barang') or 1
            total = price * container_qty * colli_amount
        elif method.startswith('Harga/colli_'):
            # colli-based combinations: price × colli
            total = price * colli_amount
        elif method == 'Manual':
            # Manual: price × colli
            total = price * colli_amount
        else:
            total = 0
        
        # Update tax rows if this barang has tax and tree is provided
        if tree and data.get('has_tax', False):
            self._calculate_tax_amounts(item_id, total, pricing_data_store, tree)
        
        return total
    
    
    
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
                print("Testing4")
                self._edit_auto_pricing(tree, item_id, pricing_data_store, colli_amount)
            elif column == '#5':  # harga_unit column
                print("Testing5")
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
                            values=[
                                'Manual',
                                'Harga/m3_pp', 'Harga/m3_pd', 'Harga/m3_dd',
                                'Harga/ton_pp', 'Harga/ton_pd', 'Harga/ton_dd',
                                'Harga/colli_pp', 'Harga/colli_pd', 'Harga/colli_dd',
                                'Harga/container_pp', 'Harga/container_pd', 'Harga/container_dd',
                                'Harga/container20_pp', 'Harga/container20_pd', 'Harga/container20_dd',
                                'Harga/container21_pp', 'Harga/container21_pd', 'Harga/container21_dd',
                                'Harga/container40hc_pp', 'Harga/container40hc_pd', 'Harga/container40hc_dd'
                            ],
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
        elif method == 'Harga/container_pp' and barang_pricing['harga_container_pp'] > 0:
            return barang_pricing['harga_container_pp']
        elif method == 'Harga/container_pd' and barang_pricing['harga_container_pd'] > 0:
            return barang_pricing['harga_container_pd']
        elif method == 'Harga/container_dd' and barang_pricing['harga_container_dd'] > 0:
            return barang_pricing['harga_container_dd']
        elif method == 'Harga/container20_pp' and barang_pricing.get('harga_container_20_pp', 0) > 0:
            return barang_pricing['harga_container_20_pp']
        elif method == 'Harga/container20_pd' and barang_pricing.get('harga_container_20_pd', 0) > 0:
            return barang_pricing['harga_container_20_pd']
        elif method == 'Harga/container20_dd' and barang_pricing.get('harga_container_20_dd', 0) > 0:
            return barang_pricing['harga_container_20_dd']
        elif method == 'Harga/container21_pp' and barang_pricing.get('harga_container_21_pp', 0) > 0:
            return barang_pricing['harga_container_21_pp']
        elif method == 'Harga/container21_pd' and barang_pricing.get('harga_container_21_pd', 0) > 0:
            return barang_pricing['harga_container_21_pd']
        elif method == 'Harga/container21_dd' and barang_pricing.get('harga_container_21_dd', 0) > 0:
            return barang_pricing['harga_container_21_dd']
        elif method == 'Harga/container40hc_pp' and barang_pricing.get('harga_container_40hc_pp', 0) > 0:
            return barang_pricing['harga_container_40hc_pp']
        elif method == 'Harga/container40hc_pd' and barang_pricing.get('harga_container_40hc_pd', 0) > 0:
            return barang_pricing['harga_container_40hc_pd']
        elif method == 'Harga/container40hc_dd' and barang_pricing.get('harga_container_40hc_dd', 0) > 0:
            return barang_pricing['harga_container_40hc_dd']
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

        elif method.startswith('Harga/container'):
            # container-based combinations: price × container_barang × colli
            container_qty = pricing_info.get('container_barang') or 1
            base_total = price * container_qty * colli_amount

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
            ("colli", "colli", '#27ae60'),
            ("container", "container", '#ff6b6b')
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

        # Grab sample pricing info to show per-size container buttons
        sample_pricing_info = {}
        for data in pricing_data_store.values():
            if isinstance(data, dict) and data.get('pricing_info') and not data.get('is_tax_row', False):
                sample_pricing_info = data['pricing_info']
                break

        if not satuan or not door:
            tk.Label(
                result_frame,
                text="Pilih Satuan dan Door/Package untuk melihat kombinasi",
                font=('Arial', 10),
                bg='#ecf0f1',
                fg='#7f8c8d'
            ).pack(pady=10)
            return

        info_text = f"Kombinasi: {satuan.upper()} - {door.upper()}"
        tk.Label(
            result_frame,
            text=info_text,
            font=('Arial', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(5, 10))

        if satuan == 'container':
            container_methods = [
                ("Container 20'", "container20", sample_pricing_info.get(f"harga_container_20_{door}", 0)),
                ("Container 21'", "container21", sample_pricing_info.get(f"harga_container_21_{door}", 0)),
                ("Container 40'HC", "container40hc", sample_pricing_info.get(f"harga_container_40hc_{door}", 0)),
                ("Container", "container", sample_pricing_info.get(f"harga_container_{door}", 0)),
            ]

            for label, method_key, price in container_methods:
                btn = tk.Button(
                    result_frame,
                    text=f"Apply {label} {door.upper()} (Rp {price:,.0f})",
                    font=('Arial', 12, 'bold'),
                    bg='#e67e22',
                    fg='white',
                    padx=25,
                    pady=10,
                    relief='flat',
                    cursor='hand2',
                    command=lambda m=f"Harga/{method_key}_{door}": self._auto_fill_all(tree, pricing_data_store, m)
                )
                btn.pack(pady=5, fill='x')
            return

        combination_method = f"Harga/{satuan}_{door}"
        combination_text = f"{satuan.upper()}_{door.upper()}"

        btn = tk.Button(
            result_frame,
            text=f"Apply {combination_text}",
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
        """Auto fill all items with selected pricing method and update tax calculations"""
        updated_count = 0
        try:
            for item_id in pricing_data_store.keys():
                # Skip tax rows
                if pricing_data_store[item_id].get('is_tax_row', False):
                    continue
                    
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
                    total = self._calculate_total_price_with_tax(item_id, pricing_data_store, colli_amount, tree)
                    tree.set(item_id, 'total_harga', f"Rp {total:,.0f}")
                    
                    updated_count += 1
            
            print(f"Auto fill completed: {updated_count} items updated with method {method}")
            messagebox.showinfo("Berhasil", f"Metode {method} telah diterapkan ke {updated_count} barang!\nPajak otomatis dihitung untuk barang yang memiliki pajak.")
            
        except Exception as e:
            print(f"Error in _auto_fill_all: {str(e)}")
            messagebox.showerror("Error", f"Gagal menerapkan auto fill: {str(e)}")

        
    def _quick_fill_manual_with_tax(self, tree, pricing_data_store, amount):
        """Quick fill all items with manual amount and update tax calculations"""
        updated_count = 0
        try:
            print(f"Starting quick fill manual with amount: {amount}")
            
            for item_id in pricing_data_store.keys():
                # Skip tax rows
                if pricing_data_store[item_id].get('is_tax_row', False):
                    continue
                    
                if tree.exists(item_id):
                    # Update data store
                    pricing_data_store[item_id]['current_method'] = 'Manual'
                    pricing_data_store[item_id]['current_price'] = amount
                    
                    # Update tree display
                    tree.set(item_id, 'auto_pricing', 'Manual')
                    tree.set(item_id, 'harga_unit', f"{amount:,.0f}")
                    
                    # Calculate total with tax
                    colli_amount = pricing_data_store[item_id]['colli_amount']
                    total = self._calculate_total_price_with_tax(item_id, pricing_data_store, colli_amount, tree)
                    tree.set(item_id, 'total_harga', f"Rp {total:,.0f}")
                    
                    updated_count += 1
                    print(f"Updated item {item_id}: price={amount}, total={total}")
            
            print(f"Manual fill completed: {updated_count} items updated")
            
            if updated_count > 0:
                messagebox.showinfo("Berhasil", f"Harga manual Rp {amount:,.0f} telah diterapkan ke {updated_count} barang!\nPajak otomatis dihitung untuk barang yang memiliki pajak.")
            else:
                messagebox.showwarning("Peringatan", "Tidak ada barang yang berhasil diupdate!")
            
        except Exception as e:
            print(f"Error in _quick_fill_manual_with_tax: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal mengisi harga manual: {str(e)}")
        
        
    def _create_pricing_actions(self, parent_frame, pricing_window, tree, pricing_data_store, selected_items, colli_amount, result):
        """Create action buttons with tax support"""
        btn_frame = tk.Frame(parent_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', padx=25, pady=20)
        
        # Action buttons
        action_frame = tk.Frame(btn_frame, bg='#ecf0f1')
        action_frame.pack()
        
        def confirm_pricing_with_tax():
            try:
                pricing_data = {}
                barang_data = {}
                tax_data = {}
                total_amount = 0
                
                for item_id, data in pricing_data_store.items():
                    if tree.exists(item_id):
                        # Handle barang rows
                        if not data.get('is_tax_row', False):
                            price = data['current_price']
                            method = data['current_method']
                            total = self._calculate_total_price_with_tax(item_id, pricing_data_store, colli_amount, tree)
                            
                            barang_data[item_id] = {
                                'harga_per_unit': price,
                                'total_harga': total,
                                'metode_pricing': method,
                                'has_tax': data.get('has_tax', False)
                            }
                            total_amount += total
                        
                        # Handle tax rows
                        else:
                            parent_id = data['parent_id']
                            tax_type = data['tax_type']
                            tax_amount = data['current_price']
                            
                            if parent_id not in tax_data:
                                tax_data[parent_id] = {}
                            
                            tax_data[parent_id][tax_type] = {
                                'amount': tax_amount,
                                'rate': data['tax_rate']
                            }
                            total_amount += tax_amount
                
                if not barang_data:
                    messagebox.showwarning("Peringatan", "Tidak ada data pricing yang valid!")
                    return
                
                # Enhanced confirmation dialog with tax info
                tax_count = len([data for data in barang_data.values() if data['has_tax']])
                total_tax_amount = sum([sum([tax['amount'] for tax in taxes.values()]) for taxes in tax_data.values()])
                
                confirm_msg = f"Konfirmasi penambahan barang dengan harga dan pajak:\n\n"
                confirm_msg += f"📊 RINGKASAN:\n"
                confirm_msg += f"• Total {len(barang_data)} barang\n"
                confirm_msg += f"• Barang dengan pajak: {tax_count}\n"
                confirm_msg += f"• Colli per barang: {colli_amount}\n"
                confirm_msg += f"• Total nilai barang: Rp {total_amount - total_tax_amount:,.0f}\n"
                if total_tax_amount > 0:
                    confirm_msg += f"• Total pajak: Rp {total_tax_amount:,.0f}\n"
                confirm_msg += f"• GRAND TOTAL: Rp {total_amount:,.0f}\n\n"
                confirm_msg += f"🚀 Lanjutkan proses?"
                
                if messagebox.askyesno("Konfirmasi Harga & Pajak", confirm_msg):
                    # Combine barang and tax data
                    pricing_data.update(barang_data)
                    for parent_id, taxes in tax_data.items():
                        pricing_data[f"ppn_{parent_id}"] = {
                            'harga_per_unit': taxes.get('ppn', {}).get('amount', 0),
                            'total_harga': taxes.get('ppn', {}).get('amount', 0),
                            'metode_pricing': 'PPN 1.1%',
                            'is_tax': True,
                            'parent_id': parent_id
                        }
                        pricing_data[f"pph_{parent_id}"] = {
                            'harga_per_unit': taxes.get('pph', {}).get('amount', 0),
                            'total_harga': taxes.get('pph', {}).get('amount', 0),
                            'metode_pricing': 'PPH 23 2%',
                            'is_tax': True,
                            'parent_id': parent_id
                        }
                    
                    result['confirmed'] = True
                    result['pricing_data'] = pricing_data
                    result['tax_data'] = tax_data
                    print(f"Pricing confirmed with {len(barang_data)} barang items and {len(tax_data)} tax items, total: {total_amount}")
                    pricing_window.destroy()
                    
            except Exception as e:
                print(f"Error in confirm_pricing_with_tax: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        def cancel_pricing():
            print("Pricing canceled by user")
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
            command=confirm_pricing_with_tax
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
        
        try:
            # Load dan resize image
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
        
            # Set sebagai window icon
            pricing_window.iconphoto(False, icon_photo)
            
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")
        
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
                    SELECT 
                        b.*,
                        COALESCE(s.nama_customer, b.pengirim) AS sender_name,
                        COALESCE(r.nama_customer, b.penerima) AS receiver_name
                    FROM barang b 
                    LEFT JOIN customers s 
                        ON (CAST(b.pengirim AS TEXT) = CAST(s.customer_id AS TEXT) OR b.pengirim = s.nama_customer)
                    LEFT JOIN customers r 
                        ON (CAST(b.penerima AS TEXT) = CAST(r.customer_id AS TEXT) OR b.penerima = r.nama_customer)
                    WHERE b.barang_id = ?
                """, (item['id'],))
                
                if barang_data:
                    barang_details[item['id']] = dict(barang_data)
            except Exception as e:
                print(f"Error getting barang details for {item['id']}: {e}")
                barang_details[item['id']] = {}
        
        return barang_details

    def _populate_edit_pricing_table(self, tree, selected_items, barang_details, pricing_data_store):
        """Populate the edit pricing table with current data including tax rows"""
        print(f"Selected items: {selected_items}")
        
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
                'harga_container_pp': barang_detail.get('container_pp', 0) or 0,
                'harga_container_pd': barang_detail.get('container_pd', 0) or 0,
                'harga_container_dd': barang_detail.get('container_dd', 0) or 0,
                # Container size specific pricing
                'harga_container_20_pp': barang_detail.get('container_20_pp', 0) or 0,
                'harga_container_20_pd': barang_detail.get('container_20_pd', 0) or 0,
                'harga_container_20_dd': barang_detail.get('container_20_dd', 0) or 0,
                'harga_container_21_pp': barang_detail.get('container_21_pp', 0) or 0,
                'harga_container_21_pd': barang_detail.get('container_21_pd', 0) or 0,
                'harga_container_21_dd': barang_detail.get('container_21_dd', 0) or 0,
                'harga_container_40hc_pp': barang_detail.get('container_40hc_pp', 0) or 0,
                'harga_container_40hc_pd': barang_detail.get('container_40hc_pd', 0) or 0,
                'harga_container_40hc_dd': barang_detail.get('container_40hc_dd', 0) or 0,
                # Base measurements
                'm3_barang': barang_detail.get('m3_barang', 0) or 0,
                'ton_barang': barang_detail.get('ton_barang', 0) or 0,
                'container_barang': barang_detail.get('container_barang') or 1,
                # Tax info - check if barang has tax
                'has_tax': barang_detail.get('pajak', 0) == 1
            }
            
            # Get current price from item data
            current_price = float(str(item.get('current_harga', 0)).replace(',', ''))
            colli = int(item.get('colli', 1))
            
            # Store data for calculations
            pricing_data_store[item['id']] = {
                'item': item,
                'pricing_info': pricing_info,
                'current_method': "Harga/" + selected_items[0]['satuan'] + "_" + selected_items[0]['door_type'],
                'current_price': current_price,
                'original_price': current_price,
                'colli_amount': colli,
                'has_tax': pricing_info['has_tax']
            }
            
            total_baru = 0
            
            if(selected_items[0]['satuan'] == 'm3'):
                total_baru = current_price * colli * (barang_detail.get('m3_barang', 0) or 0)
            elif (selected_items[0]['satuan'] == 'ton'):
                total_baru = current_price * colli * (barang_detail.get('ton_barang', 0) or 0)
            elif (selected_items[0]['satuan'] == 'container'):
                total_baru = current_price * colli * (barang_detail.get('container_barang', 0) or 0)
            else:
                total_baru = current_price * colli
            
            # Insert main barang row into tree
            tree.insert('', tk.END, iid=item['id'], values=(
                item['name'],
                str(colli),
                f"{current_price:,.0f}",
                "Harga/" + selected_items[0]['satuan'] + "_" + selected_items[0]['door_type'],
                f"{current_price:,.0f}",
                f"Rp {total_baru:,.0f}",
            ), tags=('barang_row',))
            
            # If barang has tax (pajak = 1), add PPN and PPH rows
            if pricing_info['has_tax']:
                # Calculate current tax amounts
                ppn_amount = total_baru * 0.011  # PPN 1.1%
                pph_amount = total_baru * 0.02   # PPH 23 2%
                
                # Add PPN row (1.1%)
                ppn_id = f"ppn_{item['id']}"
                tree.insert('', tk.END, iid=ppn_id, values=(
                    f"  └── PPN 1.1% - {item['name'][:20]}...",
                    str(colli),
                    f"{ppn_amount:,.0f}",
                    'PPN 1.1%',
                    f"{ppn_amount:,.0f}",
                    f"Rp {ppn_amount:,.0f}"
                ), tags=('tax_row', 'ppn_row'))
                
                # Store PPN data
                pricing_data_store[ppn_id] = {
                    'item': item,
                    'parent_id': item['id'],
                    'tax_type': 'ppn',
                    'tax_rate': 0.011,
                    'current_price': ppn_amount,
                    'original_price': ppn_amount,
                    'colli_amount': colli,
                    'is_tax_row': True
                }
                
                # Add PPH row (2%)
                pph_id = f"pph_{item['id']}"
                tree.insert('', tk.END, iid=pph_id, values=(
                    f"  └── PPH 23 2% - {item['name'][:20]}...",
                    str(colli),
                    f"{pph_amount:,.0f}",
                    'PPH 23 2%',
                    f"{pph_amount:,.0f}",
                    f"Rp {pph_amount:,.0f}"
                ), tags=('tax_row', 'pph_row'))
                
                # Store PPH data
                pricing_data_store[pph_id] = {
                    'item': item,
                    'parent_id': item['id'],
                    'tax_type': 'pph',
                    'tax_rate': 0.02,
                    'current_price': pph_amount,
                    'original_price': pph_amount,
                    'colli_amount': colli,
                    'is_tax_row': True
                }
        
        # Configure row styling
        tree.tag_configure('barang_row', background='#f8f9fa')
        tree.tag_configure('tax_row', background='#fff3cd', foreground='#856404')  # Light yellow for tax
        tree.tag_configure('ppn_row', background='#d1ecf1', foreground='#0c5460')  # Light blue for PPN
        tree.tag_configure('pph_row', background='#f8d7da', foreground='#721c24')  # Light red for PPH
     
    def _calculate_edit_tax_amounts(self, parent_id, parent_total, pricing_data_store, tree):
        """Calculate and update tax amounts for PPN and PPH rows in edit dialog"""
        ppn_id = f"ppn_{parent_id}"
        pph_id = f"pph_{parent_id}"
        
        # Calculate PPN (1.1%)
        if ppn_id in pricing_data_store:
            ppn_amount = parent_total * 0.011
            pricing_data_store[ppn_id]['current_price'] = ppn_amount
            
            # Update PPN row in tree
            if tree.exists(ppn_id):
                tree.set(ppn_id, 'harga_lama', f"{ppn_amount:,.0f}")
                tree.set(ppn_id, 'harga_baru', f"{ppn_amount:,.0f}")
                tree.set(ppn_id, 'total_baru', f"Rp {ppn_amount:,.0f}")
        
        # Calculate PPH (2%)
        if pph_id in pricing_data_store:
            pph_amount = parent_total * 0.02
            pricing_data_store[pph_id]['current_price'] = pph_amount
            
            # Update PPH row in tree
            if tree.exists(pph_id):
                tree.set(pph_id, 'harga_lama', f"{pph_amount:,.0f}")
                tree.set(pph_id, 'harga_baru', f"{pph_amount:,.0f}")
                tree.set(pph_id, 'total_baru', f"Rp {pph_amount:,.0f}")
     
    def _calculate_edit_total_price_with_tax(self, item_id, pricing_data_store, tree=None):
        """Calculate total price for edit dialog and update tax if needed"""
        data = pricing_data_store[item_id]
        method = data['current_method']
        price = data['current_price']
        pricing_info = data['pricing_info']
        colli_amount = data['colli_amount']
        
        print(f"Calculating edit total for item {item_id} with method {method}, price {price}, colli {colli_amount}")

        # Parse combination methods
        total = 0
        if method.startswith('Harga/m3_'):
            # m3-based combinations: price × m3_barang × colli
            total = price * pricing_info['m3_barang'] * colli_amount
        elif method.startswith('Harga/ton_'):
            # ton-based combinations: price × ton_barang × colli  
            total = price * pricing_info['ton_barang'] * colli_amount
        elif method.startswith('Harga/container'):
            # container-based combinations: price × container_barang × colli
            container_qty = pricing_info.get('container_barang') or 1
            total = price * container_qty * colli_amount
        elif method.startswith('Harga/colli_'):
            # colli-based combinations: price × colli
            total = price * colli_amount
        elif method == 'Manual':
            # Manual: price × colli
            total = price * colli_amount
        else:
            total = 0
        
        # Update tax rows if this barang has tax and tree is provided
        if tree and data.get('has_tax', False):
            self._calculate_edit_tax_amounts(item_id, total, pricing_data_store, tree)
        
        return total
     
    def _setup_edit_table_editing(self, tree, pricing_data_store):
        """Setup double-click editing for edit table cells with tax support"""
        def on_double_click(event):
            item_id = tree.selection()[0] if tree.selection() else None
            if not item_id:
                return
            
            # Skip editing for tax rows
            if pricing_data_store.get(item_id, {}).get('is_tax_row', False):
                messagebox.showinfo("Info", "Baris pajak dihitung otomatis berdasarkan harga barang utama.")
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
        """Edit auto pricing method for edit dialog with tax calculation"""
        bbox = tree.bbox(item_id, 'auto_pricing')
        if not bbox:
            return
        
        # Create combobox with combination options
        current_method = pricing_data_store.get(item_id, {}).get('current_method', 'Manual')
        combo_var = tk.StringVar(value=current_method)
        combo = ttk.Combobox(tree, textvariable=combo_var, 
                            values=['Manual', 'Harga/m3_pp', 'Harga/m3_pd', 'Harga/m3_dd',
                                'Harga/ton_pp', 'Harga/ton_pd', 'Harga/ton_dd',
                                'Harga/colli_pp', 'Harga/colli_pd', 'Harga/colli_dd',
                                'Harga/container_pp', 'Harga/container_pd', 'Harga/container_dd',
                                'Harga/container20_pp', 'Harga/container20_pd', 'Harga/container20_dd',
                                'Harga/container21_pp', 'Harga/container21_pd', 'Harga/container21_dd',
                                'Harga/container40hc_pp', 'Harga/container40hc_pd', 'Harga/container40hc_dd'],
                            state='readonly')
        
        combo.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        combo.focus_set()
        
        def on_combo_change(event=None):
            new_method = combo_var.get()
            if item_id not in pricing_data_store:
                pricing_data_store[item_id] = {}
            pricing_data_store[item_id]['current_method'] = new_method
            
            # Auto-set price based on method
            new_price = self._calculate_edit_auto_price(item_id, new_method, pricing_data_store)
            pricing_data_store[item_id]['current_price'] = new_price
            
            # Update tree
            tree.set(item_id, 'auto_pricing', new_method)
            tree.set(item_id, 'harga_baru', f"{new_price:,.0f}")
            
            # Calculate total with tax
            total = self._calculate_edit_total_price_with_tax(item_id, pricing_data_store, tree)
            tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
            
            combo.destroy()
        
        combo.bind('<<ComboboxSelected>>', on_combo_change)
        combo.bind('<Return>', on_combo_change)
        combo.bind('<Escape>', lambda e: combo.destroy())
        combo.bind('<FocusOut>', lambda e: combo.destroy())
        
    def _edit_harga_baru_edit(self, tree, item_id, pricing_data_store):
        """Edit harga baru for edit dialog with tax calculation"""
        bbox = tree.bbox(item_id, 'harga_baru')
        if not bbox:
            return
        
        # Create entry with safe access
        current_price = pricing_data_store.get(item_id, {}).get('current_price', 0)
        entry_var = tk.StringVar(value=str(int(current_price)))
        entry = tk.Entry(tree, textvariable=entry_var)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        def on_entry_confirm(event=None):
            try:
                new_price = float(entry_var.get().replace(',', ''))
                if item_id not in pricing_data_store:
                    pricing_data_store[item_id] = {}
                pricing_data_store[item_id]['current_price'] = new_price
                pricing_data_store[item_id]['current_method'] = 'Manual'
                
                # Update tree
                tree.set(item_id, 'harga_baru', f"{new_price:,.0f}")
                tree.set(item_id, 'auto_pricing', 'Manual')
                
                # Calculate total with tax
                total = self._calculate_edit_total_price_with_tax(item_id, pricing_data_store, tree)
                tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
                
            except ValueError:
                pass  # Invalid input, ignore
            
            entry.destroy()
        
        entry.bind('<Return>', on_entry_confirm)
        entry.bind('<Escape>', lambda e: entry.destroy())
        entry.bind('<FocusOut>', lambda e: on_entry_confirm())
         
    def _calculate_edit_auto_price(self, item_id, method, pricing_data_store):
        """Calculate automatic price for edit dialog based on combination method"""
        try:
            data = pricing_data_store.get(item_id, {})
            pricing_info = data.get('pricing_info', {})
            
            # Handle combination methods
            if method == 'Harga/m3_pp' and pricing_info.get('harga_m3_pp', 0) > 0:
                return pricing_info['harga_m3_pp']
            elif method == 'Harga/m3_pd' and pricing_info.get('harga_m3_pd', 0) > 0:
                return pricing_info['harga_m3_pd']
            elif method == 'Harga/m3_dd' and pricing_info.get('harga_m3_dd', 0) > 0:
                return pricing_info['harga_m3_dd']
            elif method == 'Harga/ton_pp' and pricing_info.get('harga_ton_pp', 0) > 0:
                return pricing_info['harga_ton_pp']
            elif method == 'Harga/ton_pd' and pricing_info.get('harga_ton_pd', 0) > 0:
                return pricing_info['harga_ton_pd']
            elif method == 'Harga/ton_dd' and pricing_info.get('harga_ton_dd', 0) > 0:
                return pricing_info['harga_ton_dd']
            elif method == 'Harga/colli_pp' and pricing_info.get('harga_colli_pp', 0) > 0:
                return pricing_info['harga_colli_pp']
            elif method == 'Harga/colli_pd' and pricing_info.get('harga_colli_pd', 0) > 0:
                return pricing_info['harga_colli_pd']
            elif method == 'Harga/colli_dd' and pricing_info.get('harga_colli_dd', 0) > 0:
                return pricing_info['harga_colli_dd']
            elif method == 'Harga/container_pp' and pricing_info.get('harga_container_pp', 0) > 0:
                return pricing_info['harga_container_pp']
            elif method == 'Harga/container_pd' and pricing_info.get('harga_container_pd', 0) > 0:
                return pricing_info['harga_container_pd']
            elif method == 'Harga/container_dd' and pricing_info.get('harga_container_dd', 0) > 0:
                return pricing_info['harga_container_dd']
            elif method == 'Harga/container20_pp' and pricing_info.get('harga_container_20_pp', 0) > 0:
                return pricing_info['harga_container_20_pp']
            elif method == 'Harga/container20_pd' and pricing_info.get('harga_container_20_pd', 0) > 0:
                return pricing_info['harga_container_20_pd']
            elif method == 'Harga/container20_dd' and pricing_info.get('harga_container_20_dd', 0) > 0:
                return pricing_info['harga_container_20_dd']
            elif method == 'Harga/container21_pp' and pricing_info.get('harga_container_21_pp', 0) > 0:
                return pricing_info['harga_container_21_pp']
            elif method == 'Harga/container21_pd' and pricing_info.get('harga_container_21_pd', 0) > 0:
                return pricing_info['harga_container_21_pd']
            elif method == 'Harga/container21_dd' and pricing_info.get('harga_container_21_dd', 0) > 0:
                return pricing_info['harga_container_21_dd']
            elif method == 'Harga/container40hc_pp' and pricing_info.get('harga_container_40hc_pp', 0) > 0:
                return pricing_info['harga_container_40hc_pp']
            elif method == 'Harga/container40hc_pd' and pricing_info.get('harga_container_40hc_pd', 0) > 0:
                return pricing_info['harga_container_40hc_pd']
            elif method == 'Harga/container40hc_dd' and pricing_info.get('harga_container_40hc_dd', 0) > 0:
                return pricing_info['harga_container_40hc_dd']
            else:
                # Return original price if no valid combination found
                return data.get('original_price', 0)
                
        except Exception as e:
            print(f"Error calculating edit auto price for {item_id}: {e}")
            return pricing_data_store.get(item_id, {}).get('original_price', 0)
        
        
    def _setup_edit_pricing_controls(self, controls_frame, pricing_tree, pricing_data_store):
        """Setup combination pricing controls for edit dialog"""
        
        # State variables for combination
        selected_satuan = tk.StringVar()
        selected_door = tk.StringVar()
        
        # Step 1: Satuan selection buttons
        satuan_types = [
            ("m³", "m3", '#3498db'),
            ("ton", "ton", '#e74c3c'),
            ("colli", "colli", '#27ae60'),
            ("container", "container", '#ff6b6b')
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
        self.make_button_keyboard_accessible(custom_btn)
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

        # Grab sample pricing info to show per-size container buttons
        sample_pricing_info = {}
        for data in pricing_data_store.values():
            if isinstance(data, dict) and data.get('pricing_info') and not data.get('is_tax_row', False):
                sample_pricing_info = data['pricing_info']
                break

        if not satuan or not door:
            tk.Label(
                result_frame,
                text="Pilih Satuan dan Door/Package untuk melihat kombinasi",
                font=('Arial', 10),
                bg='#ecf0f1',
                fg='#7f8c8d'
            ).pack(pady=10)
            return

        info_text = f"Kombinasi: {satuan.upper()} - {door.upper()}"
        tk.Label(
            result_frame,
            text=info_text,
            font=('Arial', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(5, 10))

        if satuan == 'container':
            container_methods = [
                ("Container 20'", "container20", sample_pricing_info.get(f"harga_container_20_{door}", 0)),
                ("Container 21'", "container21", sample_pricing_info.get(f"harga_container_21_{door}", 0)),
                ("Container 40'HC", "container40hc", sample_pricing_info.get(f"harga_container_40hc_{door}", 0)),
                ("Container", "container", sample_pricing_info.get(f"harga_container_{door}", 0)),
            ]

            for label, method_key, price in container_methods:
                btn = tk.Button(
                    result_frame,
                    text=f"Apply {label} {door.upper()} (Rp {price:,.0f})",
                    font=('Arial', 12, 'bold'),
                    bg='#e67e22',
                    fg='white',
                    padx=25,
                    pady=10,
                    relief='flat',
                    cursor='hand2',
                    command=lambda m=f"Harga/{method_key}_{door}": self._edit_auto_fill_all(pricing_tree, pricing_data_store, m)
                )
                btn.pack(pady=5, fill='x')
            return

        combination_method = f"Harga/{satuan}_{door}"
        combination_text = f"{satuan.upper()}_{door.upper()}"

        btn = tk.Button(
            result_frame,
            text=f"Apply {combination_text}",
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
        """Auto fill all items with selected pricing method for edit dialog including tax"""
        updated_count = 0
        try:
            for item_id in pricing_data_store.keys():
                # Skip tax rows - they will be calculated automatically
                if pricing_data_store.get(item_id, {}).get('is_tax_row', False):
                    continue
                    
                if pricing_tree.exists(item_id):
                    # Ensure item data exists
                    if item_id not in pricing_data_store:
                        pricing_data_store[item_id] = {}
                        
                    pricing_data_store[item_id]['current_method'] = method
                    
                    # Calculate new price
                    new_price = self._calculate_edit_auto_price(item_id, method, pricing_data_store)
                    pricing_data_store[item_id]['current_price'] = new_price
                    
                    # Update tree
                    pricing_tree.set(item_id, 'auto_pricing', method)
                    pricing_tree.set(item_id, 'harga_baru', f"{new_price:,.0f}")
                    
                    # Calculate total with tax
                    total = self._calculate_edit_total_price_with_tax(item_id, pricing_data_store, pricing_tree)
                    pricing_tree.set(item_id, 'total_baru', f"Rp {total:,.0f}")
                    
                    updated_count += 1
            
            print(f"Edit auto fill completed: {updated_count} items updated with method {method}")
            messagebox.showinfo("Berhasil", f"Metode {method} telah diterapkan ke {updated_count} barang!\nPajak otomatis dihitung untuk barang yang memiliki pajak.")
            
        except Exception as e:
            print(f"Error in _edit_auto_fill_all: {str(e)}")
            messagebox.showerror("Error", f"Gagal menerapkan auto fill: {str(e)}")
            
    def _edit_quick_fill_manual(self, pricing_tree, pricing_data_store, amount):
        """Quick fill all items with manual amount for edit dialog including tax"""
        updated_count = 0
        try:
            print(f"Starting edit quick fill manual with amount: {amount}")
            
            for item_id in pricing_data_store.keys():
                # Skip tax rows - they will be calculated automatically
                if pricing_data_store.get(item_id, {}).get('is_tax_row', False):
                    continue
                    
                if pricing_tree.exists(item_id):
                    # Ensure item data exists
                    if item_id not in pricing_data_store:
                        pricing_data_store[item_id] = {}
                        
                    # Update data store
                    pricing_data_store[item_id]['current_method'] = 'Manual'
                    pricing_data_store[item_id]['current_price'] = amount
                    
                    # Update tree display
                    pricing_tree.set(item_id, 'auto_pricing', 'Manual')
                    pricing_tree.set(item_id, 'harga_baru', f"{amount:,.0f}")
                    
                    # Calculate total with tax
                    total = self._calculate_edit_total_price_with_tax(item_id, pricing_data_store, pricing_tree)
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
                    print(f"Data di confirm: {data}")
                    
                    # Skip tax rows
                    if data.get('is_tax_row', False):
                        continue
                        
                    if pricing_tree.exists(item_id):
                        current_price = data.get('current_price', 0)
                        original_price = data.get('original_price', 0)
                        method = data.get('current_method', 'Manual')
                        colli = data.get('colli_amount', 1)
                        
                        # Ambil data dari pricing_info dengan safe access
                        pricing_info = data.get('pricing_info', {})
                        m3_barang = pricing_info.get('m3_barang', 0)
                        ton_barang = pricing_info.get('ton_barang', 0)
                        
                        # Safe parsing untuk satuan dari method
                        satuan = 'manual'
                        if method and '/' in method and '_' in method:
                            try:
                                satuan = method.split('/')[1].split('_')[0]
                            except (IndexError, AttributeError):
                                satuan = 'manual'
                        
                        total = 0
                        
                        if satuan == "m3" and m3_barang > 0:
                            total = current_price * colli * m3_barang
                        elif satuan == "ton" and ton_barang > 0:
                            total = current_price * colli * ton_barang
                        else:
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
                            item_info = data.get('item', {})
                            changed_items.append({
                                'id': item_id,
                                'name': item_info.get('name', f'Item {item_id}'),
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
                    # Skip tax rows
                    if data.get('is_tax_row', False):
                        continue
                        
                    if pricing_tree.exists(item_id):
                        original_price = data.get('original_price', 0)
                        
                        # Reset to original values
                        data['current_method'] = 'Manual'
                        data['current_price'] = original_price
                        
                        # Update tree
                        pricing_tree.set(item_id, 'auto_pricing', 'Manual')
                        pricing_tree.set(item_id, 'harga_baru', f"{original_price:,.0f}")
                        
                        # Calculate total
                        colli = data.get('colli_amount', 1)
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
        
          
    def edit_barang_colli_in_container(self):
        """Edit colli amount of selected barang in container"""
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        selection = self.container_barang_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang yang akan diedit jumlah collinya!")
            return
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            # Get selected barang details
            selected_items = []
            for item in selection:
                values = self.container_barang_tree.item(item)['values']
                
                # **PERBAIKAN: Ambil barang_id langsung dari kolom pertama**
                barang_id = values[0]        # Barang_ID column (index 0) ✅
                pengirim = values[1]         # Pengirim column (index 1)
                penerima = values[2]         # Penerima column (index 2)
                nama_barang = values[3]      # Nama barang column (index 3)
                current_colli = values[9]    # Colli column (index 9)
                harga_unit = values[10]      # Harga per unit (index 10)
                assigned_at = values[12]     # Assigned at timestamp (index 12)
                
                selected_items.append({
                    'id': barang_id,  # ✅ Sudah pasti benar!
                    'name': nama_barang,
                    'pengirim': pengirim,
                    'penerima': penerima,
                    'current_colli': current_colli,
                    'harga_unit': harga_unit,
                    'assigned_at': assigned_at
                })
            
            if not selected_items:
                messagebox.showerror("Error", "Tidak dapat menemukan data barang yang dipilih!")
                return
            
            # Show edit colli dialog
            self.show_edit_colli_dialog(selected_items, container_id)
            
        except Exception as e:
            print(f"Error in edit_barang_colli_in_container: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal mengedit colli: {str(e)}")


    def show_edit_colli_dialog(self, selected_items, container_id):
        """Show dialog to edit colli, satuan, and dates with tax recalculation - DATEPICKER VERSION"""
        edit_window = tk.Toplevel(self.window)
        edit_window.title("🔢 Edit Colli, Satuan & Tanggal")
        edit_window.geometry("600x500")
        edit_window.configure(bg='#ecf0f1')
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        try:
            # Load dan resize image
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            edit_window.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")
        
        # Center window
        edit_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - 300
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - 250
        edit_window.geometry(f"600x500+{x}+{y}")
        
        # Header
        header = tk.Label(
            edit_window,
            text="🔢 EDIT COLLI, SATUAN & TANGGAL",
            font=('Arial', 16, 'bold'),
            bg='#16a085',
            fg='white',
            pady=15
        )
        header.pack(fill='x')

        # Info frame
        info_frame = tk.Frame(edit_window, bg='#ecf0f1')
        info_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(info_frame,
                text=f"📝 Mengedit colli, satuan, dan tanggal untuk {len(selected_items)} barang | 💡 Harga total dan pajak akan dihitung ulang",
                font=('Arial', 11, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack()
        
        # Main frame with scrollbar for multiple items
        main_frame = tk.Frame(edit_window, bg='#ffffff', relief='solid', bd=1)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(main_frame, bg='#ffffff')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store colli and date entries
        edit_entries = {}
        
        # Create form for each item
        for i, item in enumerate(selected_items):
            item_frame = tk.LabelFrame(scrollable_frame, 
                                    text=f"Barang {i+1}: {item['name'][:30]}...",
                                    font=('Arial', 10, 'bold'), bg='#ffffff', fg='#2c3e50')
            item_frame.pack(fill='x', padx=15, pady=10)
            
            # Item details
            details_frame = tk.Frame(item_frame, bg='#ffffff')
            details_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(details_frame, text=f"Pengirim: {item['pengirim']}", 
                    font=('Arial', 9), bg='#ffffff').pack(anchor='w')
            tk.Label(details_frame, text=f"Penerima: {item['penerima']}", 
                    font=('Arial', 9), bg='#ffffff').pack(anchor='w')
            
            # Colli input
            colli_frame = tk.Frame(item_frame, bg='#ffffff')
            colli_frame.pack(fill='x', padx=10, pady=10)
            
            tk.Label(colli_frame, text="Jumlah Colli:", 
                    font=('Arial', 10, 'bold'), bg='#ffffff').pack(side='left')
            
            current_colli_label = tk.Label(colli_frame, 
                                        text=f"(Saat ini: {item['current_colli']})", 
                                        font=('Arial', 9), bg='#ffffff', fg='#7f8c8d')
            current_colli_label.pack(side='left', padx=(5, 10))
            
            colli_var = tk.StringVar(value=str(item['current_colli']))
            colli_entry = tk.Entry(colli_frame, textvariable=colli_var,
                                font=('Arial', 10), width=10)
            colli_entry.pack(side='left', padx=5)

            # Satuan input
            satuan_frame = tk.Frame(item_frame, bg='#ffffff')
            satuan_frame.pack(fill='x', padx=10, pady=10)

            tk.Label(satuan_frame, text="📏 Satuan:",
                    font=('Arial', 10, 'bold'), bg='#ffffff').pack(side='left')

            # Get current satuan from database
            try:
                current_satuan_data = self.db.execute_one("""
                    SELECT satuan FROM detail_container
                    WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                """, (item['id'], container_id, item['assigned_at']))

                current_satuan = current_satuan_data[0] if current_satuan_data and current_satuan_data[0] else 'pcs'
            except Exception as satuan_error:
                print(f"Error getting current satuan: {satuan_error}")
                current_satuan = 'pcs'

            current_satuan_label = tk.Label(satuan_frame,
                                        text=f"(Saat ini: {current_satuan})",
                                        font=('Arial', 9), bg='#ffffff', fg='#7f8c8d')
            current_satuan_label.pack(side='left', padx=(5, 10))

            satuan_var = tk.StringVar(value=current_satuan)
            satuan_options = ["pallet", "koli", "package", "dos", "pcs"]
            satuan_combo = ttk.Combobox(satuan_frame, textvariable=satuan_var,
                                       values=satuan_options, state='readonly', width=10)
            satuan_combo.pack(side='left', padx=5)

            # ✅ TANGGAL INPUT - DATEPICKER
            date_frame = tk.Frame(item_frame, bg='#ffffff')
            date_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(date_frame, text="📅 Tanggal:",
                    font=('Arial', 10, 'bold'), bg='#ffffff').pack(side='left')

            # Get current date from database (in YYYY-MM-DD format)
            try:
                current_date_data = self.db.execute_one("""
                    SELECT tanggal FROM detail_container
                    WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                """, (item['id'], container_id, item['assigned_at']))

                current_date_db = current_date_data[0] if current_date_data and current_date_data[0] else datetime.now().strftime('%Y-%m-%d')
            except Exception as date_error:
                print(f"Error getting current date: {date_error}")
                current_date_db = datetime.now().strftime('%Y-%m-%d')
            
            # ✅ CONVERT TO INDONESIAN FORMAT FOR DISPLAY
            current_date_indonesian = self.format_date_indonesian(current_date_db)
            
            # ✅ DateEntry dengan format Indonesia (DD/MM/YYYY)
            date_entry = DateEntry(
                date_frame,
                font=('Arial', 10),
                width=12,
                background='#16a085',  # Warna teal
                foreground='white',
                borderwidth=2,
                date_pattern='dd/MM/yyyy',  # ✅ FORMAT INDONESIA!
                locale='id_ID'
            )
            date_entry.pack(side='left', padx=(5, 10))
            
            # ✅ Set nilai awal dari database (convert YYYY-MM-DD → date object)
            try:
                date_obj = datetime.strptime(current_date_db, '%Y-%m-%d').date()
                date_entry.set_date(date_obj)
            except Exception as e:
                print(f"Error setting date: {e}")
                date_entry.set_date(datetime.now().date())
            
            # Label info (saat ini)
            current_date_label = tk.Label(date_frame, 
                                        text=f"(Saat ini: {current_date_indonesian})", 
                                        font=('Arial', 9), bg='#ffffff', fg='#7f8c8d')
            current_date_label.pack(side='left', padx=(10, 0))
            
            # ✅ SIMPAN REFERENCE
            edit_entries[item['id']] = {
                'colli_var': colli_var,
                'colli_entry': colli_entry,
                'satuan_var': satuan_var,
                'satuan_combo': satuan_combo,
                'date_entry': date_entry,  # ✅ DateEntry object
                'item': item
            }
        
        # Action buttons
        btn_frame = tk.Frame(edit_window, bg='#ecf0f1')
        btn_frame.pack(fill='x', padx=20, pady=15)
        
        # ✅ NESTED FUNCTION - save_colli_and_date_changes
        def save_colli_and_date_changes():
            """Save colli and date changes with DatePicker format"""
            try:
                print("🚀 Starting save_colli_and_date_changes...")
                success_count = 0
                error_count = 0
                tax_updated_count = 0
                changes_made = []
                
                for barang_id, entry_data in edit_entries.items():
                    try:
                        new_colli = int(entry_data['colli_var'].get())
                        old_colli = int(entry_data['item']['current_colli'])

                        # Get new satuan from dropdown
                        new_satuan = entry_data['satuan_var'].get()

                        print(f"\n📦 Processing Barang ID: {barang_id}")
                        print(f"   Old Colli: {old_colli}, New Colli: {new_colli}")
                        print(f"   New Satuan: {new_satuan}")

                        # ✅ GET TANGGAL DARI DateEntry (sudah format DD/MM/YYYY)
                        new_date_indonesian = entry_data['date_entry'].get_date().strftime('%d/%m/%Y')
                        print(f"   New Date (Indonesian): {new_date_indonesian}")
                        
                        if new_colli <= 0:
                            messagebox.showwarning("Peringatan", 
                                                f"Colli untuk '{entry_data['item']['name']}' harus lebih dari 0!")
                            error_count += 1
                            continue
                        
                        # ✅ CONVERT INDONESIAN DATE TO DATABASE FORMAT (YYYY-MM-DD)
                        try:
                            date_obj = datetime.strptime(new_date_indonesian, '%d/%m/%Y')
                            new_date_db = date_obj.strftime('%Y-%m-%d')
                            print(f"   New Date (DB Format): {new_date_db}")
                        except Exception as date_error:
                            print(f"❌ Date conversion error: {date_error}")
                            messagebox.showwarning("Format Tanggal Salah", 
                                                f"Format tanggal untuk '{entry_data['item']['name']}' tidak valid!\n\n"
                                                f"Gunakan format: DD/MM/YYYY\n"
                                                f"Contoh: 31/10/2025")
                            error_count += 1
                            continue
                        
                        # Check if there are any changes
                        colli_changed = new_colli != old_colli
                        
                        # Get old date for comparison
                        
                        print("Checking Assign at: " + entry_data['item']['assigned_at'])
                        
                        
                        
                        try:
                            old_data = self.db.execute_one("""
                                SELECT tanggal, satuan FROM detail_container
                                WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                            """, (barang_id, container_id, entry_data['item']['assigned_at']))

                            old_date_db = old_data[0] if old_data and old_data[0] else None
                            old_satuan = old_data[1] if old_data and len(old_data) > 1 and old_data[1] else 'pcs'

                            date_changed = new_date_db != old_date_db
                            satuan_changed = new_satuan != old_satuan

                            print(f"   Old Date (DB): {old_date_db}")
                            print(f"   Old Satuan: {old_satuan}")
                            print(f"   Date Changed: {date_changed}, Colli Changed: {colli_changed}, Satuan Changed: {satuan_changed}")
                        except Exception as get_data_error:
                            print(f"⚠️ Error getting old data: {get_data_error}")
                            date_changed = True
                            satuan_changed = True

                        if colli_changed or date_changed or satuan_changed:
                            # Calculate new total price
                            harga_unit = float(str(entry_data['item']['harga_unit']).replace(',', ''))
                            
                            print(f"   Harga Unit: {harga_unit}")
                            
                            # Get barang data for calculation
                            barang_data = self.db.execute_one("""
                                SELECT b.*, dc.door_type
                                FROM barang b
                                JOIN detail_container dc ON b.barang_id = dc.barang_id
                                WHERE b.barang_id = ? AND dc.container_id = ?
                            """, (barang_id, container_id))

                            if barang_data:
                                try:
                                    m3_barang = float(barang_data['m3_barang']) if barang_data['m3_barang'] else 0.0
                                except (KeyError, TypeError, ValueError):
                                    m3_barang = 0.0

                                try:
                                    ton_barang = float(barang_data['ton_barang']) if barang_data['ton_barang'] else 0.0
                                except (KeyError, TypeError, ValueError):
                                    ton_barang = 0.0

                                try:
                                    container_barang = float(barang_data['container_barang']) if barang_data['container_barang'] else 0.0
                                except (KeyError, TypeError, ValueError):
                                    container_barang = 0.0

                                print(f"   New Satuan: {new_satuan}, M3: {m3_barang}, Ton: {ton_barang}, Container: {container_barang}")

                                # Calculate new total based on NEW satuan from dropdown
                                if new_satuan == 'm3':
                                    new_total = harga_unit * new_colli * m3_barang
                                elif new_satuan == 'ton':
                                    new_total = harga_unit * new_colli * ton_barang
                                elif new_satuan == 'container':
                                    new_total = harga_unit * new_colli * container_barang
                                else:
                                    new_total = harga_unit * new_colli
                            else:
                                new_total = harga_unit * new_colli
                            
                            print(f"   New Total: {new_total}")
                            
                            # ✅ UPDATE WITH DATABASE FORMAT DATE (YYYY-MM-DD) AND SATUAN
                            print(f"   🔄 Updating database...")
                            self.db.execute("""
                                UPDATE detail_container
                                SET colli_amount = ?, total_harga = ?, tanggal = ?, satuan = ?
                                WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                            """, (new_colli, new_total, new_date_db, new_satuan, barang_id, container_id,
                                entry_data['item']['assigned_at']))
                            
                            print(f"   ✅ Database updated successfully!")
                            
                            # Tax recalculation
                            tax_recalculated = False
                            try:
                                print(f"   🧾 Checking tax calculation...")
                                barang_tax_data = self.db.execute_one(
                                    "SELECT pajak, penerima FROM barang WHERE barang_id = ?", 
                                    (barang_id,)
                                )
                                
                                if barang_tax_data and barang_tax_data[0] == 1:
                                    print(f"   💰 Tax enabled for this item")
                                    penerima_id = barang_tax_data[1]
                                    receiver_data = self.db.get_customer_by_id(penerima_id)
                                    receiver_name = receiver_data.get('nama_customer', 'Unknown') if receiver_data else 'Unknown'
                                    
                                    ppn_amount = new_total * 0.011
                                    pph23_amount = new_total * 0.02
                                    
                                    print(f"   PPN: {ppn_amount}, PPH23: {pph23_amount}")
                                    
                                    existing_tax = self.db.execute_one("""
                                        SELECT tax_id FROM barang_tax 
                                        WHERE container_id = ? AND barang_id = ?
                                    """, (container_id, barang_id))
                                    
                                    if existing_tax:
                                        tax_id = existing_tax[0]
                                        print(f"   🔄 Updating existing tax record (ID: {tax_id})")
                                        self.db.execute("""
                                            UPDATE barang_tax 
                                            SET ppn_amount = ?, pph23_amount = ?
                                            WHERE tax_id = ?
                                        """, (ppn_amount, pph23_amount, tax_id))
                                        
                                        # Update tax_id in detail_container
                                        self.db.execute("""
                                            UPDATE detail_container 
                                            SET tax_id = ?
                                            WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                                        """, (tax_id, barang_id, container_id, entry_data['item']['assigned_at']))
                                    else:
                                        print(f"   ➕ Creating new tax record")
                                        self.db.execute("""
                                            INSERT INTO barang_tax (container_id, barang_id, penerima, ppn_amount, pph23_amount, created_at)
                                            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                                        """, (container_id, barang_id, receiver_name, ppn_amount, pph23_amount))
                                        
                                        # Get the newly created tax_id
                                        new_tax = self.db.execute_one("""
                                            SELECT tax_id FROM barang_tax 
                                            WHERE container_id = ? AND barang_id = ?
                                            ORDER BY created_at DESC LIMIT 1
                                        """, (container_id, barang_id))
                                        
                                        if new_tax:
                                            tax_id = new_tax[0]
                                            self.db.execute("""
                                                UPDATE detail_container 
                                                SET tax_id = ?
                                                WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                                            """, (tax_id, barang_id, container_id, entry_data['item']['assigned_at']))
                                    
                                    tax_recalculated = True
                                    tax_updated_count += 1
                                    print(f"   ✅ Tax recalculated successfully!")
                                else:
                                    print(f"   ℹ️ Tax not enabled for this item")
                                    
                            except Exception as tax_error:
                                print(f"   ⚠️ Error recalculating tax: {tax_error}")
                                import traceback
                                traceback.print_exc()
                            
                            # ✅ BUILD CHANGE DESCRIPTION WITH INDONESIAN DATE
                            change_desc = []
                            if colli_changed:
                                change_desc.append(f"Colli: {old_colli} → {new_colli}")
                            if satuan_changed:
                                change_desc.append(f"Satuan: {old_satuan} → {new_satuan}")
                            if date_changed:
                                try:
                                    old_date_obj = datetime.strptime(old_date_db, '%Y-%m-%d')
                                    old_date_indonesian = old_date_obj.strftime('%d/%m/%Y')
                                except:
                                    old_date_indonesian = old_date_db if old_date_db else 'N/A'
                                change_desc.append(f"Tanggal: {old_date_indonesian} → {new_date_indonesian}")
                            
                            changes_made.append({
                                'name': entry_data['item']['name'],
                                'changes': ", ".join(change_desc),
                                'old_total': harga_unit * old_colli,
                                'new_total': new_total,
                                'tax_recalculated': tax_recalculated
                            })
                            success_count += 1
                            print(f"   ✅ Successfully processed Barang ID: {barang_id}")
                        else:
                            print(f"   ℹ️ No changes detected for Barang ID: {barang_id}")
                            
                    except ValueError as ve:
                        error_count += 1
                        print(f"❌ ValueError for barang {barang_id}: {ve}")
                        messagebox.showwarning("Peringatan", 
                                            f"Format colli tidak valid untuk '{entry_data['item']['name']}'!")
                    except Exception as e:
                        error_count += 1
                        print(f"❌ Error updating barang {barang_id}: {e}")
                        import traceback
                        traceback.print_exc()
                
                print(f"\n📊 Summary: Success={success_count}, Errors={error_count}, Tax Updated={tax_updated_count}")
                
                # Show results
                if success_count > 0:
                    result_msg = f"✅ Berhasil mengupdate {success_count} barang!\n"
                    
                    if tax_updated_count > 0:
                        result_msg += f"🧾 Pajak diperbarui untuk {tax_updated_count} barang dengan pajak.\n"
                    
                    result_msg += "\nDetail perubahan:\n"
                    for change in changes_made[:5]:
                        result_msg += f"• {change['name'][:25]}...\n"
                        result_msg += f"  {change['changes']}\n"
                        result_msg += f"  Total: Rp {change['old_total']:,.0f} → Rp {change['new_total']:,.0f}\n"
                        if change['tax_recalculated']:
                            result_msg += f"  📊 Pajak dihitung ulang\n"
                    
                    if len(changes_made) > 5:
                        result_msg += f"... dan {len(changes_made) - 5} perubahan lainnya\n"
                    
                    messagebox.showinfo("Sukses", result_msg)
                    
                    # Refresh displays
                    print("🔄 Refreshing display...")
                    self.load_container_barang(container_id)
                    
                    if tax_updated_count > 0:
                        self.load_tax_summary_tree(container_id)
                    
                    edit_window.destroy()
                else:
                    messagebox.showinfo("Info", "Tidak ada perubahan yang disimpan.")
                    
                if error_count > 0:
                    messagebox.showwarning("Peringatan", f"{error_count} barang gagal diupdate.")
                    
            except Exception as e:
                print(f"❌ FATAL ERROR in save_colli_and_date_changes: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Gagal menyimpan perubahan: {str(e)}")
        
        
        # Create buttons
        save_btn = tk.Button(btn_frame, text="💾 Simpan Perubahan",
                font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                padx=25, pady=10, command=save_colli_and_date_changes)
        self.make_button_keyboard_accessible(save_btn)
        save_btn.pack(side='left', padx=(0, 10))

        cancel_btn = tk.Button(btn_frame, text="❌ Batal",
                font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                padx=25, pady=10, command=edit_window.destroy)
        self.make_button_keyboard_accessible(cancel_btn)
        cancel_btn.pack(side='left')
        
        # Focus on first entry
        if edit_entries:
            first_entry = list(edit_entries.values())[0]['colli_entry']
            first_entry.focus_set()
            first_entry.select_range(0, tk.END)
    
    # Helper method to refresh tax summary
    def refresh_tax_summary(self, container_id):
        """Refresh tax summary after tax-related operations"""
        try:
            if hasattr(self, 'tax_summary_tree'):
                self.load_tax_summary_tree(container_id)
                print(f"✅ Tax summary refreshed for container {container_id}")
        except Exception as e:
            print(f"⚠️ Error refreshing tax summary: {e}")

    # Method to calculate total with proper pricing method  
    def _calculate_new_total_with_pricing_method(self, harga_unit, new_colli, barang_data):
        """Calculate new total price based on pricing method"""
        try:
            satuan = barang_data.get('satuan', 'manual')
            m3_barang = float(barang_data.get('m3_barang', 0) or 0)
            ton_barang = float(barang_data.get('ton_barang', 0) or 0)
            container_barang = float(barang_data.get('container_barang', 0) or 0)

            if satuan == 'm3' and m3_barang > 0:
                # m3-based pricing: harga_unit * m3_barang * colli
                return harga_unit * m3_barang * new_colli
            elif satuan == 'ton' and ton_barang > 0:
                # ton-based pricing: harga_unit * ton_barang * colli
                return harga_unit * ton_barang * new_colli
            elif satuan == 'container' and container_barang > 0:
                # container-based pricing: harga_unit * container_barang * colli
                return harga_unit * container_barang * new_colli
            else:
                # colli-based or manual pricing: harga_unit * colli
                return harga_unit * new_colli
                
        except Exception as e:
            print(f"Error calculating total with pricing method: {e}")
            # Fallback to simple multiplication
            return harga_unit * new_colli
    
    def edit_barang_price_in_container(self):
        """Edit price of selected barang in container with tax recalculation"""
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
                
                # **PERBAIKAN: Ambil barang_id langsung dari kolom pertama**
                barang_id = values[0]        # Barang_ID column (index 0) ✅
                pengirim = values[1]         # Pengirim column (index 1)
                penerima = values[2]         # Penerima column (index 2) 
                nama_barang = values[3]      # Nama barang column (index 3)
                satuan = values[4]           # Satuan column (index 4)
                door_type = values[5]        # Door type column (index 5)
                dimensi = values[6]          # Dimensi column (index 6)
                m3_barang = values[7]        # M3 column (index 7)
                ton_barang = values[8]       # Ton column (index 8)
                colli = values[9]            # Colli column (index 9)
                current_harga = values[10]   # Harga per unit (index 10)
                current_total = values[11]   # Total harga (index 11)
                assigned_at = values[12]     # Assigned at timestamp (index 12)
                
                print(f"Debug edit price - barang_id: {barang_id}, nama: {nama_barang}")
                print(f"Current harga: {current_harga}, Current total: {current_total}")
                
                # Safe parsing untuk harga yang mungkin berformat currency
                def safe_parse_currency(value, default=0):
                    """Safely parse currency value that might contain commas, Rp, etc."""
                    try:
                        if not value or str(value).strip() in ['-', '', 'None']:
                            return default
                        
                        # Clean currency formatting
                        clean_value = str(value).replace('Rp', '').replace(',', '').replace(' ', '').strip()
                        
                        if not clean_value:
                            return default
                        
                        return float(clean_value)
                        
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing currency value '{value}': {e}")
                        return default
                
                # Parse current prices safely
                parsed_current_harga = safe_parse_currency(current_harga, 0)
                parsed_current_total = safe_parse_currency(current_total, 0)
                
                # Safe parsing untuk colli
                def safe_parse_colli(value, default=1):
                    """Safely parse colli value"""
                    try:
                        if not value or str(value).strip() in ['-', '', 'None']:
                            return default
                        return int(float(str(value)))
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing colli value '{value}': {e}")
                        return default
                
                parsed_colli = safe_parse_colli(colli, 1)
                
                selected_items.append({
                    'id': barang_id,  # ✅ Sudah pasti benar!
                    'name': nama_barang,
                    'pengirim': pengirim,
                    'penerima': penerima,
                    'satuan': satuan,
                    'door_type': door_type,
                    'current_harga': parsed_current_harga,
                    'current_total': parsed_current_total,
                    'colli': parsed_colli,
                    'assigned_at': assigned_at
                })
                
                print(f"Added item: {nama_barang}, barang_id: {barang_id}, harga: {parsed_current_harga}, total: {parsed_current_total}, colli: {parsed_colli}")
            
            if not selected_items:
                messagebox.showerror("Error", "Tidak dapat menemukan data barang yang dipilih!")
                return
            
            # Create edit pricing dialog
            edit_result = self.create_edit_pricing_dialog(selected_items, container_id)
            
            if edit_result and edit_result['confirmed']:
                # Update prices in database with tax recalculation
                success_count = 0
                error_count = 0
                tax_updated_count = 0
                
                for barang_id, price_data in edit_result['pricing_data'].items():
                    try:
                        # Find the corresponding item for assigned_at
                        corresponding_item = next((item for item in selected_items if str(item['id']) == str(barang_id)), None)
                        
                        if corresponding_item:
                            new_harga_unit = price_data['harga_per_unit']
                            new_total_harga = price_data['total_harga']
                            
                            # Update dengan assigned_at untuk unique identification
                            update_query = """
                                UPDATE detail_container 
                                SET harga_per_unit = ?, total_harga = ? 
                                WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                            """
                            update_params = (
                                new_harga_unit, 
                                new_total_harga, 
                                barang_id, 
                                container_id,
                                corresponding_item['assigned_at']
                            )
                            
                            print(f"Updating price: {update_query}")
                            print(f"Parameters: {update_params}")
                            
                            # Check if record exists
                            check_query = "SELECT COUNT(*) FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at = ?"
                            check_params = (barang_id, container_id, corresponding_item['assigned_at'])
                            check_result = self.db.execute(check_query, check_params)
                            count = check_result[0][0] if check_result else 0
                            
                            print(f"Records found to update: {count}")
                            
                            if count > 0:
                                result = self.db.execute(update_query, update_params)
                                print(f"✅ Updated price for barang {barang_id}")
                            else:
                                # Try fallback without assigned_at
                                print(f"⚠️ Trying fallback update without assigned_at...")
                                fallback_query = """
                                    UPDATE detail_container 
                                    SET harga_per_unit = ?, total_harga = ? 
                                    WHERE barang_id = ? AND container_id = ?
                                """
                                fallback_params = (new_harga_unit, new_total_harga, barang_id, container_id)
                                result = self.db.execute(fallback_query, fallback_params)
                                print(f"✅ Updated price for barang {barang_id} (fallback method)")
                            
                            # TAMBAHAN: Recalculate tax if barang has tax
                            tax_recalculated = False
                            try:
                                barang_tax_data = self.db.execute_one(
                                    "SELECT pajak, penerima FROM barang WHERE barang_id = ?", 
                                    (barang_id,)
                                )
                                
                                if barang_tax_data and barang_tax_data[0] == 1:  # pajak = 1
                                    penerima_id = barang_tax_data[1]
                                    
                                    # Get receiver name
                                    receiver_data = self.db.get_customer_by_id(penerima_id)
                                    receiver_name = receiver_data.get('nama_customer', 'Unknown') if receiver_data else 'Unknown'
                                    
                                    # Calculate new tax amounts based on new total
                                    ppn_amount = new_total_harga * 0.011  # PPN 1.1%
                                    pph23_amount = new_total_harga * 0.02  # PPH 23 2%
                                    
                                    # Check if tax record exists for this container and barang
                                    existing_tax = self.db.execute_one("""
                                        SELECT tax_id FROM barang_tax 
                                        WHERE container_id = ? AND barang_id = ?
                                    """, (container_id, barang_id))
                                    
                                    if existing_tax:
                                        # Update existing tax record
                                        tax_id = existing_tax[0]
                                        self.db.execute("""
                                            UPDATE barang_tax 
                                            SET ppn_amount = ?, pph23_amount = ?
                                            WHERE tax_id = ?
                                        """, (ppn_amount, pph23_amount, tax_id))
                                        
                                        print(f"✅ Updated tax for barang {barang_id}: PPN={ppn_amount:,.0f}, PPH23={pph23_amount:,.0f}")
                                    else:
                                        # Create new tax record
                                        self.db.execute("""
                                            INSERT INTO barang_tax (container_id, barang_id, penerima, ppn_amount, pph23_amount, created_at)
                                            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                                        """, (container_id, barang_id, receiver_name, ppn_amount, pph23_amount))
                                        
                                        print(f"✅ Created new tax for barang {barang_id}: PPN={ppn_amount:,.0f}, PPH23={pph23_amount:,.0f}")
                                    
                                    # Update tax_id in detail_container if needed
                                    if existing_tax:
                                        tax_id = existing_tax[0]
                                        try:
                                            self.db.execute("""
                                                UPDATE detail_container 
                                                SET tax_id = ?
                                                WHERE barang_id = ? AND container_id = ? AND assigned_at = ?
                                            """, (tax_id, barang_id, container_id, corresponding_item['assigned_at']))
                                            print(f"✅ Linked tax_id {tax_id} to detail_container")
                                        except Exception as tax_link_error:
                                            print(f"⚠️ Warning: Could not link tax_id to detail_container: {tax_link_error}")
                                    
                                    tax_recalculated = True
                                    tax_updated_count += 1
                                    
                            except Exception as tax_error:
                                print(f"⚠️ Error recalculating tax for barang {barang_id}: {tax_error}")
                                # Don't fail the whole operation if tax calculation fails
                                pass
                            
                            success_count += 1
                            
                        else:
                            # Fallback: update without assigned_at (should not happen with new approach)
                            print(f"⚠️ No corresponding item found for barang_id {barang_id}, using fallback...")
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
                            print(f"✅ Updated price for barang {barang_id} (no assigned_at)")
                            
                    except Exception as e:
                        error_count += 1
                        print(f"❌ Error updating price for barang {barang_id}: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Show enhanced result with tax information
                if success_count > 0:
                    result_msg = f"✅ Berhasil mengupdate harga {success_count} barang!"
                    
                    if tax_updated_count > 0:
                        result_msg += f"\n🧾 Pajak diperbarui untuk {tax_updated_count} barang dengan pajak."
                    
                    result_msg += f"\n\n📊 Detail:"
                    result_msg += f"\n• Barang diupdate: {success_count}"
                    if tax_updated_count > 0:
                        result_msg += f"\n• Pajak dihitung ulang: {tax_updated_count}"
                        result_msg += f"\n• PPN 1.1% dan PPH 23 2% telah disesuaikan dengan harga baru"
                    
                    messagebox.showinfo("Sukses", result_msg)
                    
                    # Refresh displays
                    self.load_container_barang(container_id)
                    
                    # Refresh tax summary if there were tax updates
                    if tax_updated_count > 0:
                        self.load_tax_summary_tree(container_id)
                        print(f"🔄 Tax summary refreshed after updating {tax_updated_count} tax records")
                
                if error_count > 0:
                    messagebox.showwarning("Peringatan", f"⚠️ {error_count} barang gagal diupdate.")
            
        except Exception as e:
            print(f"❌ Error in edit_barang_price_in_container: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal mengedit harga: {str(e)}")
        
          
    def load_customers(self):
        """Load all customers for search dropdown"""
        try:
            # Get unique customers from barang table
            customers = self.db.get_all_customers()
            customer_list = [row['nama_customer'] for row in customers if row['nama_customer']]
            self.receiver_search_combo['values'] = customer_list
        except Exception as e:
            print(f"Error loading customers: {e}")
            
    def load_pengirim(self):
        """Load pengirim customers for search dropdown"""
        try:
            customers = self.db.get_all_customers()
            customer_list = [row['nama_customer'] for row in customers if row['nama_customer']]
            self.sender_search_combo['values'] = customer_list
            self.original_pengirim_values = customer_list
        except Exception as e:
            print(f"Error loading pengirim customers: {e}")

    def load_barang(self):
        """Load distinct barang names for search dropdown"""
        try:
            barang_list = self.db.execute("SELECT DISTINCT nama_barang FROM barang ORDER BY nama_barang")
            barang_names = [barang[0] for barang in barang_list if barang[0]]
            self.barang_search_combo['values'] = barang_names
            self.original_barang_values = barang_names
        except Exception as e:
            print(f"Error loading barang: {e}")

    def load_customer_barang_tree(self, sender_name=None, receiver_name=None, barang_name=None):
        """Load barang based on sender, receiver, and/or barang name selection - OPTIMIZED"""
        try:
            print(f"Loading customer barang tree with sender: {sender_name}, receiver: {receiver_name}, barang: {barang_name}")

            # PERBAIKAN: Cache data barang untuk menghindari query berulang
            if not hasattr(self, '_cached_barang_data') or self._cache_invalid:
                all_barang = self.db.get_all_barang()
                all_barang = [barang for barang in all_barang if barang is not None]
                self._cached_barang_data = all_barang
                self._cache_invalid = False
            else:
                all_barang = self._cached_barang_data

            # PERBAIKAN: Pre-load customer data untuk menghindari query berulang
            if not hasattr(self, '_cached_customers'):
                self._cached_customers = {}

            # Filter data
            filtered_data = []
            sender_lower = sender_name.lower() if sender_name else None
            receiver_lower = receiver_name.lower() if receiver_name else None
            barang_lower = barang_name.lower() if barang_name else None
            
            for barang in all_barang:
                try:
                    if barang is None:
                        continue
                    
                    # Get sender name (with caching)
                    pengirim_id = barang.get('pengirim', '')
                    if pengirim_id:
                        if pengirim_id not in self._cached_customers:
                            try:
                                sender_data = self.db.get_sender_by_id(pengirim_id)
                                if sender_data:
                                    self._cached_customers[pengirim_id] = sender_data.get('nama_pengirim', '')
                                else:
                                    customer_data = self.db.get_customer_by_id(pengirim_id)
                                    self._cached_customers[pengirim_id] = customer_data.get('nama_customer', '') if customer_data else ''
                            except:
                                self._cached_customers[pengirim_id] = barang.get('sender_name', '')
                        
                        pengirim = self._cached_customers.get(pengirim_id, '')
                    else:
                        pengirim = ''
                    
                    # Get receiver name (with caching)
                    penerima_id = barang.get('penerima', '')
                    if penerima_id:
                        if penerima_id not in self._cached_customers:
                            try:
                                customer_data = self.db.get_customer_by_id(penerima_id)
                                self._cached_customers[penerima_id] = customer_data.get('nama_customer', '') if customer_data else ''
                            except:
                                self._cached_customers[penerima_id] = barang.get('receiver_name', '')
                        
                        penerima = self._cached_customers.get(penerima_id, '')
                    else:
                        penerima = ''
                    
                    # Filter check
                    show_item = True

                    if sender_lower and sender_lower not in pengirim.lower():
                        show_item = False

                    if receiver_lower and receiver_lower not in penerima.lower():
                        show_item = False

                    if barang_lower:
                        nama_barang = str(barang.get('nama_barang', '')).lower()
                        if barang_lower not in nama_barang:
                            show_item = False
                    
                    if show_item:
                        # Format for display
                        panjang = barang.get('panjang_barang', '-')
                        lebar = barang.get('lebar_barang', '-')
                        tinggi = barang.get('tinggi_barang', '-')
                        dimensi = f"{panjang}×{lebar}×{tinggi}"
                        
                        volume = str(barang.get('m3_barang', '-'))
                        berat = str(barang.get('ton_barang', '-'))
                        
                        row_data = (
                            str(barang.get('barang_id', '')),
                            pengirim or '-',
                            penerima or '-',
                            str(barang.get('nama_barang', '-')),
                            dimensi,
                            volume,
                            berat
                        )
                        
                        filtered_data.append(row_data)
                        
                except Exception as e:
                    print(f"Error processing barang: {e}")
                    continue
            
            # Set filtered data to tree
            self.available_tree.set_data(filtered_data)
            
            print(f"Filtered {len(filtered_data)} items from {len(all_barang)} total")
            
        except Exception as e:
            print(f"Error loading customer barang tree: {e}")
            import traceback
            traceback.print_exc()
            self.available_tree.set_data([])
        
        
    def load_available_barang(self):
        """Load available barang ke PaginatedTreeView"""
        try:
            # Ambil data dari database
            barang_list = self.db.get_all_barang()

            # Refresh barang dropdown list
            self.load_barang()

            # Format data
            formatted_data = []
            for barang in barang_list:
                if barang is None:
                    continue

                row_data = (
                    str(barang.get('barang_id', '')),
                    str(barang.get('sender_name', '')),
                    str(barang.get('receiver_name', '')),
                    str(barang.get('nama_barang', '')),
                    f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}",
                    f"{float(barang.get('m3_barang', 0)):.4f}" if barang.get('m3_barang') else '0.0000',
                    format_ton(barang.get('ton_barang', 0)) if barang.get('ton_barang') else '0'
                )
                formatted_data.append(row_data)
            self.available_tree.set_data(formatted_data)
            print(f"Loaded {len(formatted_data)} items to PaginatedTreeView")

        except Exception as e:
            print(f"Error loading barang: {e}")
            self.available_tree.set_data([])  # Set empty jika error
        
           
    def clear_selection(self):
        """Clear customer and barang selection"""
        self.selected_container_var.set("")
        self.sender_search_var.set("")
        self.receiver_search_var.set("")
        self.barang_search_var.set("")
        self.colli_var.set("1")
        self.satuan_var.set("pcs")

        self.tanggal_entry.set_date(datetime.now().date())

        self.load_available_barang()
        self.load_container_barang(None)
    
    print("[DEBUG] Selection cleared - tanggal reset to today")
    
    def add_selected_barang_to_container(self):
        """Add selected barang from treeview to container with pricing and tax calculation"""
        # ============================================
        # STEP 1: Validate Container Selection
        # ============================================
        if not self.selected_container_var.get():
            messagebox.showwarning("Peringatan", "Pilih container terlebih dahulu!")
            return
        
        # ============================================
        # STEP 2: Validate Barang Selection
        # ============================================
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih barang dari daftar barang tersedia!")
            return
        
        # ============================================
        # STEP 3: Validate Colli
        # ============================================
        try:
            colli_amount = int(self.colli_var.get())
            if colli_amount <= 0:
                messagebox.showwarning("Peringatan", "Jumlah colli harus lebih dari 0!")
                return
        except ValueError:
            messagebox.showwarning("Peringatan", "Jumlah colli harus berupa angka!")
            return
        
        # ============================================
        # STEP 4: Validate Tanggal Indonesia
        # ============================================
        tanggal_indonesian = self.tanggal_entry.get().strip()  # ✅ DateEntry sudah return DD/MM/YYYY
        
        if not tanggal_indonesian:
            messagebox.showwarning("Validasi", "Masukkan tanggal!")
            return
        
        if not self.validate_indonesian_date(tanggal_indonesian):
            messagebox.showerror(
                "Format Tanggal Salah",
                f"Format tanggal tidak valid!\n\n"
                f"Input Anda: {tanggal_indonesian}\n\n"
                f"Gunakan format: DD/MM/YYYY\n"
                f"Contoh: 31/10/2025"
            )
            return
        
        # ============================================
        # STEP 5: Convert ke Format Database
        # ============================================
        tanggal_db = self.parse_indonesian_date(tanggal_indonesian)
        
        print(f"[DEBUG] Tanggal Input (Indonesia): {tanggal_indonesian}")
        print(f"[DEBUG] Tanggal Database (YYYY-MM-DD): {tanggal_db}")
        
        try:
            container_id = int(self.selected_container_var.get().split(' - ')[0])
            
            # ============================================
            # STEP 6: Get Selected Barang from Treeview
            # ============================================
            selected_items = []
            for item in selection:
                values = self.available_tree.item(item)['values']
                # Based on treeview structure: ID, Pengirim, Penerima, Nama, Dimensi, Volume, Berat
                barang_id = values[0]      # ID column
                barang_sender = values[1]  # Pengirim column
                barang_receiver = values[2] # Penerima column
                barang_name = values[3]    # Nama barang column
                
                # Validate sender/receiver selection if any is selected
                sender_selected = self.sender_search_var.get()
                receiver_selected = self.receiver_search_var.get()
                
                validation_error = False
                error_message = ""
                
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
            
            # ============================================
            # STEP 7: Show Pricing Dialog
            # ============================================
            pricing_result = self.create_pricing_dialog(selected_items, colli_amount)
            
            if not pricing_result:
                return  # User cancelled
            
            # ============================================
            # STEP 8: Add Barang to Container with Pricing
            # ============================================
            success_count = 0
            error_count = 0
            tax_calculated_count = 0
            success_details = []
            error_details = []
            total_tax_amount = 0
            
            for item in selected_items:
                try:
                    barang_id = item['id']
                    price_data = pricing_result['pricing_data'].get(barang_id, {
                        'harga_per_unit': 0, 
                        'total_harga': 0
                    })
                    
                    print(f"Processing item {barang_id}: {price_data}")

                    # Get satuan from dropdown instead of pricing method
                    satuan_value = self.satuan_var.get()

                    # ✅ KIRIM TANGGAL DATABASE FORMAT (YYYY-MM-DD)
                    success = self.db.assign_barang_to_container_with_pricing(
                        barang_id,
                        container_id,
                        satuan_value,  # Use satuan from dropdown
                        price_data['metode_pricing'].split('_')[1] if 'metode_pricing' in price_data else 'manual',
                        colli_amount,
                        price_data['harga_per_unit'],
                        price_data['total_harga'],
                        tanggal_db  # ✅ KIRIM FORMAT DATABASE (YYYY-MM-DD)
                    )
                    
                    if success:
                        success_count += 1
                        success_details.append(f"✅ {item['name']} (ID: {barang_id})")
                        print(f"✅ Added barang {barang_id} ({item['name']}) dengan tanggal {tanggal_indonesian}")
                        
                        # ============================================
                        # STEP 9: Calculate Tax if Applicable
                        # ============================================
                        try:
                            barang_data = self.db.execute_one(
                                "SELECT pajak, penerima FROM barang WHERE barang_id = ?", 
                                (barang_id,)
                            )
                            
                            if barang_data and barang_data[0] == 1:  # pajak = 1
                                penerima_id = barang_data[1]
                                
                                # Get receiver name
                                receiver_data = self.db.get_customer_by_id(penerima_id)
                                receiver_name = receiver_data.get('nama_customer', 'Unknown') if receiver_data else 'Unknown'
                                
                                # Calculate tax amounts
                                total_nilai = price_data['total_harga']
                                ppn_amount = total_nilai * 0.011  # PPN 1.1%
                                pph23_amount = total_nilai * 0.02  # PPH 23 2%
                                total_tax = ppn_amount + pph23_amount
                                
                                tax_calculated_count += 1
                                total_tax_amount += total_tax
                                
                                print(f"✅ Tax calculated for barang {barang_id}: PPN={ppn_amount:,.0f}, PPH={pph23_amount:,.0f}")
                                    
                        except Exception as tax_error:
                            print(f"⚠️ Error calculating tax for barang {barang_id}: {tax_error}")
                            # Don't fail the whole process if tax calculation fails
                            continue
                        
                    else:
                        error_count += 1
                        error_details.append(f"❌ {item['name']} (ID: {barang_id}) - Database operation failed")
                        
                except Exception as e:
                    error_count += 1
                    error_details.append(f"❌ {item['name']} (ID: {item['id']}) - {str(e)}")
                    print(f"❌ Error adding barang {item['id']} ({item['name']}): {e}")
            
            # ============================================
            # STEP 10: Show Result Message
            # ============================================
            result_msg = ""
            if success_count > 0:
                result_msg += f"🎉 Berhasil menambahkan {success_count} barang ke container!\n"
                result_msg += f"Setiap barang ditambahkan dengan {colli_amount} colli.\n"
                result_msg += f"Tanggal: {tanggal_indonesian}\n"
                
                if tax_calculated_count > 0:
                    result_msg += f"\n💰 PAJAK DIHITUNG:\n"
                    result_msg += f"• Barang dengan pajak: {tax_calculated_count}\n"
                    result_msg += f"• Total pajak: Rp {total_tax_amount:,.0f}\n"
                    result_msg += f"• PPN 1.1% + PPH 23 2% telah disimpan ke database\n"
                
                result_msg += f"\nDetail berhasil:\n" + "\n".join(success_details[:5])  # Show max 5 items
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
            
            # ============================================
            # STEP 11: Refresh Displays
            # ============================================
            if success_count > 0:
                # Refresh displays based on current sender/receiver/barang filter
                sender = self.sender_search_var.get() if self.sender_search_var.get() != "" else None
                receiver = self.receiver_search_var.get() if self.receiver_search_var.get() != "" else None
                barang = self.barang_search_var.get() if self.barang_search_var.get() != "" else None

                # Refresh available barang list with current filters
                self.load_customer_barang_tree(sender, receiver, barang)
                    
                # Refresh container barang list
                self.load_container_barang(container_id)
                
                # Refresh tax summary
                self.load_tax_summary_tree(container_id)
                
                # Refresh other lists
                self.load_containers()  # Refresh container list to update item count
                self.load_customers()   # Refresh customer list
                self.load_pengirim()    # Refresh pengirim list
                
                print(f"✅ Successfully added {success_count} barang with date {tanggal_indonesian} ({tanggal_db})")
            
        except ValueError as ve:
            messagebox.showerror("Error", f"Format data tidak valid: {str(ve)}")
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Error in add_selected_barang_to_container: {error_detail}")
            messagebox.showerror("Error", f"Gagal menambah barang ke container: {str(e)}")
        
           
    def center_window(self):
        """Center window with boundary checks"""
        self.window.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        window_width = min(int(screen_width * 0.85), 1400)
        window_height = min(int(screen_height * 0.90), 1000)
        
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2) - 50
        
        if x + window_width > screen_width:
            x = screen_width - window_width - 20
        if x < 0:
            x = 20
        if y + window_height > screen_height:
            y = screen_height - window_height - 50
        if y < 0:
            y = 20
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.lift()
        self.window.focus_force()
    
    def load_container_combo(self):
        """Load containers into combobox"""
        try:
            containers = self.db.get_all_containers()
            container_list = []
            for c in containers:
                container_text = f"{c['container_id']} - {c.get('container', 'No Container')}"
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
            self.load_tax_summary_tree(container_id)
            
            # Update label
            container_info = selection.split(' - ', 1)[1] if ' - ' in selection else selection
            self.container_label.config(text=f"📦 Barang dalam Container: {container_info}")
    
         
    def remove_barang_from_container(self):
        """Remove selected barang from container with tax cleanup"""
        
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
                
                # **PERBAIKAN: Ambil barang_id langsung dari kolom pertama**
                barang_id = values[0]        # Barang_ID column (index 0) ✅
                pengirim = values[1]         # Pengirim column (index 1)
                penerima = values[2]         # Penerima column (index 2)
                nama_barang = values[3]      # Nama barang column (index 3)
                satuan = values[4]           # Satuan column (index 4)
                door_type = values[5]        # Door type column (index 5)
                dimensi = values[6]          # Dimensi column (index 6)
                m3_barang = values[7]        # M3 column (index 7)
                ton_barang = values[8]       # Ton column (index 8)
                colli = values[9]            # Colli column (index 9)
                harga_unit = values[10]      # Harga per unit (index 10)
                total_harga = values[11]     # Total harga (index 11)
                assigned_at = values[12]     # Assigned at timestamp (index 12)
                
                print(f"\n{'='*60}")
                print(f"🔍 DEBUG - Treeview values:")
                print(f"{'='*60}")
                print(f"Barang ID   : {barang_id}  ← LANGSUNG DAPAT!")
                print(f"Nama Barang : '{nama_barang}'")
                print(f"Pengirim    : '{pengirim}'")
                print(f"Penerima    : '{penerima}'")
                print(f"Assigned at : '{assigned_at}'")
                print(f"Type        : {type(assigned_at)}")
                print(f"Length      : {len(str(assigned_at))}")
                
                # **TIDAK PERLU QUERY LAGI! Langsung pakai barang_id**
                selected_items.append({
                    'id': barang_id,  # ✅ Sudah pasti benar!
                    'nama': nama_barang,
                    'pengirim': pengirim,
                    'penerima': penerima,
                    'colli': colli,
                    'harga_unit': harga_unit,
                    'total_harga': total_harga,
                    'assigned_at': assigned_at
                })
            
            if not selected_items:
                messagebox.showerror("Error", "Tidak dapat menemukan data barang yang dipilih!")
                return
            
            # Confirm removal with details including pricing
            if len(selected_items) == 1:
                item = selected_items[0]
                confirm_msg = f"Hapus barang dari container?\n\n" + \
                            f"Barang ID: {item['id']}\n" + \
                            f"Barang: {item['nama']}\n" + \
                            f"Pengirim: {item['pengirim']}\n" + \
                            f"Penerima: {item['penerima']}\n" + \
                            f"Colli: {item['colli']}\n" + \
                            f"Harga/Unit: Rp {item['harga_unit']}\n" + \
                            f"Total Harga: Rp {item['total_harga']}\n" + \
                            f"Assigned At: {item['assigned_at']}\n\n" + \
                            f"Barang dan data pajaknya akan dihapus dari container."
            else:
                total_nilai = 0
                confirm_msg = f"Hapus {len(selected_items)} barang dari container?\n\n"
                for i, item in enumerate(selected_items[:3], 1):
                    confirm_msg += f"{i}. {item['nama']} (ID: {item['id']}) - {item['colli']} colli - Rp {item['total_harga']}\n"
                    try:
                        clean_total = str(item['total_harga']).replace(',', '').replace('Rp', '').replace(' ', '')
                        if clean_total and clean_total.replace('.', '').isdigit():
                            total_nilai += float(clean_total)
                    except Exception as parse_error:
                        print(f"Error parsing total_harga {item['total_harga']}: {parse_error}")
                if len(selected_items) > 3:
                    confirm_msg += f"... dan {len(selected_items) - 3} barang lainnya\n"
                confirm_msg += f"\nTotal nilai yang akan dihapus: Rp {total_nilai:,.0f}\n"
                confirm_msg += f"Semua barang dan data pajaknya akan dihapus dari container."
            
            if not messagebox.askyesno("Konfirmasi Hapus", confirm_msg):
                return
            
            # Remove barang from container with tax cleanup
            success_count = 0
            error_count = 0
            tax_cleaned_count = 0
            
            for item in selected_items:
                print(f"\n{'='*60}")
                print(f"🗑️ Processing removal for: {item['nama']} (ID: {item['id']})")
                print(f"{'='*60}")

                try:
                    # ========================================
                    # 🔍 DEBUG: CEK FORMAT DI DATABASE
                    # ========================================
                    print(f"\n📊 STEP 1: Checking database format...")
                    debug_query = """
                        SELECT 
                            assigned_at,
                            typeof(assigned_at) as type,
                            length(assigned_at) as len,
                            quote(assigned_at) as quoted
                        FROM detail_container 
                        WHERE barang_id = ? AND container_id = ?
                    """
                    debug_result = self.db.execute(debug_query, (item['id'], container_id))
                    
                    if debug_result:
                        print(f"   Records found in DB: {len(debug_result)}")
                        for idx, row in enumerate(debug_result):
                            print(f"\n   Record {idx + 1}:")
                            print(f"   ├─ Value in DB  : '{row[0]}'")
                            print(f"   ├─ Type         : {row[1]}")
                            print(f"   ├─ Length       : {row[2]}")
                            print(f"   ├─ Quoted       : {row[3]}")
                            print(f"   └─ Expected (UI): '{item['assigned_at']}'")
                            print(f"   └─ Match?       : {str(row[0]) == str(item['assigned_at'])}")
                    else:
                        print(f"   ❌ No records found in database!")
                    
                    # ========================================
                    # 🔍 STEP 2: GET TAX_ID
                    # ========================================
                    print(f"\n📊 STEP 2: Getting tax_id...")
                    tax_id = None
                    try:
                        # Try dengan assigned_at exact match
                        tax_query = "SELECT tax_id, assigned_at FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at = ?"
                        tax_result = self.db.execute_one(tax_query, (item['id'], container_id, item['assigned_at']))
                        
                        if tax_result and tax_result[0]:
                            tax_id = tax_result[0]
                            print(f"   ✅ Found tax_id: {tax_id} (exact match)")
                            print(f"   └─ assigned_at in record: '{tax_result[1]}'")
                        else:
                            # Try dengan LIKE pattern (untuk handle microseconds)
                            assigned_at_pattern = str(item['assigned_at'])[:19] + '%'
                            tax_query_like = "SELECT tax_id, assigned_at FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at LIKE ?"
                            tax_result_like = self.db.execute_one(tax_query_like, (item['id'], container_id, assigned_at_pattern))
                            
                            if tax_result_like and tax_result_like[0]:
                                tax_id = tax_result_like[0]
                                print(f"   ✅ Found tax_id: {tax_id} (LIKE pattern match)")
                                print(f"   └─ assigned_at in record: '{tax_result_like[1]}'")
                            else:
                                # Fallback tanpa assigned_at
                                tax_query_fallback = "SELECT tax_id FROM detail_container WHERE barang_id = ? AND container_id = ?"
                                tax_result_fallback = self.db.execute_one(tax_query_fallback, (item['id'], container_id))
                                if tax_result_fallback and tax_result_fallback[0]:
                                    tax_id = tax_result_fallback[0]
                                    print(f"   ⚠️ Found tax_id: {tax_id} (fallback - no assigned_at)")
                                else:
                                    print(f"   ❌ No tax_id found")
                            
                    except Exception as tax_query_error:
                        print(f"   ❌ Error getting tax_id: {tax_query_error}")
                    
                    # ========================================
                    # 🔍 STEP 3: DELETE RECORD
                    # ========================================
                    print(f"\n📊 STEP 3: Attempting delete...")
                    
                    # Try 1: Exact match dengan assigned_at
                    delete_query = "DELETE FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at = ?"
                    delete_params = (item['id'], container_id, item['assigned_at'])
                    
                    print(f"   Query: {delete_query}")
                    print(f"   Params: {delete_params}")
                    
                    check_query = "SELECT COUNT(*) FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at = ?"
                    check_result = self.db.execute(check_query, delete_params)
                    count = check_result[0][0] if check_result else 0
                    
                    print(f"   Records matching (exact): {count}")
                    
                    if count > 0:
                        # Execute delete
                        result = self.db.execute(delete_query, delete_params)
                        print(f"   ✅ Deleted successfully (exact match)")
                        success_count += 1
                    else:
                        # Try 2: LIKE pattern untuk handle microseconds
                        print(f"\n   ⚠️ Trying LIKE pattern...")
                        assigned_at_pattern = str(item['assigned_at'])[:19] + '%'
                        delete_query_like = "DELETE FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at LIKE ?"
                        delete_params_like = (item['id'], container_id, assigned_at_pattern)
                        
                        print(f"   Pattern: '{assigned_at_pattern}'")
                        
                        check_query_like = "SELECT COUNT(*) FROM detail_container WHERE barang_id = ? AND container_id = ? AND assigned_at LIKE ?"
                        check_result_like = self.db.execute(check_query_like, delete_params_like)
                        count_like = check_result_like[0][0] if check_result_like else 0
                        
                        print(f"   Records matching (LIKE): {count_like}")
                        
                        if count_like > 0:
                            result = self.db.execute(delete_query_like, delete_params_like)
                            print(f"   ✅ Deleted successfully (LIKE match)")
                            success_count += 1
                        else:
                            # Try 3: Fallback tanpa assigned_at
                            print(f"\n   ⚠️ Trying fallback (no assigned_at)...")
                            alt_delete_query = "DELETE FROM detail_container WHERE barang_id = ? AND container_id = ?"
                            alt_delete_params = (item['id'], container_id)
                            
                            alt_check_result = self.db.execute("SELECT COUNT(*) FROM detail_container WHERE barang_id = ? AND container_id = ?", alt_delete_params)
                            alt_count = alt_check_result[0][0] if alt_check_result else 0
                            
                            print(f"   Records matching (fallback): {alt_count}")
                            
                            if alt_count > 0:
                                result = self.db.execute(alt_delete_query, alt_delete_params)
                                print(f"   ✅ Deleted successfully (fallback)")
                                success_count += 1
                            else:
                                error_count += 1
                                print(f"   ❌ No records found to delete!")
                                continue
                    
                    # ========================================
                    # 🔍 STEP 4: DELETE TAX RECORD
                    # ========================================
                    if tax_id:
                        print(f"\n📊 STEP 4: Deleting tax record...")
                        try:
                            tax_delete_result = self.db.execute("DELETE FROM barang_tax WHERE tax_id = ?", (tax_id,))
                            if tax_delete_result:
                                tax_cleaned_count += 1
                                print(f"   ✅ Deleted tax record: {tax_id}")
                            else:
                                print(f"   ⚠️ Tax record {tax_id} may not exist")
                        except Exception as tax_delete_error:
                            print(f"   ⚠️ Error deleting tax: {tax_delete_error}")
                    
                    print(f"\n{'='*60}")
                    print(f"✅ Completed removal for: {item['nama']}")
                    print(f"{'='*60}\n")
                    
                except Exception as e:
                    error_count += 1
                    print(f"\n{'='*60}")
                    print(f"❌ FAILED for: {item['nama']}")
                    print(f"{'='*60}")
                    print(f"Error: {e}")
                    import traceback
                    traceback.print_exc()
                    print(f"{'='*60}\n")
            
            # Show result message with tax cleanup info
            result_msg = ""
            if error_count == 0:
                result_msg = f"✅ {success_count} barang berhasil dihapus dari container!\n"
                if tax_cleaned_count > 0:
                    result_msg += f"🧾 {tax_cleaned_count} data pajak terkait berhasil dihapus.\n"
                result_msg += f"\nBarang telah dikembalikan ke daftar barang tersedia."
                messagebox.showinfo("Sukses", result_msg)
            else:
                result_msg = f"✅ Berhasil: {success_count} barang\n" + \
                            f"❌ Gagal: {error_count} barang\n"
                if tax_cleaned_count > 0:
                    result_msg += f"🧾 Tax cleanup: {tax_cleaned_count} record\n"
                result_msg += f"\nPeriksa log untuk detail error."
                messagebox.showwarning("Sebagian Berhasil", result_msg)
            
            # Refresh displays
            self.load_available_barang()
            self.load_container_barang(container_id)
            self.load_tax_summary_tree(container_id)
            self.load_containers()
            self.load_container_combo()
            self.load_customers()
            self.load_pengirim()
            
            if tax_cleaned_count > 0:
                self.refresh_tax_summary(container_id)
                print(f"🔄 Tax summary refreshed after cleaning {tax_cleaned_count} tax records")
            
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
            self.db.rollback()
        
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
            
            # Calculate totals including pricing - PERBAIKAN: kalikan dengan colli
            total_volume = 0
            total_weight = 0
            total_colli = 0
            total_nilai = 0
            
            for b in container_barang:
                try:
                    # Get colli amount first
                    colli_value = safe_get(b, 'colli_amount', 0)
                    colli = int(colli_value) if colli_value not in [None, '', '-'] else 0
                    total_colli += colli
                    
                    # PERBAIKAN: Volume dikalikan dengan colli
                    m3_value = safe_get(b, 'm3_barang', 0)
                    m3_per_unit = float(m3_value) if m3_value not in [None, '', '-'] else 0
                    total_volume += m3_per_unit * colli
                    
                    # PERBAIKAN: Berat dikalikan dengan colli
                    ton_value = safe_get(b, 'ton_barang', 0)
                    ton_per_unit = float(ton_value) if ton_value not in [None, '', '-'] else 0
                    total_weight += ton_per_unit * colli
                    
                    # Calculate total pricing (sudah benar, total_harga sudah hasil kali)
                    total_harga_value = safe_get(b, 'total_harga', 0)
                    total_nilai += float(total_harga_value) if total_harga_value not in [None, '', '-'] else 0
                    
                except (ValueError, TypeError) as ve:
                    print(f"Error calculating totals for barang: {ve}")
                    continue
            
            # Group by customer with pricing - PERBAIKAN: kalikan dengan colli
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
                    
                    # Get colli for this barang
                    colli_value = safe_get(barang, 'colli_amount', 0)
                    colli = int(colli_value) if colli_value not in [None, '', '-'] else 0
                    customer_summary[customer]['colli'] += colli
                    
                    # PERBAIKAN: Volume dikalikan dengan colli
                    try:
                        m3_value = safe_get(barang, 'm3_barang', 0)
                        m3_per_unit = float(m3_value) if m3_value not in [None, '', '-'] else 0
                        customer_summary[customer]['volume'] += m3_per_unit * colli
                    except (ValueError, TypeError):
                        pass
                    
                    # PERBAIKAN: Berat dikalikan dengan colli
                    try:
                        ton_value = safe_get(barang, 'ton_barang', 0)
                        ton_per_unit = float(ton_value) if ton_value not in [None, '', '-'] else 0
                        customer_summary[customer]['weight'] += ton_per_unit * colli
                    except (ValueError, TypeError):
                        pass
                    
                    # Nilai (sudah benar)
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
        """Show container summary in a dialog with pricing information - showing sender and receiver"""
        try:
            # ✅ PERBAIKAN: Ambil data lengkap dengan JOIN ke kapals
            container_id = container.get('container_id') if hasattr(container, 'get') else container['container_id']
            
            # Query lengkap dengan JOIN
            full_container_data = self.db.execute_one("""
                SELECT 
                    c.container_id,
                    c.kapal_id,
                    c.etd,
                    c.party,
                    c.container,
                    c.seal,
                    c.ref_joa,
                    k.feeder,
                    k.destination,
                    k.etd_sub as kapal_etd,
                    k.cls,
                    k.open as open,
                    k.full as full
                FROM containers c
                LEFT JOIN kapals k ON c.kapal_id = k.kapal_id
                WHERE c.container_id = ?
            """, (container_id,))
            
            # Override container data dengan hasil query lengkap
            if full_container_data:
                container = dict(full_container_data)
            
            summary_window = tk.Toplevel(self.window)
            
            # Get container name safely
            container_name = container.get('container', 'N/A') if hasattr(container, 'get') else (container['container'] if 'container' in container else 'N/A')
            
            summary_window.title(f"📊 Summary Container - {container_name}")
            
            # Responsive sizing
            screen_width = summary_window.winfo_screenwidth()
            screen_height = summary_window.winfo_screenheight()
            dialog_width = min(1200, int(screen_width * 0.85))
            dialog_height = min(800, int(screen_height * 0.85))
            
            summary_window.geometry(f"{dialog_width}x{dialog_height}")
            summary_window.configure(bg='#ecf0f1')
            summary_window.transient(self.window)
            summary_window.grab_set()
            
            try:
                icon_image = Image.open("assets/logo.jpg")
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                summary_window.iconphoto(False, icon_photo)
            except Exception as e:
                print(f"Icon tidak ditemukan: {e}")
            
            # Center window with boundary check
            summary_window.update_idletasks()
            parent_x = self.window.winfo_x()
            parent_y = self.window.winfo_y()
            parent_width = self.window.winfo_width()
            parent_height = self.window.winfo_height()
            
            x = parent_x + (parent_width // 2) - (dialog_width // 2)
            y = parent_y + (parent_height // 2) - (dialog_height // 2)
            
            if x + dialog_width > screen_width:
                x = screen_width - dialog_width - 20
            if x < 0:
                x = 20
            if y + dialog_height > screen_height:
                y = screen_height - dialog_height - 50
            if y < 0:
                y = 20
            
            summary_window.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            summary_window.lift()
            summary_window.focus_force()
            
            # Safe getter for all data structures
            def safe_get(obj, key, default='-'):
                try:
                    if obj is None:
                        return default
                    if hasattr(obj, 'get'):
                        return obj.get(key, default) if obj.get(key) is not None else default
                    elif hasattr(obj, '__getitem__'):
                        return obj[key] if obj[key] is not None else default
                    elif hasattr(obj, key):
                        val = getattr(obj, key, default)
                        return val if val is not None else default
                    return default
                except:
                    return default
            
            # Header
            header = tk.Label(summary_window, text=f"📊 SUMMARY CONTAINER: {container_name}",
                            font=('Arial', 16, 'bold'), bg='#e67e22', fg='white', pady=15)
            header.pack(fill='x')
            
            # Create notebook
            summary_notebook = ttk.Notebook(summary_window)
            summary_notebook.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Tab 1: Overview
            overview_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(overview_frame, text='📋 Overview')
            
            # Container info
            info_frame = tk.Frame(overview_frame, bg='#ffffff', relief='solid', bd=1)
            info_frame.pack(fill='x', padx=10, pady=10)
            
            tk.Label(info_frame, text="🚢 INFORMASI CONTAINER", 
                    font=('Arial', 14, 'bold'), bg='#ffffff').pack(pady=10)
            
            # ✅ PERBAIKAN: Ambil dan format semua tanggal
            etd_container = safe_get(container, 'etd')
            etd_kapal = safe_get(container, 'kapal_etd')
            cls_date = safe_get(container, 'cls')
            open_date = safe_get(container, 'open')
            full_date = safe_get(container, 'full')
            
            # Format ke Indonesia
            etd_display = self.format_date_indonesian(etd_container or etd_kapal) if (etd_container or etd_kapal) else '-'
            cls_display = self.format_date_indonesian(cls_date) if cls_date else '-'
            open_display = self.format_date_indonesian(open_date) if open_date else '-'
            full_display = self.format_date_indonesian(full_date) if full_date else '-'
            
            info_lines = [
                f"Container: {safe_get(container, 'container')}",
                f"Feeder: {safe_get(container, 'feeder')}",
                f"Destination: {safe_get(container, 'destination')}",
                f"ETD: {etd_display}",
                f"CLS: {cls_display}",
                f"Open: {open_display}",
                f"Full: {full_display}",
                f"Seal: {safe_get(container, 'seal')}",
                f"Party: {safe_get(container, 'party')}",
                f"Ref JOA: {safe_get(container, 'ref_joa')}"
            ]
            
            tk.Label(info_frame, text="\n".join(info_lines), font=('Arial', 10), 
                    bg='#ffffff', justify='left').pack(padx=20, pady=10)
            
            # Stats
            stats_frame = tk.Frame(overview_frame, bg='#ffffff', relief='solid', bd=1)
            stats_frame.pack(fill='x', padx=10, pady=10)
            
            tk.Label(stats_frame, text="📊 STATISTIK MUATAN & NILAI", 
                    font=('Arial', 14, 'bold'), bg='#ffffff').pack(pady=10)
            
            stats_text = f"""Total Barang: {len(barang_list)} items
    Total Volume: {total_volume:.3f} m³
    Total Berat: {total_weight:.3f} ton
    Total Colli: {total_colli} kemasan
    Total Nilai: Rp {total_nilai:,.0f}"""
            
            tk.Label(stats_frame, text=stats_text, font=('Arial', 12, 'bold'), 
                    bg='#ffffff', justify='left').pack(padx=20, pady=10)
            
            # Tab 2: Per Penerima
            penerima_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(penerima_frame, text='👥 Per Penerima')
            
            tk.Label(penerima_frame, text="👥 RINGKASAN PER PENERIMA", 
                    font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            # Calculate summary by receiver only
            penerima_summary = {}
            
            print("\n=== DEBUG: Processing barang_list ===")
            for idx, barang in enumerate(barang_list):
                try:
                    # Debug: print struktur data barang
                    if idx == 0:
                        print(f"Sample barang keys: {list(barang.keys()) if hasattr(barang, 'keys') else 'Not a dict'}")
                    
                    # Try multiple field names for receiver
                    penerima = (safe_get(barang, 'receiver_name') or 
                            safe_get(barang, 'nama_customer') or 
                            safe_get(barang, 'penerima') or '-')
                    
                    print(f"Barang {idx}: penerima = {penerima}")
                    
                    if penerima not in penerima_summary:
                        penerima_summary[penerima] = {
                            'count': 0, 'volume': 0, 'weight': 0, 'colli': 0, 'nilai': 0
                        }
                    
                    colli = int(safe_get(barang, 'colli_amount', 0) or 0)
                    penerima_summary[penerima]['count'] += 1
                    penerima_summary[penerima]['volume'] += float(safe_get(barang, 'm3_barang', 0) or 0) * colli
                    penerima_summary[penerima]['weight'] += float(safe_get(barang, 'ton_barang', 0) or 0) * colli
                    penerima_summary[penerima]['colli'] += colli
                    penerima_summary[penerima]['nilai'] += float(safe_get(barang, 'total_harga', 0) or 0)
                    
                except Exception as e:
                    print(f"Error processing barang {idx}: {e}")
                    continue
            
            print(f"Penerima summary: {penerima_summary}")
            
            # Penerima tree
            penerima_tree_container = tk.Frame(penerima_frame, bg='#ecf0f1')
            penerima_tree_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            penerima_tree = ttk.Treeview(penerima_tree_container,
                                        columns=('Penerima', 'Jumlah_Barang', 'Volume', 'Berat', 'Total_Colli', 'Total_Nilai'),
                                        show='headings', height=15)

            penerima_tree.heading('Penerima', text='Penerima')
            penerima_tree.heading('Jumlah_Barang', text='Jumlah Barang')
            penerima_tree.heading('Volume', text='Total Volume (m³)')
            penerima_tree.heading('Berat', text='Total Berat (ton)')
            penerima_tree.heading('Total_Colli', text='Total Colli')
            penerima_tree.heading('Total_Nilai', text='Total Nilai (Rp)')
            
            penerima_tree.column('Penerima', width=200)
            penerima_tree.column('Jumlah_Barang', width=120)
            penerima_tree.column('Volume', width=100)
            penerima_tree.column('Berat', width=100)
            penerima_tree.column('Total_Colli', width=100)
            penerima_tree.column('Total_Nilai', width=150)
            
            for penerima, data in penerima_summary.items():
                penerima_tree.insert('', tk.END, values=(
                    penerima, data['count'], f"{data['volume']:.3f}",
                    f"{data['weight']:.3f}", data['colli'], f"{data['nilai']:,.0f}"
                ))
            
            penerima_v_scroll = ttk.Scrollbar(penerima_tree_container, orient='vertical', command=penerima_tree.yview)
            penerima_tree.configure(yscrollcommand=penerima_v_scroll.set)
            penerima_tree.pack(side='left', fill='both', expand=True)
            penerima_v_scroll.pack(side='right', fill='y')
            
            # Tab 3: Detail Barang
            items_frame = tk.Frame(summary_notebook, bg='#ecf0f1')
            summary_notebook.add(items_frame, text='📦 Detail Barang')
            
            tk.Label(items_frame, text="📦 DETAIL SEMUA BARANG DENGAN HARGA", 
                    font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
            
            items_tree_container = tk.Frame(items_frame, bg='#ecf0f1')
            items_tree_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            items_detail_tree = ttk.Treeview(items_tree_container,
                                        columns=('Pengirim', 'Penerima', 'Nama', 'Dimensi', 'Volume', 'Berat', 'Colli', 'Harga_Unit', 'Total_Harga', 'Tanggal'),
                                        show='headings', height=15)

            headers = ['Pengirim', 'Penerima', 'Nama Barang', 'P×L×T (cm)', 'Total Volume (m³)', 'Total Berat (ton)', 'Colli', 'Harga/Unit', 'Total Harga', 'Tanggal']
            widths = [100, 100, 150, 100, 80, 80, 60, 100, 100, 90]
            
            for col, header, width in zip(items_detail_tree['columns'], headers, widths):
                items_detail_tree.heading(col, text=header)
                items_detail_tree.column(col, width=width)
            
            for barang in barang_list:
                try:
                    # Get pengirim with multiple fallbacks
                    pengirim = (safe_get(barang, 'sender_name') or 
                            safe_get(barang, 'pengirim_nama') or 
                            safe_get(barang, 'pengirim') or '-')
                    
                    # Get penerima with multiple fallbacks
                    penerima = (safe_get(barang, 'receiver_name') or 
                            safe_get(barang, 'penerima_nama') or
                            safe_get(barang, 'nama_customer') or 
                            safe_get(barang, 'penerima') or '-')
                    
                    panjang = safe_get(barang, 'panjang_barang', '-')
                    lebar = safe_get(barang, 'lebar_barang', '-')
                    tinggi = safe_get(barang, 'tinggi_barang', '-')
                    dimensi = f"{panjang}×{lebar}×{tinggi}"
                    
                    # ✅ PERBAIKAN: Format tanggal ke Indonesia
                    tanggal_raw = safe_get(barang, 'tanggal', '-')
                    if tanggal_raw and tanggal_raw != '-':
                        tanggal = self.format_date_indonesian(str(tanggal_raw))
                    else:
                        tanggal = '-'
                    
                    harga_unit = safe_get(barang, 'harga_per_unit', 0)
                    total_harga = safe_get(barang, 'total_harga', 0)

                    harga_unit_display = f"{float(harga_unit):,.0f}" if str(harga_unit).replace('.', '').replace('-', '').isdigit() and harga_unit != '-' else str(harga_unit)
                    total_harga_display = f"{float(total_harga):,.0f}" if str(total_harga).replace('.', '').replace('-', '').isdigit() and total_harga != '-' else str(total_harga)

                    # Calculate total volume and weight (m3_barang * colli, ton_barang * colli)
                    colli = int(safe_get(barang, 'colli_amount', 0))
                    m3_per_unit = float(safe_get(barang, 'm3_barang', 0)) if safe_get(barang, 'm3_barang', '-') != '-' else 0
                    ton_per_unit = float(safe_get(barang, 'ton_barang', 0)) if safe_get(barang, 'ton_barang', '-') != '-' else 0

                    total_volume = m3_per_unit * colli
                    total_weight = ton_per_unit * colli

                    items_detail_tree.insert('', tk.END, values=(
                        pengirim, penerima, safe_get(barang, 'nama_barang', '-'),
                        dimensi, f"{total_volume:.4f}",
                        f"{total_weight:.4f}",
                        colli,
                        harga_unit_display, total_harga_display, tanggal
                    ))
                except Exception as item_error:
                    print(f"Error adding item: {item_error}")
                    continue
            
            items_v_scroll = ttk.Scrollbar(items_tree_container, orient='vertical', command=items_detail_tree.yview)
            items_h_scroll = ttk.Scrollbar(items_tree_container, orient='horizontal', command=items_detail_tree.xview)
            items_detail_tree.configure(yscrollcommand=items_v_scroll.set, xscrollcommand=items_h_scroll.set)
            
            items_detail_tree.grid(row=0, column=0, sticky='nsew')
            items_v_scroll.grid(row=0, column=1, sticky='ns')
            items_h_scroll.grid(row=1, column=0, sticky='ew')
            
            items_tree_container.grid_rowconfigure(0, weight=1)
            items_tree_container.grid_columnconfigure(0, weight=1)
            
            # Close button
            tk.Button(summary_window, text="✅ Tutup", font=('Arial', 12, 'bold'),
                    bg='#27ae60', fg='white', padx=30, pady=10,
                    command=summary_window.destroy).pack(pady=10)
            
        except Exception as dialog_error:
            print(f"Error creating summary dialog: {dialog_error}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal membuat dialog summary: {str(dialog_error)}")
            
        
        
    def view_selected_container_summary(self):
        """View detailed summary of selected container from tree including pricing"""
        # Get selected item from container tree
        selected_items = self.container_tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Peringatan", "Pilih container dari tabel terlebih dahulu!")
            return
        
        try:
            # Get the first selected item
            selected_item = selected_items[0]
            
            # Get container data from tree item
            item_values = self.container_tree.item(selected_item)['values']
            
            if not item_values:
                messagebox.showerror("Error", "Data container tidak valid!")
                return
            
            # Extract container ID (assuming it's in the first column)
            container_id = int(item_values[0])  # Adjust index if container ID is in different column
            
            print(f"Selected container ID from tree: {container_id}")
            
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
            
            # Calculate totals including pricing - PERBAIKAN: kalikan dengan colli
            total_volume = 0
            total_weight = 0
            total_colli = 0
            total_nilai = 0
            
            for b in container_barang:
                try:
                    # Get colli amount first
                    colli_value = safe_get(b, 'colli_amount', 0)
                    colli = int(colli_value) if colli_value not in [None, '', '-'] else 0
                    total_colli += colli
                    
                    # PERBAIKAN: Volume dikalikan dengan colli
                    m3_value = safe_get(b, 'm3_barang', 0)
                    m3_per_unit = float(m3_value) if m3_value not in [None, '', '-'] else 0
                    total_volume += m3_per_unit * colli
                    
                    # PERBAIKAN: Berat dikalikan dengan colli
                    ton_value = safe_get(b, 'ton_barang', 0)
                    ton_per_unit = float(ton_value) if ton_value not in [None, '', '-'] else 0
                    total_weight += ton_per_unit * colli
                    
                    # Calculate total pricing (sudah benar)
                    total_harga_value = safe_get(b, 'total_harga', 0)
                    total_nilai += float(total_harga_value) if total_harga_value not in [None, '', '-'] else 0
                    
                except (ValueError, TypeError) as ve:
                    print(f"Error calculating totals for barang: {ve}")
                    continue
            
            # Group by customer with pricing - PERBAIKAN: kalikan dengan colli
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
                    
                    # Get colli for this barang
                    colli_value = safe_get(barang, 'colli_amount', 0)
                    colli = int(colli_value) if colli_value not in [None, '', '-'] else 0
                    customer_summary[customer]['colli'] += colli
                    
                    # PERBAIKAN: Volume dikalikan dengan colli
                    try:
                        m3_value = safe_get(barang, 'm3_barang', 0)
                        m3_per_unit = float(m3_value) if m3_value not in [None, '', '-'] else 0
                        customer_summary[customer]['volume'] += m3_per_unit * colli
                    except (ValueError, TypeError):
                        pass
                    
                    # PERBAIKAN: Berat dikalikan dengan colli
                    try:
                        ton_value = safe_get(barang, 'ton_barang', 0)
                        ton_per_unit = float(ton_value) if ton_value not in [None, '', '-'] else 0
                        customer_summary[customer]['weight'] += ton_per_unit * colli
                    except (ValueError, TypeError):
                        pass
                    
                    # Nilai (sudah benar)
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
            print(f"Error in view_selected_container_summary: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal membuat summary container: {str(e)}")
        
        
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
    
    def validate_kapal_etd(self, kapal_id, etd):
        """
        Validasi STRICT apakah kombinasi kapal_id + etd ada di tabel kapals
        
        Args:
            kapal_id (int): ID kapal
            etd (str): ETD date dalam format YYYY-MM-DD
        
        Returns:
            bool: True jika valid, False jika tidak ditemukan
        """
        try:
            # Query untuk cek apakah kapal dengan ETD ini ada
            result = self.db.execute_one("""
                SELECT kapal_id, feeder, etd_sub 
                FROM kapals 
                WHERE kapal_id = ? AND etd_sub = ?
            """, (kapal_id, etd))
            
            if result:
                print(f"[VALID ✓] Kapal ID {kapal_id} dengan ETD {etd} ditemukan: {result[1]}")
                return True
            else:
                print(f"[INVALID ✗] Kapal ID {kapal_id} dengan ETD {etd} TIDAK ditemukan!")
                return False
                
        except Exception as e:
            print(f"[ERROR] Validasi kapal ETD error: {e}")
            return False
    
    def add_container(self):
        """Add new container - kapal_id didapat dari kombinasi feeder + ETD"""
        try:
            # ============================================
            # STEP 1: Get Input Values
            # ============================================
            feeder_name = self.kapal_var.get().strip()
            etd_indonesian = self.etd_entry.get().strip()
            party = self.party_entry.get().strip()
            container = self.container_entry.get().strip()
            seal = self.seal_entry.get().strip()
            ref_joa = self.ref_joa_entry.get().strip()
            
            # ============================================
            # STEP 2: Validasi Input
            # ============================================
            if not feeder_name:
                messagebox.showwarning("Validasi", "Pilih atau ketik nama kapal terlebih dahulu!")
                return
            
            if not container:
                messagebox.showwarning("Validasi", "Masukkan nomor container!")
                return
            
            if not etd_indonesian:
                messagebox.showwarning("Validasi", "Masukkan ETD!")
                return
            
            # ============================================
            # STEP 3: Validasi Format Tanggal Indonesia
            # ============================================
            if not self.validate_indonesian_date(etd_indonesian):
                messagebox.showerror(
                    "Format Tanggal Salah",
                    f"Format ETD tidak valid!\n\n"
                    f"Input Anda: {etd_indonesian}\n\n"
                    f"Gunakan format: DD/MM/YYYY\n"
                    f"Contoh: 31/10/2025"
                )
                return
            
            # ============================================
            # STEP 4: Convert ke Format Database
            # ============================================
            etd_db = self.parse_indonesian_date(etd_indonesian)
            
            print(f"\n{'='*60}")
            print(f"[DEBUG] ADD CONTAINER - Input Values:")
            print(f"{'='*60}")
            print(f"Feeder Name     : '{feeder_name}'")
            print(f"ETD (Indonesia) : {etd_indonesian}")
            print(f"ETD (Database)  : {etd_db}")
            print(f"Container       : {container}")
            print(f"Party           : {party}")
            print(f"Seal            : {seal}")
            print(f"Ref JOA         : {ref_joa}")
            print(f"{'='*60}\n")
            
            # ============================================
            # STEP 5: ✅ CARI KAPAL_ID berdasarkan FEEDER + ETD
            # ============================================
            kapal_result = self.db.execute_one("""
                SELECT kapal_id, feeder, etd_sub, destination
                FROM kapals 
                WHERE feeder = ? AND etd_sub = ?
            """, (feeder_name, etd_db))
            
            if not kapal_result:
                # ✅ Jika tidak ditemukan, cari semua ETD yang tersedia untuk feeder ini
                available_etds = self.db.execute("""
                    SELECT DISTINCT etd_sub FROM kapals 
                    WHERE feeder = ?
                    ORDER BY etd_sub DESC
                """, (feeder_name,))
                
                if available_etds:
                    etd_list = "\n".join([f"• {self.format_date_indonesian(e[0])}" for e in available_etds])
                    messagebox.showerror(
                        "❌ Kapal dengan ETD Tidak Ditemukan",
                        f"Kapal '{feeder_name}' dengan ETD '{etd_indonesian}' tidak ditemukan!\n\n"
                        f"ETD yang tersedia untuk kapal ini:\n{etd_list}\n\n"
                        f"Silakan:\n"
                        f"1. Pilih ETD yang tersedia di atas, atau\n"
                        f"2. Tambahkan data kapal dengan ETD '{etd_indonesian}' di menu Kelola Kapal"
                    )
                else:
                    messagebox.showerror(
                        "❌ Kapal Tidak Ditemukan",
                        f"Kapal '{feeder_name}' tidak ditemukan di database!\n\n"
                        f"Silakan tambahkan kapal ini terlebih dahulu di menu Kelola Kapal."
                    )
                return
            
            # ✅ Kapal ditemukan!
            kapal_id = kapal_result[0]
            kapal_feeder = kapal_result[1]
            kapal_etd = kapal_result[2]
            kapal_destination = kapal_result[3] if len(kapal_result) > 3 else '-'
            
            print(f"\n{'='*60}")
            print(f"[DEBUG] ✅ KAPAL FOUND:")
            print(f"{'='*60}")
            print(f"Kapal ID     : {kapal_id}")
            print(f"Feeder       : {kapal_feeder}")
            print(f"ETD (DB)     : {kapal_etd}")
            print(f"Destination  : {kapal_destination}")
            print(f"{'='*60}\n")
            
            # ============================================
            # STEP 6: INSERT ke Database
            # ============================================
            self.db.execute_insert(
                "INSERT INTO containers (kapal_id, etd, party, container, seal, ref_joa) VALUES (?, ?, ?, ?, ?, ?)", 
                (kapal_id, etd_db, party, container, seal, ref_joa)
            )
            
            # ============================================
            # STEP 7: Success & Refresh
            # ============================================
            messagebox.showinfo(
                "✅ Sukses", 
                f"Container berhasil ditambahkan!\n\n"
                f"Container   : {container}\n"
                f"Kapal       : {kapal_feeder}\n"
                f"ETD         : {etd_indonesian}\n"
                f"Destination : {kapal_destination}\n"
                f"Kapal ID    : {kapal_id}"
            )

            # Refresh
            self.clear_form()
            self.load_containers()
            self.load_container_combo()
            
            if self.refresh_callback:
                self.refresh_callback()
                
            print(f"✅ Container '{container}' berhasil ditambahkan dengan kapal_id={kapal_id}")

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"[ERROR] add_container failed:")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            messagebox.showerror("Database Error", f"Gagal menambahkan container:\n{str(e)}")
         
     
    def edit_container(self):
        """Edit selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih container yang akan diedit!")
            return
        
        item = self.container_tree.item(selection[0])
        container_id = item['values'][0]
        
        # Query dengan etd
        container = self.db.execute_one("""
            SELECT 
                c.container_id,
                c.kapal_id,
                k.feeder as kapal_feeder,
                c.etd,
                c.party,
                c.container,
                c.seal,
                c.ref_joa
            FROM containers c
            LEFT JOIN kapals k ON c.kapal_id = k.kapal_id
            WHERE c.container_id = ?
        """, (container_id,))
        
        if not container:
            messagebox.showerror("Error", "Container tidak ditemukan!")
            return
        
        # Open edit dialog
        self.show_edit_container_dialog(container_id, container)


    def show_edit_container_dialog(self, container_id, container):
        """Show container edit dialog with STRICT ETD validation"""
        try:
            edit_window = tk.Toplevel(self.window)
            edit_window.title(f"✏️ Edit Container - ID: {container_id}")
            edit_window.geometry("650x550")
            edit_window.configure(bg='#ecf0f1')
            edit_window.transient(self.window)
            edit_window.grab_set()

            try:
                icon_image = Image.open("assets/logo.jpg")
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                edit_window.iconphoto(False, icon_photo)
            except Exception as e:
                print(f"Icon tidak ditemukan: {e}")

            # Center dialog
            edit_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - 325
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - 275
            edit_window.geometry(f"650x550+{x}+{y}")

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

            # 1. Kapal (Dropdown) - HANYA NAMA FEEDER
            row = tk.Frame(form_frame, bg='#ffffff')
            row.pack(fill='x', pady=12, padx=20)
            
            tk.Label(row, text="Kapal:", font=('Arial', 11, 'bold'), 
                    bg='#ffffff', width=15, anchor='w').pack(side='left')
            
            kapal_var = tk.StringVar()
            kapal_combo = ttk.Combobox(row, textvariable=kapal_var, 
                                    font=('Arial', 11), width=35, state='normal')  # ✅ state='normal' untuk allow typing
            kapal_combo.pack(side='left', padx=(10, 0))
            
            # ✅ Load HANYA NAMA FEEDER (bukan kapal_id - feeder)
            kapals = self.db.execute("SELECT DISTINCT feeder FROM kapals ORDER BY feeder")
            kapal_options = [k[0] for k in kapals]
            kapal_combo['values'] = kapal_options
            
            # ✅ Set current value - HANYA NAMA FEEDER
            if container[2]:  # container[2] = kapal_feeder
                kapal_combo.set(container[2])

            # 2. ETD
            row = tk.Frame(form_frame, bg='#ffffff')
            row.pack(fill='x', pady=12, padx=20)
            
            tk.Label(row, text="ETD:", font=('Arial', 11, 'bold'), 
                    bg='#ffffff', width=15, anchor='w').pack(side='left')
            
            etd_entry = DateEntry(
                row,
                font=('Arial', 11),
                width=33,
                background='#e67e22',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/MM/yyyy'
            )
            etd_entry.pack(side='left', padx=(10, 0))
            
            # Set current date value
            if container[3]:  # etd
                try:
                    date_obj = datetime.strptime(str(container[3]), '%Y-%m-%d').date()
                    etd_entry.set_date(date_obj)
                except:
                    pass

            # 3. Party
            row = tk.Frame(form_frame, bg='#ffffff')
            row.pack(fill='x', pady=12, padx=20)
            
            tk.Label(row, text="Party:", font=('Arial', 11, 'bold'),
                    bg='#ffffff', width=15, anchor='w').pack(side='left')

            party_options = ["20'", "21'", "40'HC"]
            party_entry = ttk.Combobox(row, values=party_options, state='readonly', font=('Arial', 11), width=32)
            party_entry.pack(side='left', padx=(10, 0))
            if safe_get(container[4]) in party_options:
                party_entry.set(safe_get(container[4]))
            else:
                party_entry.set('')

            # 4. Container
            row = tk.Frame(form_frame, bg='#ffffff')
            row.pack(fill='x', pady=12, padx=20)
            
            tk.Label(row, text="Container:", font=('Arial', 11, 'bold'), 
                    bg='#ffffff', width=15, anchor='w').pack(side='left')
            
            container_entry = tk.Entry(row, font=('Arial', 11), width=35)
            container_entry.pack(side='left', padx=(10, 0))
            container_entry.insert(0, safe_get(container[5]))

            # 5. Seal
            row = tk.Frame(form_frame, bg='#ffffff')
            row.pack(fill='x', pady=12, padx=20)
            
            tk.Label(row, text="Seal:", font=('Arial', 11, 'bold'), 
                    bg='#ffffff', width=15, anchor='w').pack(side='left')
            
            seal_entry = tk.Entry(row, font=('Arial', 11), width=35)
            seal_entry.pack(side='left', padx=(10, 0))
            seal_entry.insert(0, safe_get(container[6]))

            # 6. Ref JOA
            row = tk.Frame(form_frame, bg='#ffffff')
            row.pack(fill='x', pady=12, padx=20)
            
            tk.Label(row, text="Ref JOA:", font=('Arial', 11, 'bold'), 
                    bg='#ffffff', width=15, anchor='w').pack(side='left')
            
            ref_joa_entry = tk.Entry(row, font=('Arial', 11), width=35)
            ref_joa_entry.pack(side='left', padx=(10, 0))
            ref_joa_entry.insert(0, safe_get(container[7]))

            # ✅ Save function with FEEDER + ETD matching
            def save_container():
                try:
                    # ============================================
                    # STEP 1: Get Input Values
                    # ============================================
                    feeder_name = kapal_var.get().strip()
                    etd_indonesian = etd_entry.get().strip()
                    
                    container_value = container_entry.get().strip()
                    party_value = party_entry.get().strip()
                    seal_value = seal_entry.get().strip()
                    ref_joa_value = ref_joa_entry.get().strip()
                    
                    # ============================================
                    # STEP 2: Validasi Input
                    # ============================================
                    if not feeder_name:
                        messagebox.showwarning("Validasi", "Pilih kapal!")
                        return
                    
                    if not container_value:
                        messagebox.showwarning("Validasi", "Container tidak boleh kosong!")
                        return
                    
                    if not etd_indonesian:
                        messagebox.showwarning("Validasi", "ETD tidak boleh kosong!")
                        return
                    
                    # ============================================
                    # STEP 3: Validasi Format Tanggal
                    # ============================================
                    if not self.validate_indonesian_date(etd_indonesian):
                        messagebox.showerror(
                            "Format Tanggal Salah",
                            f"Format ETD tidak valid!\n\n"
                            f"Input Anda: {etd_indonesian}\n\n"
                            f"Gunakan format: DD/MM/YYYY"
                        )
                        return
                    
                    # ============================================
                    # STEP 4: Convert ke Database Format
                    # ============================================
                    etd_db = self.parse_indonesian_date(etd_indonesian)
                    
                    print(f"\n{'='*60}")
                    print(f"[DEBUG] EDIT CONTAINER - Save Attempt:")
                    print(f"{'='*60}")
                    print(f"Container ID    : {container_id}")
                    print(f"Feeder Name     : '{feeder_name}'")
                    print(f"ETD (Indonesia) : {etd_indonesian}")
                    print(f"ETD (Database)  : {etd_db}")
                    print(f"{'='*60}\n")
                    
                    # ============================================
                    # STEP 5: ✅ CARI KAPAL_ID berdasarkan FEEDER + ETD
                    # ============================================
                    kapal_result = self.db.execute_one("""
                        SELECT kapal_id, feeder, etd_sub, destination
                        FROM kapals 
                        WHERE feeder = ? AND etd_sub = ?
                    """, (feeder_name, etd_db))
                    
                    if not kapal_result:
                        # ✅ Jika tidak ditemukan, tampilkan ETD yang tersedia
                        available_etds = self.db.execute("""
                            SELECT DISTINCT etd_sub FROM kapals 
                            WHERE feeder = ?
                            ORDER BY etd_sub DESC
                        """, (feeder_name,))
                        
                        if available_etds:
                            etd_list = "\n".join([f"• {self.format_date_indonesian(e[0])}" for e in available_etds])
                            messagebox.showerror(
                                "❌ Error - Kapal dengan ETD Tidak Ditemukan",
                                f"Kapal '{feeder_name}' dengan ETD '{etd_indonesian}' tidak ditemukan di database!\n\n"
                                f"Kemungkinan penyebab:\n"
                                f"• ETD yang dipilih salah\n"
                                f"• Data kapal dengan ETD ini belum diinput\n"
                                f"• ETD di data kapal berbeda\n\n"
                                f"ETD yang tersedia untuk kapal ini:\n{etd_list}\n\n"
                                f"Silakan:\n"
                                f"1. Cek kembali ETD yang benar\n"
                                f"2. Atau tambahkan data kapal dengan ETD tersebut"
                            )
                        else:
                            messagebox.showerror(
                                "❌ Error - Kapal Tidak Ditemukan",
                                f"Kapal '{feeder_name}' tidak ditemukan di database!\n\n"
                                f"Silakan tambahkan kapal ini di menu Kelola Kapal."
                            )
                        return  # ✅ STOP - tidak bisa update
                    
                    # ✅ Kapal ditemukan!
                    kapal_id = kapal_result[0]
                    
                    print(f"\n{'='*60}")
                    print(f"[DEBUG] ✅ KAPAL FOUND:")
                    print(f"{'='*60}")
                    print(f"Kapal ID     : {kapal_id}")
                    print(f"Feeder       : {kapal_result[1]}")
                    print(f"ETD (DB)     : {kapal_result[2]}")
                    print(f"Destination  : {kapal_result[3]}")
                    print(f"{'='*60}\n")
                    
                    # ============================================
                    # STEP 6: Konfirmasi Update
                    # ============================================
                    if not messagebox.askyesno("Konfirmasi Update", 
                            f"Simpan perubahan untuk container ID {container_id}?"):
                        return

                    # ============================================
                    # STEP 7: UPDATE Database
                    # ============================================
                    self.db.execute("""
                        UPDATE containers SET 
                        kapal_id = ?, etd = ?, party = ?, container = ?, seal = ?, ref_joa = ?, 
                        updated_at = CURRENT_TIMESTAMP
                        WHERE container_id = ?
                    """, (
                        kapal_id,
                        etd_db,
                        party_value,
                        container_value,
                        seal_value,
                        ref_joa_value,
                        container_id
                    ))

                    messagebox.showinfo("Sukses", "✅ Container berhasil diupdate!")
                    
                    # Refresh
                    self.load_containers()
                    self.load_container_combo()
                    
                    if self.refresh_callback:
                        self.refresh_callback()
                        
                    edit_window.destroy()

                except Exception as e:
                    print(f"\n{'='*60}")
                    print(f"[ERROR] save_container failed:")
                    print(f"{'='*60}")
                    import traceback
                    traceback.print_exc()
                    print(f"{'='*60}\n")
                    messagebox.showerror("Error", f"Gagal menyimpan perubahan:\n{str(e)}")

            # Buttons
            btn_frame = tk.Frame(edit_window, bg='#ecf0f1')
            btn_frame.pack(fill='x', pady=15, padx=20)

            save_btn = tk.Button(btn_frame, text="💾 Simpan Perubahan", bg='#27ae60', fg='white',
                    font=('Arial', 12, 'bold'), padx=20, pady=10,
                    command=save_container)
            self.make_button_keyboard_accessible(save_btn)
            save_btn.pack(side='left', padx=(0,10))

            close_btn = tk.Button(btn_frame, text="❌ Tutup", bg='#e74c3c', fg='white',
                    font=('Arial', 12, 'bold'), padx=20, pady=10,
                    command=edit_window.destroy)
            self.make_button_keyboard_accessible(close_btn)
            close_btn.pack(side='right')

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"[ERROR] show_edit_container_dialog failed:")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            messagebox.showerror("Error", f"Gagal membuat dialog edit:\n{str(e)}")
        
        
    def is_valid_date_format(self, date_string):
        """Validate date format YYYY-MM-DD"""
        if not date_string:
            return True  # Empty is valid
        
        try:       
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
        container_name = item['values'][4]  # Container column
        
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
            self.load_pengirim()   # Refresh pengirim
            
            if self.refresh_callback:
                self.refresh_callback()
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus container: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.container_entry.delete(0, tk.END)
        self.party_entry.set('')
        self.seal_entry.delete(0, tk.END)
        self.ref_joa_entry.delete(0, tk.END)
        

        today_indonesian = datetime.now().strftime('%d/%m/%Y')
        self.etd_entry.set_date(today_indonesian)
        
        if hasattr(self, 'editing_container_id'):
            delattr(self, 'editing_container_id')
    
    def load_containers(self):
        """Load containers into PaginatedTreeView with Indonesian date format"""
        try:
            # SELECT dengan etd
            containers = self.db.execute("""
                SELECT 
                    c.container_id,
                    c.kapal_id,
                    k.feeder as kapal_feeder,
                    c.etd,
                    c.party,
                    c.container,
                    c.seal,
                    c.ref_joa,
                    c.created_at,
                    c.updated_at
                FROM containers c
                LEFT JOIN kapals k ON c.kapal_id = k.kapal_id
                ORDER BY c.container_id DESC
            """)
            
            # Format data untuk PaginatedTreeView
            formatted_data = []
            
            for container in containers:
                # Count barang in this container
                container_barang = self.db.get_barang_in_container(container[0])
                item_count = len(container_barang)
                
                # ✅ CONVERT ETD TO INDONESIAN FORMAT
                etd_indonesian = self.format_date_indonesian(container[3]) if container[3] else '-'
                
                formatted_data.append({
                    'iid': str(container[0]),
                    'values': (
                        container[0],  # container_id
                        container[2] if container[2] else '-',  # kapal_feeder
                        etd_indonesian,  # ✅ ETD in DD/MM/YYYY format
                        container[4] if container[4] else '-',  # party
                        container[5] if container[5] else '-',  # container
                        container[6] if container[6] else '-',  # seal
                        container[7] if container[7] else '-',  # ref_joa
                        f"{item_count} items"
                    )
                })
            
            # Set data ke PaginatedTreeView
            self.container_tree.set_data(formatted_data)
            
            print(f"Loaded {len(formatted_data)} containers with Indonesian date format")
            
        except Exception as e:
            print(f"Error loading containers: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal memuat daftar container: {str(e)}")
            
        
    
    # Tambahkan fungsi helper di awal class ContainerWindow (setelah __init__)

    def format_date_indonesian(self, date_string):
        """Convert date from YYYY-MM-DD to DD/MM/YYYY (Indonesian format)"""
        try:
            if not date_string or date_string in ['-', '', 'None', None]:
                return '-'
            
            # Handle different date formats
            date_str = str(date_string)
            
            # If already in DD/MM/YYYY format, return as is
            if '/' in date_str and len(date_str.split('/')[0]) <= 2:
                return date_str
            
            # Convert from YYYY-MM-DD to DD/MM/YYYY
            if '-' in date_str:
                parts = date_str.split(' ')[0].split('-')  # Remove time if exists
                if len(parts) == 3 and len(parts[0]) == 4:
                    return f"{parts[2]}/{parts[1]}/{parts[0]}"
            
            return date_str
            
        except Exception as e:
            print(f"Error formatting date: {e}")
            return str(date_string) if date_string else '-'

    def parse_indonesian_date(self, date_string):
        """Convert DD/MM/YYYY back to YYYY-MM-DD for database"""
        try:
            if not date_string or date_string in ['-', '', 'None']:
                return None
            
            # If already in YYYY-MM-DD format
            if '-' in date_string and len(date_string.split('-')[0]) == 4:
                return date_string
            
            # Convert from DD/MM/YYYY to YYYY-MM-DD
            if '/' in date_string:
                parts = date_string.split('/')
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[1]}-{parts[0]}"
            
            return date_string
            
        except Exception as e:
            print(f"Error parsing Indonesian date: {e}")
            return date_string
        
        
        
    def validate_indonesian_date(self, date_string):
        """Validate Indonesian date format DD/MM/YYYY"""
        try:
            if not date_string or date_string.strip() in ['-', '', 'None']:
                return False
            
            # Check basic format
            if '/' not in date_string:
                return False
            
            parts = date_string.strip().split('/')
            if len(parts) != 3:
                return False
            
            day, month, year = parts
            
            # Check if all parts are numbers
            if not (day.isdigit() and month.isdigit() and year.isdigit()):
                return False
            
            # Check ranges
            day_int = int(day)
            month_int = int(month)
            year_int = int(year)
            
            if not (1 <= day_int <= 31):
                return False
            if not (1 <= month_int <= 12):
                return False
            if not (1900 <= year_int <= 2100):
                return False
            datetime(year_int, month_int, day_int)
            
            return True
            
        except (ValueError, Exception) as e:
            print(f"Date validation error: {e}")
            return False
        
        
    def load_container_barang(self, container_id):
        """Load barang in specific container with pricing using PaginatedTreeView"""
        try:
            # Validasi container_id
            if container_id is None:
                print("[WARNING] container_id is None, clearing tree")
                self.container_barang_tree.set_data([])
                return
            
            # Get data dari database
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            
            if not container_barang:
                print(f"[INFO] No barang found for container {container_id}")
                self.container_barang_tree.set_data([])
                return
            
            formatted_data = []
            
            for barang in container_barang:
                try:
                    # Safe getter function
                    def safe_get(row, key, default='-'):
                        try:
                            value = row[key] if row[key] is not None else default
                            return value
                        except (KeyError, IndexError, TypeError):
                            return default
                    
                    # Extract data dengan safe_get
                    barang_id = safe_get(barang, 'barang_id', '')
                    
                    # Pengirim
                    pengirim = (safe_get(barang, 'sender_name') or 
                            safe_get(barang, 'pengirim_nama') or 
                            safe_get(barang, 'pengirim') or '-')
                    
                    # Penerima  
                    penerima = (safe_get(barang, 'receiver_name') or
                            safe_get(barang, 'penerima_nama') or
                            safe_get(barang, 'nama_customer') or
                            safe_get(barang, 'penerima') or '-')
                    
                    # Nama barang
                    nama_barang = safe_get(barang, 'nama_barang', '-')
                    
                    # Satuan dan Door Type
                    satuan = safe_get(barang, 'satuan', 'manual')
                    door_type = safe_get(barang, 'door_type', '-')
                    
                    # Dimensi
                    try:
                        panjang = safe_get(barang, 'panjang_barang', '-')
                        lebar = safe_get(barang, 'lebar_barang', '-')
                        tinggi = safe_get(barang, 'tinggi_barang', '-')
                        dimensi = f"{panjang}×{lebar}×{tinggi}"
                    except:
                        dimensi = '-'
                    
                    # Volume (m³)
                    try:
                        m3_value = safe_get(barang, 'm3_barang', 0)
                        m3_barang = f"{float(m3_value):.4f}" if m3_value not in [None, '', '-'] else '0.0000'
                    except (ValueError, TypeError):
                        m3_barang = '0.0000'
                    
                    # Berat (ton)
                    try:
                        ton_value = safe_get(barang, 'ton_barang', 0)
                        ton_barang = format_ton(ton_value) if ton_value not in [None, '', '-'] else '0'
                    except (ValueError, TypeError):
                        ton_barang = '0'
                    
                    # Colli
                    try:
                        colli_value = safe_get(barang, 'colli_amount', 0)
                        colli_amount = int(colli_value) if colli_value not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        colli_amount = 0
                    
                    # Harga per unit
                    try:
                        harga_value = safe_get(barang, 'harga_per_unit', 0)
                        if harga_value in [None, '', '-']:
                            harga_display = '0'
                        else:
                            harga_float = float(str(harga_value).replace(',', ''))
                            harga_display = f"{harga_float:,.0f}"
                    except (ValueError, TypeError):
                        harga_display = '0'
                    
                    # Total harga
                    try:
                        total_value = safe_get(barang, 'total_harga', 0)
                        if total_value in [None, '', '-']:
                            total_display = 'Rp 0'
                        else:
                            total_float = float(str(total_value).replace(',', ''))
                            total_display = f"Rp {total_float:,.0f}"
                    except (ValueError, TypeError):
                        total_display = 'Rp 0'
                    
                    # Assigned at (untuk unique ID)
                    assigned_at = safe_get(barang, 'assigned_at', '')
                    
                    
                    
                    # Create unique iid
                    unique_iid = f"{barang_id}_{assigned_at}"
                    
                    # Append to formatted data
                    formatted_data.append({
                        'iid': unique_iid,
                        'values': (
                            barang_id,           # Barang_ID
                            pengirim,            # Pengirim
                            penerima,            # Penerima
                            nama_barang,         # Nama Barang
                            satuan,              # Satuan
                            door_type,           # Door Type
                            dimensi,             # Dimensi (P×L×T)
                            m3_barang,           # Volume (m³)
                            ton_barang,          # Berat (ton)
                            colli_amount,        # Colli
                            harga_display,       # Harga/Unit
                            total_display,       # Total Harga
                            assigned_at      # ✅ Tanggal (DD/MM/YYYY)
                        )
                    })
                    
                except Exception as row_error:
                    print(f"[ERROR] Processing barang row: {row_error}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Set data ke PaginatedTreeView
            self.container_barang_tree.set_data(formatted_data)
            print(f"✅ Loaded {len(formatted_data)} barang in container {container_id}")
            
        except Exception as e:
            print(f"[ERROR] load_container_barang: {e}")
            import traceback
            traceback.print_exc()
            self.container_barang_tree.set_data([])
            messagebox.showerror("Error", f"Gagal memuat data barang:\n{str(e)}")
    
        
        
        

