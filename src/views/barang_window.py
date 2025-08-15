import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase

class BarangWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_window()
    
    def create_window(self):
        """Create barang management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📦 Data Barang")
        self.window.geometry("1000x700")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.window,
            text="📦 KELOLA DATA BARANG",
            font=('Arial', 18, 'bold'),
            bg='#27ae60',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Form frame
        form_frame = tk.Frame(self.window, bg='#ecf0f1')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Customer selection
        tk.Label(form_frame, text="Pilih Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(form_frame, textvariable=self.customer_var, font=('Arial', 11), width=47, state='readonly')
        self.customer_combo.pack(fill='x', pady=(5, 10))
        
        # Load customers into combobox
        self.load_customer_combo()
        
        # Barang name
        tk.Label(form_frame, text="Nama Barang:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.barang_entry = tk.Entry(form_frame, font=('Arial', 12), width=50)
        self.barang_entry.pack(fill='x', pady=(5, 10))
        
        # Dimensions frame
        dim_frame = tk.Frame(form_frame, bg='#ecf0f1')
        dim_frame.pack(fill='x', pady=10)
        
        # Panjang
        tk.Label(dim_frame, text="Panjang (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.panjang_entry = tk.Entry(dim_frame, font=('Arial', 10), width=10)
        self.panjang_entry.pack(side='left', padx=(5, 20))
        
        # Lebar
        tk.Label(dim_frame, text="Lebar (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.lebar_entry = tk.Entry(dim_frame, font=('Arial', 10), width=10)
        self.lebar_entry.pack(side='left', padx=(5, 20))
        
        # Tinggi
        tk.Label(dim_frame, text="Tinggi (cm):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.tinggi_entry = tk.Entry(dim_frame, font=('Arial', 10), width=10)
        self.tinggi_entry.pack(side='left', padx=5)
        
        # Other fields frame
        other_frame = tk.Frame(form_frame, bg='#ecf0f1')
        other_frame.pack(fill='x', pady=10)
        
        # M3
        tk.Label(other_frame, text="Volume (m³):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.m3_entry = tk.Entry(other_frame, font=('Arial', 10), width=10)
        self.m3_entry.pack(side='left', padx=(5, 20))
        
        # Ton
        tk.Label(other_frame, text="Berat (ton):", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.ton_entry = tk.Entry(other_frame, font=('Arial', 10), width=10)
        self.ton_entry.pack(side='left', padx=(5, 20))
        
        # Colli
        tk.Label(other_frame, text="Colli:", font=('Arial', 10, 'bold'), bg='#ecf0f1').pack(side='left')
        self.col_entry = tk.Entry(other_frame, font=('Arial', 10), width=10)
        self.col_entry.pack(side='left', padx=5)
        
        # Harga
        price_frame = tk.Frame(form_frame, bg='#ecf0f1')
        price_frame.pack(fill='x', pady=10)
        
        tk.Label(price_frame, text="Harga Satuan (Rp):", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.harga_entry = tk.Entry(price_frame, font=('Arial', 12), width=30)
        self.harga_entry.pack(anchor='w', pady=(5, 0))
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=15)
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Tambah Barang",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            command=self.add_barang
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
        
        # Barang list
        list_frame = tk.Frame(self.window, bg='#ecf0f1')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(list_frame, text="📋 DAFTAR BARANG", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        # Treeview for barang list
        tree_frame = tk.Frame(list_frame, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Customer', 'Nama', 'Dimensi', 'Volume', 'Berat', 'Colli', 'Harga'), show='headings', height=8)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Customer', text='Customer')
        self.tree.heading('Nama', text='Nama Barang')
        self.tree.heading('Dimensi', text='P×L×T (cm)')
        self.tree.heading('Volume', text='Volume (m³)')
        self.tree.heading('Berat', text='Berat (ton)')
        self.tree.heading('Colli', text='Colli')
        self.tree.heading('Harga', text='Harga (Rp)')
        
        self.tree.column('ID', width=40)
        self.tree.column('Customer', width=120)
        self.tree.column('Nama', width=150)
        self.tree.column('Dimensi', width=100)
        self.tree.column('Volume', width=80)
        self.tree.column('Berat', width=80)
        self.tree.column('Colli', width=60)
        self.tree.column('Harga', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load existing barang
        self.load_barang()
        
        # Focus on customer combo
        self.customer_combo.focus()
    
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (1000 // 2)
        y = parent_y + (parent_height // 2) - (700 // 2)
        
        self.window.geometry(f"1000x700+{x}+{y}")
    
    def load_customer_combo(self):
        """Load customers into combobox"""
        customers = self.db.get_all_customers()
        customer_list = [f"{c['customer_id']} - {c['nama_customer']}" for c in customers]
        self.customer_combo['values'] = customer_list
    
    def add_barang(self):
        """Add new barang"""
        customer_text = self.customer_var.get()
        if not customer_text:
            messagebox.showerror("Error", "Pilih customer terlebih dahulu!")
            self.customer_combo.focus()
            return
        
        customer_id = int(customer_text.split(' - ')[0])
        nama_barang = self.barang_entry.get().strip()
        
        if not nama_barang:
            messagebox.showerror("Error", "Nama barang harus diisi!")
            self.barang_entry.focus()
            return
        
        try:
            # Get numeric values
            panjang = float(self.panjang_entry.get()) if self.panjang_entry.get() else None
            lebar = float(self.lebar_entry.get()) if self.lebar_entry.get() else None
            tinggi = float(self.tinggi_entry.get()) if self.tinggi_entry.get() else None
            m3 = float(self.m3_entry.get()) if self.m3_entry.get() else None
            ton = float(self.ton_entry.get()) if self.ton_entry.get() else None
            col = int(self.col_entry.get()) if self.col_entry.get() else None
            harga = float(self.harga_entry.get()) if self.harga_entry.get() else None
            
            barang_id = self.db.create_barang(
                customer_id=customer_id,
                nama_barang=nama_barang,
                panjang_barang=panjang,
                lebar_barang=lebar,
                tinggi_barang=tinggi,
                m3_barang=m3,
                ton_barang=ton,
                col_barang=col,
                harga_satuan=harga
            )
            
            messagebox.showinfo("Sukses", f"Barang berhasil ditambahkan dengan ID: {barang_id}")
            self.clear_form()
            self.load_barang()
            
        except ValueError:
            messagebox.showerror("Error", "Pastikan format angka benar!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan barang: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.customer_var.set('')
        self.barang_entry.delete(0, tk.END)
        self.panjang_entry.delete(0, tk.END)
        self.lebar_entry.delete(0, tk.END)
        self.tinggi_entry.delete(0, tk.END)
        self.m3_entry.delete(0, tk.END)
        self.ton_entry.delete(0, tk.END)
        self.col_entry.delete(0, tk.END)
        self.harga_entry.delete(0, tk.END)
        self.customer_combo.focus()
    
    def load_barang(self):
        """Load barang into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load barang from database
        barang_list = self.db.get_all_barang()
        for barang in barang_list:
            # Format dimensions
            dimensi = f"{barang.get('panjang_barang', '-')}×{barang.get('lebar_barang', '-')}×{barang.get('tinggi_barang', '-')}"
            
            # Format currency
            harga = f"Rp {barang.get('harga_satuan', 0):,.0f}" if barang.get('harga_satuan') else '-'
            
            self.tree.insert('', tk.END, values=(
                barang['barang_id'],
                barang['nama_customer'],
                barang['nama_barang'],
                dimensi,
                barang.get('m3_barang', '-'),
                barang.get('ton_barang', '-'),
                barang.get('col_barang', '-'),
                harga
            ))
