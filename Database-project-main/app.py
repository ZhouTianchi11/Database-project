import customtkinter as ctk
from tkinter import *
from tkinter import messagebox, ttk
import database

current_cid = None
current_admin_id = None

# -------------------- Login Window --------------------
def open_login_window():
    global current_cid, current_admin_id
    current_cid = None
    current_admin_id = None
    win = ctk.CTk()
    win.title("E-Commerce System")
    win.geometry("520x440")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="E-Commerce System", font=("Arial", 26, "bold")).pack(pady=25)

    e_id = ctk.CTkEntry(win, placeholder_text="ID", width=320)
    e_id.pack(pady=6)
    e_pw = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=320)
    e_pw.pack(pady=6)

    def customer_login():
        global current_cid
        uid = e_id.get().strip()
        pwd = e_pw.get().strip()
        if not uid or not pwd:
            messagebox.showwarning("Warning", "Please fill ID and Password")
            return
        user = database.login_customer(uid, pwd)
        if user:
            current_cid = uid
            win.destroy()
            open_customer_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Customer ID or Password")

    def admin_login():
        global current_admin_id
        uid = e_id.get().strip()
        pwd = e_pw.get().strip()
        if not uid or not pwd:
            messagebox.showwarning("Warning", "Please fill ID and Password")
            return
        admin = database.login_admin(uid, pwd)
        if admin:
            current_admin_id = uid
            win.destroy()
            open_admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Admin ID or Password")

    ctk.CTkButton(win, text="Login as Customer", command=customer_login, width=320).pack(pady=5)
    ctk.CTkButton(win, text="Login as Admin", command=admin_login, width=320, fg_color="#e67e22").pack(pady=5)

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), exit()))
    win.mainloop()

