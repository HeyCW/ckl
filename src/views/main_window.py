import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.utils.icon_cache import icon_cache

# Lazy imports - akan di-load saat dibutuhkan saja
# Ini membuat startup aplikasi jauh lebih cepat

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

        # Calculate responsive window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Use 65% of screen width and 75% of screen height (better for 1366x768)
        window_width = min(int(screen_width * 0.65), 1000)
        window_height = min(int(screen_height * 0.75), 700)

        # Minimum size for usability
        window_width = max(window_width, 800)
        window_height = max(window_height, 550)

        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg='#f0f0f0')

        # Set icon menggunakan cache system
        icon_photo = icon_cache.get_icon("assets/logo.jpg", (32, 32))
        if icon_photo:
            self.root.iconphoto(False, icon_photo)

        # Center window
        self.center_window(window_width, window_height)

        # Show window
        self.root.deiconify()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_closing)

    def center_window(self, window_width, window_height):
        """Center window on screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
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

        # Main content area (reduced padding for smaller screens)
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Sync status row - its own row with plenty of width, rather
        # than crammed into the header (which overflows the header
        # alongside the welcome text at the app's own minimum window
        # width of 800px).
        sync_row = tk.Frame(main_frame, bg='#ecf0f1')
        sync_row.pack(fill='x', pady=(0, 5))

        self.sync_btn = tk.Button(
            sync_row,
            text="🔄 Sync",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='white',
            relief='flat',
            padx=10,
            pady=3,
            command=self.manual_sync
        )
        self.sync_btn.pack(side='right')

        self.sync_status_label = tk.Label(
            sync_row,
            text="",
            font=('Arial', 10, 'bold'),
            bg='#ecf0f1'
        )
        self.sync_status_label.pack(side='right', padx=(0, 10))
        self.update_sync_status_label()

        # Title
        title_label = tk.Label(
            main_frame,
            text="📊 PILIH MENU",
            font=('Arial', 20, 'bold'),  # Slightly smaller font for compact layout
            fg='#2c3e50',
            bg='#ecf0f1'
        )
        title_label.pack(pady=(0, 20))  # Restore breathing room

        # Content container with proper spacing
        content_frame = tk.Frame(main_frame, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Menu buttons container
        menu_frame = tk.Frame(content_frame, bg='#ecf0f1')
        menu_frame.pack(pady=10)

        # Row 1: Customer and Barang
        row1_frame = tk.Frame(menu_frame, bg='#ecf0f1')
        row1_frame.pack(pady=12)
        
        
        # Customer button (more compact for smaller screens)
        customer_btn = tk.Button(
            row1_frame,
            text="👥\nDATA CUSTOMER\nTambah & Lihat Customer",
            font=('Arial', 12, 'bold'),  # Slightly smaller font
            bg='#3498db',
            fg='white',
            relief='flat',
            width=20,  # Slightly narrower
            height=6,  # Reduced height
            command=self.show_customer_window
        )
        customer_btn.pack(side='left', padx=15)  # Reduced horizontal spacing

        # Barang button
        barang_btn = tk.Button(
            row1_frame,
            text="📦\nDATA BARANG\nTambah & Lihat Barang",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_barang_window
        )
        barang_btn.pack(side='left', padx=15)

        kapal_btn = tk.Button(
            row1_frame,
            text="🚢\nDATA KAPAL\nTambah & Lihat Kapal",
            font=('Arial', 12, 'bold'),
            bg="#e62222",
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_kapal_window
        )
        kapal_btn.pack(side='left', padx=15)
        
        # Row 2: Container, Job Order, Customer Orders
        row2_frame = tk.Frame(menu_frame, bg='#ecf0f1')
        row2_frame.pack(pady=12)

        # Container button
        container_btn = tk.Button(
            row2_frame,
            text="🚢\nDATA CONTAINER\nTambah & Lihat Container",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_container_window
        )
        container_btn.pack(side='left', padx=15)

        # Job Order button
        job_order_btn = tk.Button(
            row2_frame,
            text="📋\nDATA JOB ORDER\nLihat Job Order",
            font=('Arial', 12, 'bold'),
            bg="#8813dc",
            fg='white',
            relief='flat',
            width=20,
            height=6,
            command=self.show_job_order_window
        )
        job_order_btn.pack(side='left', padx=15)

        # Row 3: Lifting button (only for owner)
        if self.is_owner():
            row3_frame = tk.Frame(menu_frame, bg='#ecf0f1')
            row3_frame.pack(pady=12)

            lifting_btn = tk.Button(
                row3_frame,
                text="🚧\nDATA LIFTING\nTambah & Lihat Lifting",
                font=('Arial', 12, 'bold'),
                bg="#f39c12",
                fg='white',
                relief='flat',
                width=20,
                height=6,
                command=self.show_lifting_window
            )
            lifting_btn.pack(side='left', padx=15)
    
    def show_customer_window(self):
        """Show customer management window"""
        try:
            from src.views.customer_window import CustomerWindow
            CustomerWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window customer:\n{str(e)}", parent=self.root)

    def show_lifting_window(self):
        """Show lifting management window - OWNER ONLY"""
        # Double check: Validasi role sebelum buka window
        if not self.is_owner():
            messagebox.showwarning(
                "Akses Ditolak",
                "⚠️ Maaf, menu Data Lifting hanya dapat diakses oleh Owner atau Admin.\n\n"
                "Silakan hubungi administrator untuk mendapatkan akses.",
                parent=self.root)
            return

        try:
            from src.views.lifting_window import LiftingWindow
            LiftingWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window lifting:\n{str(e)}", parent=self.root)
    
    def show_job_order_window(self):
        """Show job order management window"""
        try:
            from src.views.job_order_window import JobOrderWindow
            JobOrderWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window job order:\n{str(e)}", parent=self.root)

    def show_barang_window(self):
        """Show barang management window"""
        try:
            from src.views.barang_window import BarangWindow
            BarangWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window barang:\n{str(e)}", parent=self.root)

    def show_kapal_window(self):
        """Show kapal management window"""
        try:
            from src.views.kapal_window import KapalWindow
            KapalWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window kapal:\n{str(e)}", parent=self.root)

    def show_container_window(self):
        """Show container management window"""
        try:
            from src.views.container_window import ContainerWindow
            ContainerWindow(self.root, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka window container:\n{str(e)}", parent=self.root)

    def on_window_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Konfirmasi", "Yakin ingin keluar dari aplikasi?", parent=self.root):
            self.root.quit()

    def refresh_sync_status_text(self):
        """Update the online/offline + pending-changes label text.
        Reads local state only (no network call) - safe to call often."""
        if not hasattr(self, 'sync_status_label') or not self.sync_status_label.winfo_exists():
            return
        try:
            status = self.db.get_sync_status()
        except Exception:
            return
        if status['online']:
            self.sync_status_label.config(text="🟢 Online", fg='#2ecc71')
        else:
            pending = status['pending_changes']
            suffix = f" ({pending} belum sync)" if pending else ""
            self.sync_status_label.config(text=f"🔴 Offline{suffix}", fg='#e74c3c')

    def update_sync_status_label(self):
        """Refresh the label, then reschedule itself. Only call this
        once to start the periodic refresh loop - use
        refresh_sync_status_text() for a one-off update (e.g. right
        after a manual sync), or this would stack duplicate timers.
        """
        self.refresh_sync_status_text()
        self.root.after(15000, self.update_sync_status_label)

    def manual_sync(self):
        """Sync button: push pending offline changes, refresh the mirror."""
        self.sync_btn.config(state='disabled', text="🔄 Syncing...")
        self.root.update_idletasks()
        try:
            result = self.db.sync_now()
        except Exception as e:
            result = None
            messagebox.showerror("Sync Gagal", f"Terjadi kesalahan saat sync:\n{e}", parent=self.root)
        finally:
            self.sync_btn.config(state='normal', text="🔄 Sync")

        # Update the indicator before the dialog, not after - it's a
        # blocking modal, so anything after it wouldn't run until the
        # user dismisses it, leaving the indicator stale behind the dialog.
        self.refresh_sync_status_text()

        if result is not None:
            if result.ok:
                messagebox.showinfo(
                    "Sync Selesai",
                    f"Berhasil sync!\nDikirim: {result.pushed} perubahan\nDiperbarui: {result.pulled} data",
                    parent=self.root
                )
            else:
                messagebox.showwarning(
                    "Masih Offline",
                    f"Tidak bisa terhubung ke server:\n{result.reason}",
                    parent=self.root
                )

# Usage example
if __name__ == "__main__":
    root = tk.Tk()
    
    # Contoh user yang login
    # current_user = {'username': 'admin', 'role': 'owner'}  # Owner bisa akses
    # current_user = {'username': 'user1', 'role': 'user'}   # User biasa tidak bisa
    
    current_user = {'username': 'admin', 'role': 'owner'}
    
    app = MainWindow(root, current_user=current_user)
    root.mainloop()
