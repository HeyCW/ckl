"""Test edit dialog to see if container fields appear"""
import tkinter as tk
from src.views.barang_window import BarangWindow
from src.models.database import AppDatabase

# Create test window
root = tk.Tk()
root.title("Test Edit Dialog")
root.geometry("800x600")

# Init database
db = AppDatabase()

# Get a barang for testing
barang_list = db.get_all_barang()
if barang_list:
    test_barang = barang_list[0]
    print(f"Testing with barang: {test_barang}")
    print(f"Container fields in data:")
    print(f"  container_20_pp: {test_barang.get('container_20_pp')}")
    print(f"  container_21_pp: {test_barang.get('container_21_pp')}")
    print(f"  container_40hc_pp: {test_barang.get('container_40hc_pp')}")

    # Create barang window instance
    barang_win = BarangWindow(root, db, None)

    # Try to open edit dialog
    barang_win.open_update_dialog(test_barang)

    root.mainloop()
else:
    print("No barang found in database. Please add some data first.")
