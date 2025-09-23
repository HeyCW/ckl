import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from PIL import Image as PILImage, ImageTk
import io
import base64
import traceback

class DigitalSignaturePad:
    def __init__(self, parent, width=400, height=150):
        self.parent = parent
        self.width = width
        self.height = height
        self.signature_data = []
        self.current_stroke = []
        self.last_x = 0
        self.last_y = 0
        
        # Create signature canvas
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(padx=10, pady=5)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        
        # Control buttons frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(pady=5)
        
        ttk.Button(controls_frame, text="Clear", command=self.clear_signature).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Undo Last Stroke", command=self.undo_stroke).pack(side='left', padx=5)
        
    def start_draw(self, event):
        self.last_x = event.x
        self.last_y = event.y
        self.current_stroke = [(event.x, event.y)]
        
    def draw(self, event):
        # Draw line from last position to current position
        self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                               width=2, fill='black', capstyle=tk.ROUND, smooth=tk.TRUE)
        self.current_stroke.append((event.x, event.y))
        self.last_x = event.x
        self.last_y = event.y
        
    def end_draw(self, event):
        if self.current_stroke:
            self.signature_data.append(self.current_stroke)
            self.current_stroke = []
            
    def clear_signature(self):
        self.canvas.delete("all")
        self.signature_data = []
        
    def undo_stroke(self):
        if self.signature_data:
            self.signature_data.pop()
            self.redraw_signature()
            
    def redraw_signature(self):
        self.canvas.delete("all")
        for stroke in self.signature_data:
            for i in range(1, len(stroke)):
                x1, y1 = stroke[i-1]
                x2, y2 = stroke[i]
                self.canvas.create_line(x1, y1, x2, y2,
                                       width=2, fill='black', capstyle=tk.ROUND, smooth=tk.TRUE)
    
    def has_signature(self):
        return len(self.signature_data) > 0
    
    def save_signature_as_image(self):
        """Save signature as PNG image and return the file path"""
        if not self.has_signature():
            return None
            
        # Create a PIL image
        img = PILImage.new('RGB', (self.width, self.height), 'white')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw all strokes
        for stroke in self.signature_data:
            if len(stroke) > 1:
                # Convert stroke to list of coordinates for PIL
                points = []
                for point in stroke:
                    points.extend(point)
                if len(points) >= 4:  # Need at least 2 points (4 coordinates)
                    draw.line(points, fill='black', width=2)
        
        # Save to temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        temp_file.close()
        
        return temp_file.name

