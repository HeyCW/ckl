import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.views.barang_window import BarangWindow
from src.views.container_window import ContainerWindow
from src.views.customer_window import CustomerWindow
from src.views.report_window import ReportsWindow

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
        
        # Close button
        close_btn = tk.Button(
            header_frame,
            text="❌ Keluar",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            command=self.on_window_closing
        )
        close_btn.pack(side='right', padx=20, pady=20)
        
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
        
        # Menu buttons container
        menu_frame = tk.Frame(main_frame, bg='#ecf0f1')
        menu_frame.pack(expand=True)
        
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
            height=8,
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
            height=8,
            command=self.show_barang_window
        )
        barang_btn.pack(side='left', padx=30)
        
        # Row 2: Container and Reports
        row2_frame = tk.Frame(menu_frame, bg='#ecf0f1')
        row2_frame.pack(pady=20)
        
        # Container button
        container_btn = tk.Button(
            row2_frame,
            text="🚢\n\nDATA CONTAINER\n\nTambah & Lihat Container",
            font=('Arial', 14, 'bold'),
            bg='#e67e22',
            fg='white',
            relief='flat',
            width=20,
            height=8,
            command=self.show_container_window
        )
        container_btn.pack(side='left', padx=30)
        
        # Reports button
        reports_btn = tk.Button(
            row2_frame,
            text="📋\n\nLAPORAN\n\nLihat Semua Data",
            font=('Arial', 14, 'bold'),
            bg='#9b59b6',
            fg='white',
            relief='flat',
            width=20,
            height=8,
            command=self.show_reports_window
        )
        reports_btn.pack(side='left', padx=30)
        
        # Statistics at bottom
        self.create_stats_section(main_frame)
    
    def create_stats_section(self, parent):
        """Create statistics section"""
        stats_frame = tk.Frame(parent, bg='#ecf0f1')
        stats_frame.pack(side='bottom', fill='x', pady=(30, 0))
        
        stats_title = tk.Label(
            stats_frame,
            text="📈 RINGKASAN DATA",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        )
        stats_title.pack()
        
        # Stats container
        stats_container = tk.Frame(stats_frame, bg='#ecf0f1')
        stats_container.pack(pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(
            stats_container,
            text="🔄 Refresh",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            command=self.refresh_stats
        )
        refresh_btn.pack(pady=(0, 10))
        
        # Stats labels container
        self.stats_labels_frame = tk.Frame(stats_container, bg='#ecf0f1')
        self.stats_labels_frame.pack()
        
        # Load initial stats
        self.refresh_stats()
    
    def refresh_stats(self):
        """Refresh statistics display"""
        # Clear existing stats
        for widget in self.stats_labels_frame.winfo_children():
            widget.destroy()
        
        # Get stats from database
        stats = self.db.get_dashboard_stats()
        
        # Customer count
        customer_stat = tk.Label(
            self.stats_labels_frame,
            text=f"👥 Customer: {stats['total_customers']}",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        )
        customer_stat.pack(side='left', padx=10)
        
        # Barang count
        barang_stat = tk.Label(
            self.stats_labels_frame,
            text=f"📦 Barang: {stats['total_barang']}",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        )
        barang_stat.pack(side='left', padx=10)
        
        # Container count
        container_stat = tk.Label(
            self.stats_labels_frame,
            text=f"🚢 Container: {stats['total_containers']}",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        )
        container_stat.pack(side='left', padx=10)
        
        # Total users
        total_users = len(self.db.get_all_users())
        users_stat = tk.Label(
            self.stats_labels_frame,
            text=f"👤 Users: {total_users}",
            font=('Arial', 12, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        )
        users_stat.pack(side='left', padx=10)
    
    def show_customer_window(self):
        """Show customer management window"""
        try:
            CustomerWindow(self.root, self.db, self.refresh_stats)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window customer:\n{str(e)}")
    
    def show_barang_window(self):
        """Show barang management window"""
        try:
            BarangWindow(self.root, self.db, self.refresh_stats)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window barang:\n{str(e)}")
    
    def show_container_window(self):
        """Show container management window"""
        try:
            ContainerWindow(self.root, self.db, self.refresh_stats)
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