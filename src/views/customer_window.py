import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from src.models.database import AppDatabase

class CustomerWindow:
    def __init__(self, parent, db, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.create_window()
    
    def create_window(self):
        """Create customer management window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("📋 Data Customer")
        self.window.geometry("1000x750")
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
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tab 1: Manual Input
        manual_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(manual_frame, text='✍️ Input Manual')
        self.create_manual_tab(manual_frame)
        
        # Tab 2: Excel Upload
        excel_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(excel_frame, text='📊 Upload Excel')
        self.create_excel_tab(excel_frame)
        
        # Tab 3: Customer List
        list_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(list_frame, text='📋 Daftar Customer')
        self.create_list_tab(list_frame)
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="❌ Tutup",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=10,
            command=self.window.destroy
        )
        close_btn.pack(pady=10)
    
    def create_manual_tab(self, parent):
        """Create manual input tab"""
        # Form frame
        form_frame = tk.Frame(parent, bg='#ecf0f1')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Instructions
        instruction_label = tk.Label(
            form_frame,
            text="📝 Tambah Customer Satu per Satu",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1'
        )
        instruction_label.pack(pady=(0, 20))
        
        # Name field
        tk.Label(form_frame, text="Nama Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.name_entry = tk.Entry(form_frame, font=('Arial', 12), width=50)
        self.name_entry.pack(fill='x', pady=(5, 10))
        
        # Address field
        tk.Label(form_frame, text="Alamat Customer:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        self.address_entry = tk.Text(form_frame, font=('Arial', 12), height=4, width=50)
        self.address_entry.pack(fill='x', pady=(5, 10))
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=20)
        
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
        clear_btn.pack(side='left')
        
        # Focus on name entry
        self.name_entry.focus()
    
    def create_excel_tab(self, parent):
        """Create Excel upload tab"""
        # Main container
        main_container = tk.Frame(parent, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Instructions
        instruction_frame = tk.Frame(main_container, bg='#ffffff', relief='solid', bd=1)
        instruction_frame.pack(fill='x', pady=(0, 20))
        
        instruction_title = tk.Label(
            instruction_frame,
            text="📊 Upload Data Customer dari Excel",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50',
            bg='#ffffff'
        )
        instruction_title.pack(pady=(10, 5))
        
        instruction_text = tk.Label(
            instruction_frame,
            text="Format Excel yang dibutuhkan:\n\n" +
                 "Kolom A: Nama Customer\n" +
                 "Kolom B: Alamat Customer\n\n" +
                 "Pastikan baris pertama adalah header (Nama, Alamat)",
            font=('Arial', 10),
            fg='#34495e',
            bg='#ffffff',
            justify='left'
        )
        instruction_text.pack(pady=(0, 10), padx=20)
        
        # File selection
        file_frame = tk.Frame(main_container, bg='#ecf0f1')
        file_frame.pack(fill='x', pady=10)
        
        tk.Label(file_frame, text="Pilih File Excel:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        file_input_frame = tk.Frame(file_frame, bg='#ecf0f1')
        file_input_frame.pack(fill='x', pady=(5, 0))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_input_frame, textvariable=self.file_path_var, font=('Arial', 11), state='readonly')
        self.file_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        browse_btn = tk.Button(
            file_input_frame,
            text="📁 Browse",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            command=self.browse_file
        )
        browse_btn.pack(side='right', padx=(5, 0))
        
        # Preview area - reduced height to make room for buttons
        preview_frame = tk.Frame(main_container, bg='#ecf0f1')
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(preview_frame, text="📋 Preview Data:", font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(anchor='w')
        
        # Preview treeview with fixed height
        preview_tree_frame = tk.Frame(preview_frame, bg='#ecf0f1')
        preview_tree_frame.pack(fill='x', pady=5)
        
        self.preview_tree = ttk.Treeview(preview_tree_frame, columns=('Nama', 'Alamat'), show='headings', height=8)
        self.preview_tree.heading('Nama', text='Nama Customer')
        self.preview_tree.heading('Alamat', text='Alamat')
        self.preview_tree.column('Nama', width=250)
        self.preview_tree.column('Alamat', width=350)
        
        preview_scrollbar = ttk.Scrollbar(preview_tree_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side='left', fill='x', expand=True)
        preview_scrollbar.pack(side='right', fill='y')
        
        # Upload buttons - ensure they're always visible
        upload_btn_frame = tk.Frame(main_container, bg='#ecf0f1')
        upload_btn_frame.pack(fill='x', pady=15)
        
        # Make buttons larger and more visible
        self.upload_btn = tk.Button(
            upload_btn_frame,
            text="⬆️ Upload ke Database",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=15,
            command=self.upload_excel_data,
            state='disabled'
        )
        self.upload_btn.pack(side='left', padx=(0, 15))
        
        download_template_btn = tk.Button(
            upload_btn_frame,
            text="📥 Download Template",
            font=('Arial', 14, 'bold'),
            bg='#f39c12',
            fg='white',
            padx=30,
            pady=15,
            command=self.download_template
        )
        download_template_btn.pack(side='left')
        
        # Status label with better spacing
        self.status_label = tk.Label(
            main_container,
            text="",
            font=('Arial', 11),
            fg='#e74c3c',
            bg='#ecf0f1',
            wraplength=800,
            justify='left'
        )
        self.status_label.pack(pady=10, fill='x')
    
    def create_list_tab(self, parent):
        """Create customer list tab"""
        # Container
        list_container = tk.Frame(parent, bg='#ecf0f1')
        list_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(list_container, bg='#ecf0f1')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="📋 DAFTAR CUSTOMER", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(side='left')
        
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            command=self.load_customers
        )
        refresh_btn.pack(side='right')
        
        # Treeview for customer list
        tree_frame = tk.Frame(list_container, bg='#ecf0f1')
        tree_frame.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Nama', 'Alamat', 'Created'), show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nama', text='Nama Customer')
        self.tree.heading('Alamat', text='Alamat')
        self.tree.heading('Created', text='Tanggal Dibuat')
        
        self.tree.column('ID', width=50)
        self.tree.column('Nama', width=200)
        self.tree.column('Alamat', width=300)
        self.tree.column('Created', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load existing customers
        self.load_customers()
        
        # Add tab change event to refresh data when switching to this tab
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (1000 // 2)
        y = parent_y + (parent_height // 2) - (750 // 2)
        
        self.window.geometry(f"1000x750+{x}+{y}")
    
    def browse_file(self):
        """Browse for Excel file"""
        file_types = [
            ('Excel files', '*.xlsx *.xls'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Pilih File Excel",
            filetypes=file_types,
            parent=self.window
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.preview_excel_file(filename)
    
    def preview_excel_file(self, filename):
        """Preview Excel file content"""
        try:
            self.status_label.config(text="📄 Membaca file Excel...", fg='#3498db')
            
            # Clear previous preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Check file exists
            if not os.path.exists(filename):
                self.status_label.config(
                    text="❌ File tidak ditemukan!", 
                    fg='#e74c3c'
                )
                self.upload_btn.config(state='disabled')
                return
            
            # Try to read Excel file with different engines
            df = None
            try:
                # Try with openpyxl first (for .xlsx)
                df = pd.read_excel(filename, engine='openpyxl')
            except:
                try:
                    # Try with xlrd (for .xls)
                    df = pd.read_excel(filename, engine='xlrd')
                except Exception as e:
                    self.status_label.config(
                        text=f"❌ Error membaca Excel: {str(e)}\n\nPastikan file Excel tidak sedang dibuka di aplikasi lain!", 
                        fg='#e74c3c'
                    )
                    self.upload_btn.config(state='disabled')
                    return
            
            # Check if DataFrame is empty
            if df is None or df.empty:
                self.status_label.config(
                    text="❌ File Excel kosong atau tidak valid!", 
                    fg='#e74c3c'
                )
                self.upload_btn.config(state='disabled')
                return
            
            # Print columns for debugging
            print(f"Kolom yang ditemukan: {list(df.columns)}")
            
            # Check if required columns exist (case insensitive)
            df.columns = df.columns.str.strip()  # Remove whitespace
            
            # Try to find Nama column (case insensitive)
            nama_col = None
            alamat_col = None
            
            for col in df.columns:
                if col.lower().strip() in ['nama', 'name', 'nama customer', 'customer']:
                    nama_col = col
                elif col.lower().strip() in ['alamat', 'address', 'alamat customer']:
                    alamat_col = col
            
            if nama_col is None:
                available_cols = ', '.join(df.columns.tolist())
                self.status_label.config(
                    text=f"❌ Kolom 'Nama' tidak ditemukan!\n\nKolom yang tersedia: {available_cols}\n\nPastikan ada kolom 'Nama'", 
                    fg='#e74c3c'
                )
                self.upload_btn.config(state='disabled')
                return
            
            # Set default alamat column if not found
            if alamat_col is None:
                if len(df.columns) > 1:
                    alamat_col = df.columns[1]  # Use second column as address
                else:
                    alamat_col = 'Alamat'  # Create dummy column
                    df[alamat_col] = ''
            
            # Filter out rows with empty names
            valid_rows = df[df[nama_col].notna() & (df[nama_col].astype(str).str.strip() != '')]
            
            if len(valid_rows) == 0:
                self.status_label.config(
                    text="❌ Tidak ada data valid! Pastikan kolom 'Nama' tidak kosong.", 
                    fg='#e74c3c'
                )
                self.upload_btn.config(state='disabled')
                return
            
            # Preview first 100 rows
            preview_data = valid_rows.head(100)
            row_count = len(valid_rows)
            
            for _, row in preview_data.iterrows():
                nama = str(row[nama_col]).strip() if pd.notna(row[nama_col]) else ''
                alamat = str(row[alamat_col]).strip() if pd.notna(row[alamat_col]) else ''
                
                if nama:  # Only show rows with name
                    self.preview_tree.insert('', tk.END, values=(nama, alamat))
            
            # Store column names for upload
            self.nama_column = nama_col
            self.alamat_column = alamat_col
            
            self.status_label.config(
                text=f"✅ File berhasil dibaca: {row_count} baris data valid\n📋 Kolom: {nama_col}, {alamat_col}", 
                fg='#27ae60'
            )
            self.upload_btn.config(state='normal')
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error detail: {error_detail}")
            
            self.status_label.config(
                text=f"❌ Error membaca file: {str(e)}\n\nTips:\n• Pastikan file Excel tidak sedang dibuka\n• Cek format kolom (Nama, Alamat)\n• Coba download template terlebih dahulu", 
                fg='#e74c3c'
            )
            self.upload_btn.config(state='disabled')
    
    def upload_excel_data(self):
        """Upload Excel data to database"""
        filename = self.file_path_var.get()
        if not filename:
            messagebox.showerror("Error", "Pilih file Excel terlebih dahulu!")
            return
        
        try:
            print(f"🔄 Starting upload from file: {filename}")
            
            # Read Excel file with stored column names
            df = pd.read_excel(filename)
            print(f"📊 Excel loaded with {len(df)} rows")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Use stored column names from preview
            nama_col = getattr(self, 'nama_column', 'Nama')
            alamat_col = getattr(self, 'alamat_column', 'Alamat')
            print(f"🏷️ Using columns: {nama_col}, {alamat_col}")
            
            # Validate data
            if nama_col not in df.columns:
                messagebox.showerror("Error", f"Kolom '{nama_col}' tidak ditemukan!")
                return
            
            # Filter out empty names
            original_count = len(df)
            df = df[df[nama_col].notna() & (df[nama_col].astype(str).str.strip() != '')]
            valid_count = len(df)
            
            print(f"📊 Original rows: {original_count}, Valid rows: {valid_count}")
            
            if len(df) == 0:
                messagebox.showerror("Error", "Tidak ada data valid untuk diupload!")
                return
            
            # Confirm upload
            if not messagebox.askyesno(
                "Konfirmasi", 
                f"Upload {len(df)} customer ke database?\n\nData yang sudah ada tidak akan terduplikasi."
            ):
                print("❌ Upload cancelled by user")
                return
            
            print("🚀 Starting database upload...")
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.window)
            progress_window.title("Upload Progress")
            progress_window.geometry("400x200")
            progress_window.transient(self.window)
            progress_window.grab_set()
            
            # Center progress window
            progress_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (400 // 2)
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (200 // 2)
            progress_window.geometry(f"400x200+{x}+{y}")
            
            progress_label = tk.Label(progress_window, text="Memulai upload...", font=('Arial', 12))
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            progress_bar['maximum'] = len(df)
            
            detail_label = tk.Label(progress_window, text="", font=('Arial', 10), fg='#666')
            detail_label.pack(pady=5)
            
            # Upload data
            success_count = 0
            error_count = 0
            duplicate_count = 0
            
            print(f"📝 Processing {len(df)} rows...")
            
            for idx, (_, row) in enumerate(df.iterrows()):
                try:
                    nama = str(row[nama_col]).strip()
                    alamat = str(row[alamat_col]).strip() if alamat_col in df.columns and pd.notna(row[alamat_col]) else ''
                    
                    print(f"📋 Row {idx+1}: Processing '{nama}' - '{alamat}'")
                    
                    if nama:
                        # Check if customer already exists
                        existing = self.db.execute_one(
                            "SELECT customer_id FROM customers WHERE nama_customer = ?",
                            (nama,)
                        )
                        
                        if not existing:
                            print(f"➕ Creating new customer: {nama}")
                            customer_id = self.db.create_customer(nama, alamat)
                            print(f"✅ Customer created with ID: {customer_id}")
                            success_count += 1
                        else:
                            print(f"⚠️ Customer '{nama}' already exists, skipping")
                            duplicate_count += 1
                    else:
                        print(f"❌ Empty name at row {idx+1}, skipping")
                
                except Exception as e:
                    print(f"💥 Error adding customer '{nama}': {str(e)}")
                    import traceback
                    traceback.print_exc()
                    error_count += 1
                
                # Update progress
                progress_bar['value'] = idx + 1
                progress_label.config(text=f"Processing {idx + 1} of {len(df)}")
                detail_label.config(text=f"{nama[:40]}...")
                progress_window.update()
            
            # Close progress window
            progress_window.destroy()
            
            print(f"🏁 Upload completed!")
            print(f"✅ Success: {success_count}")
            print(f"⚠️ Duplicates: {duplicate_count}")
            print(f"❌ Errors: {error_count}")
            
            # Show results
            messagebox.showinfo(
                "Upload Selesai", 
                f"Upload selesai!\n\n" +
                f"✅ Berhasil: {success_count} customer\n" +
                f"⚠️ Duplikat dilewati: {duplicate_count} customer\n" +
                f"❌ Error: {error_count} customer"
            )
            
            # Force refresh main dashboard stats
            if self.refresh_callback:
                print("🔄 Calling refresh callback...")
                self.refresh_callback()
            
            # Refresh customer list and switch to list tab
            print("🔄 Refreshing customer list...")
            self.load_customers()
            
            # Switch to customer list tab to show results
            print("📋 Switching to customer list tab...")
            self.notebook.select(2)  # Select third tab (index 2)
            
            # Clear file selection
            self.file_path_var.set("")
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            self.upload_btn.config(state='disabled')
            self.status_label.config(text="")
            
            print("✅ Upload process completed successfully!")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Upload error: {error_detail}")
            messagebox.showerror("Error", f"Gagal upload data:\n{str(e)}")
            
            # Close progress window if still open
            try:
                progress_window.destroy()
            except:
                pass
    
    def download_template(self):
        """Download Excel template"""
        try:
            print("📥 Creating template...")
            
            # Create sample data
            template_data = {
                'Nama': ['PT. Contoh Satu', 'PT. Contoh Dua', 'CV. Contoh Tiga'],
                'Alamat': [
                    'Jl. Contoh No. 1, Jakarta',
                    'Jl. Sample No. 2, Surabaya', 
                    'Jl. Example No. 3, Bandung'
                ]
            }
            
            df = pd.DataFrame(template_data)
            print("✅ Template data created")
            
            # Save file with correct parameters
            filename = filedialog.asksaveasfilename(
                parent=self.window,
                title="Simpan Template Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile="template_customer.xlsx"  # ✅ initialfile bukan initialname
            )
            
            if filename:
                print(f"💾 Saving template to: {filename}")
                
                # Ensure directory exists
                directory = os.path.dirname(filename)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                
                # Save Excel file
                df.to_excel(filename, index=False, engine='openpyxl')
                print("✅ Template saved successfully")
                
                messagebox.showinfo("Sukses", f"Template berhasil disimpan:\n{filename}")
            else:
                print("❌ Save cancelled by user")
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"💥 Template download error: {error_detail}")
            
            messagebox.showerror("Error", f"Gagal membuat template:\n\nError: {str(e)}\n\nPastikan pandas dan openpyxl terinstall:\npip install pandas openpyxl")
    
    def add_customer(self):
        """Add new customer manually"""
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
            
            # Refresh customer list and switch to list tab
            self.load_customers()
            if self.refresh_callback:
                self.refresh_callback()
            
            # Switch to customer list tab to show the new customer
            self.notebook.select(2)  # Select third tab (index 2)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan customer: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(1.0, tk.END)
        self.name_entry.focus()
    
    def load_customers(self):
        """Load customers into treeview"""
        try:
            print("🔄 Loading customers from database...")
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load customers from database
            customers = self.db.get_all_customers()
            print(f"📊 Found {len(customers)} customers in database")
            
            for customer in customers:
                # Format date
                created_date = customer.get('created_at', '')[:10] if customer.get('created_at') else '-'
                
                self.tree.insert('', tk.END, values=(
                    customer['customer_id'],
                    customer['nama_customer'],
                    customer['alamat_customer'] or '-',
                    created_date
                ))
                print(f"📋 Loaded: {customer['customer_id']} - {customer['nama_customer']}")
            
            print("✅ Customer list loaded successfully")
            
        except Exception as e:
            print(f"💥 Error loading customers: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Gagal memuat daftar customer: {str(e)}")
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # If switching to customer list tab, refresh the data
        if "Daftar Customer" in tab_text:
            self.load_customers()
            print("Tab changed to Customer List - data refreshed")