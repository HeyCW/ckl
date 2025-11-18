import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.views.barang_window import BarangWindow
from src.views.container_window import ContainerWindow
from src.views.customer_window import CustomerWindow
from src.views.kapal_window import KapalWindow
from src.views.pengirim_window import SenderWindow
from src.views.report_window import ReportsWindow
from src.views.job_order_window import JobOrderWindow
from src.views.lifting_window import LiftingWindow
from src.views.customer_orders_window import CustomerOrdersWindow
from PIL import Image, ImageTk

class MainWindow:
    def __init__(self, root, current_user=None):
        self.root = root
        self.db = AppDatabase()
        self.current_user = current_user  # Simpan info user yang login
        
        self.setup_main_window()
        self.create_main_interface()
    
    def setup_main_window(self):
        """Setup main window"""
        self.root.title("Aplikasi Data Shipping")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        try:
            # Load dan resize image
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            
            # Set sebagai window icon
            self.root.iconphoto(False, icon_photo)
            
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")
        
        # Center window
        self.center_window()
        
        # Show window
        self.root.deiconify()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_closing)
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (1000 // 2)
        y = (screen_height // 2) - (700 // 2)
        
        self.root.geometry(f"1000x700+{x}+{y}")
    
    def is_owner(self):
        """Check if current user strictly owner"""
        if not self.current_user:
            return False
        
        user_role = self.current_user.get('role', '').lower()
        return user_role == 'owner'


    def create_main_interface(self):
        """Create main interface with big buttons and simple layout"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Welcome message dengan nama user
        username = self.current_user.get('username', 'User') if self.current_user else 'User'
        user_role = self.current_user.get('role', 'user') if self.current_user else 'user'
        
        welcome_label = tk.Label(
            header_frame,
            text=f"🏠 APLIKASI DATA SHIPPING  |  👤 {username} ({user_role.upper()})",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        welcome_label.pack(side='left', padx=20, pady=25)
        
        # Logout button
        logout_btn = tk.Button(
            header_frame,
            text="🚪 Keluar",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=10,
            pady=5,
            command=self.on_window_closing
        )
        logout_btn.pack(side='right', padx=20, pady=20)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="📊 PILIH MENU",
            font=('Arial', 24, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        )
        title_label.pack(pady=(0, 30))
        
        # Content container with proper spacing
        content_frame = tk.Frame(main_frame, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True)
        
        # Menu buttons container
        menu_frame = tk.Frame(content_frame, bg='#ecf0f1')
        menu_frame.pack(pady=(0, 20))
        
        # Row 1: Customer and Barang
        row1_frame = tk.Frame(menu_frame, bg='#ecf0f1')
        row1_frame.pack(pady=20)
        
        
        # Customer button
        customer_btn = tk.Button(
            row1_frame,
            text="👥\n\nDATA CUSTOMER\n\nTambah & Lihat Customer",
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_customer_window
        )
        customer_btn.pack(side='left', padx=30)
        
        # Barang button
        barang_btn = tk.Button(
            row1_frame,
            text="📦\n\nDATA BARANG\n\nTambah & Lihat Barang",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_barang_window
        )
        barang_btn.pack(side='left', padx=30)
        
        kapal_btn = tk.Button(
            row1_frame,
            text="🚢\n\nDATA KAPAL\n\nTambah & Lihat Kapal",
            font=('Arial', 14, 'bold'),
            bg="#e62222",
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_kapal_window
        )
        kapal_btn.pack(side='left', padx=30)
        
        # Row 2: Container, Job Order, Customer Orders
        row2_frame = tk.Frame(menu_frame, bg='#ecf0f1')
        row2_frame.pack(pady=(0, 20))

        # Container button
        container_btn = tk.Button(
            row2_frame,
            text="🚢\n\nDATA CONTAINER\n\nTambah & Lihat Container",
            font=('Arial', 14, 'bold'),
            bg='#e67e22',
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_container_window
        )
        container_btn.pack(side='left', padx=30)

        # Job Order button
        job_order_btn = tk.Button(
            row2_frame,
            text="📋\n\nDATA JOB ORDER\n\nLihat Job Order",
            font=('Arial', 14, 'bold'),
            bg="#8813dc",
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_job_order_window
        )
        job_order_btn.pack(side='left', padx=30)

        # Customer Orders button (NEW)
        # customer_orders_btn = tk.Button(
        #     row2_frame,
        #     text="📊\n\nCUSTOMER ORDERS\n\nLihat Pesanan Customer",
        #     font=('Arial', 14, 'bold'),
        #     bg="#16a085",
        #     fg='white',
        #     relief='flat',
        #     width=20,
        #     height=6,
        #     command=self.show_customer_orders_window
        # )
        # customer_orders_btn.pack(side='left', padx=30)

        # Row 3: Lifting button (only for owner)
        if self.is_owner():
            row3_frame = tk.Frame(menu_frame, bg='#ecf0f1')
            row3_frame.pack(pady=(0, 20))

            lifting_btn = tk.Button(
                row3_frame,
                text="🚧\n\nDATA LIFTING\n\nTambah & Lihat Lifting",
                font=('Arial', 14, 'bold'),
                bg="#f39c12",
                fg='white',
                relief='flat',
                width=20,
                height=6,
                command=self.show_lifting_window
            )
            lifting_btn.pack(side='left', padx=30)
    
    def show_customer_window(self):
        """Show customer management window"""
        try:
            CustomerWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window customer:\n{str(e)}")

    def show_customer_orders_window(self):
        """Show customer orders window"""
        try:
            CustomerOrdersWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window customer orders:\n{str(e)}")

    def show_lifting_window(self):
        """Show lifting management window - OWNER ONLY"""
        # Double check: Validasi role sebelum buka window
        if not self.is_owner():
            messagebox.showwarning(
                "Akses Ditolak",
                "⚠️ Maaf, menu Data Lifting hanya dapat diakses oleh Owner atau Admin.\n\n"
                "Silakan hubungi administrator untuk mendapatkan akses."
            )
            return
        
        try:
            LiftingWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window lifting:\n{str(e)}")
    
    def show_job_order_window(self):
        """Show job order management window"""
        try:
            JobOrderWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window job order:\n{str(e)}")

    def show_barang_window(self):
        """Show barang management window"""
        try:
            BarangWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window barang:\n{str(e)}")
            
    def show_kapal_window(self):
        """Show kapal management window"""
        try:
            KapalWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window kapal:\n{str(e)}")

    def show_container_window(self):
        """Show container management window"""
        try:
            ContainerWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window container:\n{str(e)}")
    
    def show_reports_window(self):
        """Show reports window"""
        try:
            ReportsWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window laporan:\n{str(e)}")
    
    def on_window_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Konfirmasi", "Yakin ingin keluar dari aplikasi?"):
            self.root.quit()

# Usage example
if __name__ == "__main__":
    root = tk.Tk()
    
    # Contoh user yang login
    # current_user = {'username': 'admin', 'role': 'owner'}  # Owner bisa akses
    # current_user = {'username': 'user1', 'role': 'user'}   # User biasa tidak bisa
    
    current_user = {'username': 'admin', 'role': 'owner'}
    
    app = MainWindow(root, current_user=current_user)
    root.mainloop()