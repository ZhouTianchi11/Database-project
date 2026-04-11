import customtkinter as ctk
from tkinter import Listbox, END, Text, messagebox
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
    win.mainloop()

def open_admin_dashboard():
    win = ctk.CTk()
    win.title("Admin Dashboard")
    win.geometry("1200x800") 

    top_bar = ctk.CTkFrame(win, height=60)
    top_bar.pack(fill="x", padx=15, pady=10)
    ctk.CTkLabel(top_bar, text="Admin Panel", font=("Arial", 20, "bold")).pack(side="left", padx=20)

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            win.destroy()
            import main
            main.open_login_window()

    ctk.CTkButton(top_bar, text="Logout", fg_color="#e74c3c", command=logout, width=100).pack(side="right", padx=20)

    # Use TabView for Vendor, Product, and Order Management
    tabview = ctk.CTkTabview(win)
    tabview.pack(fill="both", expand=True, padx=15, pady=10)
    
    tab_vendor = tabview.add("Vendor Management")
    tab_product = tabview.add("Product Catalog")
    tab_orders = tabview.add("Order Management") 

    # -------------------- Vendor Management --------------------
    setup_vendor_management(tab_vendor)

    # -------------------- Product Catalog Management --------------------
    setup_product_management(tab_product)
    
    # -------------------- Order Management --------------------
    setup_order_management(tab_orders)

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_admin_login_and_dashboard()))
    win.mainloop()

def setup_vendor_management(tab):
    left_frame = ctk.CTkFrame(tab, width=500)
    left_frame.pack(side="left", fill="y", padx=(15, 7.5), pady=15)
    left_frame.pack_propagate(False)

    ctk.CTkLabel(left_frame, text="Vendor List", font=("Arial", 16, "bold")).pack(pady=10)
    vendor_list = Listbox(left_frame, font=("Arial", 18), height=20)
    vendor_list.pack(fill="both", expand=True, padx=10, pady=10)

    def load_vendors():
        vendor_list.delete(0, END)
        vendors = database.get_all_vendors()
        for v in vendors:
            vendor_list.insert(END, f"ID:{v[0]} | Name:{v[1]} | Rating:{v[2]}")
        if not vendors:
            vendor_list.insert(END, "No vendors available")
    
    load_vendors()

    right_frame = ctk.CTkFrame(tab)
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

    def add_vendor():
        vid = v_add_id.get().strip()
        name = v_add_name.get().strip()

        if not vid or not name:
            messagebox.showwarning("Warning", "Please fill ID and Name")
            return
        if database.add_vendor(vid, name):
            messagebox.showinfo("Success", "Vendor added successfully")
            load_vendors()
            v_add_id.delete(0, END)
            v_add_name.delete(0, END)
        else:
            messagebox.showerror("Error", "Failed to add vendor")

    def delete_vendor():
        sel = vendor_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a vendor to delete")
            return
        txt = vendor_list.get(sel[0])
        vid = txt.split("ID:")[1].split(" |")[0]
        
        if messagebox.askyesno("Confirm", f"Delete vendor {vid} and all their products?"):
            if database.delete_vendor(vid):
                messagebox.showinfo("Success", "Vendor deleted")
                load_vendors()
            else:
                messagebox.showerror("Error", "Failed to delete vendor")

    btn_frame = ctk.CTkFrame(add_frame)
    btn_frame.pack(pady=10)
    ctk.CTkButton(btn_frame, text="Add Vendor", fg_color="#27ae60", command=add_vendor, width=120).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Delete Vendor", fg_color="#e74c3c", command=delete_vendor, width=120).pack(side="left", padx=5)

