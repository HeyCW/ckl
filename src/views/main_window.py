import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.views.barang_window import BarangWindow
from src.views.container_window import ContainerWindow
from src.views.customer_window import CustomerWindow
from src.views.report_window import ReportsWindow
from PIL import Image, ImageTk

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.db = AppDatabase()
        
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
    
    def create_main_interface(self):
        """Create main interface with big buttons and simple layout"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Welcome message
        welcome_label = tk.Label(
            header_frame,
            text="🏠 APLIKASI DATA SHIPPING",
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
            padx=20,
            pady=10,
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
        
        # Row 2: Container and Reports
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
        
        # # Reports button
        # reports_btn = tk.Button(
        #     row2_frame,
        #     text="📋\n\nLAPORAN\n\nLihat Semua Data",
        #     font=('Arial', 14, 'bold'),
        #     bg='#9b59b6',
        #     fg='white',
        #     relief='flat',
        #     width=20,
        #     height=6,
        #     command=self.show_reports_window
        # )
        # reports_btn.pack(side='left', padx=30)
    
    def show_customer_window(self):
        """Show customer management window"""
        try:
            CustomerWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window customer:\n{str(e)}")
    
    def show_barang_window(self):
        """Show barang management window"""
        try:
            BarangWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window barang:\n{str(e)}")
    
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
    app = MainWindow(root)
    root.mainloop()