# -------------------- Admin Dashboard (FULLY FIXED Vendor Management) --------------------
def open_admin_dashboard():
    win = ctk.CTk()
    win.title("Admin Dashboard")
    win.geometry("1400x850")

    top_bar = ctk.CTkFrame(win, height=60)
    top_bar.pack(fill="x", padx=15, pady=10)
    ctk.CTkLabel(top_bar, text="Admin Panel", font=("Arial", 20, "bold")).pack(side="left", padx=20)

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            win.destroy()
            open_login_window()
    ctk.CTkButton(top_bar, text="Logout", fg_color="#e74c3c", command=logout, width=100).pack(side="right", padx=20)

    tabview = ctk.CTkTabview(win)
    tabview.pack(fill="both", expand=True, padx=15, pady=10)
    tab_vendor = tabview.add("Vendor Management")
    tab_product = tabview.add("Product Management")
    tab_order = tabview.add("Order Management")

    # -------------------- Vendor Management (FIXED: Full UI Restored) --------------------
    # Left: Vendor List
    left_frame = ctk.CTkFrame(tab_vendor, width=420)
    left_frame.pack(side="left", fill="y", padx=(15, 7.5), pady=15)
    left_frame.pack_propagate(False)

    ctk.CTkLabel(left_frame, text="Vendor List", font=("Arial", 16, "bold")).pack(pady=10)
    vendor_list = Listbox(left_frame, font=("Arial", 13), height=25)
    vendor_list.pack(fill="both", expand=True, padx=10, pady=10)

    def load_vendors():
        vendor_list.delete(0, END)
        vendors = database.get_all_vendors()
        for v in vendors:
            vendor_list.insert(END, f"ID:{v[0]} | Name:{v[1]}")
        if not vendors:
            vendor_list.insert(END, "No vendors available")
    load_vendors()

    # Right: Add/Delete Vendor Form
    right_frame = ctk.CTkFrame(tab_vendor)
    right_frame.pack(side="right", fill="both", expand=True, padx=(7.5, 15), pady=15)

    # Add New Vendor Section
    add_frame = ctk.CTkFrame(right_frame)
    add_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(add_frame, text="Add New Vendor", font=("Arial", 16, "bold")).pack(pady=10)

    # Vendor ID
    id_row = ctk.CTkFrame(add_frame)
    id_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(id_row, text="Vendor ID:", width=100).pack(side="left", padx=5)
    v_add_id = ctk.CTkEntry(id_row, width=250)
    v_add_id.pack(side="right", padx=5)

    # Vendor Name
    name_row = ctk.CTkFrame(add_frame)
    name_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(name_row, text="Vendor Name:", width=100).pack(side="left", padx=5)
    v_add_name = ctk.CTkEntry(name_row, width=250)
    v_add_name.pack(side="right", padx=5)

    # Password
    pwd_row = ctk.CTkFrame(add_frame)
    pwd_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(pwd_row, text="Password:", width=100).pack(side="left", padx=5)
    v_add_pw = ctk.CTkEntry(pwd_row, width=250, show="*")
    v_add_pw.pack(side="right", padx=5)

    # Add Vendor Button
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
            refresh_vendor_combobox()
            v_add_id.delete(0, END)
            v_add_name.delete(0, END)
            v_add_pw.delete(0, END)
        else:
            messagebox.showerror("Error", "Failed to add vendor")

    ctk.CTkButton(add_frame, text="Add Vendor", fg_color="#27ae60", command=add_vendor, width=200).pack(pady=15)

    # Delete Vendor Section
    delete_frame = ctk.CTkFrame(right_frame)
    delete_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(delete_frame, text="Delete Vendor", font=("Arial", 16, "bold")).pack(pady=10)

    # Vendor ID Input for Delete
    del_row = ctk.CTkFrame(delete_frame)
    del_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(del_row, text="Vendor ID:", width=100).pack(side="left", padx=5)
    v_del_id = ctk.CTkEntry(del_row, width=250)
    v_del_id.pack(side="right", padx=5)

    # Delete Vendor Button
    def delete_vendor():
        vid = v_del_id.get().strip()
        if not vid:
            messagebox.showwarning("Warning", "Please enter a Vendor ID")
            return
        if messagebox.askyesno("Confirm", "Delete this vendor and all its products?"):
            if database.delete_vendor(vid):
                messagebox.showinfo("Success", "Vendor deleted")
                load_vendors()
                refresh_vendor_combobox()
                v_del_id.delete(0, END)
            else:
                messagebox.showerror("Error", "Delete failed")

    ctk.CTkButton(delete_frame, text="Delete Vendor", fg_color="#e74c3c", command=delete_vendor, width=200).pack(pady=15)

    # -------------------- Product Management --------------------
    product_main = ctk.CTkFrame(tab_product)
    product_main.pack(fill="both", expand=True, padx=15, pady=15)

    top_section = ctk.CTkFrame(product_main)
    top_section.pack(fill="x", padx=0, pady=(0, 15))

    vendor_row = ctk.CTkFrame(top_section)
    vendor_row.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(vendor_row, text="Select Vendor:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
    vendor_combobox = ttk.Combobox(vendor_row, width=30, state="readonly")
    vendor_combobox.pack(side="left", padx=5)

    vendor_map = {}
    def load_vendor_combobox():
        nonlocal vendor_map
        vendors = database.get_all_vendors()
        vendor_map.clear()
        display_list = []
        for v in vendors:
            vid = v[0]
            vname = v[1]
            display = f"{vid} - {vname}"
            vendor_map[display] = vid
            display_list.append(display)
        vendor_combobox['values'] = display_list
        if display_list:
            vendor_combobox.current(0)

    def refresh_vendor_combobox():
        load_vendor_combobox()
        product_list.delete(0, END)
        p_name.delete(0, END)
        p_price.delete(0, END)
        p_stock.delete(0, END)
        p_tag.delete(0, END)

    load_vendor_combobox()

    form_row = ctk.CTkFrame(top_section)
    form_row.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(form_row, text="Product Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    p_name = ctk.CTkEntry(form_row, width=180)
    p_name.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Price:", font=("Arial", 11)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    p_price = ctk.CTkEntry(form_row, width=80)
    p_price.grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Stock:", font=("Arial", 11)).grid(row=0, column=4, sticky="w", padx=5, pady=5)
    p_stock = ctk.CTkEntry(form_row, width=80)
    p_stock.grid(row=0, column=5, padx=5, pady=5)

    ctk.CTkLabel(form_row, text="Tag:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    p_tag = ctk.CTkEntry(form_row, width=180)
    p_tag.grid(row=1, column=1, padx=5, pady=5)

    list_section = ctk.CTkFrame(product_main)
    list_section.pack(fill="both", expand=True, padx=0, pady=(15, 0))

    ctk.CTkLabel(list_section, text="Product List", font=("Arial", 14, "bold")).pack(pady=5)
    product_list = Listbox(list_section, font=("Arial", 12), height=15)
    product_list.pack(fill="both", expand=True, padx=10, pady=10)

    btn_row = ctk.CTkFrame(product_main)
    btn_row.pack(fill="x", padx=0, pady=(0, 15))

    def load_products_by_vendor(vid):
        product_list.delete(0, END)
        products = database.get_vendor_products(vid)
        for p in products:
            product_list.insert(END, f"ID:{p[0]} | {p[2]} | ${p[3]} | Stock:{p[4]} | Tag:{p[5]}")

    def query_products():
        selected = vendor_combobox.get()
        if not selected:
            messagebox.showwarning("Warning", "Select a vendor")
            return
        vid = vendor_map.get(selected)
        load_products_by_vendor(vid)

    def add_product():
        selected = vendor_combobox.get()
        if not selected:
            messagebox.showwarning("Warning", "Please select a vendor first")
            return
        vid = vendor_map.get(selected)
        name = p_name.get().strip()
        price = p_price.get().strip()
        stock = p_stock.get().strip()
        tag = p_tag.get().strip()
        if not (name and price and stock):
            messagebox.showwarning("Warning", "Please fill name, price, stock")
            return
        if database.add_product(vid, name, price, stock, tag):
            messagebox.showinfo("Success", "Product added")
            load_products_by_vendor(vid)
            p_name.delete(0, END)
            p_price.delete(0, END)
            p_stock.delete(0, END)
            p_tag.delete(0, END)
        else:
            messagebox.showerror("Error", "Failed to add product")

    def update_product():
        sel = product_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a product first")
            return
        pid = product_list.get(sel[0]).split("ID:")[1].split(" |")[0]
        name = p_name.get().strip()
        price = p_price.get().strip()
        stock = p_stock.get().strip()
        tag = p_tag.get().strip()
        if database.update_product(pid, name, price, stock, tag):
            messagebox.showinfo("Success", "Product updated")
            query_products()
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
                query_products()
            else:
                messagebox.showerror("Error", "Delete failed")

    def fill_product_form(evt):
        sel = product_list.curselection()
        if not sel:
            return
        txt = product_list.get(sel[0])
        parts = txt.split(" | ")
        name = parts[1]
        price = parts[2].replace("$", "")
        stock = parts[3].split("Stock:")[1]
        tag = parts[4].split("Tag:")[1]
        p_name.delete(0, END)
        p_name.insert(0, name)
        p_price.delete(0, END)
        p_price.insert(0, price)
        p_stock.delete(0, END)
        p_stock.insert(0, stock)
        p_tag.delete(0, END)
        p_tag.insert(0, tag)

    product_list.bind("<<ListboxSelect>>", fill_product_form)

    ctk.CTkButton(btn_row, text="Query Products", command=query_products, width=120).grid(row=0, column=0, padx=5)
    ctk.CTkButton(btn_row, text="Add Product", fg_color="#27ae60", command=add_product, width=120).grid(row=0, column=1, padx=5)
    ctk.CTkButton(btn_row, text="Update Product", fg_color="#f39c12", command=update_product, width=120).grid(row=0, column=2, padx=5)
    ctk.CTkButton(btn_row, text="Delete Product", fg_color="#e74c3c", command=delete_product, width=120).grid(row=0, column=3, padx=5)
    btn_row.grid_columnconfigure((0,1,2,3), weight=1)

    # -------------------- Order Management --------------------
    order_main = ctk.CTkFrame(tab_order)
    order_main.pack(fill="both", expand=True, padx=15, pady=15)

    order_list = Listbox(order_main, font=("Arial", 13), height=15)
    order_list.pack(fill="both", expand=True, padx=10, pady=10)

    detail_frame = ctk.CTkFrame(order_main)
    detail_frame.pack(fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(detail_frame, text="Order Details:", font=("Arial",12,"bold")).pack(anchor="w", padx=5, pady=2)
    detail_text = Text(detail_frame, height=12, font=("Consolas", 11), wrap="word")
    detail_text.pack(fill="both", expand=True, padx=5, pady=5)

    def load_orders():
        order_list.delete(0, END)
        conn = database.connect_db()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SELECT order_id, customer_id, total_price, status, order_time FROM orders ORDER BY order_time DESC")
        orders = cur.fetchall()
        cur.close()
        conn.close()
        for o in orders:
            order_list.insert(END, f"Order:{o[0]} | Customer:{o[1]} | ${o[2]:.2f} | {o[3]} | {o[4]}")

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
        details = database.get_order_full_details(oid)
        if not details:
            detail_text.insert(END, "No order details available.")
            return

        detail_text.insert(END, f"--- Order ID: {oid} ---\n")
        detail_text.insert(END, f"{'Product Name':<25} {'Qty':<6} {'Unit Price':<12} {'Subtotal':<12}\n")
        detail_text.insert(END, "-" * 60 + "\n")
        
        total = 0.0
        for d in details:
            product_name = str(d[0])
            quantity = int(d[1])
            unit_price = float(d[2])
            subtotal = float(d[3])
            
            detail_text.insert(END, f"{product_name:<25} {quantity:<6} ${unit_price:<11.2f} ${subtotal:<11.2f}\n")
            total += subtotal
        
        detail_text.insert(END, "-" * 60 + "\n")
        detail_text.insert(END, f"Total Amount: ${total:.2f}")

    def cancel_order():
        sel = order_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an order first")
            return
        txt = order_list.get(sel[0])
        if not txt.startswith("Order:"):
            return
        oid = txt.split("Order:")[1].split("|")[0].strip()
        
        if messagebox.askyesno("Confirm", "Cancel this order?"):
            if database.cancel_order(oid):
                messagebox.showinfo("Success", "Order canceled successfully")
                load_orders()
                detail_text.delete(1.0, END)
            else:
                messagebox.showerror("Error", "Failed to cancel order")

    btn_frame = ctk.CTkFrame(order_main)
    btn_frame.pack(fill="x", padx=10, pady=10)
    ctk.CTkButton(btn_frame, text="Refresh", command=load_orders).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Show Details", command=show_order_details).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Cancel Order", command=cancel_order, fg_color="#e74c3c").pack(side="right", padx=5)

    def on_order_click(evt):
        show_order_details()
    order_list.bind("<<ListboxSelect>>", on_order_click)

    load_orders()

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_login_window()))
    win.mainloop()

# -------------------- Customer Dashboard --------------------
def open_customer_dashboard():
    win = ctk.CTk()
    win.title(f"Customer Dashboard | {current_cid}")
    win.geometry("1100x720")

    top = ctk.CTkFrame(win, height=60)
    top.pack(fill=X, padx=20, pady=10)
    ctk.CTkLabel(top, text=f"Welcome, {current_cid}", font=("Arial", 18)).pack(side="left", padx=20)

    def logout():
        if messagebox.askyesno("Logout", "Confirm logout?"):
            win.destroy()
            open_login_window()
    ctk.CTkButton(top, text="Logout", fg_color="#e74c3c", command=logout, width=100).pack(side="right", padx=10)

    def open_cart_page():
        win.destroy()
        open_cart()
    ctk.CTkButton(top, text="My Cart", command=open_cart_page, width=100).pack(side="right")

    def open_orders_page():
        win.destroy()
        open_my_orders()
    ctk.CTkButton(top, text="My Orders", command=open_orders_page, width=100).pack(side="right")

    search_frame = ctk.CTkFrame(win)
    search_frame.pack(fill=X, padx=20, pady=5)
    ctk.CTkLabel(search_frame, text="Search Products:").pack(side="left", padx=10)
    search_entry = ctk.CTkEntry(search_frame, width=350)
    search_entry.pack(side="left", padx=10)

    product_list = Listbox(win, font=("Arial", 13), height=18)
    product_list.pack(fill=BOTH, expand=True, padx=20, pady=10)

    def load_all_products(key=""):
        product_list.delete(0, END)
        if key:
            items = database.search_products(key)
        else:
            items = database.get_all_products()
        for p in items:
            product_list.insert(END, f"ID:{p[0]} | {p[2]} | ${p[3]} | Stock:{p[4]} | Tag:{p[5]}")

    def search_products():
        load_all_products(search_entry.get().strip())
    ctk.CTkButton(search_frame, text="Search", command=search_products).pack(side="left", padx=5)
    ctk.CTkButton(search_frame, text="Refresh", command=lambda: load_all_products("")).pack(side="left", padx=5)

    qty_frame = ctk.CTkFrame(win)
    qty_frame.pack(fill=X, padx=20, pady=5)
    ctk.CTkLabel(qty_frame, text="Quantity:").pack(side="left", padx=10)
    qty_entry = ctk.CTkEntry(qty_frame, width=80)
    qty_entry.insert(0, "1")
    qty_entry.pack(side="left", padx=5)

    def add_selected_to_cart():
        sel = product_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a product first")
            return
        txt = product_list.get(sel[0])
        pid = txt.split("ID:")[1].split(" |")[0]
        qty = qty_entry.get().strip()
        if database.add_to_cart(current_cid, pid, qty):
            messagebox.showinfo("Success", "Added to cart")
        else:
            messagebox.showerror("Error", "Failed to add to cart")

    ctk.CTkButton(win, text="Add to Cart", fg_color="#27ae60", command=add_selected_to_cart, width=180).pack(pady=10)
    load_all_products("")
    win.mainloop()

# -------------------- Shopping Cart --------------------
def open_cart():
    win = ctk.CTk()
    win.title("My Shopping Cart")
    win.geometry("1200x700")

    top_bar = ctk.CTkFrame(win, height=60)
    top_bar.pack(fill="x", padx=10, pady=10)
    back_btn = ctk.CTkButton(top_bar, text="Back", command=lambda: (win.destroy(), open_customer_dashboard()), width=120)
    back_btn.pack(side="left", padx=10)

    cart_container = ctk.CTkFrame(win)
    cart_container.pack(fill="both", expand=True, padx=20, pady=10)

    header_frame = ctk.CTkFrame(cart_container)
    header_frame.pack(fill="x", padx=0, pady=(0,5))
    ctk.CTkLabel(header_frame, text="Product", font=("Arial",12,"bold"), width=200).grid(row=0, column=0, padx=5, pady=5)
    ctk.CTkLabel(header_frame, text="Price", font=("Arial",12,"bold"), width=80).grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkLabel(header_frame, text="Quantity", font=("Arial",12,"bold"), width=80).grid(row=0, column=2, padx=5, pady=5)
    ctk.CTkLabel(header_frame, text="Subtotal", font=("Arial",12,"bold"), width=100).grid(row=0, column=3, padx=5, pady=5)
    ctk.CTkLabel(header_frame, text="Actions", font=("Arial",12,"bold"), width=150).grid(row=0, column=4, padx=5, pady=5)

    canvas = Canvas(cart_container)
    scrollbar = Scrollbar(cart_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    total_frame = ctk.CTkFrame(win)
    total_frame.pack(fill="x", padx=20, pady=10)
    total_label = ctk.CTkLabel(total_frame, text="Total: $0.00", font=("Arial",14,"bold"))
    total_label.pack(side="right", padx=10)

    def load_cart_items():
        # Clear all existing widgets first
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Get latest cart data from database
        cart_items = database.get_cart(current_cid)
        total = 0.0

        for item in cart_items:
            cart_id, product_id, product_name, price, quantity, subtotal = item
            total += float(subtotal)

            # Create item row
            row_frame = ctk.CTkFrame(scrollable_frame)
            row_frame.pack(fill="x", padx=5, pady=2)

            ctk.CTkLabel(row_frame, text=product_name, font=("Arial",11), width=200).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkLabel(row_frame, text=f"${float(price):.2f}", font=("Arial",11), width=80).grid(row=0, column=1, padx=5, pady=5)
            qty_entry = ctk.CTkEntry(row_frame, width=60, justify="center")
            qty_entry.insert(0, str(quantity))
            qty_entry.grid(row=0, column=2, padx=5, pady=5)
            subtotal_label = ctk.CTkLabel(row_frame, text=f"${float(subtotal):.2f}", font=("Arial",11), width=100)
            subtotal_label.grid(row=0, column=3, padx=5, pady=5)

            btn_frame = ctk.CTkFrame(row_frame)
            btn_frame.grid(row=0, column=4, padx=5, pady=5)

            # Update quantity function
            def update_qty(cid=cart_id, entry=qty_entry, label=subtotal_label, p=price):
                new_qty = entry.get().strip()
                if not new_qty.isdigit() or int(new_qty) < 1:
                    messagebox.showwarning("Warning", "Please enter a valid positive number")
                    return
                if database.update_cart_item(cid, new_qty):
                    new_subtotal = float(p) * int(new_qty)
                    label.configure(text=f"${new_subtotal:.2f}")
                    load_cart_items()
                else:
                    messagebox.showerror("Error", "Failed to update quantity")

            # Delete item function
            def delete_item(cid=cart_id):
                if messagebox.askyesno("Confirm", "Delete this item from cart?"):
                    if database.remove_cart_item(cid):
                        load_cart_items()
                    else:
                        messagebox.showerror("Error", "Failed to delete item")

            ctk.CTkButton(btn_frame, text="Update", command=update_qty, width=60, fg_color="#3498db").grid(row=0, column=0, padx=2)
            ctk.CTkButton(btn_frame, text="Delete", command=delete_item, width=60, fg_color="#e74c3c").grid(row=0, column=1, padx=2)

        # Update total label
        total_label.configure(text=f"Total: ${total:.2f}")

    # Checkout function (FIXED: Force clear cart after successful order)
    def checkout():
        if database.create_order_from_cart(current_cid):
            messagebox.showinfo("Success", "Order placed successfully!")

            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            total_label.configure(text="Total: $0.00")

            load_cart_items()

            win.destroy()
            open_customer_dashboard()
        else:
            messagebox.showerror("Error", "Checkout failed")

    # Checkout button
    checkout_btn = ctk.CTkButton(win, text="Checkout", fg_color="#27ae60", command=checkout, width=150)
    checkout_btn.pack(pady=10)

    # Initial load
    load_cart_items()

    # Window close protocol
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_customer_dashboard()))
    win.mainloop()

