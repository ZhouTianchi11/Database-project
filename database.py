import pymysql
from pymysql import Error
from tkinter import messagebox

def connect_db():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="test",
            password="666666",
            database="ecommerce_platform"
        )
        return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Connection failed: {str(e)}")
        return None

def get_all_products():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM Product")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def get_vendor_products(vid):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM Product WHERE vendor_id=%s", (vid,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def add_product(vid, name, price, stock, t1, t2, t3, img):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        price = float(price)
        stock = int(stock)
        cur.execute("""
            INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3, image_path)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (vid, name, price, stock, t1, t2, t3, img))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Add Product Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def update_product(pid, name, price, stock, t1, t2, t3, img):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        price = float(price)
        stock = int(stock)
        cur.execute("""
            UPDATE Product
            SET product_name=%s, price=%s, stock=%s, tag1=%s, tag2=%s, tag3=%s, image_path=%s
            WHERE product_id=%s
        """, (name, price, stock, t1, t2, t3, img, pid))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Update Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def delete_product(pid):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Order_Item WHERE product_id=%s", (pid,))
        cur.execute("DELETE FROM Product WHERE product_id=%s", (pid,))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Delete Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def login_customer(uid, pwd):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM Customer WHERE customer_id=%s AND password=%s", (uid, pwd))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

def login_vendor(uid, pwd):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM Vendor WHERE vendor_id=%s AND password=%s", (uid, pwd))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

def create_order(cid, cart):
    conn = connect_db()
    if not conn:
        messagebox.showerror("Checkout Error", "Database connection failed")
        return False
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        if not cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return False

        total = 0
        for item in cart:
            pid = item['product_id']
            qty = item['quantity']
            cur.execute("SELECT price, stock, product_name FROM Product WHERE product_id=%s", (pid,))
            p = cur.fetchone()
            if not p:
                messagebox.showerror("Error", "Product not found")
                return False
            if p['stock'] < qty:
                messagebox.showerror("Error", f"Insufficient stock: {p['stock']} left")
                return False
            total += p['price'] * qty

        cur.execute("INSERT INTO Orders (customer_id, total_price, status) VALUES (%s,%s,'pending')", (cid, total))
        oid = cur.lastrowid

        for item in cart:
            cur.execute("INSERT INTO Order_Item (order_id, product_id, quantity) VALUES (%s,%s,%s)",
                        (oid, item['product_id'], item['quantity']))
            cur.execute("UPDATE Product SET stock=stock-%s WHERE product_id=%s",
                        (item['quantity'], item['product_id']))

        conn.commit()
        messagebox.showinfo("Success", f"Order placed! Order ID: {oid}")
        return True

    except Error as e:
        conn.rollback()
        messagebox.showerror("Checkout Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def get_vendor_orders_detailed(vid):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("""
            SELECT o.order_id, o.order_time, o.total_price, o.status, c.name AS customer_name
            FROM Orders o
            JOIN Customer c ON o.customer_id = c.customer_id
            WHERE EXISTS (
                SELECT 1 FROM Order_Item oi
                JOIN Product p ON oi.product_id = p.product_id
                WHERE oi.order_id = o.order_id AND p.vendor_id = %s
            )
            ORDER BY o.order_time DESC
        """, (vid,))
        orders = cur.fetchall()

        for order in orders:
            cur.execute("""
                SELECT p.product_name, p.price, oi.quantity
                FROM Order_Item oi
                JOIN Product p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s AND p.vendor_id = %s
            """, (order["order_id"], vid))
            order["items"] = cur.fetchall()
            order["status"] = order.get("status", "Pending")

        return orders
    except Error as e:
        messagebox.showerror("Order Error", str(e))
        return []
    finally:
        cur.close()
        conn.close()