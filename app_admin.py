import customtkinter as ctk
from tkinter import Listbox, END, messagebox
import database

def open_admin_login_and_dashboard():
    """Entry point for Admin flow"""
    win = ctk.CTk()
    win.title("Admin Login")
    win.geometry("400x300")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="Admin Login", font=("Arial", 20, "bold")).pack(pady=20)

    e_id = ctk.CTkEntry(win, placeholder_text="Admin ID", width=250)
    e_id.pack(pady=5)
    e_pw = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=250)
    e_pw.pack(pady=5)

    def login():
        uid = e_id.get().strip()
        pwd = e_pw.get().strip()
        if not uid or not pwd:
            messagebox.showwarning("Warning", "Please fill ID and Password")
            return
        admin = database.login_admin(uid, pwd)
        if admin:
            win.destroy()
            open_admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Admin ID or Password")

    ctk.CTkButton(win, text="Login", command=login, width=250).pack(pady=10)
    
    # Allow closing to go back to main selection if needed, 
    # but typically login windows just exit or return to main menu.
    # For this structure, we assume main.py handles the "Back" logic if needed,
    # or this is a standalone launcher.
    win.mainloop()

def open_admin_dashboard():
    win = ctk.CTk()
    win.title("Admin Dashboard")
    win.geometry("800x600")

    top_bar = ctk.CTkFrame(win, height=60)
    top_bar.pack(fill="x", padx=15, pady=10)
    ctk.CTkLabel(top_bar, text="Admin Panel", font=("Arial", 20, "bold")).pack(side="left", padx=20)

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            win.destroy()
            # Return to main login selection
            import main
            main.open_login_window()

    ctk.CTkButton(top_bar, text="Logout", fg_color="#e74c3c", command=logout, width=100).pack(side="right", padx=20)

    # Vendor Management Tab
    tab_vendor = ctk.CTkFrame(win)
    tab_vendor.pack(fill="both", expand=True, padx=15, pady=10)

    left_frame = ctk.CTkFrame(tab_vendor, width=300)
    left_frame.pack(side="left", fill="y", padx=(15, 7.5), pady=15)
    left_frame.pack_propagate(False)

    ctk.CTkLabel(left_frame, text="Vendor List", font=("Arial", 16, "bold")).pack(pady=10)
    vendor_list = Listbox(left_frame, font=("Arial", 13), height=20)
    vendor_list.pack(fill="both", expand=True, padx=10, pady=10)

    def load_vendors():
        vendor_list.delete(0, END)
        vendors = database.get_all_vendors()
        for v in vendors:
            vendor_list.insert(END, f"ID:{v[0]} | Name:{v[1]} | Rating:{v[2]}")
        if not vendors:
            vendor_list.insert(END, "No vendors available")
    load_vendors()

    right_frame = ctk.CTkFrame(tab_vendor)
    right_frame.pack(side="right", fill="both", expand=True, padx=(7.5, 15), pady=15)

    add_frame = ctk.CTkFrame(right_frame)
    add_frame.pack(fill="x", padx=20, pady=20)
    ctk.CTkLabel(add_frame, text="Onboard New Vendor", font=("Arial", 16, "bold")).pack(pady=10)

    id_row = ctk.CTkFrame(add_frame)
    id_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(id_row, text="Vendor ID:", width=100).pack(side="left", padx=5)
    v_add_id = ctk.CTkEntry(id_row, width=250)
    v_add_id.pack(side="right", padx=5)

    name_row = ctk.CTkFrame(add_frame)
    name_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(name_row, text="Vendor Name:", width=100).pack(side="left", padx=5)
    v_add_name = ctk.CTkEntry(name_row, width=250)
    v_add_name.pack(side="right", padx=5)

    pwd_row = ctk.CTkFrame(add_frame)
    pwd_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(pwd_row, text="Password:", width=100).pack(side="left", padx=5)
    v_add_pw = ctk.CTkEntry(pwd_row, width=250, show="*")
    v_add_pw.pack(side="right", padx=5)

    def add_vendor():
        vid = v_add_id.get().strip()
        name = v_add_name.get().strip()
        pw = v_add_pw.get().strip()
        if not vid or not name or not pw:
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        if database.add_vendor(vid, name, pw):
            messagebox.showinfo("Success", "Vendor added successfully")
            load_vendors()
            v_add_id.delete(0, END)
            v_add_name.delete(0, END)
            v_add_pw.delete(0, END)
        else:
            messagebox.showerror("Error", "Failed to add vendor")

    ctk.CTkButton(add_frame, text="Add Vendor", fg_color="#27ae60", command=add_vendor, width=200).pack(pady=15)

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_admin_login_and_dashboard())) # Or main menu
    win.mainloop()