import customtkinter as ctk
from tkinter import Listbox, END, Text, Canvas, Scrollbar, messagebox
import database

current_cid = None

def open_customer_login_and_dashboard():
    """Entry point for Customer flow"""
    global current_cid
    current_cid = None
    
    win = ctk.CTk()
    win.title("Customer Login")
    win.geometry("400x300")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="Customer Login", font=("Arial", 20, "bold")).pack(pady=20)

    e_id = ctk.CTkEntry(win, placeholder_text="Customer ID", width=250)
    e_id.pack(pady=5)
    e_pw = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=250)
    e_pw.pack(pady=5)

    def login():
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

    ctk.CTkButton(win, text="Login", command=login, width=250).pack(pady=10)
    win.mainloop()

def open_customer_dashboard():
    global current_cid
    win = ctk.CTk()
    win.title(f"Customer Dashboard | {current_cid}")
    win.geometry("1100x720")

    top = ctk.CTkFrame(win, height=60)
    top.pack(fill="x", padx=20, pady=10)
    ctk.CTkLabel(top, text=f"Welcome, {current_cid}", font=("Arial", 18)).pack(side="left", padx=20)

    def logout():
        if messagebox.askyesno("Logout", "Confirm logout?"):
            win.destroy()
            import main
            main.open_login_window()

    ctk.CTkButton(top, text="Logout", fg_color="#e74c3c", command=logout, width=100).pack(side="right", padx=10)

    def open_cart_page():
        win.destroy()
        open_cart()

    ctk.CTkButton(top, text="My Cart", command=open_cart_page, width=100).pack(side="right")

    def open_orders_page():
        win.destroy()
        open_my_orders()

    ctk.CTkButton(top, text="My Orders", command=open_orders_page, width=100).pack(side="right")
    
    # Added My Profile Button
    def open_profile_page():
        win.destroy()
        open_my_profile()
        
    ctk.CTkButton(top, text="My Profile", command=open_profile_page, width=100).pack(side="right")

    search_frame = ctk.CTkFrame(win)
    search_frame.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(search_frame, text="Search Products (Name/Tag):").pack(side="left", padx=10)
    search_entry = ctk.CTkEntry(search_frame, width=350)
    search_entry.pack(side="left", padx=10)

    product_list = Listbox(win, font=("Arial", 18), height=18)
    product_list.pack(fill="both", expand=True, padx=20, pady=10)

    def load_all_products(key=""):
        product_list.delete(0, END)
        if key:
            items = database.search_products(key)
        else:
            items = database.get_all_products()
        for p in items:
            tags = [t for t in [p[5], p[6], p[7]] if t]
            tag_str = ", ".join(tags) if tags else "No Tags"
            product_list.insert(END, f"ID:{p[0]} | {p[2]} | ${p[3]} | Stock:{p[4]} | Tags:{tag_str}")

    def search_products():
        load_all_products(search_entry.get().strip())
        
    ctk.CTkButton(search_frame, text="Search", command=search_products).pack(side="left", padx=5)
    ctk.CTkButton(search_frame, text="Refresh", command=lambda: load_all_products("")).pack(side="left", padx=5)

    qty_frame = ctk.CTkFrame(win)
    qty_frame.pack(fill="x", padx=20, pady=5)
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

def open_my_profile():
    global current_cid
    win = ctk.CTk()
    win.title("My Profile")
    win.geometry("600x500")

    # Fetch current data
    profile = database.get_customer_profile(current_cid)
    if not profile:
        messagebox.showerror("Error", "Could not load profile")
        win.destroy()
        open_customer_dashboard()
        return

    # profile: (name, contact_number, shipping_address)
    current_name = profile[0]
    current_contact = profile[1] if profile[1] else ""
    current_address = profile[2] if profile[2] else ""

    ctk.CTkLabel(win, text="Edit Profile", font=("Arial", 20, "bold")).pack(pady=20)

    form_frame = ctk.CTkFrame(win)
    form_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Name
    ctk.CTkLabel(form_frame, text="Full Name:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    entry_name = ctk.CTkEntry(form_frame, width=300)
    entry_name.grid(row=0, column=1, padx=10, pady=10)
    entry_name.insert(0, current_name)

    # Contact
    ctk.CTkLabel(form_frame, text="Contact Number:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
    entry_contact = ctk.CTkEntry(form_frame, width=300)
    entry_contact.grid(row=1, column=1, padx=10, pady=10)
    entry_contact.insert(0, current_contact)

    # Address
    ctk.CTkLabel(form_frame, text="Shipping Address:").grid(row=2, column=0, sticky="nw", padx=10, pady=10)
    entry_address = ctk.CTkTextbox(form_frame, width=300, height=100)
    entry_address.grid(row=2, column=1, padx=10, pady=10)
    entry_address.insert("1.0", current_address)

    def save_profile():
        name = entry_name.get().strip()
        contact = entry_contact.get().strip()
        address = entry_address.get("1.0", END).strip()

        if not name:
            messagebox.showwarning("Warning", "Name cannot be empty")
            return

        if database.update_customer_profile(current_cid, name, contact, address):
            messagebox.showinfo("Success", "Profile updated successfully")
            win.destroy()
            open_customer_dashboard()
        else:
            messagebox.showerror("Error", "Failed to update profile")

    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(fill="x", padx=20, pady=20)
    
    ctk.CTkButton(btn_frame, text="Save Changes", command=save_profile, fg_color="#27ae60", width=150).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="Cancel", command=lambda: (win.destroy(), open_customer_dashboard()), fg_color="#95a5a6", width=150).pack(side="right", padx=10)

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_customer_dashboard()))
    win.mainloop()

