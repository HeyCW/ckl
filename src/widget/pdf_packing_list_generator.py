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
from src.utils.helpers import format_ton

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
        
    def _create_pdf_document_packing(self, container, barang_list, container_id, filter_criteria, signature_path, invoice_suffix=""):
        """Create the actual PDF document matching Invoice format exactly"""
        print("[DEBUG] Starting _create_pdf_document_packing")
        
        try:
            # Generate filename with suffix
            filter_suffix = ""
            if filter_criteria:
                receiver = filter_criteria.get('receiver_name', 'Unknown')[:10]
                receiver = "".join(c for c in receiver if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filter_suffix = f"_{receiver}"
            
            invoice_suffix_file = f"_{invoice_suffix}" if invoice_suffix else ""
            
            filename = f"PackingList_Container_{container_id}{filter_suffix}{invoice_suffix_file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            print(f"[DEBUG] Generated filename: {filename}")
            
            # Ask user where to save
            print("[DEBUG] Showing file save dialog...")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename,
                title="Save PDF Packing List"
            )
            
            if not file_path:
                print("[DEBUG] No file path provided")
                return
            
            print(f"[DEBUG] Creating PDF at: {file_path}")
            
            # Create PDF document - SAME SIZE as Invoice
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=20, bottomMargin=50)
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles - SAME as Invoice
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=TA_RIGHT,
                fontName='Helvetica-Bold',
                spaceAfter=10
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_LEFT
            )
            
            small_style = ParagraphStyle(
                'Small',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_LEFT
            )
            
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
            
            # ========================================
            # HEADER SECTION - Match Invoice Layout
            # ========================================
            
            # Logo and Title Row
            logo_path = "assets/logo-cklogistik.jpg"
            if logo_path and os.path.exists(logo_path):
                try:
                    # Increased logo size by ~20%
                    logo_img = Image(logo_path, width=6*cm, height=1.8*cm)
                    
                    # Create header table: Logo | Company Info | Title
                    header_data = [
                        [
                            logo_img,
                            Paragraph("Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607", small_style),
                            Paragraph("CUSTOMER PACKING LIST", title_style)
                        ]
                    ]
                    
                    # Adjusted column widths for larger logo
                    header_table = Table(header_data, colWidths=[6*cm, 6.5*cm, 6*cm])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (0, 0), 0),
                        ('LEFTPADDING', (1, 0), (1, 0), 30),
                        ('LEFTPADDING', (2, 0), (2, 0), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    
                    story.append(header_table)
                    story.append(Spacer(1, 15))
                    
                except Exception as logo_error:
                    print(f"[ERROR] Logo error: {logo_error}")
                    # Fallback without logo
                    story.append(Paragraph("CUSTOMER PACKING LIST", title_style))
                    story.append(Spacer(1, 15))
            else:
                story.append(Paragraph("CUSTOMER PACKING LIST", title_style))
                story.append(Spacer(1, 15))
            
            # ========================================
            # CUSTOMER INFO SECTION - Match Invoice
            # ========================================
            
            # Get receiver from filter
            receiver_name = filter_criteria.get('receiver_name', '-') if filter_criteria else '-'
            
            # Invoice Number - Format sama dengan Invoice
            current_month_roman = {
                1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
                7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
            }
            
            month_roman = current_month_roman.get(datetime.now().month, "X")
            year = datetime.now().year
            
            # Format: CKL/SUB/X/2025/container_id + suffix
            base_invoice = f"CKL/SUB/{month_roman}/{year}/{container_id:05d}"
            
            if invoice_suffix:
                invoice_number = f"{base_invoice} {invoice_suffix}"
            else:
                invoice_number = base_invoice
            
            # ETD Date
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
            
            destination = safe_get('destination')
            destination_upper = destination.upper() if destination != '-' else destination
            
            customer_data = [
                ['Bill To (Nama Customer)', ':', receiver, '', 'Invoice Number', ':', invoice_number],
                ['', '', '', '', '', '', ''],
                ['Feeder (Nama Kapal)', ':', safe_get('feeder'), '', 'Tanggal (ETD)', ':', formatted_etd],  
                ['Destination (Tujuan)', ':', destination_upper, '', 'Party (Volume)', ':', f"{safe_get('party')} m3"],
            ]
            
            customer_table = Table(customer_data, colWidths=[4*cm, 0.3*cm, 5*cm, 1*cm, 3.5*cm, 0.3*cm, 4.9*cm])
            customer_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('ALIGN', (4, 0), (4, -1), 'LEFT'),
                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            story.append(customer_table)
            story.append(Spacer(1, 15))
            
            # ========================================
            # ITEMS TABLE - MATCH Invoice format
            # ========================================
            
            # Table header - Add all columns like Invoice
            table_data = [[
                'No.', 
                'No.\nContainer', 
                'Pengirim', 
                'Jenis Barang', 
                'Kubikasi', 
                'M3', 
                'Ton', 
                'Col',
                'Catatan'
            ]]
            
            # Items data
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            
            container_no = safe_get('container')
            
            for i, barang_row in enumerate(barang_list, 1):
                try:
                    if hasattr(barang_row, 'keys'):
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
                    pengirim = str(safe_barang_get('sender_name', '-'))
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    
                    # Format dimensi
                    try:
                        p_str = f"{float(p):.1f}" if p != '-' else '-'
                        l_str = f"{float(l):.1f}" if l != '-' else '-'
                        t_str = f"{float(t):.1f}" if t != '-' else '-'
                    except:
                        p_str, l_str, t_str = str(p), str(l), str(t)
                    
                    kubikasi = f"{p_str}*{l_str}*{t_str}"
                    
                    m3 = safe_barang_get('m3_barang', 0)
                    ton = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    catatan = str(safe_barang_get('keterangan', ''))
                    
                    # Add to totals
                    try:
                        total_m3 += float(m3) if m3 not in [None, '', '-'] else 0
                        total_ton += float(ton) if ton not in [None, '', '-'] else 0
                        total_colli += int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                    
                    # Format values
                    m3_val = f"{float(m3):.3f}" if m3 not in [None, '', '-'] else "0.000"
                    ton_val = format_ton(ton)
                    colli_val = f"{float(colli):.2f}" if colli not in [None, '', '-'] else "0.00"
                    
                    # Add row
                    table_data.append([
                        str(i),
                        container_no,
                        pengirim,
                        nama_barang,
                        kubikasi,
                        m3_val,
                        ton_val,
                        colli_val,
                        catatan[:20]  # Limit catatan length
                    ])
                    
                except Exception as e:
                    print(f"[ERROR] Error processing item {i}: {e}")
                    continue
            
            # TOTAL row - Match Invoice style
            table_data.append([
                'TOTAL',
                '',
                '',
                '',
                '',
                f"{total_m3:.3f}",
                format_ton(total_ton),
                f"{total_colli:.0f}",
                ''
            ])
            
            # Create table - Column widths optimized for A4
            items_table = Table(table_data, colWidths=[
                0.8*cm,  # No
                2.0*cm,  # No. Container
                3.0*cm,  # Pengirim
                4.5*cm,  # Jenis Barang
                2.5*cm,  # Kubikasi
                1.5*cm,  # M3
                1.5*cm,  # Ton
                1.2*cm,  # Col
                2.0*cm   # Catatan
            ])
            
            # Table styling - MATCH Invoice exactly
            items_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                
                # Data rows
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # No.
                ('ALIGN', (1, 1), (1, -2), 'CENTER'),  # Container
                ('ALIGN', (2, 1), (4, -2), 'LEFT'),    # Pengirim to Kubikasi
                ('ALIGN', (5, 1), (7, -2), 'RIGHT'),   # M3, Ton, Col
                ('ALIGN', (8, 1), (8, -2), 'LEFT'),    # Catatan
                ('VALIGN', (0, 1), (-1, -2), 'TOP'),
                
                # Total row
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, -1), (4, -1), 'CENTER'),
                ('ALIGN', (5, -1), (-1, -1), 'RIGHT'),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # ========================================
            # FOOTER SECTION - Bank info (optional)
            # ========================================
            
            footer_text = """mohon pembayaran dapat di transfer ke rekening:

    A/N : PT CAHAYA KARUNIA LOGISTIK
    468-651-1189
    BCA Cabang Surabaya"""
            
            footer_para = Paragraph(footer_text.replace('\n', '<br/>'), small_style)
            story.append(footer_para)
            story.append(Spacer(1, 10))
            
            # Signature area
            signature_text = "Surabaya,"
            story.append(Paragraph(signature_text, normal_style))
            
            # Build PDF
            print("[DEBUG] Building final PDF...")
            doc.build(story)
            print(f"[SUCCESS] PDF successfully created at: {file_path}")
            
            # Success message
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"[DEBUG] PDF file size: {file_size} bytes")
                
                if file_size > 0:
                    messagebox.showinfo(
                        "Sukses",
                        f"📄 PDF Packing List berhasil dibuat!\n\n"
                        f"📁 Lokasi: {file_path}\n"
                        f"📦 Container: {container_no}\n"
                        f"🔤 Invoice Number: {invoice_number}\n"
                        f"👤 Customer: {receiver_name}\n\n"
                        f"📅 Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
                    )
                    
                    if messagebox.askyesno("Buka File?", "Apakah Anda ingin membuka PDF sekarang?"):
                        try:
                            if os.name == 'nt':
                                os.startfile(file_path)
                            elif os.name == 'posix':
                                os.system(f'open "{file_path}"')
                        except Exception as e:
                            messagebox.showwarning("Info", f"File berhasil disimpan.\nSilakan buka manual: {file_path}")
                else:
                    print("[ERROR] PDF file created but has 0 bytes")
                    messagebox.showerror("Error", "PDF file is empty!")
            else:
                print("[ERROR] PDF file was not created")
                messagebox.showerror("Error", "PDF file was not created!")
                    
        except Exception as e:
            error_msg = f"Error in _create_pdf_document_packing: {str(e)}"
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
    
    def generate_combined_pdf_invoice_with_tax(self, container_ids, ref_joa, filter_criteria=None, all_barang=[]):
        """
        Generate combined PDF invoice for multiple containers - filter by RECEIVER ONLY
        
        Args:
            container_ids: list of container IDs to combine
            ref_joa: Reference JOA number
            filter_criteria: dict with 'receiver_name' (sender is ignored)
            all_barang: pre-collected barang list (same as packing list)
        """
        print(f"[DEBUG] Starting COMBINED PDF Invoice for JOA: {ref_joa}")
        print(f"[DEBUG] Container IDs: {container_ids}")
        print(f"[DEBUG] Filter criteria: {filter_criteria}")
        
        try:
            # Collect all containers
            all_containers = []
            
            for container_id in container_ids:
                container = self.db.get_container_by_id(container_id)
                if not container:
                    print(f"[ERROR] Container {container_id} not found!")
                    continue
                
                all_containers.append(container)
            
            # Filter barang by receiver (same logic as packing list)
            if filter_criteria:
                receiver_filter = filter_criteria.get('receiver_name', '')
                # ambil hanya barang sesuai receiver
                filtered_barang = [b for b in all_barang if b.get('receiver_name', '') == receiver_filter]
            else:
                # kalau tidak ada filter → ambil semua
                filtered_barang = all_barang
                
            all_barang = filtered_barang
            
            if not all_containers:
                messagebox.showerror("Error", "No valid containers found!")
                return
            
            if not all_barang:
                messagebox.showwarning("Warning", "No items found for selected receiver!")
                return
            
            # Count unique senders
            unique_senders = set()
            for barang in all_barang:
                if hasattr(barang, 'keys'):
                    sender = barang['sender_name'] if 'sender_name' in barang.keys() and barang['sender_name'] else ''
                else:
                    sender = barang.get('sender_name', '')
                if sender:
                    unique_senders.add(sender)
            
            print(f"[DEBUG] Combined {len(all_barang)} items from {len(all_containers)} containers")
            print(f"[DEBUG] Total {len(unique_senders)} unique senders: {', '.join(unique_senders)}")
            
            # INPUT SUFFIX untuk Combined Invoice Number
            print("[DEBUG] Asking for invoice suffix...")
            invoice_suffix = ""
            
            try:
                suffix_dialog = tk.Toplevel()
                suffix_dialog.title("Invoice Number Suffix")
                suffix_dialog.geometry("400x250")
                suffix_dialog.resizable(False, False)
                suffix_dialog.grab_set()
                suffix_dialog.transient()
                
                suffix_dialog.geometry("+%d+%d" % (suffix_dialog.winfo_screenwidth()//2 - 200, 
                                                suffix_dialog.winfo_screenheight()//2 - 125))
                
                suffix_result = {"value": "", "cancelled": True}
                
                main_frame = ttk.Frame(suffix_dialog)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                title_label = ttk.Label(main_frame, 
                                    text="Invoice Number Suffix (Combined)",
                                    font=('Arial', 12, 'bold'))
                title_label.pack(pady=(0, 10))
                
                exp_label = ttk.Label(main_frame,
                                    text="Masukkan huruf/abjad yang akan ditambahkan\ndi akhir nomor invoice (contoh: A, B, C, dst)",
                                    font=('Arial', 10))
                exp_label.pack(pady=(0, 15))
                
                example_label = ttk.Label(main_frame,
                                        text=f"Contoh: JOA {ref_joa} → Invoice JOA-{ref_joa}-A",
                                        font=('Arial', 9),
                                        foreground='blue')
                example_label.pack(pady=(0, 15))
                
                input_frame = ttk.Frame(main_frame)
                input_frame.pack(fill='x', pady=(0, 20))
                
                ttk.Label(input_frame, text="Suffix:", font=('Arial', 10)).pack(side='left')
                suffix_entry = ttk.Entry(input_frame, font=('Arial', 10), width=10)
                suffix_entry.pack(side='left', padx=(10, 0))
                suffix_entry.focus()
                
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill='x')
                
                def on_ok():
                    value = suffix_entry.get().strip().upper()
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
                invoice_suffix = ""
            
            # Generate combined PDF invoice with suffix
            self._create_pdf_invoice_document_combined(
                all_containers, 
                all_barang, 
                container_ids,
                ref_joa,
                filter_criteria,
                invoice_suffix
            )
            
            print("[DEBUG] Combined PDF invoice generation completed successfully!")
            
        except Exception as e:
            error_msg = f"Error in generate_combined_pdf_invoice_with_tax: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to create combined PDF invoice: {str(e)}")
                 
    def _create_pdf_invoice_document_combined(self, containers, barang_list, container_ids, ref_joa, filter_criteria=None, invoice_suffix=""):
        """Create combined PDF invoice for multiple containers - WITH TAX CHECK"""
        print("[DEBUG] Starting _create_pdf_invoice_document_combined - WITH TAX CHECK")
        
        try:
            # Use first container as template
            container = containers[0]
            
            # Generate filename
            filter_suffix = ""
            if filter_criteria:
                receiver = filter_criteria.get('receiver_name', 'Unknown')[:10]
                receiver = "".join(c for c in receiver if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filter_suffix = f"_{receiver}"
            
            suffix_file = f"_{invoice_suffix}" if invoice_suffix else ""
            filename = f"Invoice_Combined_JOA_{ref_joa}{suffix_file}{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            print(f"[DEBUG] Generated filename: {filename}")
            
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename,
                title="Save Combined PDF Invoice"
            )
            
            if not file_path:
                print("[DEBUG] No file path provided")
                return
            
            print(f"[DEBUG] Creating combined PDF at: {file_path}")
            
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=20, bottomMargin=50)
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18,
                                        alignment=TA_RIGHT, fontName='Helvetica-Bold', spaceAfter=0)
            company_info_style = ParagraphStyle('CompanyInfo', parent=styles['Normal'], fontSize=10,
                                            alignment=TA_LEFT, spaceAfter=10, leading=14)
            invoice_info_style = ParagraphStyle('InvoiceInfo', parent=styles['Normal'], fontSize=10,
                                            alignment=TA_RIGHT, spaceAfter=10)
            item_text_style = ParagraphStyle('ItemText', parent=styles['Normal'], fontSize=9,
                                            leading=12, alignment=TA_LEFT, wordWrap='CJK')
            
            # ========================================
            # HEADER: Logo (kiri) + Company Info (tengah) + Title (kanan)
            # ========================================
            logo_path = "assets/logo-cklogistik.jpg"
            if logo_path and os.path.exists(logo_path):
                try:
                    # LOGO DIPERBESAR (~20% lebih besar)
                    logo_img = Image(logo_path, width=8.4*cm, height=2.4*cm)

                    # TULISAN PERUSAHAAN DI SEBELAH KANAN LOGO
                    company_text = "Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607"
                    company_para = Paragraph(company_text, company_info_style)
                    title_para = Paragraph("SALES INVOICE", title_style)

                    # SUSUNAN: Logo | Company Text | Title (3 kolom)
                    # Adjusted column widths for larger logo
                    header_data = [[logo_img, company_para, title_para]]
                    header_table = Table(header_data, colWidths=[8.4*cm, 5*cm, 5.1*cm])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (0, 0), 0),
                        ('LEFTPADDING', (1, 0), (1, 0), 30),
                        ('LEFTPADDING', (2, 0), (2, 0), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))

                except Exception as logo_error:
                    print(f"[ERROR] Logo error: {logo_error}")
                    company_text = "CV. CAHAYA KARUNIA<br/>Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607"
                    company_para = Paragraph(company_text, company_info_style)
                    title_para = Paragraph("PACKING LISTS", title_style)
                    header_data = [[company_para, title_para]]
                    header_table = Table(header_data, colWidths=[10*cm, 8*cm])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
            else:
                company_text = "CV. CAHAYA KARUNIA<br/>Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607"
                company_para = Paragraph(company_text, company_info_style)
                title_para = Paragraph("PACKING LISTS", title_style)
                header_data = [[company_para, title_para]]
                header_table = Table(header_data, colWidths=[10*cm, 8*cm])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))
            
            # Safe way to get container values
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return str(container.get(key, default) or default)
                    else:
                        return str(container[key] if key in container and container[key] else default)
                except:
                    return str(default)
            
            # Build story
            story = []
            story.append(header_table)
            story.append(Spacer(1, 20))
            
            # ========================================
            # INVOICE INFO
            # ========================================
            current_month_roman = {
                1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
                7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
            }
            
            month_roman = current_month_roman.get(datetime.now().month, "IX")
            year = datetime.now().year
            base_invoice = f"{ref_joa}"
            
            if invoice_suffix:
                invoice_number = f"{base_invoice} {invoice_suffix}"
            else:
                invoice_number = base_invoice
            
            print(f"[DEBUG] Generated combined invoice number: {invoice_number}")
            
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
            
            # Customer info
            if filter_criteria:
                receiver = filter_criteria.get('receiver_name', '')
                
                # Get destination and make uppercase
                destination = safe_get('destination')
                destination_upper = destination.upper() if destination != '-' else destination
                
                customer_data = [
                    ['Bill To (Nama Customer)', ':', receiver, '', 'Invoice Number', ':', invoice_number],
                    ['', '', '', '', '', '', ''],
                    ['Feeder (Nama Kapal)', ':', safe_get('feeder'), '', 'Tanggal (ETD)', ':', formatted_etd],  
                    ['Destination (Tujuan)', ':', destination_upper, '', 'Party (Volume)', ':', f"{safe_get('party')} m3"],
                ]
                
                # Adjusted column widths - kecilkan kolom kiri, besarkan kolom kanan untuk invoice number
                customer_table = Table(customer_data, colWidths=[4*cm, 0.3*cm, 4.5*cm, 0.8*cm, 3.2*cm, 0.3*cm, 5.4*cm])
                customer_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                    ('ALIGN', (4, 0), (4, -1), 'LEFT'),
                    ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                    ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                
                story.append(customer_table)
                story.append(Spacer(1, 20))
            
            # ========================================
            # GET TAX INFORMATION - CEK FIELD PAJAK ✅
            # ========================================
            tax_summary = {}
            try:
                if filter_criteria:
                    receiver = filter_criteria.get('receiver_name', '')
                    
                    # Aggregate tax from all containers - DENGAN CEK PAJAK
                    total_ppn_amount = 0
                    total_pph_amount = 0
                    ppn_rates = []
                    pph_rates = []
                    has_any_taxable = False  # Flag untuk cek apakah ada barang kena pajak
                    
                    for container_id in container_ids:
                        # QUERY BARU - Join dengan barang untuk cek field pajak = 1
                        tax_query = """
                            SELECT 
                                AVG(bt.ppn_rate) as avg_ppn_rate,
                                AVG(bt.pph23_rate) as avg_pph_rate,
                                SUM(bt.ppn_amount) as total_ppn_amount,
                                SUM(bt.pph23_amount) as total_pph_amount
                            FROM barang_tax bt
                            INNER JOIN barang b ON bt.barang_id = b.barang_id
                            WHERE bt.container_id = ? 
                            AND bt.penerima = ?
                            AND b.pajak = 1
                        """
                        result = self.db.execute(tax_query, (container_id, receiver))
                        
                        if result and len(result) > 0:
                            row = result[0]
                            if row['avg_ppn_rate'] or row['avg_pph_rate']:
                                has_any_taxable = True
                                
                            if row['avg_ppn_rate']:
                                ppn_rates.append(row['avg_ppn_rate'])
                            if row['avg_pph_rate']:
                                pph_rates.append(row['avg_pph_rate'])
                            total_ppn_amount += row['total_ppn_amount'] or 0
                            total_pph_amount += row['total_pph_amount'] or 0
                    
                    # Hanya set has_tax = True jika ada barang dengan pajak = 1
                    if has_any_taxable and (ppn_rates or pph_rates):
                        avg_ppn = (sum(ppn_rates) / len(ppn_rates)) if ppn_rates else 0
                        avg_pph = (sum(pph_rates) / len(pph_rates)) if pph_rates else 0
                        
                        tax_summary[receiver] = {
                            'ppn_rate': avg_ppn * 100,
                            'pph_rate': avg_pph * 100,
                            'ppn_amount': total_ppn_amount,
                            'pph_amount': total_pph_amount,
                            'has_tax': True
                        }
                        print(f"[DEBUG] Combined tax found: PPN=Rp {total_ppn_amount:,.0f}, PPH=Rp {total_pph_amount:,.0f}")
                    else:
                        # TIDAK ADA PAJAK
                        tax_summary[receiver] = {
                            'ppn_rate': 0, 'pph_rate': 0, 
                            'ppn_amount': 0, 'pph_amount': 0, 
                            'has_tax': False
                        }
                        print(f"[DEBUG] No taxable items found (pajak = 0 or no barang with pajak = 1)")
            except Exception as e:
                print(f"[ERROR] Getting tax info: {e}")
                import traceback
                traceback.print_exc()
            
            # ========================================
            # ITEMS TABLE WITH PRICING - DENGAN KOLOM PENGIRIM ✅
            # ========================================
            
            # Prepare data with container info
            items_with_container = []
            for barang_row in barang_list:
                try:
                    if hasattr(barang_row, 'keys'):
                        barang = {key: barang_row[key] for key in barang_row.keys()}
                    else:
                        barang = dict(barang_row)
                    
                    # Get container number for this item
                    item_container_id = barang.get('container_id', container_ids[0])
                    item_container = next((c for c, cid in zip(containers, container_ids) if cid == item_container_id), container)
                    container_no = item_container.get('container', f'ID {item_container_id}') if hasattr(item_container, 'get') else str(item_container_id)
                    
                    items_with_container.append({
                        'barang': barang,
                        'container_no': container_no
                    })
                except Exception as e:
                    print(f"[ERROR] Processing barang: {e}")
                    continue
            
            # Table header - DENGAN KOLOM PENGIRIM ✅
            table_data = [[
                'No.', 
                'Container',
                'Pengirim',      # ✅ KOLOM BARU
                'Jenis Barang', 
                'Kubikasi', 
                'M3', 
                'Ton', 
                'Col',
                'Unit Price',
                'Total Price'
            ]]
            
            # Totals
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            total_price = 0
            
            item_counter = 1
            
            # Process each item - DENGAN KOLOM PENGIRIM ✅
            for item in items_with_container:
                try:
                    barang = item['barang']
                    container_no = item['container_no']
                    
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except Exception:
                            return default
                    
                    # Pengirim - AMBIL DATA PENGIRIM ✅
                    pengirim_text = str(safe_barang_get('sender_name', '-'))
                    pengirim = Paragraph(pengirim_text, item_text_style)
                    
                    # Jenis Barang (TANPA pengirim karena sudah ada kolom terpisah) ✅
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))
                    
                    # Hanya tampilkan nama barang dan jenis barang
                    combined_text = f"{nama_barang}"
                    
                    if jenis_barang != '-' and jenis_barang != nama_barang:
                        combined_text += f"<br/><i>{jenis_barang}</i>"
                    
                    combined_jenis = Paragraph(combined_text, item_text_style)
                    
                    # Kubikasi
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')

                    try:
                        p = str(float(p)) if p != '-' else '-'
                        l = str(float(l)) if l != '-' else '-'
                        t = str(float(t)) if t != '-' else '-'
                    except (ValueError, TypeError):
                        pass

                    kubikasi_text = f"{p}*{l}*{t}"
                    kubikasi = Paragraph(kubikasi_text, item_text_style)
                    
                    # Values
                    m3_per_unit = safe_barang_get('m3_barang', 0)
                    ton_per_unit = safe_barang_get('ton_barang', 0)
                    colli = safe_barang_get('colli_amount', 0)
                    unit_price = safe_barang_get('harga_per_unit', 0)
                    total_harga = safe_barang_get('total_harga', 0)
                    
                    # Convert to float/int for calculation
                    try:
                        m3_float = float(m3_per_unit) if m3_per_unit not in [None, '', '-'] else 0
                        ton_float = float(ton_per_unit) if ton_per_unit not in [None, '', '-'] else 0
                        colli_int = int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        m3_float = 0
                        ton_float = 0
                        colli_int = 0
                    
                    # Calculate total: M3 * Colli and Ton * Colli
                    total_m3_item = m3_float * colli_int
                    total_ton_item = ton_float * colli_int
                    
                    # Add to grand total
                    total_m3 += total_m3_item
                    total_ton += total_ton_item
                    total_colli += colli_int
                    
                    try:
                        total_price += float(total_harga) if total_harga not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        pass
                    
                    # Format values - CONDITIONAL DECIMAL FORMATTING ✅
                    if total_m3_item >= 1:
                        m3_val = f"{total_m3_item:.0f}"  # Tanpa desimal jika >= 1
                    else:
                        m3_val = f"{total_m3_item:.3f}"  # 3 desimal jika < 1

                    ton_val = format_ton(total_ton_item)

                    colli_val = f"{colli_int}"
                    unit_price_val = f"Rp {float(unit_price):,.0f}" if unit_price not in [None, '', '-'] else "Rp 0"
                    total_price_val = f"Rp {float(total_harga):,.0f}" if total_harga not in [None, '', '-'] else "Rp 0"
                    
                    # Append row - DENGAN KOLOM PENGIRIM ✅
                    table_data.append([
                        str(item_counter), 
                        container_no,
                        pengirim,           # ✅ KOLOM PENGIRIM
                        combined_jenis,
                        kubikasi,
                        m3_val,
                        ton_val, 
                        colli_val,
                        unit_price_val,
                        total_price_val
                    ])
                    
                    item_counter += 1
                    
                except Exception as e:
                    print(f"[ERROR] Error processing item {item_counter}: {e}")
                    continue
            
            # ========================================
            # ADD TAX ROWS - HANYA JIKA has_tax = True ✅
            # ========================================
            tax_row_count = 0  # Counter untuk track berapa baris pajak
            receiver = filter_criteria.get('receiver_name', '') if filter_criteria else ''
            if receiver in tax_summary and tax_summary[receiver]['has_tax']:
                tax_data = tax_summary[receiver]
                
                # PPN row - DENGAN KOLOM PENGIRIM KOSONG ✅
                if tax_data['ppn_amount'] > 0:
                    table_data.append([
                        '', '', '', f"PPN {tax_data['ppn_rate']:.1f}%",  # Kolom pengirim kosong
                        '', '', '', '', '', f"Rp {tax_data['ppn_amount']:,.0f}"
                    ])
                    total_price += tax_data['ppn_amount']
                    tax_row_count += 1
                    print(f"[DEBUG] Added PPN row: Rp {tax_data['ppn_amount']:,.0f}")
                
                # PPH row (PPH 23) - DENGAN KOLOM PENGIRIM KOSONG ✅
                if tax_data['pph_amount'] > 0:
                    table_data.append([
                        '', '', '', f"PPH 23",  # Kolom pengirim kosong
                        '', '', '', '', '', f"- Rp {tax_data['pph_amount']:,.0f}"
                    ])
                    total_price += tax_data['pph_amount']
                    tax_row_count += 1
                    print(f"[DEBUG] Added PPH row: Rp {tax_data['pph_amount']:,.0f}")
            else:
                print("[DEBUG] No tax rows added (has_tax = False)")
            
            # Add total row - MERGE 5 KOLOM (termasuk pengirim) ✅
            total_row_index = len(table_data)
            
            # Format total M3 dan Ton dengan conditional decimal ✅
            total_m3_formatted = f"{total_m3:.0f}" if total_m3 >= 1 else f"{total_m3:.3f}"
            total_ton_formatted = format_ton(total_ton)
            
            table_data.append([
                'TOTAL',  # Akan di-merge dengan 4 kolom berikutnya
                '', 
                '', 
                '', 
                '',  # Kolom Pengirim kosong
                total_m3_formatted,
                total_ton_formatted, 
                f"{total_colli:.0f}",
                '',
                f"Rp {total_price:,.0f}"
            ])
            
            # Create table - DENGAN LEBAR KOLOM DISESUAIKAN ✅
            items_table = Table(table_data, colWidths=[
                1.2*cm,  # No (dikurangi)
                1.8*cm,  # Container (dikurangi)
                2.5*cm,  # Pengirim ✅ BARU
                3.5*cm,  # Jenis Barang (dikurangi karena tanpa pengirim)
                2.5*cm,  # Kubikasi (dikurangi)
                1.3*cm,  # M3 (dikurangi)
                1.3*cm,  # Ton (dikurangi)
                1.0*cm,  # Col (dikurangi)
                2.0*cm,  # Unit Price (dikurangi)
                2.4*cm   # Total Price
            ])
            
            # Table styling - DENGAN INDEX KOLOM DISESUAIKAN ✅
            style_list = [
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTSIZE', (0, 0), (-1, 0), 9),  # Font lebih kecil karena lebih banyak kolom
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                
                # Data rows
                ('FONTSIZE', (0, 1), (-1, total_row_index - 1), 8),  # Font lebih kecil
                ('FONTNAME', (0, 1), (-1, total_row_index - 1), 'Helvetica'),
                ('ALIGN', (0, 1), (1, total_row_index - 1), 'CENTER'),  # No & Container
                ('ALIGN', (2, 1), (2, total_row_index - 1), 'LEFT'),    # Pengirim ✅
                ('ALIGN', (3, 1), (4, total_row_index - 1), 'LEFT'),    # Jenis Barang & Kubikasi
                ('ALIGN', (5, 1), (-1, total_row_index - 1), 'RIGHT'),  # M3, Ton, Col, Prices
                ('VALIGN', (0, 1), (-1, total_row_index - 1), 'TOP'),
                
                # Total row - MERGE 5 KOLOM (0-4, termasuk pengirim) ✅
                ('SPAN', (0, total_row_index), (4, total_row_index)),  # ✅ Merge 5 kolom
                ('FONTSIZE', (0, total_row_index), (-1, total_row_index), 10),
                ('FONTNAME', (0, total_row_index), (-1, total_row_index), 'Helvetica-Bold'),
                ('BACKGROUND', (0, total_row_index), (-1, total_row_index), colors.lightgrey),
                ('ALIGN', (0, total_row_index), (0, total_row_index), 'CENTER'),
                ('ALIGN', (5, total_row_index), (-1, total_row_index), 'RIGHT'),
                ('VALIGN', (0, total_row_index), (-1, total_row_index), 'MIDDLE'),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Padding - dikurangi untuk fit lebih banyak kolom
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]
            
            items_table.setStyle(TableStyle(style_list))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # Build PDF
            print("[DEBUG] Building final combined PDF invoice...")
            doc.build(story)
            print(f"[SUCCESS] Combined PDF invoice created at: {file_path}")
            
            # Success message
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                if file_size > 0:
                    # Build display invoice number
                    display_invoice = base_invoice
                    if invoice_suffix:
                        display_invoice += f" {invoice_suffix}"
                    
                    messagebox.showinfo(
                        "Success",
                        f"✅ Combined Invoice PDF created!\n\n"
                        f"📁 Location: {file_path}\n"
                        f"📦 Containers: {len(containers)}\n"
                        f"📄 REF JOA: {ref_joa}\n"
                        f"🔤 Invoice Number: {display_invoice}\n"
                        f"💰 Total Amount: Rp {total_price:,.0f}\n\n"
                        f"📅 Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
                    )
                    
                    if messagebox.askyesno("Open File?", "Open the PDF now?"):
                        try:
                            if os.name == 'nt':
                                os.startfile(file_path)
                            elif os.name == 'posix':
                                os.system(f'open "{file_path}"')
                        except Exception as e:
                            messagebox.showwarning("Info", f"File saved but couldn't open automatically.\nPlease open manually: {file_path}")
                            
        except Exception as e:
            error_msg = f"Error in _create_pdf_invoice_document_combined: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to create combined PDF: {str(e)}")
            
             
    def generate_combined_pdf_packing_list(self, container_ids, ref_joa, filter_criteria=None, all_barang = []):
        """
        Generate combined PDF packing list for multiple containers - filter by RECEIVER ONLY
        
        Args:
            container_ids: list of container IDs
            ref_joa: Reference JOA number
            filter_criteria: dict with 'receiver_name' (sender ignored)
        """
        print(f"[DEBUG] Starting COMBINED Packing List PDF for JOA: {ref_joa}")
        print(f"[DEBUG] Container IDs: {container_ids}")
        print(f"[DEBUG] Filter criteria: {filter_criteria}")
        
        try:
            # Collect all containers and barang
            all_containers = []
            
            for container_id in container_ids:
                container = self.db.get_container_by_id(container_id)
                if not container:
                    print(f"[ERROR] Container {container_id} not found!")
                    continue
                
                all_containers.append(container)
                
            if filter_criteria:
                receiver_filter = filter_criteria.get('receiver_name', '')
                # ambil hanya barang sesuai receiver
                filtered_barang = [b for b in all_barang if b.get('receiver_name', '') == receiver_filter]
            else:
                # kalau tidak ada filter → ambil semua
                filtered_barang = all_barang
                
            all_barang = filtered_barang
            
            
            if not all_containers:
                messagebox.showerror("Error", "No valid containers found!")
                return
            
            if not all_barang:
                messagebox.showwarning("Warning", "No items found for selected receiver!")
                return
            
            # Count unique senders
            unique_senders = set()
            for barang in all_barang:
                if hasattr(barang, 'keys'):
                    sender = barang['sender_name'] if 'sender_name' in barang.keys() and barang['sender_name'] else ''
                else:
                    sender = barang.get('sender_name', '')
                if sender:
                    unique_senders.add(sender)
            
            print(f"[DEBUG] Combined {len(all_barang)} items from {len(all_containers)} containers")
            print(f"[DEBUG] Total {len(unique_senders)} unique senders: {', '.join(unique_senders)}")
            
            # INPUT SUFFIX
            print("[DEBUG] Asking for suffix...")
            invoice_suffix = ""
            
            try:
                suffix_dialog = tk.Toplevel()
                suffix_dialog.title("Packing List Number Suffix")
                suffix_dialog.geometry("400x250")
                suffix_dialog.resizable(False, False)
                suffix_dialog.grab_set()
                suffix_dialog.transient()
                
                suffix_dialog.geometry("+%d+%d" % (suffix_dialog.winfo_screenwidth()//2 - 200, 
                                                suffix_dialog.winfo_screenheight()//2 - 125))
                
                suffix_result = {"value": "", "cancelled": True}
                
                main_frame = ttk.Frame(suffix_dialog)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                title_label = ttk.Label(main_frame, 
                                    text="Packing List Number Suffix (Combined)",
                                    font=('Arial', 12, 'bold'))
                title_label.pack(pady=(0, 10))
                
                exp_label = ttk.Label(main_frame,
                                    text="Masukkan huruf/abjad suffix\n(contoh: A, B, C, dst)",
                                    font=('Arial', 10))
                exp_label.pack(pady=(0, 15))
                
                example_label = ttk.Label(main_frame,
                                        text=f"Contoh: JOA {ref_joa} → PL JOA-{ref_joa}-A",
                                        font=('Arial', 9),
                                        foreground='blue')
                example_label.pack(pady=(0, 15))
                
                input_frame = ttk.Frame(main_frame)
                input_frame.pack(fill='x', pady=(0, 20))
                
                ttk.Label(input_frame, text="Suffix:", font=('Arial', 10)).pack(side='left')
                suffix_entry = ttk.Entry(input_frame, font=('Arial', 10), width=10)
                suffix_entry.pack(side='left', padx=(10, 0))
                suffix_entry.focus()
                
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill='x')
                
                def on_ok():
                    value = suffix_entry.get().strip().upper()
                    if value and not value.isalpha():
                        messagebox.showwarning("Peringatan", "Hanya huruf/abjad!")
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
                ttk.Button(button_frame, text="Skip", command=on_skip).pack(side='left', padx=5)
                ttk.Button(button_frame, text="Batal", command=on_cancel).pack(side='right')
                
                suffix_dialog.bind("<Return>", lambda e: on_ok())
                suffix_dialog.bind("<Escape>", lambda e: on_cancel())
                
                suffix_dialog.wait_window()
                
                if suffix_result["cancelled"]:
                    print("[DEBUG] User cancelled")
                    return
                
                invoice_suffix = suffix_result["value"]
                print(f"[DEBUG] Suffix: '{invoice_suffix}'")
                
            except Exception as suffix_error:
                print(f"[ERROR] Suffix dialog error: {suffix_error}")
                invoice_suffix = ""
            
            # Generate combined PDF
            self._create_combined_packing_list_pdf(
                all_containers, 
                all_barang, 
                container_ids,
                ref_joa,
                filter_criteria,
                invoice_suffix
            )
            
            print("[DEBUG] Combined packing list PDF completed!")
            
        except Exception as e:
            error_msg = f"Error in generate_combined_pdf_packing_list: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed: {str(e)}")

    def _create_combined_packing_list_pdf(self, containers, barang_list, container_ids, ref_joa, filter_criteria=None, invoice_suffix=""):
        """Create combined packing list PDF - Container as separate column"""
        print("[DEBUG] Starting _create_combined_packing_list_pdf - Container Column")
        
        try:
            container = containers[0]  # Use first as template
            
            # Generate filename
            filter_suffix = ""
            if filter_criteria:
                receiver = filter_criteria.get('receiver_name', 'Unknown')[:10]
                receiver = "".join(c for c in receiver if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filter_suffix = f"_{receiver}"
            
            suffix_file = f"_{invoice_suffix}" if invoice_suffix else ""
            filename = f"PackingList_Combined_JOA_{ref_joa}{suffix_file}{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            print(f"[DEBUG] Filename: {filename}")
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename,
                title="Save Combined Sales Invoice PDF"
            )
            
            if not file_path:
                return
            
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=20, bottomMargin=50)
            
            styles = getSampleStyleSheet()
            
            # Styles
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16,
                                        alignment=TA_RIGHT, fontName='Helvetica-Bold', spaceAfter=0)
            company_info_style = ParagraphStyle('CompanyInfo', parent=styles['Normal'], fontSize=9,
                                            alignment=TA_LEFT, spaceAfter=10)
            invoice_info_style = ParagraphStyle('InvoiceInfo', parent=styles['Normal'], fontSize=9,
                                            alignment=TA_RIGHT, spaceAfter=10)
            item_text_style = ParagraphStyle('ItemText', parent=styles['Normal'], fontSize=8,
                                            leading=11, alignment=TA_LEFT, wordWrap='CJK')
            
            # ========================================
            # HEADER: Logo + Company Info + Title
            # ========================================
            logo_path = "assets/logo-cklogistik.jpg"
            if logo_path and os.path.exists(logo_path):
                try:
                    # LOGO DIPERBESAR (~20% lebih besar)
                    logo_img = Image(logo_path, width=8.4*cm, height=2.4*cm)

                    # TULISAN PERUSAHAAN DI SEBELAH KANAN LOGO
                    company_text = "Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607"
                    company_para = Paragraph(company_text, company_info_style)
                    title_para = Paragraph("PACKING LISTS", title_style)

                    # SUSUNAN: Logo | Company Text | Title (3 kolom)
                    # Adjusted column widths for larger logo
                    header_data = [[logo_img, company_para, title_para]]
                    header_table = Table(header_data, colWidths=[8.4*cm, 5*cm, 5.1*cm])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (0, 0), 0),
                        ('LEFTPADDING', (1, 0), (1, 0), 30),
                        ('LEFTPADDING', (2, 0), (2, 0), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    
                except Exception as logo_error:
                    print(f"[ERROR] Logo error: {logo_error}")
                    company_text = "CV. CAHAYA KARUNIA<br/>Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607"
                    company_para = Paragraph(company_text, company_info_style)
                    title_para = Paragraph("PACKING LISTS", title_style)
                    header_data = [[company_para, title_para]]
                    header_table = Table(header_data, colWidths=[10*cm, 8*cm])
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
            else:
                company_text = "CV. CAHAYA KARUNIA<br/>Jln. Teluk Bone Selatan No. 5. Surabaya<br/>Phone: 031-5016607"
                company_para = Paragraph(company_text, company_info_style)
                title_para = Paragraph("PACKING LISTS", title_style)
                header_data = [[company_para, title_para]]
                header_table = Table(header_data, colWidths=[10*cm, 8*cm])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))
            
            def safe_get(key, default='-'):
                try:
                    if hasattr(container, 'get'):
                        return str(container.get(key, default) or default)
                    else:
                        return str(container[key] if key in container and container[key] else default)
                except:
                    return str(default)
            
            story = []
            story.append(header_table)
            story.append(Spacer(1, 15))
            
            # ========================================
            # INVOICE INFO
            # ========================================
            current_month_roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
                                7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}
            month_roman = current_month_roman.get(datetime.now().month, "IX")
            year = datetime.now().year
            base_invoice = f"{ref_joa}"
            
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
            
            # Customer info
            if filter_criteria:
                receiver = filter_criteria.get('receiver_name', '')
                
                destination = safe_get('destination')
                destination_upper = destination.upper() if destination != '-' else destination
                
                customer_data = [
                    ['Bill To (Nama Customer)', ':', receiver, '', 'Invoice Number', ':', invoice_number],
                    ['', '', '', '', '', '', ''],
                    ['Feeder (Nama Kapal)', ':', safe_get('feeder'), '', 'Tanggal (ETD)', ':', formatted_etd],  
                    ['Destination (Tujuan)', ':', destination_upper, '', 'Party (Volume)', ':', f"{safe_get('party')} m3"],
                ]
                
                customer_table = Table(customer_data, colWidths=[4*cm, 0.3*cm, 5*cm, 1*cm, 3.5*cm, 0.3*cm, 4.9*cm])
                customer_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                    ('ALIGN', (4, 0), (4, -1), 'LEFT'),
                    ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                    ('ALIGN', (6, 0), (6, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(customer_table)
                story.append(Spacer(1, 15))
            
            # ========================================
            # ITEMS TABLE - DENGAN KOLOM CONTAINER DAN PENGIRIM
            # ========================================
            
            # Prepare data with container info
            items_with_container = []
            for barang_row in barang_list:
                try:
                    if hasattr(barang_row, 'keys'):
                        barang = {key: barang_row[key] for key in barang_row.keys()}
                    else:
                        barang = dict(barang_row)
                    
                    # Get container number for this item
                    item_container_id = barang.get('container_id', container_ids[0])
                    item_container = next((c for c, cid in zip(containers, container_ids) if cid == item_container_id), container)
                    container_no = item_container.get('container', f'ID {item_container_id}') if hasattr(item_container, 'get') else str(item_container_id)
                    
                    items_with_container.append({
                        'barang': barang,
                        'container_no': container_no
                    })
                except Exception as e:
                    print(f"[ERROR] Processing barang: {e}")
                    continue
            
            # Table header - TAMBAH KOLOM PENGIRIM
            table_data = [[
                'No.', 
                'Container',
                'Pengirim',
                'Jenis Barang', 
                'Kubikasi', 
                'M3', 
                'Ton', 
                'Col',
                'Catatan'
            ]]
            
            total_m3 = 0
            total_ton = 0
            total_colli = 0
            
            item_counter = 1
            
            # Process each item
            for item in items_with_container:
                try:
                    barang = item['barang']
                    container_no = item['container_no']
                    
                    def safe_barang_get(key, default='-'):
                        try:
                            value = barang.get(key, default)
                            return value if value not in [None, '', 'NULL', 'null'] else default
                        except:
                            return default
                    
                    # Pengirim - KOLOM TERPISAH
                    pengirim_text = str(safe_barang_get('sender_name', '-'))
                    pengirim_para = Paragraph(pengirim_text, item_text_style)
                    
                    # Jenis Barang (TANPA pengirim karena sudah terpisah)
                    nama_barang = str(safe_barang_get('nama_barang', '-'))
                    jenis_barang = str(safe_barang_get('jenis_barang', '-'))
                    
                    combined_text = f"{nama_barang}"
                    
                    if jenis_barang != '-' and jenis_barang != nama_barang:
                        combined_text += f"<br/><i>{jenis_barang}</i>"
                    
                    combined_jenis = Paragraph(combined_text, item_text_style)
                    
                    # Kubikasi
                    p = safe_barang_get('panjang_barang', '-')
                    l = safe_barang_get('lebar_barang', '-')
                    t = safe_barang_get('tinggi_barang', '-')
                    
                    try:
                        p = str(float(p)) if p != '-' else '-'
                        l = str(float(l)) if l != '-' else '-'
                        t = str(float(t)) if t != '-' else '-'
                    except (ValueError, TypeError):
                        pass
                    
                    kubikasi_text = f"{p}*{l}*{t}"
                    kubikasi = Paragraph(kubikasi_text, item_text_style)
                    
                    # Values
                    colli = safe_barang_get('colli_amount', 0)
                    m3_per_unit = safe_barang_get('m3_barang', 0)
                    ton_per_unit = safe_barang_get('ton_barang', 0)
                    catatan = str(safe_barang_get('keterangan', safe_barang_get('notes', '')))
                    
                    # Convert to float/int
                    try:
                        m3_float = float(m3_per_unit) if m3_per_unit not in [None, '', '-'] else 0
                        ton_float = float(ton_per_unit) if ton_per_unit not in [None, '', '-'] else 0
                        colli_int = int(colli) if colli not in [None, '', '-'] else 0
                    except (ValueError, TypeError):
                        m3_float = 0
                        ton_float = 0
                        colli_int = 0
                    
                    # Calculate total per item
                    total_m3_item = m3_float * colli_int
                    total_ton_item = ton_float * colli_int
                    
                    # Add to grand total
                    total_m3 += total_m3_item
                    total_ton += total_ton_item
                    total_colli += colli_int
                    
                    # Format values - CONDITIONAL DECIMAL FORMATTING ✅
                    if total_m3_item >= 1:
                        m3_val = f"{total_m3_item:.0f}"  # Tanpa desimal jika >= 1
                    else:
                        m3_val = f"{total_m3_item:.3f}"  # 3 desimal jika < 1

                    ton_val = format_ton(total_ton_item)

                    colli_val = f"{colli_int:.0f}"
                    
                    # Item row - DENGAN KOLOM PENGIRIM
                    table_data.append([
                        str(item_counter),
                        container_no,
                        pengirim_para,
                        combined_jenis,
                        kubikasi,
                        m3_val,
                        ton_val,
                        colli_val,
                        catatan[:30]
                    ])
                    
                    item_counter += 1
                    
                except Exception as e:
                    print(f"[ERROR] Item error: {e}")
                    continue
            
            # TOTAL row - DENGAN CONDITIONAL DECIMAL FORMATTING ✅
            total_m3_formatted = f"{total_m3:.0f}" if total_m3 >= 1 else f"{total_m3:.3f}"
            total_ton_formatted = format_ton(total_ton)
            
            table_data.append([
                'TOTAL',
                '',  # Will be merged
                '',  # Will be merged
                '',  # Will be merged
                '',  # Will be merged
                total_m3_formatted,
                total_ton_formatted,
                f"{total_colli:.0f}",
                ''
            ])
            
            # Create table - ADJUSTED COLUMN WIDTHS
            items_table = Table(table_data, colWidths=[
                1.2*cm,  # No
                2.0*cm,  # Container
                2.5*cm,  # Pengirim (BARU)
                4.5*cm,  # Jenis Barang
                2.0*cm,  # Kubikasi
                1.4*cm,  # M3
                1.4*cm,  # Ton
                1.2*cm,  # Col
                3.0*cm   # Catatan
            ])
            
            # Table styling
            style_commands = [
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                
                # Data rows
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # No
                ('ALIGN', (1, 1), (1, -2), 'CENTER'),  # Container
                ('ALIGN', (2, 1), (2, -2), 'LEFT'),    # Pengirim
                ('ALIGN', (3, 1), (4, -2), 'LEFT'),    # Jenis Barang & Kubikasi
                ('ALIGN', (5, 1), (7, -2), 'RIGHT'),   # M3, Ton, Col
                ('ALIGN', (8, 1), (8, -2), 'LEFT'),    # Catatan
                ('VALIGN', (0, 1), (-1, -2), 'TOP'),
                
                # Total row
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                
                # SPAN UNTUK TOTAL - MERGE 5 KOLOM PERTAMA
                ('SPAN', (0, -1), (4, -1)),
                ('ALIGN', (0, -1), (0, -1), 'CENTER'),  # TOTAL text centered
                ('ALIGN', (5, -1), (-1, -1), 'RIGHT'),  # Numbers right aligned
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]
            
            items_table.setStyle(TableStyle(style_commands))
            
            story.append(items_table)
            story.append(Spacer(1, 15))
            
            # Build
            doc.build(story)
            print(f"[SUCCESS] Combined sales invoice created: {file_path}")
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                if file_size > 0:
                    display_invoice = base_invoice
                    if invoice_suffix:
                        display_invoice += f" {invoice_suffix}"
                    
                    messagebox.showinfo("Success",
                        f"✅ Combined Sales Invoice PDF created!\n\n"
                        f"📁 Location: {file_path}\n"
                        f"📦 Containers: {len(containers)}\n"
                        f"📄 REF JOA: {ref_joa}\n"
                        f"🔤 Invoice Number: {display_invoice}\n\n"
                        f"📅 Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
                    
                    if messagebox.askyesno("Open?", "Open PDF now?"):
                        try:
                            if os.name == 'nt':
                                os.startfile(file_path)
                            elif os.name == 'posix':
                                os.system(f'open "{file_path}"')
                        except Exception as e:
                            messagebox.showwarning("Info", f"File saved.\nOpen manually: {file_path}")
                            
        except Exception as e:
            error_msg = f"Error in _create_combined_packing_list_pdf: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed: {str(e)}")
            
            