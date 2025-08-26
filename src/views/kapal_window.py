import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class KapalWindow:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.window = None
        self.tree = None
        self.selected_item = None
        
        # Entry widgets untuk form
        self.entries = {}
        self.create_window()    
        
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
    
    def center_window(self, window, width, height):
        """Center window on parent or screen"""
        try:
            if self.parent and self.parent.winfo_exists():
                # Get parent window position and size
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_width = self.parent.winfo_width()
                parent_height = self.parent.winfo_height()
                
                # Calculate center position relative to parent
                x = parent_x + (parent_width - width) // 2
                y = parent_y + (parent_height - height) // 2
            else:
                # Center on screen if no parent
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                x = (screen_width - width) // 2
                y = (screen_height - height) // 2
            
            # Ensure window is not positioned off-screen
            x = max(0, min(x, window.winfo_screenwidth() - width))
            y = max(0, min(y, window.winfo_screenheight() - height))
            
            window.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            logger.error(f"Error centering window: {e}")
            # Fallback to default positioning
            window.geometry(f"{width}x{height}")
    
    def create_window(self):
        """Create the main kapal management window"""
        try:
            self.window = tk.Toplevel(self.parent)
            self.window.title("Manajemen Data Kapal")
            self.window.configure(bg='#f0f0f0')
            self.window.transient(self.parent)
            self.window.grab_set()
            
            # Set window size and center it
            width, height = 1200, 700
            self.center_window(self.window, width, height)

            # Create header frame
            self.create_header(self.window)

            # Create main frame
            main_frame = ttk.Frame(self.window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Create form frame
            self.create_form_frame(main_frame)
            
            # Create buttons frame
            self.create_buttons_frame(main_frame)
            
            # Create treeview frame
            self.create_treeview_frame(main_frame)
            
            # Load data
            self.load_data()
            
            # Ensure window stays on top initially
            self.window.lift()
            self.window.focus_set()
            
        except Exception as e:
            logger.error(f"Error creating kapal window: {e}")
            if hasattr(self, 'window') and self.window:
                self.window.destroy()
                self.window = None
            raise e  # Re-raise to be caught by show_window
        
    def create_header(self, parent):
        """Create header frame with title"""
        header_frame = tk.Frame(parent, bg='#28a745', height=80)  # Green header like in the image
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
            text="🚢",  # Ship emoji
            font=('Segoe UI', 20),
            bg='#e62222',
            fg='white'
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        # Title label
        title_label = tk.Label(
            title_frame,
            text="KELOLA DATA KAPAL",
            font=('Segoe UI', 16, 'bold'),
            bg='#e62222',
            fg='white'
        )
        title_label.pack(side='left')
    
    def create_form_frame(self, parent):
        """Create form for data entry"""
        form_frame = ttk.LabelFrame(parent, text="Data Kapal", padding="10")
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Define fields
        fields = [
            ("Feeder", "feeder", 0, 0),
            ("ETD Sub", "etd_sub", 0, 2),
            ("Party", "party", 0, 4),
            ("CLS", "cls", 1, 0),
            ("Open", "open", 1, 2),
            ("Full", "full", 1, 4),
            ("Destination", "destination", 2, 0)
        ]
        
        # Create form fields
        for label_text, field_name, row, col in fields:
            ttk.Label(form_frame, text=f"{label_text}:").grid(
                row=row, column=col, sticky='w', padx=(0, 5), pady=5
            )
            
            if field_name in ['etd_sub', 'cls', 'open', 'full']:
                # Date entry with placeholder text
                entry = ttk.Entry(form_frame, width=15)
                entry.grid(row=row, column=col+1, sticky='ew', padx=(0, 20), pady=5)
                # Add placeholder text
                entry.insert(0, "YYYY-MM-DD")
                entry.config(foreground='gray')
                # Bind events for placeholder behavior
                self.setup_date_placeholder(entry)
            else:
                entry = ttk.Entry(form_frame, width=20)
                entry.grid(row=row, column=col+1, sticky='ew', padx=(0, 20), pady=5)
            
            self.entries[field_name] = entry
        
        # Configure grid weights for destination field (spans multiple columns)
        if 'destination' in self.entries:
            self.entries['destination'].grid(columnspan=3, sticky='ew')
        
        # Configure column weights
        for i in range(6):
            form_frame.columnconfigure(i, weight=1)
    
    def create_styled_button(self, parent, text, command, bg_color, hover_color=None):
        """Create a styled button with custom colors"""
        if hover_color is None:
            # Create a slightly darker hover color
            hover_color = self.darken_color(bg_color)
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=('Segoe UI', 9, 'bold'),
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
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        # Button configurations with icons and colors
        buttons = [
            ("+ Tambah", self.add_kapal, "#FF8C42"),      # Orange
            ("🗂 Bersihkan", self.clear_form, "#8A9BA8"),  # Gray  
            ("✏ Edit Kapal", self.update_kapal, "#5DADE2"), # Blue
            ("🗑 Hapus Kapal", self.delete_kapal, "#E74C3C"), # Red
            ("↻ Refresh", self.load_data, "#9C27B0")       # Purple
        ]
        
        for text, command, color in buttons:
            btn = self.create_styled_button(btn_frame, text, command, color)
            btn.pack(side='left', padx=5)
    
    def create_treeview_frame(self, parent):
        """Create treeview to display data"""
        tree_frame = ttk.LabelFrame(parent, text="Daftar Kapal", padding="10")
        tree_frame.pack(fill='both', expand=True)
        
        # Create treeview with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical')
        h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal')
        
        # Treeview
        columns = ('ID', 'Feeder', 'ETD Sub', 'Party', 'CLS', 'Open', 'Full', 'Destination', 'Created', 'Updated')
        self.tree = ttk.Treeview(
            tree_container, 
            columns=columns, 
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configure scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Pack scrollbars and treeview
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Configure column headings and widths
        column_widths = {
            'ID': 50, 'Feeder': 100, 'ETD Sub': 90, 'Party': 100,
            'CLS': 90, 'Open': 90, 'Full': 90, 'Destination': 150,
            'Created': 130, 'Updated': 130
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
    
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
            
            query = '''
                INSERT INTO kapals (feeder, etd_sub, party, cls, open, full, destination)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                data['feeder'],
                data['etd_sub'] if data['etd_sub'] else None,
                data['party'],
                data['cls'] if data['cls'] else None,
                data['open'] if data['open'] else None,
                data['full'] if data['full'] else None,
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
            
            query = '''
                UPDATE kapals 
                SET feeder=?, etd_sub=?, party=?, cls=?, open=?, full=?, 
                    destination=?, updated_at=CURRENT_TIMESTAMP
                WHERE kapal_id=?
            '''
            
            params = (
                data['feeder'],
                data['etd_sub'] if data['etd_sub'] else None,
                data['party'],
                data['cls'] if data['cls'] else None,
                data['open'] if data['open'] else None,
                data['full'] if data['full'] else None,
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
    
    def load_data(self):
        """Load all kapal data into treeview"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch data from database
            query = """
                SELECT kapal_id, feeder, etd_sub, party, cls, open, full, 
                       destination, created_at, updated_at 
                FROM kapals 
                ORDER BY created_at DESC
            """
            
            result = self.db.execute(query)
            
            if result:
                for row in result:
                    # Format dates for display
                    formatted_row = []
                    for i, value in enumerate(row):
                        if i in [2, 4, 5, 6, 8, 9] and value:  # Date columns
                            try:
                                if 'T' in str(value):  # DateTime format
                                    formatted_value = datetime.fromisoformat(str(value).replace('T', ' ')).strftime('%Y-%m-%d %H:%M')
                                else:  # Date format
                                    formatted_value = str(value)
                            except:
                                formatted_value = str(value)
                        else:
                            formatted_value = str(value) if value is not None else ''
                        formatted_row.append(formatted_value)
                    
                    self.tree.insert('', 'end', values=formatted_row)
            
            logger.info(f"Loaded {len(result) if result else 0} kapal records")
            
        except Exception as e:
            logger.error(f"Error loading kapal data: {e}")
            messagebox.showerror("Error", f"Gagal memuat data: {e}")
    
    def setup_date_placeholder(self, entry):
        """Setup placeholder behavior for date entries"""
        def on_focus_in(event):
            if entry.get() == "YYYY-MM-DD":
                entry.delete(0, tk.END)
                entry.config(foreground='black')
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, "YYYY-MM-DD")
                entry.config(foreground='gray')
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
    
    def get_form_data(self):
        """Get data from form entries"""
        data = {}
        for field_name, entry in self.entries.items():
            value = entry.get().strip()
            # Skip placeholder text for date fields
            if field_name in ['etd_sub', 'cls', 'open', 'full'] and value == "YYYY-MM-DD":
                data[field_name] = None
            else:
                data[field_name] = value if value else None
        return data
    
    def clear_form(self):
        """Clear all form entries"""
        for field_name, entry in self.entries.items():
            entry.delete(0, tk.END)
            # Reset placeholder for date fields
            if field_name in ['etd_sub', 'cls', 'open', 'full']:
                entry.insert(0, "YYYY-MM-DD")
                entry.config(foreground='gray')
        self.selected_item = None
    
    def on_item_select(self, event):
        """Handle treeview item selection"""
        selected = self.tree.selection()
        if selected:
            self.selected_item = selected[0]
            values = self.tree.item(self.selected_item, 'values')
            
            # Fill form with selected data
            fields = ['feeder', 'etd_sub', 'party', 'cls', 'open', 'full', 'destination']
            for i, field in enumerate(fields):
                if field in self.entries:
                    self.entries[field].delete(0, tk.END)
                    # Skip ID column (index 0), start from index 1
                    value = values[i + 1] if i + 1 < len(values) else ''
                    if value and value != 'None':
                        # For date fields, extract just the date part
                        if field in ['etd_sub', 'cls', 'open', 'full'] and ' ' in str(value):
                            value = str(value).split(' ')[0]
                        self.entries[field].insert(0, str(value))
    
    def validate_date(self, date_string):
        """Validate date format"""
        if not date_string:
            return True
        
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False