def open_cart():
    global current_cid
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
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        cart_items = database.get_cart(current_cid)
        total = 0.0

        for item in cart_items:
            cart_id, product_id, product_name, price, quantity, subtotal = item
            total += float(subtotal)

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

            def update_qty(cid=cart_id, entry=qty_entry, label=subtotal_label, p=price):
                new_qty = entry.get().strip()
                if not new_qty.isdigit() or int(new_qty) < 1:
                    messagebox.showwarning("Warning", "Please enter a valid positive number")
                    return
                if database.update_cart_item(cid, new_qty):
                    load_cart_items() 
                else:
                    messagebox.showerror("Error", "Failed to update quantity")

            def delete_item(cid=cart_id):
                if messagebox.askyesno("Confirm", "Delete this item from cart?"):
                    if database.remove_cart_item(cid):
                        load_cart_items()
                    else:
                        messagebox.showerror("Error", "Failed to delete item")

            ctk.CTkButton(btn_frame, text="Update", command=update_qty, width=60, fg_color="#3498db").grid(row=0, column=0, padx=2)
            ctk.CTkButton(btn_frame, text="Delete", command=delete_item, width=60, fg_color="#e74c3c").grid(row=0, column=1, padx=2)

        total_label.configure(text=f"Total: ${total:.2f}")

    def checkout():
        if database.create_order_from_cart(current_cid):
            messagebox.showinfo("Success", "Order placed successfully!")
            win.destroy()
            open_customer_dashboard()
        else:
            messagebox.showerror("Error", "Checkout failed")

    checkout_btn = ctk.CTkButton(win, text="Checkout", fg_color="#27ae60", command=checkout, width=150)
    checkout_btn.pack(pady=10)

    load_cart_items()
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), open_customer_dashboard()))
    win.mainloop()

