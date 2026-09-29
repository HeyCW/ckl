import tkinter as tk
from tkinter import ttk, messagebox
from src.models.database import AppDatabase
from src.widget.paginated_tree_view import PaginatedTreeView
from src.utils.helpers import setup_window_restore_behavior, safe_error_message

# Roles the app actually recognizes. Only 'owner' unlocks the owner-only
# menus (see MainWindow.is_owner); the rest are equivalent today, but are
# kept distinct so existing accounts keep their label.
ROLES = ('owner', 'admin', 'staff')

# Matches the minimum enforced by UserDatabase.create_user /
# update_user_password - checked here too so the user gets a form-level
# message instead of a database exception.
MIN_PASSWORD_LENGTH = 6


class UserWindow:
    """Owner-only account management: create accounts, set/reset their
    passwords, and deactivate ones that shouldn't log in anymore.

    Passwords are never read back out of the database (they're stored as
    bcrypt hashes), so this window can only ever set a new one - it can't
    show what an existing password is.
    """

    def __init__(self, parent, db: AppDatabase, current_user=None):
        self.parent = parent
        self.db = db
        self.current_user = current_user or {}
        self.users_by_id = {}
        self.list_tab_loaded = False
        self.create_window()

    def get_scale_factor(self):
        """Calculate scale factor based on screen size"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        width_scale = screen_width / 1600
        height_scale = screen_height / 900

        scale = (width_scale + height_scale) / 2
        return max(0.75, min(1.3, scale))

    def scaled_font(self, base_size):
        """Return scaled font size"""
        scale = self.get_scale_factor()
        return max(8, int(base_size * scale))

    def make_button_keyboard_accessible(self, button):
        """Make button accessible via Tab and Enter keys"""
        button.config(takefocus=True)

        def on_enter_or_space(event):
            button.invoke()
            return 'break'

        button.bind('<Return>', on_enter_or_space)
        button.bind('<space>', on_enter_or_space)
        return button

    def create_window(self):
        """Create user management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("👤 Kelola User")
        self.window.configure(bg='#ecf0f1')

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_width = min(int(screen_width * 0.7), 1100)
        window_height = min(int(screen_height * 0.8), 750)
        self.window.geometry(f"{window_width}x{window_height}")

        setup_window_restore_behavior(self.window)

        self.window.minsize(780, 500)
        self.window.resizable(True, True)
        self.center_window()

        header = tk.Label(
            self.window,
            text="👤 KELOLA USER APLIKASI",
            font=('Arial', self.scaled_font(18), 'bold'),
            bg='#8e44ad',
            fg='white',
            pady=15
        )
        header.pack(fill='x')

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        add_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(add_frame, text='➕ Tambah User')
        self.create_add_tab(add_frame)

        list_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(list_frame, text='📋 Daftar User')
        self.create_list_tab(list_frame)

        close_btn = tk.Button(
            self.window,
            text="❌ Tutup",
            font=('Arial', self.scaled_font(12), 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=5,
            command=self.window.destroy
        )
        self.make_button_keyboard_accessible(close_btn)
        close_btn.pack(pady=(0, 20))

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)

        self.window.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    # ------------------------------------------------------------------
    # Tab 1: create a new account
    # ------------------------------------------------------------------

    def create_add_tab(self, parent):
        """Create the new-account form"""
        form_frame = tk.Frame(parent, bg='#ecf0f1')
        form_frame.pack(fill='both', expand=True, padx=30, pady=20)

        tk.Label(
            form_frame,
            text="📝 Buat Akun Baru",
            font=('Arial', self.scaled_font(14), 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        ).pack(pady=(0, 20))

        tk.Label(form_frame, text="Username:", font=('Arial', self.scaled_font(12), 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.username_entry = tk.Entry(form_frame, font=('Arial', self.scaled_font(12)))
        self.username_entry.pack(fill='x', pady=(5, 10))

        tk.Label(form_frame, text="Password:", font=('Arial', self.scaled_font(12), 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.password_entry = tk.Entry(form_frame, font=('Arial', self.scaled_font(12)), show='•')
        self.password_entry.pack(fill='x', pady=(5, 10))

        tk.Label(form_frame, text="Konfirmasi Password:", font=('Arial', self.scaled_font(12), 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.confirm_entry = tk.Entry(form_frame, font=('Arial', self.scaled_font(12)), show='•')
        self.confirm_entry.pack(fill='x', pady=(5, 5))

        self.show_password_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            form_frame,
            text="Tampilkan password",
            variable=self.show_password_var,
            font=('Arial', self.scaled_font(10)),
            bg='#ecf0f1',
            activebackground='#ecf0f1',
            command=self.toggle_password_visibility
        ).pack(anchor='w', pady=(0, 10))

        tk.Label(form_frame, text="Email (opsional):", font=('Arial', self.scaled_font(12), 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.email_entry = tk.Entry(form_frame, font=('Arial', self.scaled_font(12)))
        self.email_entry.pack(fill='x', pady=(5, 10))

        tk.Label(form_frame, text="Role:", font=('Arial', self.scaled_font(12), 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.role_var = tk.StringVar(value='staff')
        role_combo = ttk.Combobox(
            form_frame,
            textvariable=self.role_var,
            values=list(ROLES),
            state='readonly',
            font=('Arial', self.scaled_font(12))
        )
        role_combo.pack(fill='x', pady=(5, 10))

        tk.Label(
            form_frame,
            text=(
                f"💡 Password minimal {MIN_PASSWORD_LENGTH} karakter. "
                "Role 'owner' bisa membuka menu Data Lifting & Kelola User."
            ),
            font=('Arial', self.scaled_font(9)),
            fg='#7f8c8d',
            bg='#ecf0f1',
            wraplength=600,
            justify='left'
        ).pack(anchor='w', pady=(0, 10))

        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=10)

        add_btn = tk.Button(
            btn_frame,
            text="➕ Buat Akun",
            font=('Arial', self.scaled_font(12), 'bold'),
            bg='#27ae60',
            fg='white',
            padx=10,
            pady=5,
            command=self.add_user
        )
        self.make_button_keyboard_accessible(add_btn)
        add_btn.pack(side='left', padx=(0, 10))

        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Bersihkan",
            font=('Arial', self.scaled_font(12), 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=10,
            pady=5,
            command=self.clear_form
        )
        self.make_button_keyboard_accessible(clear_btn)
        clear_btn.pack(side='left')

        self.username_entry.focus()

    def toggle_password_visibility(self):
        """Show/hide both password fields on the create form"""
        show = '' if self.show_password_var.get() else '•'
        self.password_entry.config(show=show)
        self.confirm_entry.config(show=show)

    def add_user(self):
        """Validate the form and create the account"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        email = self.email_entry.get().strip()
        role = self.role_var.get().strip().lower()

        if not username:
            messagebox.showerror("Error", "Username harus diisi!", parent=self.window)
            self.username_entry.focus()
            return

        if ' ' in username:
            messagebox.showerror("Error", "Username tidak boleh mengandung spasi!", parent=self.window)
            self.username_entry.focus()
            return

        if len(password) < MIN_PASSWORD_LENGTH:
            messagebox.showerror(
                "Error",
                f"Password minimal {MIN_PASSWORD_LENGTH} karakter!",
                parent=self.window
            )
            self.password_entry.focus()
            return

        if password != confirm:
            messagebox.showerror("Error", "Password dan konfirmasi tidak sama!", parent=self.window)
            self.confirm_entry.focus()
            return

        if role not in ROLES:
            messagebox.showerror("Error", f"Role tidak valid: {role}", parent=self.window)
            return

        try:
            user_id = self.db.create_user(username, password, email or None, role)
            messagebox.showinfo(
                "Sukses",
                f"Akun '{username}' ({role}) berhasil dibuat dengan ID: {user_id}",
                parent=self.window
            )
            self.clear_form()

            self.list_tab_loaded = False
            if hasattr(self, 'tree'):
                self.load_users()

        except ValueError as ve:
            messagebox.showerror("Error Validasi", str(ve), parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat akun:\n{safe_error_message(e)}", parent=self.window)

    def clear_form(self):
        """Clear the create-account form"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.role_var.set('staff')
        self.username_entry.focus()

    # ------------------------------------------------------------------
    # Tab 2: existing accounts
    # ------------------------------------------------------------------

    def create_list_tab(self, parent):
        """Create the existing-accounts list"""
        list_container = tk.Frame(parent, bg='#ecf0f1')
        list_container.pack(fill='both', expand=True, padx=20, pady=20)

        header_frame = tk.Frame(list_container, bg='#ecf0f1')
        header_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            header_frame,
            text="📋 DAFTAR USER",
            font=('Arial', self.scaled_font(14), 'bold'),
            bg='#ecf0f1'
        ).pack(side='left')

        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            font=('Arial', self.scaled_font(10)),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            command=self.load_users
        )
        self.make_button_keyboard_accessible(refresh_btn)
        refresh_btn.pack(side='right')

        action_frame = tk.Frame(list_container, bg='#ecf0f1')
        action_frame.pack(fill='x', pady=(0, 10))

        reset_btn = tk.Button(
            action_frame,
            text="🔑 Ganti Password",
            font=('Arial', self.scaled_font(11), 'bold'),
            bg='#3498db',
            fg='white',
            padx=10,
            pady=5,
            command=self.reset_password
        )
        self.make_button_keyboard_accessible(reset_btn)
        reset_btn.pack(side='left', padx=(0, 10))

        toggle_btn = tk.Button(
            action_frame,
            text="🚫 Aktif / Nonaktif",
            font=('Arial', self.scaled_font(11), 'bold'),
            bg='#e67e22',
            fg='white',
            padx=10,
            pady=5,
            command=self.toggle_active
        )
        self.make_button_keyboard_accessible(toggle_btn)
        toggle_btn.pack(side='left')

        tk.Label(
            action_frame,
            text="💡 Pilih user dari tabel lalu klik aksi",
            font=('Arial', self.scaled_font(10)),
            fg='#7f8c8d',
            bg='#ecf0f1'
        ).pack(side='right')

        tree_container = tk.Frame(list_container, bg='#ecf0f1')
        tree_container.pack(fill='both', expand=True)

        columns = ('ID', 'Username', 'Email', 'Role', 'Status', 'LastLogin')

        self.tree = PaginatedTreeView(
            parent=tree_container,
            columns=columns,
            show='headings',
            height=12,
            items_per_page=15,
            selectmode='browse'
        )

        self.tree.heading('ID', text='ID')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Role', text='Role')
        self.tree.heading('Status', text='Status')
        self.tree.heading('LastLogin', text='Login Terakhir')

        self.tree.column('ID', width=60)
        self.tree.column('Username', width=180)
        self.tree.column('Email', width=220)
        self.tree.column('Role', width=110)
        self.tree.column('Status', width=110)
        self.tree.column('LastLogin', width=160)

        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', lambda e: self.reset_password())

    def load_users(self):
        """Load accounts into the tree.

        Only the non-secret columns are put into the view - the row also
        carries the bcrypt password hash, which has no business being
        rendered on screen.
        """
        try:
            users = self.db.get_all_users()
            self.users_by_id = {str(user['id']): user for user in users}

            formatted_data = []
            for user in users:
                last_login = str(user.get('last_login') or '')[:16] or '-'
                status = '✅ Aktif' if user.get('is_active') else '🚫 Nonaktif'

                formatted_data.append({
                    'iid': str(user['id']),
                    'values': (
                        user['id'],
                        user['username'],
                        user.get('email') or '-',
                        (user.get('role') or '-').lower(),
                        status,
                        last_login,
                    )
                })

            self.tree.set_data(formatted_data)
            self.list_tab_loaded = True

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat daftar user:\n{safe_error_message(e)}", parent=self.window)

    def get_selected_user(self):
        """Return the selected user dict, or None (with a prompt shown)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Perhatian", "Pilih user terlebih dahulu!", parent=self.window)
            return None

        user = self.users_by_id.get(str(selection[0]))
        if not user:
            messagebox.showerror("Error", "Data user tidak ditemukan, coba refresh.", parent=self.window)
            return None

        return user

    def toggle_active(self):
        """Activate or deactivate the selected account"""
        user = self.get_selected_user()
        if not user:
            return

        username = user['username']
        is_active = bool(user.get('is_active'))

        # An owner who deactivates their own account is locked out on the
        # next login, with nobody left holding the menu that undoes it.
        if is_active and username == self.current_user.get('username'):
            messagebox.showerror(
                "Tidak Diizinkan",
                "Anda tidak bisa menonaktifkan akun Anda sendiri.",
                parent=self.window
            )
            return

        action = "menonaktifkan" if is_active else "mengaktifkan"
        done_label = "dinonaktifkan" if is_active else "diaktifkan"

        if not messagebox.askyesno(
            "Konfirmasi",
            f"Yakin ingin {action} akun '{username}'?",
            parent=self.window
        ):
            return

        try:
            if is_active:
                self.db.deactivate_user(username)
            else:
                self.db.activate_user(username)

            messagebox.showinfo("Sukses", f"Akun '{username}' berhasil {done_label}.", parent=self.window)
            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal {action} akun:\n{safe_error_message(e)}", parent=self.window)

    def reset_password(self):
        """Open the set-new-password dialog for the selected account"""
        user = self.get_selected_user()
        if not user:
            return

        username = user['username']

        dialog = tk.Toplevel(self.window)
        dialog.title(f"🔑 Ganti Password - {username}")
        dialog.configure(bg='#ecf0f1')
        dialog.transient(self.window)
        dialog.resizable(False, False)

        dialog_width, dialog_height = 460, 340
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (dialog_width // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{max(0, x)}+{max(0, y)}")
        dialog.lift()
        dialog.focus_force()

        tk.Label(
            dialog,
            text="🔑 GANTI PASSWORD",
            font=('Arial', self.scaled_font(15), 'bold'),
            bg='#3498db',
            fg='white',
            pady=12
        ).pack(fill='x')

        form = tk.Frame(dialog, bg='#ecf0f1')
        form.pack(fill='both', expand=True, padx=25, pady=20)

        tk.Label(
            form,
            text=f"Akun: {username} ({(user.get('role') or '-').lower()})",
            font=('Arial', self.scaled_font(11), 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        ).pack(anchor='w', pady=(0, 15))

        tk.Label(form, text="Password Baru:", font=('Arial', self.scaled_font(11), 'bold'), bg='#ecf0f1').pack(anchor='w')
        new_entry = tk.Entry(form, font=('Arial', self.scaled_font(11)), show='•')
        new_entry.pack(fill='x', pady=(5, 10))

        tk.Label(form, text="Konfirmasi Password Baru:", font=('Arial', self.scaled_font(11), 'bold'), bg='#ecf0f1').pack(anchor='w')
        confirm_entry = tk.Entry(form, font=('Arial', self.scaled_font(11)), show='•')
        confirm_entry.pack(fill='x', pady=(5, 5))

        show_var = tk.BooleanVar(value=False)

        def toggle_show():
            show = '' if show_var.get() else '•'
            new_entry.config(show=show)
            confirm_entry.config(show=show)

        tk.Checkbutton(
            form,
            text="Tampilkan password",
            variable=show_var,
            font=('Arial', self.scaled_font(9)),
            bg='#ecf0f1',
            activebackground='#ecf0f1',
            command=toggle_show
        ).pack(anchor='w', pady=(0, 10))

        def on_save():
            new_password = new_entry.get()
            confirm = confirm_entry.get()

            if len(new_password) < MIN_PASSWORD_LENGTH:
                messagebox.showerror(
                    "Error",
                    f"Password minimal {MIN_PASSWORD_LENGTH} karakter!",
                    parent=dialog
                )
                new_entry.focus()
                return

            if new_password != confirm:
                messagebox.showerror("Error", "Password dan konfirmasi tidak sama!", parent=dialog)
                confirm_entry.focus()
                return

            try:
                self.db.update_user_password(username, new_password)
                messagebox.showinfo(
                    "Sukses",
                    f"Password akun '{username}' berhasil diganti.",
                    parent=self.window
                )
                dialog.destroy()
                self.load_users()

            except ValueError as ve:
                messagebox.showerror("Error Validasi", str(ve), parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengganti password:\n{safe_error_message(e)}", parent=dialog)

        btn_frame = tk.Frame(form, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=(10, 0))

        save_btn = tk.Button(
            btn_frame,
            text="💾 Simpan",
            font=('Arial', self.scaled_font(11), 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5,
            command=on_save
        )
        self.make_button_keyboard_accessible(save_btn)
        save_btn.pack(side='left', padx=(0, 10))

        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Batal",
            font=('Arial', self.scaled_font(11), 'bold'),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        self.make_button_keyboard_accessible(cancel_btn)
        cancel_btn.pack(side='left')

        new_entry.focus()

    def on_tab_changed(self, event):
        """Lazy-load the account list the first time its tab is opened"""
        try:
            selected = event.widget.index(event.widget.select())
            if selected == 1 and not self.list_tab_loaded:
                self.load_users()
        except Exception:
            pass