def setup_product_management(tab):
    # Top section: Select Vendor
    selector_frame = ctk.CTkFrame(tab)
    selector_frame.pack(fill="x", padx=15, pady=10)
    
    ctk.CTkLabel(selector_frame, text="Select Vendor to Manage Products:", font=("Arial", 14)).pack(side="left", padx=10)
    
    vendor_var = ctk.StringVar(value="")
    vendor_dropdown = ctk.CTkComboBox(selector_frame, variable=vendor_var, values=[], width=200)
    vendor_dropdown.pack(side="left", padx=10)
    
    def refresh_vendor_list():
        vendors = database.get_all_vendors()
        values = [f"{v[0]} - {v[1]}" for v in vendors]
        vendor_dropdown.configure(values=values)
        if values:
            vendor_var.set(values[0])
            
    refresh_vendor_list()
    
    ctk.CTkButton(selector_frame, text="Refresh Vendors", command=refresh_vendor_list, width=100).pack(side="left", padx=5)

    # Middle section: Product List for selected vendor
    list_frame = ctk.CTkFrame(tab)
    list_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    ctk.CTkLabel(list_frame, text="Product Catalog", font=("Arial", 16, "bold")).pack(pady=5)
    product_list = Listbox(list_frame, font=("Arial", 18), height=15)
    product_list.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Bottom section: Add/Edit Form
    form_frame = ctk.CTkFrame(tab)
    form_frame.pack(fill="x", padx=15, pady=10)
    
    # Row 1
    r1 = ctk.CTkFrame(form_frame)
    r1.pack(fill="x", pady=5)
    ctk.CTkLabel(r1, text="Name:", width=50).grid(row=0, column=0, padx=5)
    p_name = ctk.CTkEntry(r1, width=150)
    p_name.grid(row=0, column=1, padx=5)
    
    ctk.CTkLabel(r1, text="Price:", width=50).grid(row=0, column=2, padx=5)
    p_price = ctk.CTkEntry(r1, width=80)
    p_price.grid(row=0, column=3, padx=5)
    
    ctk.CTkLabel(r1, text="Stock:", width=50).grid(row=0, column=4, padx=5)
    p_stock = ctk.CTkEntry(r1, width=80)
    p_stock.grid(row=0, column=5, padx=5)
    
    # Row 2
    r2 = ctk.CTkFrame(form_frame)
    r2.pack(fill="x", pady=5)
    ctk.CTkLabel(r2, text="Tag 1:", width=50).grid(row=0, column=0, padx=5)
    p_tag1 = ctk.CTkEntry(r2, width=100)
    p_tag1.grid(row=0, column=1, padx=5)
    
    ctk.CTkLabel(r2, text="Tag 2:", width=50).grid(row=0, column=2, padx=5)
    p_tag2 = ctk.CTkEntry(r2, width=100)
    p_tag2.grid(row=0, column=3, padx=5)
    
    ctk.CTkLabel(r2, text="Tag 3:", width=50).grid(row=0, column=4, padx=5)
    p_tag3 = ctk.CTkEntry(r2, width=100)
    p_tag3.grid(row=0, column=5, padx=5)
    
    def clear_form():
        p_name.delete(0, END)
        p_price.delete(0, END)
        p_stock.delete(0, END)
        p_tag1.delete(0, END)
        p_tag2.delete(0, END)
        p_tag3.delete(0, END)

    def load_products():
        product_list.delete(0, END)
        vid_str = vendor_var.get()
        if not vid_str:
            return
        vid = vid_str.split(" - ")[0]
        products = database.get_vendor_products(vid)
        for p in products:
            tags = [t for t in [p[5], p[6], p[7]] if t]
            tag_str = ", ".join(tags) if tags else "No Tags"
            product_list.insert(END, f"ID:{p[0]} | {p[2]} | ${p[3]} | Stock:{p[4]} | Tags:{tag_str}")

    def add_product():
        vid_str = vendor_var.get()
        if not vid_str:
            messagebox.showwarning("Warning", "Select a vendor first")
            return
        vid = vid_str.split(" - ")[0]
        
        name = p_name.get().strip()
        price = p_price.get().strip()
        stock = p_stock.get().strip()
        tag1 = p_tag1.get().strip()
        tag2 = p_tag2.get().strip()
        tag3 = p_tag3.get().strip()
        
        if not (name and price and stock):
            messagebox.showwarning("Warning", "Please fill name, price, stock")
            return
        
        if database.add_product(vid, name, price, stock, tag1, tag2, tag3):
            messagebox.showinfo("Success", "Product added")
            load_products()
            clear_form()
        else:
            messagebox.showerror("Error", "Failed to add product")

    def update_product():
        sel = product_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a product first")
            return
        txt = product_list.get(sel[0])
        pid = txt.split("ID:")[1].split(" |")[0]
        
        name = p_name.get().strip()
        price = p_price.get().strip()
        stock = p_stock.get().strip()
        tag1 = p_tag1.get().strip()
        tag2 = p_tag2.get().strip()
        tag3 = p_tag3.get().strip()
        
        if database.update_product(pid, name, price, stock, tag1, tag2, tag3):
            messagebox.showinfo("Success", "Product updated")
            load_products()
        else:
            messagebox.showerror("Error", "Update failed")

    def delete_product():
        sel = product_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a product first")
            return
        pid = product_list.get(sel[0]).split("ID:")[1].split(" |")[0]
        if messagebox.askyesno("Confirm", "Delete this product?"):
            if database.delete_product(pid):
                messagebox.showinfo("Success", "Product deleted")
                load_products()
            else:
                messagebox.showerror("Error", "Delete failed")

    def fill_form(evt):
        sel = product_list.curselection()
        if not sel:
            return
        txt = product_list.get(sel[0])
        parts = txt.split(" | ")
        pid_part = parts[0] 
        
        name = parts[1]
        price = parts[2].replace("$", "")
        stock = parts[3].split("Stock:")[1]
        
        tags_str = parts[4].split("Tags:")[1] if len(parts) > 4 else ""
        tags_list = [t.strip() for t in tags_str.split(",")] if tags_str else []
        
        p_name.delete(0, END)
        p_name.insert(0, name)
        p_price.delete(0, END)
        p_price.insert(0, price)
        p_stock.delete(0, END)
        p_stock.insert(0, stock)
        
        p_tag1.delete(0, END)
        p_tag2.delete(0, END)
        p_tag3.delete(0, END)
        
        if len(tags_list) > 0: p_tag1.insert(0, tags_list[0])
        if len(tags_list) > 1: p_tag2.insert(0, tags_list[1])
        if len(tags_list) > 2: p_tag3.insert(0, tags_list[2])

    product_list.bind("<<ListboxSelect>>", fill_form)
    
    # Bind vendor change to reload products
    vendor_var.trace_add("write", lambda *args: load_products())

    btn_row = ctk.CTkFrame(form_frame)
    btn_row.pack(pady=10)
    
    ctk.CTkButton(btn_row, text="Refresh", command=load_products, width=100).grid(row=0, column=0, padx=5)
    ctk.CTkButton(btn_row, text="Add Product", fg_color="#27ae60", command=add_product, width=100).grid(row=0, column=1, padx=5)
    ctk.CTkButton(btn_row, text="Update Product", fg_color="#f39c12", command=update_product, width=100).grid(row=0, column=2, padx=5)
    ctk.CTkButton(btn_row, text="Delete Product", fg_color="#e74c3c", command=delete_product, width=100).grid(row=0, column=3, padx=5)
    
    # Initial load
    load_products()

