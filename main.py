import customtkinter as ctk
from tkinter import messagebox
import app_admin
import app_customer
# Removed import app_vendor

def open_login_window():
    win = ctk.CTk()
    win.title("E-Commerce System")
    win.geometry("520x500")
    win.resizable(False, False)
    ctk.CTkLabel(win, text="E-Commerce System", font=("Arial", 26, "bold")).pack(pady=25)
    
    def open_customer_flow():
        win.destroy()
        app_customer.open_customer_login_and_dashboard()

    # Removed open_vendor_flow function

    def open_admin_flow():
        win.destroy()
        app_admin.open_admin_login_and_dashboard()

    ctk.CTkButton(win, text="Login as Customer", command=open_customer_flow, width=320).pack(pady=5)
    # Removed Login as Vendor button
    ctk.CTkButton(win, text="Login as Admin", command=open_admin_flow, width=320, fg_color="#e67e22").pack(pady=5)

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), exit()))
    win.mainloop()

if __name__ == "__main__":
    open_login_window()