# -------------------- My Orders --------------------
def open_my_orders():
    win = ctk.CTk()
    win.title("My Orders")
    win.geometry("1000x750")

    def back():
        win.destroy()
        open_customer_dashboard()
    ctk.CTkButton(win, text="Back", command=back).pack(pady=5)

    order_list = Listbox(win, font=("Arial", 13), height=15)
    order_list.pack(fill=BOTH, expand=True, padx=20, pady=10)

    detail_frame = ctk.CTkFrame(win)
    detail_frame.pack(fill="both", expand=True, padx=20, pady=10)
    ctk.CTkLabel(detail_frame, text="Order Details:", font=("Arial",12,"bold")).pack(anchor="w", padx=5, pady=2)
    detail_text = Text(detail_frame, height=12, font=("Consolas", 11), wrap="word")
    detail_text.pack(fill="both", expand=True, padx=5, pady=5)

    def load_user_orders():
        order_list.delete(0, END)
        orders = database.get_user_orders(current_cid)
        for o in orders:
            order_list.insert(END, f"Order:{o[0]} ${o[1]:.2f} {o[2]} {o[3]}")

    ctk.CTkButton(win, text="Refresh", command=load_user_orders).pack(pady=5)

    def load_order_detail(evt):
        sel = order_list.curselection()
        if not sel:
            return
        txt = order_list.get(sel[0])
        if not txt.startswith("Order:"):
            return
        oid = txt.split("Order:")[1].split("$")[0].strip()
        
        detail_text.delete(1.0, END)
        details = database.get_order_full_details(oid)
        
        if not details:
            detail_text.insert(END, "No order details available.")
            return

        detail_text.insert(END, f"--- Order ID: {oid} ---\n")
        detail_text.insert(END, f"{'Product Name':<25} {'Qty':<6} {'Unit Price':<12} {'Subtotal':<12}\n")
        detail_text.insert(END, "-" * 55 + "\n")
        
        total = 0
        for d in details:
            name, qty, price, subtotal = d
            detail_text.insert(END, f"{name:<25} {qty:<5} ${float(price):<9.2f} ${float(subtotal):<9.2f}\n")
            total += float(subtotal)
        
        detail_text.insert(END, "-" * 55 + "\n")
        detail_text.insert(END, f"Total: ${total:.2f}")

    order_list.bind("<<ListboxSelect>>", load_order_detail)
    load_user_orders()
    win.mainloop()

if __name__ == "__main__":
    open_login_window()