def setup_order_management(tab):
    """Setup the Order Management Tab for Admins"""
    
    # Left side: Order List
    left_frame = ctk.CTkFrame(tab, width=500)
    left_frame.pack(side="left", fill="y", padx=(15, 7.5), pady=15)
    left_frame.pack_propagate(False)
    
    ctk.CTkLabel(left_frame, text="All Orders", font=("Arial", 16, "bold")).pack(pady=10)
    
    order_list = Listbox(left_frame, font=("Arial", 18), height=20)
    order_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Right side: Order Details
    right_frame = ctk.CTkFrame(tab)
    right_frame.pack(side="right", fill="both", expand=True, padx=(7.5, 15), pady=15)
    
    ctk.CTkLabel(right_frame, text="Order Details & Items", font=("Arial", 16, "bold")).pack(pady=10)
    
    detail_text = Text(right_frame, font=("Consolas", 11), wrap="word")
    detail_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add status control buttons
    status_frame = ctk.CTkFrame(right_frame)
    status_frame.pack(fill="x", padx=10, pady=5)
    
    current_selected_oid = None
    current_status = None
    
    def load_all_orders():
        order_list.delete(0, END)
        orders = database.get_all_orders()
        for o in orders:
            order_list.insert(END, f"ID:{o[0]} | Customer:{o[1]} | Total:${o[2]:.2f} | Status:{o[3]}")
            
    def show_order_details(evt=None):
        nonlocal current_selected_oid, current_status
        sel = order_list.curselection()
        if not sel:
            detail_text.delete(1.0, END)
            # Disable buttons when no selection
            shipped_btn.configure(state="disabled")
            completed_btn.configure(state="disabled")
            return
        
        txt = order_list.get(sel[0])
        oid = txt.split("ID:")[1].split(" |")[0]
        current_selected_oid = oid
        current_status = txt.split("Status:")[1].strip()
        
        detail_text.delete(1.0, END)
        
        items = database.get_order_full_details(oid)
        if not items:
            detail_text.insert(END, "No items found for this order.")
            shipped_btn.configure(state="disabled")
            completed_btn.configure(state="disabled")
            return
            
        detail_text.insert(END, f"--- Order ID: {oid} ---\n\n")
        detail_text.insert(END, f"{'Product Name':<25} {'Qty':<6} {'Unit Price':<12} {'Subtotal':<12} {'Vendor ID':<10}\n")
        detail_text.insert(END, "-" * 70 + "\n")
        
        total_items = 0.0
        for item in items:
            pname = str(item[0])
            qty = int(item[1])
            price = float(item[2])
            sub = float(item[3])
            vid = str(item[4])
            detail_text.insert(END, f"{pname:<25} {qty:<6} ${price:<11.2f} ${sub:<11.2f} {vid:<10}\n")
            total_items += sub
            
        detail_text.insert(END, "-" * 70 + "\n")
        detail_text.insert(END, f"Total Order Amount: ${total_items:.2f}\n\n")

        transactions = database.get_transactions_by_order(oid)
        if transactions:
            detail_text.insert(END, "--- Payment Transactions ---\n")
            detail_text.insert(END, f"{'Vendor':<25} {'Amount':<12} {'Date':<20} {'Status':<10}\n")
            detail_text.insert(END, "-" * 70 + "\n")
            for t in transactions:
                v_name = str(t[1])
                amount = float(t[2])
                date = str(t[3])
                status = str(t[4])
                detail_text.insert(END, f"{v_name:<25} ${amount:<11.2f} {date:<20} {status:<10}\n")
        
        # Enable appropriate buttons based on status
        if current_status == 'pending':
            shipped_btn.configure(state="normal")
            completed_btn.configure(state="disabled")
        elif current_status == 'shipped':
            shipped_btn.configure(state="disabled")
            completed_btn.configure(state="normal")
        else:  # completed
            shipped_btn.configure(state="disabled")
            completed_btn.configure(state="disabled")
    
    def mark_as_shipped():
        if current_selected_oid and messagebox.askyesno("Confirm", "Mark this order as shipped?"):
            if database.update_order_status(current_selected_oid, 'shipped'):
                messagebox.showinfo("Success", "Order marked as shipped")
                load_all_orders()
                # Re-select the same order
                for i in range(order_list.size()):
                    if order_list.get(i).startswith(f"ID:{current_selected_oid}"):
                        order_list.selection_set(i)
                        show_order_details()
                        break
            else:
                messagebox.showerror("Error", "Failed to update status")
    
    def mark_as_completed():
        if current_selected_oid and messagebox.askyesno("Confirm", "Mark this order as completed?"):
            if database.update_order_status(current_selected_oid, 'completed'):
                messagebox.showinfo("Success", "Order marked as completed")
                load_all_orders()
                # Re-select the same order
                for i in range(order_list.size()):
                    if order_list.get(i).startswith(f"ID:{current_selected_oid}"):
                        order_list.selection_set(i)
                        show_order_details()
                        break
            else:
                messagebox.showerror("Error", "Failed to update status")
    
    # Add the two status buttons
    shipped_btn = ctk.CTkButton(status_frame, text="Mark as Shipped", 
                               command=mark_as_shipped, state="disabled", width=120)
    shipped_btn.pack(side="left", padx=5)
    
    completed_btn = ctk.CTkButton(status_frame, text="Mark as Completed", 
                                 command=mark_as_completed, state="disabled", width=130)
    completed_btn.pack(side="left", padx=5)
    
    # Keep existing refresh button
    btn_frame = ctk.CTkFrame(left_frame)
    btn_frame.pack(fill="x", padx=10, pady=10)
    ctk.CTkButton(btn_frame, text="Refresh Orders", command=load_all_orders).pack(fill="x")
    
    order_list.bind("<<ListboxSelect>>", show_order_details)
    load_all_orders()