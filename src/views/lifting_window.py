import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, timedelta
from src.models.database import AppDatabase


class LiftingWindow:
    def __init__(self, parent, db: AppDatabase):
        self.parent = parent
        self.db = db
        self.create_window()

    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("📦 Lifting Report (Biaya POL & POD)")
        self.window.configure(bg="#ecf0f1")

        # === Ukuran & posisi tengah ===
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        scale = max(0.8, min(screen_width / 1920, 1.0))
        width = int(1400 * scale)
        height = int(800 * scale)
        x_pos = int((screen_width / 2) - (width / 2))
        y_pos = int((screen_height / 2) - (height / 2))
        self.window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        self.window.minsize(900, 600)

        # === Font ===
        font_small = ("Arial", int(11 * scale))
        font_normal = ("Arial", int(12 * scale))
        font_bold = ("Arial", int(13 * scale), "bold")
        font_title = ("Arial", int(16 * scale), "bold")

        # === Header ===
        title = tk.Label(
            self.window,
            text="📦 LAPORAN LIFTING (BIAYA POL & POD)",
            font=font_title,
            bg="#27ae60",
            fg="white",
            pady=int(8 * scale)
        )
        title.pack(fill="x")

        # === Filter Frame ===
        filter_frame = tk.Frame(self.window, bg="#ffffff", relief="solid", bd=1)
        filter_frame.pack(fill="x", padx=20, pady=(10, 0))

        tk.Label(
            filter_frame,
            text="🔍 Filter Tanggal (berdasarkan ETD SUB kapal):",
            font=font_bold,
            fg="#2c3e50",
            bg="#ffffff"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        controls = tk.Frame(filter_frame, bg="#ffffff")
        controls.pack(fill="x", padx=10, pady=(0, 10))

        # === Date pickers ===
        tk.Label(controls, text="Dari:", bg="#ffffff", font=font_normal).pack(side="left", padx=(0, 5))
        self.start_date = DateEntry(
            controls,
            date_pattern='yyyy-mm-dd',
            width=int(14 * scale),
            font=font_normal,
            borderwidth=2,
            background="white",
            selectmode="day",
            showweeknumbers=False,
            showothermonthdays=False,
            state="readonly"  # biar gak bisa ketik manual
        )
        try:
            self.start_date._top_cal.configure(showdropdowns=True)  # aktifkan dropdown bulan/tahun kalau versi mendukung
        except Exception:
            pass
        self.start_date.set_date(date.today() - timedelta(days=30))
        self.start_date.pack(side="left", padx=(0, 20))

        tk.Label(controls, text="Sampai:", bg="#ffffff", font=font_normal).pack(side="left", padx=(0, 5))
        self.end_date = DateEntry(
            controls,
            date_pattern='yyyy-mm-dd',
            width=int(14 * scale),
            font=font_normal,
            borderwidth=2,
            background="white",
            selectmode="day",
            showweeknumbers=False,
            showothermonthdays=False,
            state="readonly"
        )
        try:
            self.end_date._top_cal.configure(showdropdowns=True)
        except Exception:
            pass
        self.end_date.set_date(date.today())
        self.end_date.pack(side="left", padx=(0, 20))

        # === Tombol Filter & Clear ===
        tk.Button(
            controls, text="🔍 Filter", bg="#3498db", fg="white", font=font_bold,
            padx=int(12 * scale), pady=int(5 * scale), command=self.filter_data
        ).pack(side="left", padx=8)

        tk.Button(
            controls, text="❌ Clear", bg="#e67e22", fg="white", font=font_bold,
            padx=int(12 * scale), pady=int(5 * scale), command=self.clear_filter
        ).pack(side="left", padx=8)

        # === Table ===
        table_frame = tk.Frame(self.window, bg="#ecf0f1")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical")

        columns = [
            "ETD SUB", "NO JOA", "THC POL", "Freight POL", "Seal POL", "Cleaning POL", "OPS POL",
            "Asuransi POL", "PPH POL", "PPN POL", "TOTAL BIAYA POL",
            "THC POD", "OPS POD", "Seal POD", "Cleaning POD", "TOTAL BIAYA POD",
            "TOTAL BIAYA", "NILAI INVOICE", "PROFIT"
        ]

        self.tree = ttk.Treeview(
            table_frame, show="headings", columns=columns,
            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set
        )
        self.tree.pack(fill="both", expand=True)
        x_scroll.config(command=self.tree.xview)
        y_scroll.config(command=self.tree.yview)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

        # === Style Table ===
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#27ae60", foreground="white", font=font_bold)
        style.configure("Treeview", font=font_small, rowheight=int(26 * scale))
        style.map("Treeview", background=[("selected", "#3498db")])

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=int(120 * scale), anchor="center")

        self.tree.tag_configure("evenrow", background="#f8f9fa")
        self.tree.tag_configure("oddrow", background="#eaf2ef")

        # === Footer ===
        footer_frame = tk.Frame(self.window, bg="#27ae60")
        footer_frame.pack(fill="x", pady=(5, 0))
        self.total_label = tk.Label(
            footer_frame,
            text="TOTAL PROFIT: Rp 0",
            font=font_bold,
            fg="white",
            bg="#27ae60",
            pady=int(5 * scale)
        )
        self.total_label.pack(side="right", padx=20)

        self.load_data_from_db()

    # ============================================================
    def load_data_from_db(self, start_date=None, end_date=None):
        try:
            query = """
                WITH invoice_per_container AS (
                    SELECT container_id, SUM(total_harga) AS total_invoice
                    FROM detail_container
                    GROUP BY container_id
                ),
                delivery_per_container AS (
                    SELECT
                        cdc.container_id,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%THC%' THEN cdc.cost ELSE 0 END) AS thc_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%Freight%' THEN cdc.cost ELSE 0 END) AS freight_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%Seal%' THEN cdc.cost ELSE 0 END) AS seal_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%Cleaning%' THEN cdc.cost ELSE 0 END) AS cleaning_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%OPS%' THEN cdc.cost ELSE 0 END) AS ops_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%Asuransi%' THEN cdc.cost ELSE 0 END) AS asuransi_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%PPH%' THEN cdc.cost ELSE 0 END) AS pph_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' AND cdc.description LIKE '%PPN%' THEN cdc.cost ELSE 0 END) AS ppn_pol,
                        SUM(CASE WHEN cdc.delivery = 'Surabaya' THEN cdc.cost ELSE 0 END) AS total_biaya_pol,
                        SUM(CASE WHEN cdc.delivery <> 'Surabaya' AND cdc.description LIKE '%THC%' THEN cdc.cost ELSE 0 END) AS thc_pod,
                        SUM(CASE WHEN cdc.delivery <> 'Surabaya' AND cdc.description LIKE '%OPS%' THEN cdc.cost ELSE 0 END) AS ops_pod,
                        SUM(CASE WHEN cdc.delivery <> 'Surabaya' AND cdc.description LIKE '%Seal%' THEN cdc.cost ELSE 0 END) AS seal_pod,
                        SUM(CASE WHEN cdc.delivery <> 'Surabaya' AND cdc.description LIKE '%Cleaning%' THEN cdc.cost ELSE 0 END) AS cleaning_pod,
                        SUM(CASE WHEN cdc.delivery <> 'Surabaya' THEN cdc.cost ELSE 0 END) AS total_biaya_pod,
                        SUM(cdc.cost) AS total_biaya
                    FROM container_delivery_costs cdc
                    GROUP BY cdc.container_id
                )
                SELECT
                    k.etd_sub AS 'ETD SUB',
                    c.ref_joa AS 'NO JOA',
                    SUM(COALESCE(d.thc_pol,0)) AS 'THC POL',
                    SUM(COALESCE(d.freight_pol,0)) AS 'Freight POL',
                    SUM(COALESCE(d.seal_pol,0)) AS 'Seal POL',
                    SUM(COALESCE(d.cleaning_pol,0)) AS 'Cleaning POL',
                    SUM(COALESCE(d.ops_pol,0)) AS 'OPS POL',
                    SUM(COALESCE(d.asuransi_pol,0)) AS 'Asuransi POL',
                    SUM(COALESCE(d.pph_pol,0)) AS 'PPH POL',
                    SUM(COALESCE(d.ppn_pol,0)) AS 'PPN POL',
                    SUM(COALESCE(d.total_biaya_pol,0)) AS 'TOTAL BIAYA POL',
                    SUM(COALESCE(d.thc_pod,0)) AS 'THC POD',
                    SUM(COALESCE(d.ops_pod,0)) AS 'OPS POD',
                    SUM(COALESCE(d.seal_pod,0)) AS 'Seal POD',
                    SUM(COALESCE(d.cleaning_pod,0)) AS 'Cleaning POD',
                    SUM(COALESCE(d.total_biaya_pod,0)) AS 'TOTAL BIAYA POD',
                    SUM(COALESCE(d.total_biaya,0)) AS 'TOTAL BIAYA',
                    SUM(COALESCE(inv.total_invoice,0)) AS 'NILAI INVOICE'
                FROM containers c
                LEFT JOIN kapals k ON c.kapal_id = k.kapal_id
                LEFT JOIN delivery_per_container d ON c.container_id = d.container_id
                LEFT JOIN invoice_per_container inv ON c.container_id = inv.container_id
                WHERE (? IS NULL OR date(k.etd_sub) >= date(?))
                  AND (? IS NULL OR date(k.etd_sub) <= date(?))
                GROUP BY c.ref_joa, k.etd_sub
                ORDER BY date(k.etd_sub) DESC;
            """

            params = (start_date, start_date, end_date, end_date)
            rows = [dict(r) for r in self.db.execute(query, params)]

            # Bersihkan tabel
            self.tree.delete(*self.tree.get_children())
            total_profit_all = 0

            for i, row in enumerate(rows):
                total_biaya = row.get("TOTAL BIAYA", 0) or 0
                nilai_invoice = row.get("NILAI INVOICE", 0) or 0
                profit = nilai_invoice - total_biaya
                row["PROFIT"] = profit
                total_profit_all += profit

                formatted = [
                    f"{round(val):,}".replace(",", ".") if isinstance(val, (int, float)) else val
                    for val in row.values()
                ]

                self.tree.insert(
                    "", "end",
                    values=formatted,
                    tags=("evenrow" if i % 2 == 0 else "oddrow",)
                )

            self.total_label.config(
                text=f"TOTAL PROFIT: Rp {round(total_profit_all):,}".replace(",", ".")
            )

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data dari database:\n{e}")

    def filter_data(self):
        start_date = self.start_date.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date.get_date().strftime("%Y-%m-%d")
        print("DEBUG Filter Date:", start_date, end_date)
        self.load_data_from_db(start_date, end_date)

    def clear_filter(self):
        self.start_date.set_date(date.today() - timedelta(days=30))
        self.end_date.set_date(date.today())
        self.load_data_from_db()
