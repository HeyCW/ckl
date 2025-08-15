import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase

class ContainerWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_window()
    
    def create_window(self):
        """Create container management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("🚢 Data Container")
        self.window.geometry("900x600")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Header
        header = tk.Label(
            self.window,
            text="🚢 KELOLA DATA CONTAINER",
            font=('Arial', 18, 'bold'),
            bg='#e67e22',
            fg='white',
            pady=15
        )
        header.pack(fill='x')
        
        # Form frame
        form_frame = tk.Frame(self.window, bg='#ecf0f1')
        form_frame.pack(fill='x', padx=20, pady=20)
        
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
        
        # Container list
        list_frame = tk.Frame(self.window, bg='#ecf0f1')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(list_frame, text="📋 DAFTAR CONTAINER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        # Treeview for container list
        tree_frame = tk.Frame(list_frame, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Feeder', 'Party', 'Container', 'Destination', 'ETD_Sub', 'CLS'), show='headings', height=8)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Feeder', text='Feeder')
        self.tree.heading('Party', text='Party')
        self.tree.heading('Container', text='Container')
        self.tree.heading('Destination', text='Destination')
        self.tree.heading('ETD_Sub', text='ETD Sub')
        self.tree.heading('CLS', text='CLS')
        
        self.tree.column('ID', width=40)
        self.tree.column('Feeder', width=120)
        self.tree.column('Party', width=100)
        self.tree.column('Container', width=120)
        self.tree.column('Destination', width=100)
        self.tree.column('ETD_Sub', width=80)
        self.tree.column('CLS', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load existing containers
        self.load_containers()
        
        # Focus on feeder entry
        self.feeder_entry.focus()
    
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (900 // 2)
        y = parent_y + (parent_height // 2) - (600 // 2)
        
        self.window.geometry(f"900x600+{x}+{y}")
    
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan container: {str(e)}")
    
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
        self.feeder_entry.focus()
    
    def load_containers(self):
        """Load containers into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load containers from database
        containers = self.db.get_all_containers()
        for container in containers:
            self.tree.insert('', tk.END, values=(
                container['container_id'],
                container.get('feeder', '-'),
                container.get('party', '-'),
                container.get('container', '-'),
                container.get('destination', '-'),
                container.get('etd_sub', '-'),
                container.get('cls', '-')
            ))