def open_my_orders():
    global current_cid
    win = ctk.CTk()
    win.title("My Orders")
    win.geometry("1100x800")

    def back():
        win.destroy()
        open_customer_dashboard()
    
    top_frame = ctk.CTkFrame(win)
    top_frame.pack(fill="x", padx=20, pady=10)
    ctk.CTkButton(top_frame, text="Back", command=back).pack(side="left", padx=5)
    ctk.CTkLabel(top_frame, text="My Order History", font=("Arial", 16, "bold")).pack(side="left", padx=20)

    left_frame = ctk.CTkFrame(win, width=450)
    left_frame.pack(side="left", fill="y", padx=(20, 10), pady=10)
    left_frame.pack_propagate(False)
    
    ctk.CTkLabel(left_frame, text="Orders", font=("Arial", 14, "bold")).pack(pady=5)
    order_list = Listbox(left_frame, font=("Arial", 18), height=25)
    order_list.pack(fill="both", expand=True, padx=10, pady=10)

    right_frame = ctk.CTkFrame(win)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=10)

    detail_header = ctk.CTkFrame(right_frame)
    detail_header.pack(fill="x", padx=10, pady=(10, 5))
    ctk.CTkLabel(detail_header, text="Order Details & Items", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=2)
    
    items_frame = ctk.CTkFrame(right_frame)
    items_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    ctk.CTkLabel(items_frame, text="Items in Selected Order:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)
    
    item_list = Listbox(items_frame, font=("Consolas", 18), height=12, selectmode="single")
    item_list.pack(fill="both", expand=True, padx=5, pady=5)
    
    item_list.bind("<<ListboxSelect>>", lambda e: None)
    
    action_frame = ctk.CTkFrame(right_frame)
    action_frame.pack(fill="x", padx=10, pady=10)
    
    btn_remove_item = ctk.CTkButton(action_frame, text="Remove Selected Item", fg_color="#f39c12", state="disabled")
    btn_remove_item.pack(side="left", padx=5)
    
    btn_cancel_order = ctk.CTkButton(action_frame, text="Cancel Entire Order", fg_color="#e74c3c", state="disabled")
    btn_cancel_order.pack(side="right", padx=5)

    current_selected_oid = None

    def load_user_orders():
        order_list.delete(0, END)
        orders = database.get_user_orders(current_cid)
        for o in orders:
            order_list.insert(END, f"Order:{o[0]} | ${o[1]:.2f} | {o[2]} | {o[3]}")

    def load_order_details_and_items(evt=None):
        nonlocal current_selected_oid
        
        # Only process if there's actually a selection
        sel = order_list.curselection()
        if sel:
            txt = order_list.get(sel[0])
            if txt.startswith("Order:"):
                oid = txt.split("Order:")[1].split("|")[0].strip()
                current_selected_oid = oid
                
                item_list.delete(0, END)
                
                result = database.get_order_items_for_customer(oid, current_cid)
                if not result:
                    item_list.insert(END, "No items found or unauthorized.")
                    btn_remove_item.configure(state="disabled")
                    btn_cancel_order.configure(state="disabled")
                    return
                    
                items, status = result
                
                if not items:
                    item_list.insert(END, "Order is empty.")
                    btn_remove_item.configure(state="disabled")
                    btn_cancel_order.configure(state="disabled")
                    return

                for item in items:
                    item_list.insert(END, f"PID:{item[5]} | {item[1]} | Qty:{item[2]} | ${item[3]:.2f} | Sub:${item[4]:.2f}")
                

                if status == 'pending':
                    btn_remove_item.configure(state="normal")
                    btn_cancel_order.configure(state="normal")
                else:
                    btn_remove_item.configure(state="disabled")
                    btn_cancel_order.configure(state="disabled")
                    item_list.insert(END, f"\n(Status: {status} - No modifications allowed)")

    def remove_selected_item():
        nonlocal current_selected_oid
        if not current_selected_oid:
            return
        
        sel = item_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select an item to remove")
            return
        
        txt = item_list.get(sel[0])
        if not txt.startswith("PID:"):
            return
        
        pid = txt.split("PID:")[1].split("|")[0].strip()
        
        if messagebox.askyesno("Confirm", "Remove this item from the order? Stock will be restored."):
            if database.remove_order_item(current_selected_oid, pid, current_cid):
                messagebox.showinfo("Success", "Item removed")
                
                # Check if order is now empty by getting updated items
                result = database.get_order_items_for_customer(current_selected_oid, current_cid)
                if result:
                    items, status = result
                    if not items or len(items) == 0:
                        # Order is empty, auto-cancel it
                        if database.cancel_order(current_selected_oid):
                            messagebox.showinfo("Info", "Order was empty and has been automatically cancelled")
                            load_user_orders()
                            item_list.delete(0, END)
                            btn_remove_item.configure(state="disabled")
                            btn_cancel_order.configure(state="disabled")
                            current_selected_oid = None
                            order_list.selection_clear(0, END)
                        else:
                            messagebox.showerror("Error", "Failed to auto-cancel empty order")
                            # Still refresh to show empty state
                            load_user_orders()
                            load_order_details_and_items()
                    else:
                        # Order still has items, just refresh
                        load_user_orders()
                        
                        # Reselect the same order to maintain context
                        for i in range(order_list.size()):
                            order_text = order_list.get(i)
                            if order_text.startswith(f"Order:{current_selected_oid}"):
                                order_list.selection_clear(0, END)
                                order_list.selection_set(i)
                                order_list.activate(i)
                                break
                        
                        load_order_details_and_items()
                else:
                    # Could not get order items, refresh as fallback
                    load_user_orders()
                    load_order_details_and_items()
            else:
                messagebox.showerror("Error", "Failed to remove item")

    def cancel_entire_order():
        nonlocal current_selected_oid
        if not current_selected_oid:
            return
        
        if messagebox.askyesno("Confirm", "Cancel this entire order?"):
            if database.cancel_order(current_selected_oid):
                messagebox.showinfo("Success", "Order cancelled")
                load_user_orders()
                item_list.delete(0, END)
                btn_remove_item.configure(state="disabled")
                btn_cancel_order.configure(state="disabled")
            else:
                messagebox.showerror("Error", "Failed to cancel order")

    btn_remove_item.configure(command=remove_selected_item)
    btn_cancel_order.configure(command=cancel_entire_order)
    
    order_list.bind("<<ListboxSelect>>", load_order_details_and_items)
    
    load_user_orders()
    win.mainloop()
    
