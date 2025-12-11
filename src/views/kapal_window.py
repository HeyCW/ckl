import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
from datetime import datetime
import logging
from PIL import Image, ImageTk
from tkcalendar import DateEntry

from src.widget.paginated_tree_view import PaginatedTreeView
from src.utils.helpers import setup_window_restore_behavior

logger = logging.getLogger(__name__)

class KapalWindow:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.window = None
        self.tree = None
        self.selected_item = None
        self.data_loaded = False  # Track if data has been loaded

        # Entry widgets untuk form
        self.entries = {}
        self.create_window()
    
    def get_scale_factor(self):
        """Calculate scale factor based on screen size"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Base scale on 1600x900 as reference (better for 1366x768)
        width_scale = screen_width / 1600
        height_scale = screen_height / 900

        # Use average and clamp between 0.75 and 1.3
        scale = (width_scale + height_scale) / 2
        return max(0.75, min(1.3, scale))
    
    def scaled_font(self, base_size):
        """Return scaled font size"""
        scale = self.get_scale_factor()
        return max(8, int(base_size * scale))
    
    def on_window_resize(self, event):
        """Handle window resize to adjust column widths"""
        if hasattr(self, 'tree') and event.widget == self.window:
            try:
                window_width = self.window.winfo_width()
                available_width = window_width - 100
                
                # Proportional widths for kapal columns (DENGAN Shipping Line)
                self.tree.column('ID', width=int(available_width * 0.04))
                self.tree.column('Shipping Line', width=int(available_width * 0.12))
                self.tree.column('Feeder', width=int(available_width * 0.13))
                self.tree.column('ETD Sub', width=int(available_width * 0.10))
                self.tree.column('CLS', width=int(available_width * 0.10))
                self.tree.column('Open', width=int(available_width * 0.10))
                self.tree.column('Full', width=int(available_width * 0.10))
                self.tree.column('Destination', width=int(available_width * 0.13))
                self.tree.column('Created', width=int(available_width * 0.09))
                self.tree.column('Updated', width=int(available_width * 0.09))
            except:
                pass
        
    def show_window(self):
        """Show kapal management window"""
        try:
            if self.window is None or not self.window.winfo_exists():
                self.create_window()
            else:
                self.window.lift()
                self.window.focus()
        except Exception as e:
            logger.error(f"Error showing kapal window: {e}")
            messagebox.showerror("Error", f"Tidak dapat membuka window kapal: {e}")
            return False
        return True
    
    def create_window(self):
        """Create and configure the main kapal window with responsive design"""
        try:
            # Create new window
            self.window = tk.Toplevel(self.parent)
            self.window.title("🚢 Kelola Data Kapal")

            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()

            # Adaptive window size
            window_width = min(int(screen_width * 0.85), 1400)
            window_height = min(int(screen_height * 0.85), 850)

            self.window.geometry(f"{window_width}x{window_height}")
            self.window.configure(bg='#ecf0f1')
            self.window.transient(self.parent)
            self.window.grab_set()

            # Setup window restore behavior (fix minimize/restore issue)
            setup_window_restore_behavior(self.window)

            # Resizable
            self.window.minsize(850, 500)  # Reduced for 1366x768 compatibility
            self.window.resizable(True, True)

            # Set window properties
            self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
            
            try:
                # Load dan resize image
                icon_image = Image.open("assets/logo.jpg")
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.window.iconphoto(False, icon_photo)
            except Exception as e:
                print(f"Icon tidak ditemukan: {e}")
            
            # Center the window
            self.center_window()
            
            # Create main container
            main_frame = tk.Frame(self.window, bg='#ecf0f1')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Create header
            self.create_header(main_frame)
            
            # Create form frame
            self.create_form_frame(main_frame)
            
            # Create buttons frame
            self.create_buttons_frame(main_frame)
            
            # Create treeview frame
            self.create_treeview_frame(main_frame)

            # Lazy load data after window is fully rendered (improves initial load time)
            self.window.after_idle(self.lazy_load_data)

            # Focus on first entry
            if 'feeder' in self.entries:
                self.entries['feeder'].focus()

            # Bind resize event
            self.window.bind('<Configure>', self.on_window_resize)
                
            logger.info("Kapal window created successfully")
            
        except Exception as e:
            logger.error(f"Error creating kapal window: {e}")
            raise
    
    def on_window_close(self):
        """Handle window close event"""
        try:
            if self.window:
                self.window.grab_release()
                self.window.destroy()
                self.window = None
            logger.info("Kapal window closed")
        except Exception as e:
            logger.error(f"Error closing kapal window: {e}")
    
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
        window_height = min(int(screen_height * 0.85), 850)
        
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
    
    def create_header(self, parent):
        """Create header frame with title and responsive font"""
        header_frame = tk.Frame(parent, bg='#e62222', height=80)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        # Header content frame for centering
        content_frame = tk.Frame(header_frame, bg='#e62222')
        content_frame.pack(expand=True, fill='both')
        
        # Ship icon and title
        title_frame = tk.Frame(content_frame, bg='#e62222')
        title_frame.pack(expand=True)
        
        # Icon label (using ship emoji)
        icon_label = tk.Label(
            title_frame,
            text="🚢",
            font=('Segoe UI', self.scaled_font(20)),
            bg='#e62222',
            fg='white'
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        # Title label with responsive font
        title_label = tk.Label(
            title_frame,
            text="KELOLA DATA KAPAL",
            font=('Segoe UI', self.scaled_font(16), 'bold'),
            bg='#e62222',
            fg='white'
        )
        title_label.pack(side='left')
    
    def create_form_frame(self, parent):
        """Create form for data entry with responsive fonts and DatePicker"""
        form_frame = ttk.LabelFrame(parent, text="Data Kapal", padding="10")
        form_frame.pack(fill='x', pady=(10, 10))
        
        # Style for labels with responsive font
        label_font = ('Arial', self.scaled_font(10), 'bold')
        entry_font = ('Arial', self.scaled_font(10))
        
        # Define fields (DENGAN Shipping Line)
        fields = [
            ("Shipping Line", "shipping_line", 0, 0, "text"),
            ("Feeder", "feeder", 0, 2, "text"),
            ("ETD Sub", "etd_sub", 0, 4, "date"),
            ("CLS", "cls", 1, 0, "date"),
            ("Open", "open", 1, 2, "date"),
            ("Full", "full", 1, 4, "date"),
            ("Destination", "destination", 2, 0, "text")
        ]
        
        # Create form fields
        for label_text, field_name, row, col, field_type in fields:
            label = tk.Label(
                form_frame, 
                text=f"{label_text}:",
                font=label_font,
                bg='#ecf0f1'
            )
            label.grid(row=row, column=col, sticky='w', padx=(0, 5), pady=5)
            
            if field_type == "date":
                # DateEntry widget dengan format Indonesia
                entry = DateEntry(
                    form_frame,
                    width=13,
                    font=entry_font,
                    background='#FF8C42',
                    foreground='white',
                    borderwidth=2,
                    date_pattern='dd/mm/yyyy',  # Format Indonesia: Tanggal/Bulan/Tahun
                    locale='id_ID',  # Locale Indonesia
                    state='normal',
                    showweeknumbers=False,
                    firstweekday='monday'
                )
                entry.grid(row=row, column=col+1, sticky='ew', padx=(0, 20), pady=5)
            else:
                entry = tk.Entry(
                    form_frame, 
                    width=20,
                    font=entry_font
                )
                entry.grid(row=row, column=col+1, sticky='ew', padx=(0, 20), pady=5)
            
            self.entries[field_name] = entry
        
        # Configure grid weights for destination field (spans multiple columns)
        if 'destination' in self.entries:
            self.entries['destination'].grid(columnspan=3, sticky='ew')
        
        # Configure column weights
        for i in range(6):
            form_frame.columnconfigure(i, weight=1)
    
    def create_styled_button(self, parent, text, command, bg_color, hover_color=None):
        """Create a styled button with custom colors and responsive font"""
        if hover_color is None:
            hover_color = self.darken_color(bg_color)
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=('Segoe UI', self.scaled_font(9), 'bold'),
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=8,
            cursor='hand2',
            activebackground=hover_color,
            activeforeground='white'
        )
        
        # Add hover effects
        def on_enter(e):
            button.config(bg=hover_color)
        
        def on_leave(e):
            button.config(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def darken_color(self, color):
        """Darken a hex color by reducing RGB values"""
        if color.startswith('#'):
            color = color[1:]
        
        # Convert hex to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Darken by reducing each component by 20%
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def create_buttons_frame(self, parent):
        """Create buttons for CRUD operations"""
        btn_frame = tk.Frame(parent, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=(0, 10))
        
        # Button configurations with icons and colors
        buttons = [
            ("+ Tambah", self.add_kapal, "#FF8C42"),
            ("🗂 Bersihkan", self.clear_form, "#8A9BA8"),
            ("✏ Edit Kapal", self.update_kapal, "#5DADE2"),
            ("🗑 Hapus Kapal", self.delete_kapal, "#E74C3C"),
            ("↻ Refresh", self.load_data, "#9C27B0")
        ]
        
        for text, command, color in buttons:
            btn = self.create_styled_button(btn_frame, text, command, color)
            btn.pack(side='left', padx=5)
    
    def create_treeview_frame(self, parent):
        """Create treeview to display data with responsive design"""
        tree_frame = ttk.LabelFrame(parent, text="Daftar Kapal", padding="10")
        tree_frame.pack(fill='both', expand=True)
        
        # Create tree container
        tree_container = tk.Frame(tree_frame, bg='#ecf0f1')
        tree_container.pack(fill='both', expand=True)
        
        # Define columns (DENGAN Shipping Line)
        columns = ('ID', 'Shipping Line', 'Feeder', 'ETD Sub', 'CLS', 'Open', 'Full', 'Destination', 'Created', 'Updated')

        # Create PaginatedTreeView
        self.tree = PaginatedTreeView(
            parent=tree_container,
            columns=columns,
            show='headings',
            height=15,
            items_per_page=20
        )

        # Configure column headings tanpa Party
        window_width = self.window.winfo_width()
        
        column_configs = {
            'ID': ('ID', max(40, int(window_width * 0.03))),
            'Shipping Line': ('Shipping Line', max(100, int(window_width * 0.10))),
            'Feeder': ('Feeder', max(100, int(window_width * 0.12))),
            'ETD Sub': ('ETD Sub', max(90, int(window_width * 0.08))),
            'CLS': ('CLS', max(90, int(window_width * 0.08))),
            'Open': ('Open', max(90, int(window_width * 0.08))),
            'Full': ('Full', max(90, int(window_width * 0.08))),
            'Destination': ('Destination', max(150, int(window_width * 0.12))),
            'Created': ('Created', max(120, int(window_width * 0.12))),
            'Updated': ('Updated', max(120, int(window_width * 0.12)))
        }

        for col, (heading_text, width) in column_configs.items():
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, width=width, minwidth=50)

        # Pack PaginatedTreeView
        self.tree.pack(fill='both', expand=True)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

    def format_date_for_display(self, date_str):
        """Convert database date format (YYYY-MM-DD) to Indonesian format (DD/MM/YYYY)"""
        if not date_str or date_str == 'None':
            return ''
        try:
            # Parse date dari database
            date_obj = datetime.strptime(str(date_str).split(' ')[0], '%Y-%m-%d')
            # Format ke Indonesia
            return date_obj.strftime('%d/%m/%Y')
        except:
            return str(date_str)
    
    def format_date_for_database(self, date_str):
        """Convert Indonesian format (DD/MM/YYYY) to database format (YYYY-MM-DD)"""
        if not date_str or date_str == '':
            return None
        try:
            # Parse dari format Indonesia
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            # Format ke database
            return date_obj.strftime('%Y-%m-%d')
        except:
            return None

    def add_kapal(self):
        """Add new kapal data"""
        try:
            data = self.get_form_data()
            if not data:
                return
            
            # Validate required fields
            if not data.get('feeder') or not data.get('destination'):
                messagebox.showerror("Error", "Feeder dan Destination wajib diisi!")
                return

            # Query dengan shipping_line
            query = '''
                INSERT INTO kapals (shipping_line, feeder, etd_sub, cls, open, full, destination)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''

            # Params dengan shipping_line - konversi tanggal ke format database
            params = (
                data['shipping_line'],
                data['feeder'],
                self.format_date_for_database(data['etd_sub']) if data['etd_sub'] else None,
                self.format_date_for_database(data['cls']) if data['cls'] else None,
                self.format_date_for_database(data['open']) if data['open'] else None,
                self.format_date_for_database(data['full']) if data['full'] else None,
                data['destination']
            )
            
            self.db.execute(query, params)
            messagebox.showinfo("Sukses", "Data kapal berhasil ditambahkan!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            logger.error(f"Error adding kapal: {e}")
            messagebox.showerror("Error", f"Gagal menambahkan data: {e}")
        
    def update_kapal(self):
        """Update selected kapal data"""
        if not self.selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang akan diupdate!")
            return
        
        try:
            data = self.get_form_data()
            if not data:
                return
            
            # Validate required fields
            if not data.get('feeder') or not data.get('destination'):
                messagebox.showerror("Error", "Feeder dan Destination wajib diisi!")
                return
            
            # Get kapal_id from selected item
            kapal_id = self.tree.item(self.selected_item, 'values')[0]

            # Query dengan shipping_line
            query = '''
                UPDATE kapals
                SET shipping_line=?, feeder=?, etd_sub=?, cls=?, open=?, full=?,
                    destination=?, updated_at=CURRENT_TIMESTAMP
                WHERE kapal_id=?
            '''

            # Params dengan shipping_line - konversi tanggal ke format database
            params = (
                data['shipping_line'],
                data['feeder'],
                self.format_date_for_database(data['etd_sub']) if data['etd_sub'] else None,
                self.format_date_for_database(data['cls']) if data['cls'] else None,
                self.format_date_for_database(data['open']) if data['open'] else None,
                self.format_date_for_database(data['full']) if data['full'] else None,
                data['destination'],
                kapal_id
            )
            
            self.db.execute(query, params)
            messagebox.showinfo("Sukses", "Data kapal berhasil diupdate!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            logger.error(f"Error updating kapal: {e}")
            messagebox.showerror("Error", f"Gagal mengupdate data: {e}")

    def delete_kapal(self):
        """Delete selected kapal data"""
        if not self.selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang akan dihapus!")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Konfirmasi", 
            "Yakin ingin menghapus data kapal ini?\nData yang dihapus tidak dapat dikembalikan!"
        )
        
        if not result:
            return
        
        try:
            # Get kapal_id from selected item
            kapal_id = self.tree.item(self.selected_item, 'values')[0]
            
            query = "DELETE FROM kapals WHERE kapal_id=?"
            self.db.execute(query, (kapal_id,))
            
            messagebox.showinfo("Sukses", "Data kapal berhasil dihapus!")
            self.clear_form()
            self.load_data()
            
        except Exception as e:
            logger.error(f"Error deleting kapal: {e}")
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")
    
    def lazy_load_data(self):
        """Lazy load data - called after window is fully rendered"""
        if not self.data_loaded:
            print("Lazy loading kapal data...")
            self.load_data()
            self.data_loaded = True

    def load_data(self):
        """Load all kapal data into PaginatedTreeView dengan format tanggal Indonesia"""
        try:
            # Query dengan shipping_line
            query = """
                SELECT kapal_id, shipping_line, feeder, etd_sub, cls, open, full,
                    destination, created_at, updated_at
                FROM kapals
                ORDER BY created_at DESC
            """
            
            result = self.db.execute(query)
            
            # Format data untuk PaginatedTreeView
            formatted_data = []
            
            if result:
                for row in result:
                    # Format dates for display
                    formatted_row = []
                    for i, value in enumerate(row):
                        # Date columns: etd_sub(3), cls(4), open(5), full(6), created_at(8), updated_at(9)
                        if i in [3, 4, 5, 6]:  # Date columns (tanpa timestamp)
                            formatted_value = self.format_date_for_display(value)
                        elif i in [8, 9] and value:  # DateTime columns
                            try:
                                if 'T' in str(value):
                                    dt = datetime.fromisoformat(str(value).replace('T', ' '))
                                    formatted_value = dt.strftime('%d/%m/%Y %H:%M')
                                else:
                                    formatted_value = str(value)
                            except:
                                formatted_value = str(value)
                        else:
                            formatted_value = str(value) if value is not None else ''
                        formatted_row.append(formatted_value)
                    
                    # Add to formatted data with kapal_id as iid
                    formatted_data.append({
                        'iid': str(row[0]) if row[0] else '',
                        'values': tuple(formatted_row)
                    })
            
            # Set data to PaginatedTreeView
            self.tree.set_data(formatted_data)
            
            logger.info(f"Loaded {len(formatted_data)} kapal records with pagination")
            
        except Exception as e:
            logger.error(f"Error loading kapal data: {e}")
            messagebox.showerror("Error", f"Gagal memuat data: {e}")
    
    def get_form_data(self):
        """Get data from form entries"""
        data = {}
        for field_name, entry in self.entries.items():
            if field_name in ['etd_sub', 'cls', 'open', 'full']:
                # Untuk DateEntry, ambil tanggal dalam format DD/MM/YYYY
                try:
                    date_value = entry.get_date().strftime('%d/%m/%Y')
                    data[field_name] = date_value
                except:
                    data[field_name] = None
            else:
                value = entry.get().strip()
                data[field_name] = value if value else None
        return data
    
    def clear_form(self):
        """Clear all form entries"""
        for field_name, entry in self.entries.items():
            if field_name in ['etd_sub', 'cls', 'open', 'full']:
                # Untuk DateEntry, set ke tanggal hari ini
                entry.set_date(datetime.now())
            else:
                entry.delete(0, tk.END)
        self.selected_item = None
    
    def on_item_select(self, event):
        """Handle treeview item selection"""
        selected = self.tree.selection()
        if selected:
            self.selected_item = selected[0]
            values = self.tree.item(self.selected_item, 'values')
            
            # Fill form with selected data (DENGAN shipping_line)
            fields = ['shipping_line', 'feeder', 'etd_sub', 'cls', 'open', 'full', 'destination']
            for i, field in enumerate(fields):
                if field in self.entries:
                    # Skip ID column (index 0), start from index 1
                    value = values[i + 1] if i + 1 < len(values) else ''
                    
                    if field in ['etd_sub', 'cls', 'open', 'full']:
                        # Untuk DateEntry, parse tanggal dari format Indonesia
                        if value and value != 'None' and value != '':
                            try:
                                date_obj = datetime.strptime(value, '%d/%m/%Y')
                                self.entries[field].set_date(date_obj)
                            except:
                                self.entries[field].set_date(datetime.now())
                        else:
                            self.entries[field].set_date(datetime.now())
                    else:
                        # Untuk Entry biasa
                        self.entries[field].delete(0, tk.END)
                        if value and value != 'None':
                            self.entries[field].insert(0, str(value))
    
    def validate_date(self, date_string):
        """Validate date format"""
        if not date_string:
            return True
        
        try:
            datetime.strptime(date_string, '%d/%m/%Y')
            return True
        except ValueError:
            return False