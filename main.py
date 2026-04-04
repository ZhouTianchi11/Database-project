import customtkinter as ctk
from tkinter import messagebox
import app_admin
import app_vendor
import app_customer

def open_login_window():
    win = ctk.CTk()
    win.title("E-Commerce System")
    win.geometry("520x500")
    win.resizable(False, False)
    ctk.CTkLabel(win, text="E-Commerce System", font=("Arial", 26, "bold")).pack(pady=25)
    def open_customer_flow():
        win.destroy()
        app_customer.open_customer_login_and_dashboard()

    def open_vendor_flow():
        win.destroy()
        app_vendor.open_vendor_login_and_dashboard()

    def open_admin_flow():
        win.destroy()
        app_admin.open_admin_login_and_dashboard()

    ctk.CTkButton(win, text="Login as Customer", command=open_customer_flow, width=320).pack(pady=5)
    ctk.CTkButton(win, text="Login as Vendor", command=open_vendor_flow, width=320, fg_color="#3498db").pack(pady=5)
    ctk.CTkButton(win, text="Login as Admin", command=open_admin_flow, width=320, fg_color="#e67e22").pack(pady=5)

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), exit()))
    win.mainloop()

if __name__ == "__main__":
    open_login_window()