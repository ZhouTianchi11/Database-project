import customtkinter as ctk
from tkinter import Listbox, END, Text, messagebox
import database 

current_vid = None

def open_vendor_login_and_dashboard():
    """Entry point for Vendor flow"""
    global current_vid
    current_vid = None
    
    win = ctk.CTk()
    win.title("Vendor Login")
    win.geometry("400x300")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="Vendor Login", font=("Arial", 20, "bold")).pack(pady=20)

    e_id = ctk.CTkEntry(win, placeholder_text="Vendor ID", width=250)
    e_id.pack(pady=5)
    e_pw = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=250)
    e_pw.pack(pady=5)

    def login():
        global current_vid
        uid = e_id.get().strip()
        pwd = e_pw.get().strip()
        if not uid or not pwd:
            messagebox.showwarning("Warning", "Please fill ID and Password")
            return
        vendor = database.login_vendor(uid, pwd)
        if vendor:
            current_vid = uid
            win.destroy()
            open_vendor_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Vendor ID or Password")

    ctk.CTkButton(win, text="Login", command=login, width=250).pack(pady=10)
    win.mainloop()

def open_vendor_dashboard():
    global current_vid
    win = ctk.CTk()
    win.title(f"Vendor Dashboard | {current_vid}")
    win.geometry("1200x800")

    top_bar = ctk.CTkFrame(win, height=60)
    top_bar.pack(fill="x", padx=15, pady=10)
    ctk.CTkLabel(top_bar, text=f"Vendor Panel: {current_vid}", font=("Arial", 20, "bold")).pack(side="left", padx=20)

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            win.destroy()
            import main
            main.open_login_window()

    ctk.CTkButton(top_bar, text="Logout", fg_color="#e74c3c", command=logout, width=100).pack(side="right", padx=20)

    tabview = ctk.CTkTabview(win)
    tabview.pack(fill="both", expand=True, padx=15, pady=10)
    tab_product = tabview.add("My Products")
    tab_order = tabview.add("My Orders")

    # -------------------- Product Management --------------------
    product_main = ctk.CTkFrame(tab_product)
    product_main.pack(fill="both", expand=True, padx=15, pady=15)

    form_row = ctk.CTkFrame(product_main)
    form_row.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(form_row, text="Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    p_name = ctk.CTkEntry(form_row, width=150)
    p_name.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Price:", font=("Arial", 11)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    p_price = ctk.CTkEntry(form_row, width=80)
    p_price.grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Stock:", font=("Arial", 11)).grid(row=0, column=4, sticky="w", padx=5, pady=5)
    p_stock = ctk.CTkEntry(form_row, width=80)
    p_stock.grid(row=0, column=5, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Tag 1:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    p_tag1 = ctk.CTkEntry(form_row, width=100)
    p_tag1.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Tag 2:", font=("Arial", 11)).grid(row=1, column=2, sticky="w", padx=5, pady=5)
    p_tag2 = ctk.CTkEntry(form_row, width=100)
    p_tag2.grid(row=1, column=3, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Tag 3:", font=("Arial", 11)).grid(row=1, column=4, sticky="w", padx=5, pady=5)
    p_tag3 = ctk.CTkEntry(form_row, width=100)
    p_tag3.grid(row=1, column=5, padx=5, pady=5)

    def clear_product_form():
        p_name.delete(0, END)
        p_price.delete(0, END)
        p_stock.delete(0, END)
        p_tag1.delete(0, END)
        p_tag2.delete(0, END)
        p_tag3.delete(0, END)

    list_section = ctk.CTkFrame(product_main)
    list_section.pack(fill="both", expand=True, padx=0, pady=(15, 0))

    ctk.CTkLabel(list_section, text="My Product List", font=("Arial", 14, "bold")).pack(pady=5)
    product_list = Listbox(list_section, font=("Arial", 12), height=15)
    product_list.pack(fill="both", expand=True, padx=10, pady=10)

    btn_row = ctk.CTkFrame(product_main)
    btn_row.pack(fill="x", padx=0, pady=(0, 15))

    def load_my_products():
        product_list.delete(0, END)
        products = database.get_vendor_products(current_vid)
        for p in products:
            tags = [t for t in [p[5], p[6], p[7]] if t]
            tag_str = ", ".join(tags) if tags else "No Tags"
            product_list.insert(END, f"ID:{p[0]} | {p[2]} | ${p[3]} | Stock:{p[4]} | Tags:{tag_str}")

    def add_product():
        name = p_name.get().strip()
        price = p_price.get().strip()
        stock = p_stock.get().strip()
        tag1 = p_tag1.get().strip()
        tag2 = p_tag2.get().strip()
        tag3 = p_tag3.get().strip()
        
        if not (name and price and stock):
            messagebox.showwarning("Warning", "Please fill name, price, stock")
            return
        
        if database.add_product(current_vid, name, price, stock, tag1, tag2, tag3):
            messagebox.showinfo("Success", "Product added")
            load_my_products()
            clear_product_form()
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
            load_my_products()
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
                load_my_products()
            else:
                messagebox.showerror("Error", "Delete failed")

    def fill_product_form(evt):
        sel = product_list.curselection()
        if not sel:
            return
        txt = product_list.get(sel[0])
        parts = txt.split(" | ")
        pid_part = parts[0] 
        pid = pid_part.split(":")[1]
        
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

    product_list.bind("<<ListboxSelect>>", fill_product_form)

    ctk.CTkButton(btn_row, text="Refresh", command=load_my_products, width=120).grid(row=0, column=0, padx=5)
    ctk.CTkButton(btn_row, text="Add Product", fg_color="#27ae60", command=add_product, width=120).grid(row=0, column=1, padx=5)
    ctk.CTkButton(btn_row, text="Update Product", fg_color="#f39c12", command=update_product, width=120).grid(row=0, column=2, padx=5)
    ctk.CTkButton(btn_row, text="Delete Product", fg_color="#e74c3c", command=delete_product, width=120).grid(row=0, column=3, padx=5)
    btn_row.grid_columnconfigure((0,1,2,3), weight=1)
    
    load_my_products()

    # -------------------- Order Management --------------------
    order_main = ctk.CTkFrame(tab_order)
    order_main.pack(fill="both", expand=True, padx=15, pady=15)

    order_list = Listbox(order_main, font=("Arial", 13), height=15)
    order_list.pack(fill="both", expand=True, padx=10, pady=10)

    detail_frame = ctk.CTkFrame(order_main)
    detail_frame.pack(fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(detail_frame, text="Order Details (My Products Only):", font=("Arial",12,"bold")).pack(anchor="w", padx=5, pady=2)
    detail_text = Text(detail_frame, height=12, font=("Consolas", 11), wrap="word")
    detail_text.pack(fill="both", expand=True, padx=5, pady=5)

    def load_my_orders():
        order_list.delete(0, END)
        orders = database.get_vendor_orders(current_vid)
        for o in orders:
            order_list.insert(END, f"Order:{o[0]} | Total:${o[1]:.2f} | Status:{o[2]} | Time:{o[3]}")

    def show_order_details():
        sel = order_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an order first")
            return
        txt = order_list.get(sel[0])
        if not txt.startswith("Order:"):
            return
        oid = txt.split("Order:")[1].split("|")[0].strip()
        
        detail_text.delete(1.0, END)
        all_details = database.get_order_full_details(oid)
        
        my_details = [d for d in all_details if d[4] == current_vid] 
        
        if not my_details:
            detail_text.insert(END, "No products from your store in this order.")
            return

        detail_text.insert(END, f"--- Order ID: {oid} ---\n")
        detail_text.insert(END, f"{'Product Name':<25} {'Qty':<6} {'Unit Price':<12} {'Subtotal':<12}\n")
        detail_text.insert(END, "-" * 60 + "\n")
        
        total = 0.0
        for d in my_details:
            product_name = str(d[0])
            quantity = int(d[1])
            unit_price = float(d[2])
            subtotal = float(d[3])
            
            detail_text.insert(END, f"{product_name:<25} {quantity:<6} ${unit_price:<11.2f} ${subtotal:<11.2f}\n")
            total += subtotal
        
        detail_text.insert(END, "-" * 60 + "\n")
        detail_text.insert(END, f"Total Amount (Your Products): ${total:.2f}")

    btn_frame = ctk.CTkFrame(order_main)
    btn_frame.pack(fill="x", padx=10, pady=10)
    ctk.CTkButton(btn_frame, text="Refresh", command=load_my_orders).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Show Details", command=show_order_details).pack(side="left", padx=5)

    def on_order_click(evt):
        show_order_details()
    order_list.bind("<<ListboxSelect>>", on_order_click)

    load_my_orders()

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_vendor_login_and_dashboard()))
    win.mainloop()