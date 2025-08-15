import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase

class CustomerWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_window()
    
    def create_window(self):
        """Create customer management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📋 Data Customer")
        self.window.geometry("800x600")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.window,
            text="👥 KELOLA DATA CUSTOMER",
            font=('Arial', 18, 'bold'),
            bg='#3498db',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Form frame
        form_frame = tk.Frame(self.window, bg='#ecf0f1')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Name field
        tk.Label(form_frame, text="Nama Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.name_entry = tk.Entry(form_frame, font=('Arial', 12), width=50)
        self.name_entry.pack(fill='x', pady=(5, 10))
        
        # Address field
        tk.Label(form_frame, text="Alamat Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.address_entry = tk.Text(form_frame, font=('Arial', 12), height=3, width=50)
        self.address_entry.pack(fill='x', pady=(5, 10))
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=10)
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Tambah Customer",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            command=self.add_customer
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
        
        close_btn = tk.Button(
            btn_frame,
            text="❌ Tutup",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            command=self.window.destroy
        )
        close_btn.pack(side='right')
        
        # Customer list
        list_frame = tk.Frame(self.window, bg='#ecf0f1')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(list_frame, text="📋 DAFTAR CUSTOMER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        # Treeview for customer list
        tree_frame = tk.Frame(list_frame, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Nama', 'Alamat'), show='headings', height=10)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nama', text='Nama Customer')
        self.tree.heading('Alamat', text='Alamat')
        
        self.tree.column('ID', width=50)
        self.tree.column('Nama', width=200)
        self.tree.column('Alamat', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load existing customers
        self.load_customers()
        
        # Focus on name entry
        self.name_entry.focus()
    
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (800 // 2)
        y = parent_y + (parent_height // 2) - (600 // 2)
        
        self.window.geometry(f"800x600+{x}+{y}")
    
    def add_customer(self):
        """Add new customer"""
        name = self.name_entry.get().strip()
        address = self.address_entry.get(1.0, tk.END).strip()
        
        if not name:
            messagebox.showerror("Error", "Nama customer harus diisi!")
            self.name_entry.focus()
            return
        
        try:
            customer_id = self.db.create_customer(name, address)
            messagebox.showinfo("Sukses", f"Customer berhasil ditambahkan dengan ID: {customer_id}")
            self.clear_form()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan customer: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(1.0, tk.END)
        self.name_entry.focus()
    
    def load_customers(self):
        """Load customers into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load customers from database
        customers = self.db.get_all_customers()
        for customer in customers:
            self.tree.insert('', tk.END, values=(
                customer['customer_id'],
                customer['nama_customer'],
                customer['alamat_customer'] or '-'
            ))
