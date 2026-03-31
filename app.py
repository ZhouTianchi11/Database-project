import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import database
from config import COLOR, FONT

class ECommerceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E-Commerce System")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        self.cart = []
        self.user_id = None
        self.role = None

        self.after(100, self.show_login)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        frame = ctk.CTkFrame(self, width=420, height=440, corner_radius=20)
        frame.pack(pady=100)

        ctk.CTkLabel(frame, text="Login", font=FONT["title"]).pack(pady=35)

        id_entry = ctk.CTkEntry(frame, placeholder_text="ID", width=320, height=42)
        id_entry.pack(pady=8)
        pwd_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=320, height=42)
        pwd_entry.pack(pady=8)

        def customer_login():
            uid = id_entry.get().strip()
            pwd = pwd_entry.get().strip()
            if not uid or not pwd:
                messagebox.showwarning("Warning", "Please fill all fields")
                return
            if database.login_customer(uid, pwd):
                self.user_id = uid
                self.role = "customer"
                self.show_customer_panel()
            else:
                messagebox.showerror("Error", "Login failed")

        def vendor_login():
            uid = id_entry.get().strip()
            pwd = pwd_entry.get().strip()
            if not uid or not pwd:
                messagebox.showwarning("Warning", "Please fill all fields")
                return
            if database.login_vendor(uid, pwd):
                self.user_id = uid
                self.role = "vendor"
                self.show_vendor_panel()
            else:
                messagebox.showerror("Error", "Login failed")

        ctk.CTkButton(frame, text="Customer Login", fg_color=COLOR["primary"],
                      command=customer_login, width=320, height=42).pack(pady=10)
        ctk.CTkButton(frame, text="Vendor Login", fg_color=COLOR["success"],
                      command=vendor_login, width=320, height=42).pack(pady=5)

    def show_customer_panel(self):
        self.clear_frame()
        top_bar = ctk.CTkFrame(self, height=70)
        top_bar.pack(fill="x")

        ctk.CTkLabel(top_bar, text="Shopping Mall", font=FONT["title"]).pack(side="left", padx=30)
        ctk.CTkButton(top_bar, text="Cart", fg_color=COLOR["success"],
                      command=self.show_cart_panel).pack(side="right", padx=10)
        ctk.CTkButton(top_bar, text="Logout", fg_color=COLOR["danger"],
                      command=self.show_login).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=15)

        products = database.get_all_products()
        if not products:
            ctk.CTkLabel(scroll, text="No products available", text_color=COLOR["gray"]).pack(pady=50)
            return

        for p in products:
            card = ctk.CTkFrame(scroll, height=150, corner_radius=12)
            card.pack(fill="x", pady=10, padx=10)

            try:
                img_path = p.get("image_path", "")
                img_path = img_path.strip() if img_path else ""
                if img_path and os.path.exists(img_path):
                    img = Image.open(img_path).convert("RGB").resize((100, 100))
                    ctk_img = ctk.CTkImage(img, size=(100, 100))
                    img_label = ctk.CTkLabel(card, image=ctk_img, text="")
                    img_label.place(x=20, y=25)
                    card.ctk_img = ctk_img
            except Exception as e:
                print(f"Image load error: {e}")
                pass

            ctk.CTkLabel(card, text=p["product_name"], font=FONT["subtitle"]).place(x=140, y=30)
            ctk.CTkLabel(card, text=f"$ {p['price']}", text_color=COLOR["primary"]).place(x=140, y=65)
            ctk.CTkLabel(card, text=f"Stock: {p['stock']}").place(x=140, y=95)

            qty_entry = ctk.CTkEntry(card, width=60)
            qty_entry.insert(0, "1")
            qty_entry.place(x=300, y=65)

            def add_to_cart(pid, name, price):
                try:
                    qty = int(qty_entry.get())
                    if qty <= 0:
                        messagebox.showerror("Error", "Quantity must be greater than 0")
                        return
                    self.cart.append({
                        "product_id": pid,
                        "name": name,
                        "price": price,
                        "quantity": qty
                    })
                    messagebox.showinfo("Success", "Added to cart")
                except ValueError:
                    messagebox.showerror("Error", "Invalid quantity")

            ctk.CTkButton(card, text="Add to Cart",
                          command=lambda pid=p["product_id"], n=p["product_name"], p=p["price"]:
                          add_to_cart(pid, n, p)).place(x=380, y=65)

    def show_cart_panel(self):
        self.clear_frame()
        top_bar = ctk.CTkFrame(self, height=70)
        top_bar.pack(fill="x")

        ctk.CTkLabel(top_bar, text="Shopping Cart", font=FONT["title"]).pack(side="left", padx=30)
        ctk.CTkButton(top_bar, text="Back", command=self.show_customer_panel).pack(side="left", padx=10)
        ctk.CTkButton(top_bar, text="Logout", fg_color=COLOR["danger"], command=self.show_login).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        total = 0
        if not self.cart:
            ctk.CTkLabel(scroll, text="Your cart is empty", text_color=COLOR["gray"]).pack(pady=50)
        else:
            for item in self.cart:
                row = ctk.CTkFrame(scroll)
                row.pack(fill="x", pady=5, padx=10)
                ctk.CTkLabel(row, text=item["name"], width=250).grid(row=0, column=0, padx=15, pady=10)
                ctk.CTkLabel(row, text=f"$ {item['price']} x {item['quantity']}", width=150).grid(row=0, column=1)
                total += item["price"] * item["quantity"]

            ctk.CTkLabel(scroll, text=f"Total: $ {round(total,2)}", font=FONT["subtitle"]).pack(pady=15)

            def checkout():
                if database.create_order(self.user_id, self.cart):
                    self.cart.clear()
                    self.show_customer_panel()

            ctk.CTkButton(scroll, text="Checkout", fg_color=COLOR["success"], command=checkout).pack()

    def show_vendor_panel(self):
        self.clear_frame()
        top_bar = ctk.CTkFrame(self, height=70)
        top_bar.pack(fill="x")

        ctk.CTkLabel(top_bar, text="Vendor Dashboard", font=FONT["title"]).pack(side="left", padx=30)
        ctk.CTkButton(top_bar, text="Logout", fg_color=COLOR["danger"], command=self.show_login).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=15)

        add_frame = ctk.CTkFrame(scroll, corner_radius=12)
        add_frame.pack(fill="x", pady=15)
        ctk.CTkLabel(add_frame, text="Add New Product", font=FONT["subtitle"]).pack(pady=10)

        img_path = ctk.StringVar()
        def select_image():
            f = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg")])
            if f:
                img_path.set(f)

        input_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_frame.pack(pady=10)
        name_entry = ctk.CTkEntry(input_frame, placeholder_text="Name", width=140)
        price_entry = ctk.CTkEntry(input_frame, placeholder_text="Price", width=100)
        stock_entry = ctk.CTkEntry(input_frame, placeholder_text="Stock", width=100)
        t1 = ctk.CTkEntry(input_frame, placeholder_text="Tag1", width=100)
        t2 = ctk.CTkEntry(input_frame, placeholder_text="Tag2", width=100)
        t3 = ctk.CTkEntry(input_frame, placeholder_text="Tag3", width=100)

        for i, w in enumerate([name_entry, price_entry, stock_entry, t1, t2, t3]):
            w.grid(row=0, column=i, padx=5)

        ctk.CTkButton(input_frame, text="Image", command=select_image).grid(row=0, column=6, padx=5)

        def add_product():
            ok = database.add_product(
                self.user_id, name_entry.get(), price_entry.get(), stock_entry.get(),
                t1.get(), t2.get(), t3.get(), img_path.get()
            )
            if ok:
                messagebox.showinfo("Success", "Product added")
                self.show_vendor_panel()
            else:
                messagebox.showerror("Error", "Failed to add product")

        ctk.CTkButton(input_frame, text="Add", fg_color=COLOR["success"], command=add_product).grid(row=0, column=7, padx=5)

        ctk.CTkLabel(scroll, text="My Products", font=FONT["subtitle"]).pack(pady=15)
        products = database.get_vendor_products(self.user_id)
        for p in products:
            row = ctk.CTkFrame(scroll, corner_radius=8, height=80)
            row.pack(fill="x", pady=8, padx=10)

            try:
                img_path = p.get("image_path", "")
                img_path = img_path.strip() if img_path else ""
                if img_path and os.path.exists(img_path):
                    img = Image.open(img_path).convert("RGB").resize((60, 60))
                    ctk_img = ctk.CTkImage(img, size=(60, 60))
                    img_label = ctk.CTkLabel(row, image=ctk_img, text="")
                    img_label.grid(row=0, column=0, padx=10, pady=10)
                    row.ctk_img = ctk_img
            except Exception as e:
                print(f"Vendor image error: {e}")
                pass

            ctk.CTkLabel(row, text=p["product_name"], font=FONT["text"], width=180).grid(row=0, column=1, padx=5, pady=10)
            ctk.CTkLabel(row, text=f"$ {p['price']}", font=FONT["text"], width=80).grid(row=0, column=2, padx=5, pady=10)
            ctk.CTkLabel(row, text=f"Stock: {p['stock']}", font=FONT["text"], width=80).grid(row=0, column=3, padx=5, pady=10)

            def edit(pid):
                self.open_edit_window(pid)
            def delete(pid):
                if messagebox.askyesno("Confirm", "Delete this product?"):
                    if database.delete_product(pid):
                        self.show_vendor_panel()

            ctk.CTkButton(row, text="Edit", fg_color=COLOR["primary"],
                          command=lambda pid=p["product_id"]: edit(pid)).grid(row=0, column=4, padx=5, pady=10)
            ctk.CTkButton(row, text="Delete", fg_color=COLOR["danger"],
                          command=lambda pid=p["product_id"]: delete(pid)).grid(row=0, column=5, padx=5, pady=10)

        ctk.CTkLabel(scroll, text="Customer Orders", font=FONT["subtitle"]).pack(pady=20)
        orders = database.get_vendor_orders_detailed(self.user_id)

        if not orders:
            ctk.CTkLabel(scroll, text="No orders yet", text_color=COLOR["gray"]).pack(pady=10)
        else:
            for order in orders:
                order_card = ctk.CTkFrame(scroll, corner_radius=8)
                order_card.pack(fill="x", pady=8, padx=10)

                header_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=10, pady=5)

                ctk.CTkLabel(header_frame, text=f"Order #{order['order_id']}", font=FONT["subtitle"]).grid(row=0, column=0, padx=10, sticky="w")
                ctk.CTkLabel(header_frame, text=f"Customer: {order['customer_name']}").grid(row=0, column=1, padx=10)
                ctk.CTkLabel(header_frame, text=f"Time: {order['order_time']}").grid(row=0, column=2, padx=10)
                ctk.CTkLabel(header_frame, text=f"Status: {order['status']}", text_color=COLOR["success"]).grid(row=0, column=3, padx=10)
                ctk.CTkLabel(header_frame, text=f"Total: $ {round(order['total_price'],2)}", font=FONT["subtitle"], text_color=COLOR["primary"]).grid(row=0, column=4, padx=10, sticky="e")

                expand_btn = ctk.CTkButton(header_frame, text="▼ Details", width=80,
                                         command=lambda f=order_card: self.toggle_order_details(f))
                expand_btn.grid(row=0, column=5, padx=10)

                detail_frame = ctk.CTkFrame(order_card)
                detail_frame.pack(fill="x", padx=20, pady=5)
                detail_frame.pack_forget()

                for item in order["items"]:
                    item_row = ctk.CTkFrame(detail_frame, fg_color="transparent")
                    item_row.pack(fill="x", padx=5, pady=2)
                    ctk.CTkLabel(item_row, text=item["product_name"], width=200).grid(row=0, column=0, padx=10)
                    ctk.CTkLabel(item_row, text=f"$ {item['price']}", width=80).grid(row=0, column=1)
                    ctk.CTkLabel(item_row, text=f"Qty: {item['quantity']}", width=80).grid(row=0, column=2)
                    ctk.CTkLabel(item_row, text=f"Subtotal: $ {round(item['price']*item['quantity'],2)}", width=120).grid(row=0, column=3)

                setattr(order_card, "detail_frame", detail_frame)
                setattr(order_card, "expand_btn", expand_btn)

    def toggle_order_details(self, card):
        frame = card.detail_frame
        btn = card.expand_btn
        if frame.winfo_ismapped():
            frame.pack_forget()
            btn.configure(text="▼ Details")
        else:
            frame.pack(fill="x", padx=20, pady=5)
            btn.configure(text="▲ Hide")

    def open_edit_window(self, pid):
        try:
            products = database.get_vendor_products(self.user_id)
            prod = next((p for p in products if p["product_id"] == pid), None)
            if not prod:
                messagebox.showerror("Error", "Product not found")
                return

            win = ctk.CTkToplevel(self)
            win.title("Edit Product")
            win.geometry("600x700")
            win.transient(self)
            win.grab_set()

            img_path = ctk.StringVar(value=prod.get("image_path", "") or "")
            def select_image():
                f = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg")])
                if f:
                    img_path.set(f)

            ctk.CTkLabel(win, text="Product Name").pack(pady=5)
            name_entry = ctk.CTkEntry(win)
            name_entry.insert(0, str(prod["product_name"]))
            name_entry.pack(pady=5)

            ctk.CTkLabel(win, text="Price").pack(pady=5)
            price_entry = ctk.CTkEntry(win)
            price_entry.insert(0, str(prod["price"]))
            price_entry.pack(pady=5)

            ctk.CTkLabel(win, text="Stock").pack(pady=5)
            stock_entry = ctk.CTkEntry(win)
            stock_entry.insert(0, str(prod["stock"]))
            stock_entry.pack(pady=5)

            t1 = ctk.CTkEntry(win)
            t1.insert(0, str(prod.get("tag1", "")))
            t2 = ctk.CTkEntry(win)
            t2.insert(0, str(prod.get("tag2", "")))
            t3 = ctk.CTkEntry(win)
            t3.insert(0, str(prod.get("tag3", "")))

            ctk.CTkLabel(win, text="Tag 1").pack(pady=5)
            t1.pack(pady=5)
            ctk.CTkLabel(win, text="Tag 2").pack(pady=5)
            t2.pack(pady=5)
            ctk.CTkLabel(win, text="Tag 3").pack(pady=5)
            t3.pack(pady=5)

            ctk.CTkEntry(win, textvariable=img_path, width=400).pack(pady=5)
            ctk.CTkButton(win, text="Select Image", command=select_image).pack(pady=5)

            def save_update():
                try:
                    price_val = float(price_entry.get().strip())
                    stock_val = int(stock_entry.get().strip())
                    name_val = name_entry.get().strip()
                    if not name_val:
                        messagebox.showwarning("Warning", "Product name cannot be empty")
                        return

                    ok = database.update_product(
                        pid, name_val, price_val, stock_val,
                        t1.get().strip(), t2.get().strip(), t3.get().strip(), img_path.get().strip()
                    )
                    if ok:
                        messagebox.showinfo("Success", "Updated successfully")
                        win.destroy()
                        self.show_vendor_panel()
                    else:
                        messagebox.showerror("Error", "Update failed")
                except ValueError:
                    messagebox.showerror("Error", "Price and stock must be numbers")
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {str(e)}")

            ctk.CTkButton(win, text="Save", fg_color=COLOR["success"], command=save_update).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Open window failed: {str(e)}")

if __name__ == "__main__":
    app = ECommerceApp()
    app.mainloop()