class SignatureDialog:
    def __init__(self, parent):
        self.signature_path = None
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Tanda Tangan untuk Packing List")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Pilih Metode Tanda Tangan", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Digital signature pad
        digital_frame = ttk.Frame(notebook)
        notebook.add(digital_frame, text="Tanda Tangan Digital")
        
        ttk.Label(digital_frame, text="Gunakan mouse untuk menandatangani di area bawah ini:",
                 font=('Arial', 10)).pack(pady=10)
        
        self.signature_pad = DigitalSignaturePad(digital_frame, width=500, height=150)
        
        # Tab 2: Upload image
        upload_frame = ttk.Frame(notebook)
        notebook.add(upload_frame, text="Upload Gambar Tanda Tangan")
        
        upload_info = ttk.Label(upload_frame, 
                               text="Upload file gambar tanda tangan (PNG, JPG, JPEG)\n" +
                                    "Pastikan background gambar transparan atau putih",
                               font=('Arial', 10))
        upload_info.pack(pady=20)
        
        self.upload_button = ttk.Button(upload_frame, text="Pilih File Gambar", 
                                       command=self.upload_signature)
        self.upload_button.pack(pady=10)
        
        self.upload_status = ttk.Label(upload_frame, text="Belum ada file dipilih", 
                                      font=('Arial', 9), foreground='gray')
        self.upload_status.pack(pady=5)
        
        # Preview frame for uploaded image
        self.preview_frame = ttk.Frame(upload_frame)
        self.preview_frame.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="OK - Gunakan Tanda Tangan", 
                  command=self.confirm_signature).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Lanjutkan Tanpa Tanda Tangan", 
                  command=self.skip_signature).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Batal", 
                  command=self.cancel).pack(side='right', padx=5)
        
    def upload_signature(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File Gambar Tanda Tangan",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Validate and preview image
                img = PILImage.open(file_path)
                
                # Create thumbnail for preview
                img_copy = img.copy()
                img_copy.thumbnail((200, 100), PILImage.Resampling.LANCZOS)
                
                # Convert to PhotoImage for display
                photo = ImageTk.PhotoImage(img_copy)
                
                # Clear previous preview
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()
                
                # Show preview
                preview_label = ttk.Label(self.preview_frame, text="Preview:")
                preview_label.pack()
                
                img_label = ttk.Label(self.preview_frame, image=photo)
                img_label.image = photo  # Keep a reference
                img_label.pack(pady=5)
                
                self.signature_path = file_path
                self.upload_status.config(text=f"File dipilih: {os.path.basename(file_path)}", 
                                        foreground='green')
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat gambar: {str(e)}")
                self.upload_status.config(text="Error memuat file", foreground='red')
    
    def confirm_signature(self):
        # Check which tab is active
        current_tab = self.dialog.nametowidget(self.dialog.focus_get().winfo_parent())
        
        if "digital" in str(current_tab).lower() or self.signature_pad.has_signature():
            # Digital signature
            if self.signature_pad.has_signature():
                self.signature_path = self.signature_pad.save_signature_as_image()
                self.result = "digital"
            else:
                messagebox.showwarning("Peringatan", "Belum ada tanda tangan digital!")
                return
        else:
            # Uploaded signature
            if self.signature_path:
                self.result = "upload"
            else:
                messagebox.showwarning("Peringatan", "Belum ada file gambar dipilih!")
                return
        
        self.dialog.destroy()
    
    def skip_signature(self):
        self.result = "skip"
        self.dialog.destroy()
    
    def cancel(self):
        self.result = "cancel"
        self.dialog.destroy()
        
    def show_dialog(self):
        self.dialog.wait_window()
        return self.result, self.signature_path


class PDFPackingListGenerator:
    def __init__(self, db):
        self.db = db
    
    def generate_pdf_packing_list_with_signature(self, container_id, filter_criteria=None):
        """Generate PDF packing list without signature prompt"""
        print(f"[DEBUG] Starting PDF generation for container_id: {container_id}")
        print(f"[DEBUG] Filter criteria: {filter_criteria}")
        
        try:
            # Get container details
            container = self.db.get_container_by_id(container_id)
            if not container:
                print("[ERROR] Container tidak ditemukan!")
                messagebox.showerror("Error", "Container tidak ditemukan!")
                return
            
            print(f"[DEBUG] Container found")
            
            # Get barang in container
            container_barang = self.db.get_barang_in_container_with_colli_and_pricing(container_id)
            print(f"[DEBUG] Found {len(container_barang) if container_barang else 0} items in container")
            
            if not container_barang:
                print("[WARNING] Container kosong!")
                messagebox.showwarning("Peringatan", "Container kosong, tidak ada yang akan diprint!")
                return
            
            # Filter barang if criteria provided
            if filter_criteria:
                print(f"[DEBUG] Applying filter: {filter_criteria}")
                filtered_barang = []
                sender_filter = filter_criteria.get('sender_name', '')
                receiver_filter = filter_criteria.get('receiver_name', '')
                
                for barang in container_barang:
                    # Handle both dict and sqlite3.Row objects
                    if hasattr(barang, 'keys'):  # sqlite3.Row object
                        sender = barang['sender_name'] if 'sender_name' in barang.keys() and barang['sender_name'] else ''
                        receiver = barang['receiver_name'] if 'receiver_name' in barang.keys() and barang['receiver_name'] else ''
                    else:  # dict object
                        sender = barang.get('sender_name', '')
                        receiver = barang.get('receiver_name', '')
                    
                    if sender == sender_filter and receiver == receiver_filter:
                        filtered_barang.append(barang)
                
                container_barang = filtered_barang
                print(f"[DEBUG] After filtering: {len(container_barang)} items remain")
                
                if not container_barang:
                    print("[WARNING] No items after filtering")
                    messagebox.showwarning("Peringatan", "Tidak ada barang untuk kombinasi yang dipilih!")
                    return
            
            # INPUT SUFFIX ABJAD untuk Invoice Number
            print("[DEBUG] Asking for invoice suffix...")
            invoice_suffix = ""
            
            try:
                # Dialog untuk input suffix
                suffix_dialog = tk.Toplevel()
                suffix_dialog.title("Invoice Number Suffix")
                suffix_dialog.geometry("400x250")
                suffix_dialog.resizable(False, False)
                suffix_dialog.grab_set()
                suffix_dialog.transient()
                
                try:
                    # Load dan resize image
                    icon_image = Image.open("assets/logo.jpg")
                    icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                
                    # Set sebagai window icon
                    suffix_dialog.iconphoto(False, icon_photo)
                    
                except Exception as e:
                    print(f"Icon tidak ditemukan: {e}")
                
                # Center dialog
                suffix_dialog.geometry("+%d+%d" % (suffix_dialog.winfo_screenwidth()//2 - 200, 
                                                suffix_dialog.winfo_screenheight()//2 - 125))
                
                suffix_result = {"value": "", "cancelled": True}
                
                # Main frame
                main_frame = ttk.Frame(suffix_dialog)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                # Title
                title_label = ttk.Label(main_frame, 
                                    text="Invoice Number Suffix",
                                    font=('Arial', 12, 'bold'))
                title_label.pack(pady=(0, 10))
                
                # Explanation
                exp_label = ttk.Label(main_frame,
                                    text="Masukkan huruf/abjad yang akan ditambahkan\ndi akhir nomor invoice (contoh: A, B, C, dst)",
                                    font=('Arial', 10))
                exp_label.pack(pady=(0, 15))
                
                # Example
                example_label = ttk.Label(main_frame,
                                        text="Contoh: Container #1 → Invoice #1-A",
                                        font=('Arial', 9),
                                        foreground='blue')
                example_label.pack(pady=(0, 15))
                
                # Input frame
                input_frame = ttk.Frame(main_frame)
                input_frame.pack(fill='x', pady=(0, 20))
                
                ttk.Label(input_frame, text="Suffix:", font=('Arial', 10)).pack(side='left')
                suffix_entry = ttk.Entry(input_frame, font=('Arial', 10), width=10)
                suffix_entry.pack(side='left', padx=(10, 0))
                suffix_entry.focus()
                
                # Button frame
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill='x')
                
                def on_ok():
                    value = suffix_entry.get().strip().upper()
                    # Validate: only letters allowed
                    if value and not value.isalpha():
                        messagebox.showwarning("Peringatan", "Hanya huruf/abjad yang diperbolehkan!")
                        return
                    
                    suffix_result["value"] = value
                    suffix_result["cancelled"] = False
                    suffix_dialog.destroy()
                
                def on_cancel():
                    suffix_result["cancelled"] = True
                    suffix_dialog.destroy()
                
                def on_skip():
                    suffix_result["value"] = ""
                    suffix_result["cancelled"] = False
                    suffix_dialog.destroy()
                
                ttk.Button(button_frame, text="OK", command=on_ok).pack(side='left', padx=(0, 5))
                ttk.Button(button_frame, text="Skip (Tanpa Suffix)", command=on_skip).pack(side='left', padx=5)
                ttk.Button(button_frame, text="Batal", command=on_cancel).pack(side='right')
                
                # Bind Enter and Escape
                suffix_dialog.bind("<Return>", lambda e: on_ok())
                suffix_dialog.bind("<Escape>", lambda e: on_cancel())
                
                print("[DEBUG] Suffix dialog created, waiting for user input...")
                suffix_dialog.wait_window()
                
                if suffix_result["cancelled"]:
                    print("[DEBUG] User cancelled suffix input")
                    return
                
                invoice_suffix = suffix_result["value"]
                print(f"[DEBUG] Invoice suffix: '{invoice_suffix}'")
                
            except Exception as suffix_error:
                print(f"[ERROR] Error in suffix dialog: {suffix_error}")
                # Continue without suffix
                invoice_suffix = ""
            
            # SKIP SIGNATURE OPTIONS - NO SIGNATURE PROMPT
            print("[DEBUG] Skipping signature options - creating PDF without signature")
            signature_path = None
            
            # Generate PDF with suffix but no signature
            print("[DEBUG] Starting PDF creation with suffix...")
            self._create_pdf_document(container, container_barang, container_id, 
                                    filter_criteria, signature_path, invoice_suffix)
            
            print("[DEBUG] PDF generation completed successfully!")
            
        except Exception as e:
            error_msg = f"Error in generate_pdf_packing_list_with_signature: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Gagal membuat PDF packing list: {str(e)}")


    def _create_pdf_document(self, container, barang_list, container_id, filter_criteria, signature_path, invoice_suffix=""):
        """Create the actual PDF document without signature section"""
        print("[DEBUG] Starting _create_pdf_document")
        print(f"[DEBUG] Invoice suffix: '{invoice_suffix}'")
        
        try:
            # Generate filename with suffix
            filter_suffix = ""
            if filter_criteria:
                sender = filter_criteria.get('sender_name', 'Unknown')[:10]
                receiver = filter_criteria.get('receiver_name', 'Unknown')[:10]
                # Clean filename from invalid characters
                sender = "".join(c for c in sender if c.isalnum() or c in (' ', '-', '_')).rstrip()
                receiver = "".join(c for c in receiver if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filter_suffix = f"_{sender}_to_{receiver}"
            
            invoice_suffix_file = f"_{invoice_suffix}" if invoice_suffix else ""
            
            filename = f"PackingList_Container_{container_id}{filter_suffix}{invoice_suffix_file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            print(f"[DEBUG] Generated filename: {filename}")
            
            # Ask user where to save
            print("[DEBUG] Showing file save dialog...")
            try:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=filename,
                    title="Save PDF Packing List"
                )
            except Exception as dialog_error:
                print(f"[ERROR] File dialog error: {dialog_error}")
                # Fallback: use temp directory
                import tempfile
                temp_dir = tempfile.gettempdir()
                file_path = os.path.join(temp_dir, filename)
                print(f"[DEBUG] Using temp directory fallback: {file_path}")
            
            if not file_path:
                print("[DEBUG] No file path provided")
                return
            
            print(f"[DEBUG] Creating PDF at: {file_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
            print("[DEBUG] SimpleDocTemplate created successfully")
            
            # Get styles - DEFINE ALL STYLES FIRST BEFORE USING THEM
            styles = getSampleStyleSheet()
            
            # Custom styles to match original format
            logo_style = ParagraphStyle(
                'Logo',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_LEFT,
                textColor=colors.orange,
                fontName='Helvetica-Bold'
            )
            
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=14,
                alignment=TA_RIGHT,
                fontName='Helvetica-Bold',
                spaceAfter=0
            )
            
            company_info_style = ParagraphStyle(
                'CompanyInfo',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_LEFT,
                spaceAfter=10
            )
            
            invoice_info_style = ParagraphStyle(
                'InvoiceInfo',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_RIGHT,
                spaceAfter=10
            )
            
            small_style = ParagraphStyle(
                'Small',
                parent=styles['Normal'],
                fontSize=8
            )
            
            print("[DEBUG] Styles created successfully")
            
            # NOW HANDLE LOGO AFTER STYLES ARE DEFINED
            logo_path = "assets/logo-cklogistik.png"  # Path to logo image
            header_data = []
            
            if logo_path and os.path.exists(logo_path):
                # Use actual logo image
                try:
                    logo_img = Image(logo_path, width=10*cm, height=1.5*cm)
                    title_text = "CUSTOMER PACKING LIST"
                    
                    header_data = [
                        [logo_img, Paragraph(title_text, title_style)]
                    ]
                    
                    print("[DEBUG] Using logo image from file")
                except Exception as logo_error:
                    print(f"[ERROR] Failed to load logo: {logo_error}")
                    # Fallback to text logo
                    logo_text = "cahaya karunia<br/>logistic"
                    title_text = "CUSTOMER PACKING LIST"
                    
                    header_data = [
                        [Paragraph(logo_text, logo_style), Paragraph(title_text, title_style)]
                    ]
            else:
                # Use text logo
                print("[DEBUG] Logo file not found, using text logo")
                logo_text = "cahaya karunia<br/>logistic"
                title_text = "CUSTOMER PACKING LIST"
                
                header_data = [
                    [Paragraph(logo_text, logo_style), Paragraph(title_text, title_style)]
                ]
            
            # Safe way to get container values
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return str(container.get(key, default) or default)
                    else:
                        return str(container[key] if key in container and container[key] else default)
                except:
                    return str(default)
            
            # Build story (content)
            story = []
            print("[DEBUG] Building PDF content...")
            
            # HEADER SECTION
            header_table = Table(header_data, colWidths=[8*cm, 10*cm])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10)
            ]))
            
            story.append(header_table)
            print("[DEBUG] Added header with logo and title")
            
            # COMPANY INFO and INVOICE INFO side by side
            company_address = "Jl. Teluk Raya Selatan No. 6, Surabaya<br/>Phone: 031-60166017"
            
            # Generate invoice number with suffix
            container_no = safe_get('container')
            current_month_roman = {
                1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
                7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
            }
            
            month_roman = current_month_roman.get(datetime.now().month, "IX")
            year = datetime.now().year
            
            # Format: CKL/SUB/IX/2025/container_id + suffix
            base_invoice = f"CKL/SUB/{month_roman}/{year}/{container_id:05d}"
            if invoice_suffix:
                invoice_number = f"{base_invoice} {invoice_suffix}"
            else:
                invoice_number = base_invoice
            
            etd_date = safe_get('etd_sub')
            if etd_date and etd_date != '-':
                try:
                    if isinstance(etd_date, str):
                        etd_obj = datetime.strptime(etd_date, '%Y-%m-%d')
                    else:
                        etd_obj = etd_date
                    formatted_etd = etd_obj.strftime('%d/%m/%Y')
                except:
                    formatted_etd = etd_date
            else:
                formatted_etd = datetime.now().strftime('%d/%m/%Y')
            
            invoice_info = f"Invoice Number: {invoice_number}<br/>Tanggal (ETD): {formatted_etd}"
            
            info_data = [
                [Paragraph(company_address, company_info_style), 
                Paragraph(invoice_info, invoice_info_style)]
            ]
            
            info_table = Table(info_data, colWidths=[8*cm, 10*cm])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15)
            ]))
            
            story.append(info_table)
            print(f"[DEBUG] Added info section with invoice number: {invoice_number}")
            
            # CUSTOMER INFO SECTION
            if filter_criteria:
                sender = filter_criteria.get('sender_name', '')
                receiver = filter_criteria.get('receiver_name', '')
                
                customer_data = [
                    [f"Bill To (Nama Customer): {receiver}"],
                    [""],
                    [f"Feeder (Nama Kapal): {safe_get('feeder')}"],
                    [f"Destination (Tujuan): {safe_get('destination')}"],
                    [f"Party (Volume): {safe_get('party')} m3"]
                ]
                
                customer_table = Table(customer_data, colWidths=[18*cm])
                customer_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
                ]))
                
                story.append(customer_table)
                story.append(Spacer(1, 15))
                print("[DEBUG] Added customer info section")
            
            # ITEMS TABLE - Matching original format
            table_data = [['No.', 'No. Container', 'Pengirim', 'Jenis Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Catatan']]
            
            # Items data
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            
            print(f"[DEBUG] Processing {len(barang_list)} items...")
            
            for i, barang_row in enumerate(barang_list, 1):
                try:
                    # Handle both dict and sqlite3.Row objects
                    if hasattr(barang_row, 'keys'):  # sqlite3.Row object
                        barang = {key: barang_row[key] for key in barang_row.keys()}
                    else:
                        barang = dict(barang_row)
                    
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                    
                    # Get data
                    pengirim = str(safe_barang_get('sender_name', '-'))[:15]
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))
                    
                    # Combine nama_barang and jenis_barang like in original
                    combined_jenis = f"{nama_barang}"
                    if jenis_barang != '-' and jenis_barang != nama_barang:
                        combined_jenis += f"\n{jenis_barang}"
                    
                    # Format dimensions
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    kubikasi = f"{p}x{l}x{t}"
                    
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    
                    catatan = str(safe_barang_get('keterangan', safe_barang_get('notes', '')))
                    
                    # Add to totals
                    try:
                        total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                        total_ton += float(ton) if ton not in [None, '', '-'] else 0
                        total_colli += int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                    
                    # Format values
                    m3_val = f"{float(m3):.3f}" if m3 not in [None, '', '-'] else "0.000"
                    ton_val = f"{float(ton):.3f}" if ton not in [None, '', '-'] else "0.000"
                    colli_val = f"{int(colli):.2f}" if colli not in [None, '', '-'] else "0.00"
                    
                    # Container number with suffix
                    container_with_suffix = f"{container_no}{invoice_suffix}" if invoice_suffix else container_no
                    
                    table_data.append([
                        str(i), 
                        container_with_suffix,
                        pengirim,
                        combined_jenis,
                        kubikasi,
                        m3_val,
                        ton_val, 
                        colli_val,
                        catatan
                    ])
                    
                except Exception as e:
                    print(f"[ERROR] Error processing item {i}: {e}")
                    continue
            
            print(f"[DEBUG] Table data created with {len(table_data)} rows")
            
            # Create table with proper column widths to match original
            items_table = Table(table_data, colWidths=[
                1*cm,    # No
                2*cm,    # No. Container  
                3*cm,    # Pengirim
                4*cm,    # Jenis Barang
                2.5*cm,  # Kubikasi
                1.5*cm,  # M3
                1.5*cm,  # Ton
                1.5*cm,  # Col
                3*cm     # Catatan
            ])
            
            # Table styling to match original format
            items_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # No and No. Container columns
                ('ALIGN', (5, 1), (7, -1), 'RIGHT'),   # M3, Ton, Col columns (right align numbers)
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),   # Top align for multiline content
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
            ]))
            
            story.append(items_table)
            
            # SKIP SUMMARY AND SIGNATURE - PDF ENDS HERE
            print("[DEBUG] PDF selesai tanpa summary dan signature")
            
            # Build PDF
            print("[DEBUG] Building final PDF...")
            doc.build(story)
            print(f"[SUCCESS] PDF successfully created at: {file_path}")
            
            # Check if file exists and has size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"[DEBUG] PDF file size: {file_size} bytes")
                
                if file_size > 0:
                    suffix_status = f" (Suffix: {invoice_suffix})" if invoice_suffix else ""
                    
                    messagebox.showinfo(
                        "Sukses",
                        f"PDF Packing List berhasil dibuat!\n\n"
                        f"Lokasi: {file_path}\n"
                        f"Size: {file_size} bytes\n"
                        f"Invoice Number: {base_invoice}{' ' + invoice_suffix if invoice_suffix else ''}\n\n"
                        f"Dokumen siap untuk dicetak atau dikirim\n"
                        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
                    )
                    
                    # Ask if user wants to open the file
                    if messagebox.askyesno("Buka File?", "Apakah Anda ingin membuka PDF sekarang?"):
                        try:
                            if os.name == 'nt':  # Windows
                                os.startfile(file_path)
                            elif os.name == 'posix':  # macOS and Linux
                                os.system(f'open "{file_path}"')  # macOS
                        except Exception as e:
                            messagebox.showwarning("Info", f"File berhasil disimpan, tapi gagal membuka otomatis.\nSilakan buka manual: {file_path}")
                else:
                    print("[ERROR] PDF file created but has 0 bytes")
                    messagebox.showerror("Error", "PDF file created but is empty!")
            else:
                print("[ERROR] PDF file was not created")
                messagebox.showerror("Error", "PDF file was not created!")
                    
        except Exception as e:
            error_msg = f"Error in _create_pdf_document: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Gagal membuat PDF: {str(e)}")
    
    def _create_pdf_document(self, container, barang_list, container_id, filter_criteria, signature_path, invoice_suffix=""):
        """Create the actual PDF document matching the original format"""
        print("[DEBUG] Starting _create_pdf_document")
        print(f"[DEBUG] Signature path: {signature_path}")
        print(f"[DEBUG] Invoice suffix: '{invoice_suffix}'")
        
        try:
            # Generate filename with suffix
            filter_suffix = ""
            if filter_criteria:
                sender = filter_criteria.get('sender_name', 'Unknown')[:10]
                receiver = filter_criteria.get('receiver_name', 'Unknown')[:10]
                # Clean filename from invalid characters
                sender = "".join(c for c in sender if c.isalnum() or c in (' ', '-', '_')).rstrip()
                receiver = "".join(c for c in receiver if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filter_suffix = f"_{sender}_to_{receiver}"
            
            signature_suffix = "_signed" if signature_path else ""
            invoice_suffix_file = f"_{invoice_suffix}" if invoice_suffix else ""
            
            filename = f"PackingList_Container_{container_id}{filter_suffix}{invoice_suffix_file}{signature_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            print(f"[DEBUG] Generated filename: {filename}")
            
            # Ask user where to save
            print("[DEBUG] Showing file save dialog...")
            try:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=filename,
                    title="Save PDF Packing List"
                )
            except Exception as dialog_error:
                print(f"[ERROR] File dialog error: {dialog_error}")
                # Fallback: use temp directory
                import tempfile
                temp_dir = tempfile.gettempdir()
                file_path = os.path.join(temp_dir, filename)
                print(f"[DEBUG] Using temp directory fallback: {file_path}")
            
            if not file_path:
                print("[DEBUG] No file path provided")
                return
            
            print(f"[DEBUG] Creating PDF at: {file_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
            print("[DEBUG] SimpleDocTemplate created successfully")
            
            # Get styles - DEFINE ALL STYLES FIRST BEFORE USING THEM
            styles = getSampleStyleSheet()
            
            # Custom styles to match original format
            logo_style = ParagraphStyle(
                'Logo',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_LEFT,
                textColor=colors.orange,
                fontName='Helvetica-Bold'
            )
            
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=14,
                alignment=TA_RIGHT,
                fontName='Helvetica-Bold',
                spaceAfter=0
            )
            
            company_info_style = ParagraphStyle(
                'CompanyInfo',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_LEFT,
                spaceAfter=10
            )
            
            invoice_info_style = ParagraphStyle(
                'InvoiceInfo',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_RIGHT,
                spaceAfter=10
            )
            
            small_style = ParagraphStyle(
                'Small',
                parent=styles['Normal'],
                fontSize=8
            )
            
            print("[DEBUG] Styles created successfully")
            
            # NOW HANDLE LOGO AFTER STYLES ARE DEFINED
            logo_path = "assets/logo-cklogistik.png"  # Path to logo image
            header_data = []
            
            if logo_path and os.path.exists(logo_path):
                # Use actual logo image
                try:
                    logo_img = Image(logo_path, width=10*cm, height=1.5*cm)
                    title_text = "CUSTOMER PACKING LIST"
                    
                    header_data = [
                        [logo_img, Paragraph(title_text, title_style)]
                    ]
                    
                    print("[DEBUG] Using logo image from file")
                except Exception as logo_error:
                    print(f"[ERROR] Failed to load logo: {logo_error}")
                    # Fallback to text logo
                    logo_text = "cahaya karunia<br/>logistic"
                    title_text = "CUSTOMER PACKING LIST"
                    
                    header_data = [
                        [Paragraph(logo_text, logo_style), Paragraph(title_text, title_style)]
                    ]
            else:
                # Use text logo
                print("[DEBUG] Logo file not found, using text logo")
                logo_text = "cahaya karunia<br/>logistic"
                title_text = "CUSTOMER PACKING LIST"
                
                header_data = [
                    [Paragraph(logo_text, logo_style), Paragraph(title_text, title_style)]
                ]
            
            # Safe way to get container values
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return str(container.get(key, default) or default)
                    else:
                        return str(container[key] if key in container and container[key] else default)
                except:
                    return str(default)
            
            # Build story (content)
            story = []
            print("[DEBUG] Building PDF content...")
            
            # HEADER SECTION
            header_table = Table(header_data, colWidths=[8*cm, 10*cm])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10)
            ]))
            
            story.append(header_table)
            print("[DEBUG] Added header with logo and title")
            
            # COMPANY INFO and INVOICE INFO side by side
            company_address = "Jl. Teluk Raya Selatan No. 6, Surabaya<br/>Phone: 031-60166017"
            
            # Generate invoice number with suffix
            container_no = safe_get('container')
            current_month_roman = {
                1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
                7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
            }
            
            month_roman = current_month_roman.get(datetime.now().month, "IX")
            year = datetime.now().year
            
            # Format: CKL/SUB/IX/2025/container_id + suffix
            base_invoice = f"CKL/SUB/{month_roman}/{year}/{container_id:05d}"
            if invoice_suffix:
                invoice_number = f"{base_invoice} {invoice_suffix}"
            else:
                invoice_number = base_invoice
            
            etd_date = safe_get('etd_sub')
            if etd_date and etd_date != '-':
                try:
                    if isinstance(etd_date, str):
                        etd_obj = datetime.strptime(etd_date, '%Y-%m-%d')
                    else:
                        etd_obj = etd_date
                    formatted_etd = etd_obj.strftime('%d/%m/%Y')
                except:
                    formatted_etd = etd_date
            else:
                formatted_etd = datetime.now().strftime('%d/%m/%Y')
            
            invoice_info = f"Invoice Number: {invoice_number}<br/>Tanggal (ETD): {formatted_etd}"
            
            info_data = [
                [Paragraph(company_address, company_info_style), 
                Paragraph(invoice_info, invoice_info_style)]
            ]
            
            info_table = Table(info_data, colWidths=[8*cm, 10*cm])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15)
            ]))
            
            story.append(info_table)
            print(f"[DEBUG] Added info section with invoice number: {invoice_number}")
            
            # CUSTOMER INFO SECTION
            if filter_criteria:
                sender = filter_criteria.get('sender_name', '')
                receiver = filter_criteria.get('receiver_name', '')
                
                customer_data = [
                    [f"Bill To (Nama Customer): {receiver}"],
                    [""],
                    [f"Feeder (Nama Kapal): {safe_get('feeder')}"],
                    [f"Destination (Tujuan): {safe_get('destination')}"],
                    [f"Party (Volume): {safe_get('party')} m3"]
                ]
                
                customer_table = Table(customer_data, colWidths=[18*cm])
                customer_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
                ]))
                
                story.append(customer_table)
                story.append(Spacer(1, 15))
                print("[DEBUG] Added customer info section")
            
            # ITEMS TABLE - Matching original format
            table_data = [['No.', 'No. Container', 'Pengirim', 'Jenis Barang', 'Kubikasi', 'M3', 'Ton', 'Col', 'Catatan']]
            
            # Items data
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            
            print(f"[DEBUG] Processing {len(barang_list)} items...")
            
            for i, barang_row in enumerate(barang_list, 1):
                try:
                    # Handle both dict and sqlite3.Row objects
                    if hasattr(barang_row, 'keys'):  # sqlite3.Row object
                        barang = {key: barang_row[key] for key in barang_row.keys()}
                    else:
                        barang = dict(barang_row)
                    
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                    
                    # Get data
                    pengirim = str(safe_barang_get('sender_name', '-'))[:15]
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))
                    
                    # Combine nama_barang and jenis_barang like in original
                    combined_jenis = f"{nama_barang}"
                    if jenis_barang != '-' and jenis_barang != nama_barang:
                        combined_jenis += f"\n{jenis_barang}"
                    
                    # Format dimensions
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    kubikasi = f"{p}x{l}x{t}"
                    
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    
                    catatan = str(safe_barang_get('keterangan', safe_barang_get('notes', '')))
                    
                    # Add to totals
                    try:
                        total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                        total_ton += float(ton) if ton not in [None, '', '-'] else 0
                        total_colli += int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                    
                    # Format values
                    m3_val = f"{float(m3):.3f}" if m3 not in [None, '', '-'] else "0.000"
                    ton_val = f"{float(ton):.3f}" if ton not in [None, '', '-'] else "0.000"
                    colli_val = f"{int(colli):.2f}" if colli not in [None, '', '-'] else "0.00"
                    
                    # Container number with suffix
                    container_with_suffix = f"{container_no}{invoice_suffix}" if invoice_suffix else container_no
                    
                    table_data.append([
                        str(i), 
                        container_with_suffix,
                        pengirim,
                        combined_jenis,
                        kubikasi,
                        m3_val,
                        ton_val, 
                        colli_val,
                        catatan
                    ])
                    
                except Exception as e:
                    print(f"[ERROR] Error processing item {i}: {e}")
                    continue
            
            print(f"[DEBUG] Table data created with {len(table_data)} rows")
            
            # Create table with proper column widths to match original
            items_table = Table(table_data, colWidths=[
                1*cm,    # No
                2*cm,    # No. Container  
                3*cm,    # Pengirim
                4*cm,    # Jenis Barang
                2.5*cm,  # Kubikasi
                1.5*cm,  # M3
                1.5*cm,  # Ton
                1.5*cm,  # Col
                3*cm     # Catatan
            ])
            
            # Table styling to match original format
            items_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # No and No. Container columns
                ('ALIGN', (5, 1), (7, -1), 'RIGHT'),   # M3, Ton, Col columns (right align numbers)
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),   # Top align for multiline content
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
            ]))
            
            story.append(items_table)
            
            # HAPUS BAGIAN SUMMARY DAN SIGNATURE
            # Tidak ada summary dan tidak ada signature - langsung selesai setelah tabel
            print("[DEBUG] Items table created successfully - PDF selesai tanpa summary dan signature")
            
            # Build PDF
            print("[DEBUG] Building final PDF...")
            doc.build(story)
            print(f"[SUCCESS] PDF successfully created at: {file_path}")
            
            # Check if file exists and has size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"[DEBUG] PDF file size: {file_size} bytes")
                
                if file_size > 0:
                    signature_status = "dengan tanda tangan" if signature_path else "tanpa tanda tangan"
                    suffix_status = f" (Suffix: {invoice_suffix})" if invoice_suffix else ""
                    
                    messagebox.showinfo(
                        "Sukses",
                        f"PDF Packing List berhasil dibuat {signature_status}!\n\n"
                        f"Lokasi: {file_path}\n"
                        f"Size: {file_size} bytes\n"
                        f"Invoice Number: {base_invoice}{' ' + invoice_suffix if invoice_suffix else ''}\n\n"
                        f"Dokumen siap untuk dicetak atau dikirim\n"
                        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
                    )
                    
                    # Ask if user wants to open the file
                    if messagebox.askyesno("Buka File?", "Apakah Anda ingin membuka PDF sekarang?"):
                        try:
                            if os.name == 'nt':  # Windows
                                os.startfile(file_path)
                            elif os.name == 'posix':  # macOS and Linux
                                os.system(f'open "{file_path}"')  # macOS
                        except Exception as e:
                            messagebox.showwarning("Info", f"File berhasil disimpan, tapi gagal membuka otomatis.\nSilakan buka manual: {file_path}")
                else:
                    print("[ERROR] PDF file created but has 0 bytes")
                    messagebox.showerror("Error", "PDF file created but is empty!")
            else:
                print("[ERROR] PDF file was not created")
                messagebox.showerror("Error", "PDF file was not created!")
                    
        except Exception as e:
            error_msg = f"Error in _create_pdf_document: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Gagal membuat PDF: {str(e)}")  
         
    def _add_signature_box(self, story, signature_path=None):
        """Add signature box with optional signature image"""
        try:
            if signature_path and os.path.exists(signature_path):
                # With signature image
                print(f"[DEBUG] Adding signature image from: {signature_path}")
                
                sig_table_data = [
                    ['', 'Tanda Tangan & Stempel'],
                    ['Disiapkan oleh:', ''],
                    ['Nama:', ''],
                    ['Tanggal:', datetime.now().strftime('%d-%m-%Y')]
                ]
                
                # Add signature image to the table
                try:
                    # Create ReportLab Image object
                    sig_img = Image(signature_path, width=3*cm, height=1.5*cm)
                    sig_table_data[1][1] = sig_img
                    print("[DEBUG] Signature image added to table successfully")
                except Exception as img_error:
                    print(f"[ERROR] Failed to add signature image: {img_error}")
                    # Fallback to text
                    sig_table_data[1][1] = "[Signature Image]"
                
            else:
                # Empty signature box
                print("[DEBUG] Adding empty signature box")
                sig_table_data = [
                    ['', 'Tanda Tangan & Stempel'],
                    ['Disiapkan oleh:', ''],
                    ['Nama:', ''],
                    ['Tanggal:', datetime.now().strftime('%d-%m-%Y')]
                ]
            
            sig_table = Table(sig_table_data, colWidths=[4*cm, 6*cm], 
                             rowHeights=[None, 2*cm, None, None])
            sig_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(sig_table)
            print("[DEBUG] Signature box added successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to add signature box: {e}")
            raise
       
       
       
        
