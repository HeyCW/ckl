import tkinter as tk
from tkinter import ttk, messagebox
import math

class PaginatedTreeView:
    """Custom TreeView with pagination support"""
    
    def __init__(self, parent, columns, show='headings', height=10, items_per_page=20):
        self.parent = parent
        self.columns = columns
        self.show = show
        self.height = height
        self.items_per_page = items_per_page
        
        # Pagination state
        self.current_page = 0
        self.total_items = 0
        self.total_pages = 0
        self.all_data = []  # Store all data
        self.filtered_data = []  # Store filtered data
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create TreeView with pagination controls"""
        # Main container
        self.container = tk.Frame(self.parent, bg='#ecf0f1')
        
        # TreeView container
        tree_container = tk.Frame(self.container, bg='#ecf0f1')
        tree_container.pack(fill='both', expand=True)
        
        # Create TreeView
        self.tree = ttk.Treeview(tree_container, columns=self.columns, 
                                show=self.show, height=self.height)
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', 
                                        command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal', 
                                        command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, 
                           xscrollcommand=self.h_scrollbar.set)
        
        # Pack TreeView and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Pagination controls
        self.pagination_frame = tk.Frame(self.container, bg='#ecf0f1', height=40)
        self.pagination_frame.pack(fill='x', pady=(5, 0))
        self.pagination_frame.pack_propagate(False)
        
        self.create_pagination_controls()
    
    def create_pagination_controls(self):
        """Create pagination control buttons"""
        # Left side - Page info
        info_frame = tk.Frame(self.pagination_frame, bg='#ecf0f1')
        info_frame.pack(side='left', fill='y')
        
        self.page_info_label = tk.Label(info_frame, text="", bg='#ecf0f1', 
                                       font=('Arial', 9))
        self.page_info_label.pack(side='left', padx=(0, 20), pady=8)
        
        # Center - Navigation buttons
        nav_frame = tk.Frame(self.pagination_frame, bg='#ecf0f1')
        nav_frame.pack(side='left', fill='y')
        
        # First page
        self.first_btn = tk.Button(nav_frame, text="<<", font=('Arial', 8), 
                                  width=3, command=self.go_to_first_page,
                                  bg='#3498db', fg='white', relief='flat')
        self.first_btn.pack(side='left', padx=1, pady=4)
        
        # Previous page
        self.prev_btn = tk.Button(nav_frame, text="<", font=('Arial', 8), 
                                 width=3, command=self.go_to_prev_page,
                                 bg='#3498db', fg='white', relief='flat')
        self.prev_btn.pack(side='left', padx=1, pady=4)
        
        # Page input
        page_input_frame = tk.Frame(nav_frame, bg='#ecf0f1')
        page_input_frame.pack(side='left', padx=5, pady=4)
        
        tk.Label(page_input_frame, text="Hal:", bg='#ecf0f1', 
                font=('Arial', 8)).pack(side='left')
        
        self.page_entry = tk.Entry(page_input_frame, width=4, font=('Arial', 8),
                                  justify='center')
        self.page_entry.pack(side='left', padx=(2, 5))
        self.page_entry.bind('<Return>', self.go_to_page)
        self.page_entry.bind('<KP_Enter>', self.go_to_page)
        
        # Next page
        self.next_btn = tk.Button(nav_frame, text=">", font=('Arial', 8), 
                                 width=3, command=self.go_to_next_page,
                                 bg='#3498db', fg='white', relief='flat')
        self.next_btn.pack(side='left', padx=1, pady=4)
        
        # Last page
        self.last_btn = tk.Button(nav_frame, text=">>", font=('Arial', 8), 
                                 width=3, command=self.go_to_last_page,
                                 bg='#3498db', fg='white', relief='flat')
        self.last_btn.pack(side='left', padx=1, pady=4)
        
        # Right side - Items per page
        per_page_frame = tk.Frame(self.pagination_frame, bg='#ecf0f1')
        per_page_frame.pack(side='right', fill='y')
        
        tk.Label(per_page_frame, text="Per hal:", bg='#ecf0f1', 
                font=('Arial', 8)).pack(side='left', padx=(0, 2), pady=8)
        
        self.per_page_var = tk.StringVar(value=str(self.items_per_page))
        per_page_combo = ttk.Combobox(per_page_frame, textvariable=self.per_page_var,
                                     values=['10', '20', '50', '100'], width=5,
                                     font=('Arial', 8), state='readonly')
        per_page_combo.pack(side='left', pady=4)
        per_page_combo.bind('<<ComboboxSelected>>', self.change_items_per_page)
    
    def pack(self, **kwargs):
        """Pack the container"""
        self.container.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the container"""  
        self.container.grid(**kwargs)
    
    def heading(self, column, **kwargs):
        """Set column heading"""
        self.tree.heading(column, **kwargs)
    
    def column(self, column, **kwargs):
        """Configure column"""
        self.tree.column(column, **kwargs)
    
    def bind(self, event, callback):
        """Bind event to TreeView"""
        self.tree.bind(event, callback)
    
    def selection(self):
        """Get selected items"""
        return self.tree.selection()
    
    def item(self, item, option=None):
        """Get item details"""
        return self.tree.item(item, option)
    
    def insert(self, parent, index, **kwargs):
        """Insert item (used internally for current page)"""
        return self.tree.insert(parent, index, **kwargs)
    
    def delete(self, *items):
        """Delete items from TreeView"""
        self.tree.delete(*items)
    
    def get_children(self, item=''):
        """Get children of item"""
        return self.tree.get_children(item)
    
    def set_data(self, data, filter_func=None):
        """Set all data and refresh display"""
        # Clear existing tree data first to prevent duplicates
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.all_data = data

        # Apply filter if provided
        if filter_func:
            self.filtered_data = [item for item in data if filter_func(item)]
        else:
            self.filtered_data = data[:]

        self.total_items = len(self.filtered_data)
        self.total_pages = max(1, math.ceil(self.total_items / self.items_per_page))

        # Reset to first page
        self.current_page = 0
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh TreeView display for current page"""
        # Clear TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate page bounds
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, self.total_items)
        
        # Add items for current page
        for i in range(start_idx, end_idx):
            item_data = self.filtered_data[i]
            if isinstance(item_data, dict):
                # Handle dictionary data
                if 'values' in item_data:
                    values = item_data['values']
                else:
                    values = list(item_data.values())
                
                iid = item_data.get('iid', '')
                tags = item_data.get('tags', ())
                
                self.tree.insert('', tk.END, iid=iid, values=values, tags=tags)
            else:
                # Handle tuple/list data
                self.tree.insert('', tk.END, values=item_data)
        
        self.update_pagination_controls()
    
    def update_pagination_controls(self):
        """Update pagination control states and labels"""
        # Update page info
        if self.total_items > 0:
            start_item = (self.current_page * self.items_per_page) + 1
            end_item = min((self.current_page + 1) * self.items_per_page, self.total_items)
            info_text = f"Menampilkan {start_item}-{end_item} dari {self.total_items} items"
        else:
            info_text = "Tidak ada data"
        
        self.page_info_label.config(text=info_text)
        
        # Update page entry
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page + 1))
        
        # Update button states
        self.first_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < self.total_pages - 1 else 'disabled')
        self.last_btn.config(state='normal' if self.current_page < self.total_pages - 1 else 'disabled')
    
    def go_to_first_page(self):
        """Go to first page"""
        if self.current_page > 0:
            self.current_page = 0
            self.refresh_display()
    
    def go_to_prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_display()
    
    def go_to_next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.refresh_display()
    
    def go_to_last_page(self):
        """Go to last page"""
        if self.current_page < self.total_pages - 1:
            self.current_page = self.total_pages - 1
            self.refresh_display()
    
    def go_to_page(self, event=None):
        """Go to specific page"""
        try:
            page_num = int(self.page_entry.get()) - 1
            if 0 <= page_num < self.total_pages:
                self.current_page = page_num
                self.refresh_display()
            else:
                messagebox.showwarning("Invalid Page", f"Halaman harus antara 1 dan {self.total_pages}")
                self.page_entry.delete(0, tk.END)
                self.page_entry.insert(0, str(self.current_page + 1))
        except ValueError:
            messagebox.showwarning("Invalid Input", "Masukkan nomor halaman yang valid")
            self.page_entry.delete(0, tk.END)
            self.page_entry.insert(0, str(self.current_page + 1))
    
    def change_items_per_page(self, event=None):
        """Change items per page"""
        try:
            new_per_page = int(self.per_page_var.get())
            self.items_per_page = new_per_page
            
            # Recalculate pagination
            self.total_pages = max(1, math.ceil(self.total_items / self.items_per_page))
            
            # Adjust current page if necessary
            if self.current_page >= self.total_pages:
                self.current_page = max(0, self.total_pages - 1)
            
            self.refresh_display()
        except ValueError:
            pass
