import pymysql
from pymysql import Error
from tkinter import messagebox

def connect_db():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="ecommerce_platform",
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Connection failed: {str(e)}")
        return None

# -------------------- Auth --------------------
def login_customer(cid, pwd):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT customer_id, name, password, contact_number, shipping_address FROM customer WHERE customer_id=%s AND password=%s", (cid, pwd))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

def login_admin(aid, pwd):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin WHERE admin_id=%s AND password=%s", (aid, pwd))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

def login_vendor(vid, pwd):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT vendor_id, name, password, rating, location FROM Vendor WHERE vendor_id=%s AND password=%s", (vid, pwd))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

# -------------------- Vendor  --------------------
def get_all_vendors():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT vendor_id, name, rating, location FROM Vendor")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def add_vendor(vid, name, pwd):
    if not vid or not name or not pwd:
        return False
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT vendor_id FROM Vendor WHERE vendor_id = %s", (vid,))
        if cur.fetchone():
            messagebox.showerror("Error", f"Vendor ID {vid} already exists!")
            return False
        cur.execute(
            "INSERT INTO Vendor (vendor_id, name, password, rating, location) VALUES (%s, %s, %s, 0.0, '')",
            (vid, name, pwd)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Add Vendor Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def delete_vendor(vid):
    if not vid:
        return False
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Product WHERE vendor_id = %s", (vid,))
        cur.execute("DELETE FROM Vendor WHERE vendor_id = %s", (vid,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete Vendor Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# -------------------- Products --------------------
def get_all_products():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT * FROM Product")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def get_vendor_products(vid):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT * FROM Product WHERE vendor_id=%s", (vid,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def add_product(vid, name, price, stock, tag1, tag2="", tag3=""):
    if not vid or not name or not price or not stock:
        return False
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (vid, name, float(price), int(stock), tag1, tag2, tag3)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Add Product Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def update_product(pid, name, price, stock, tag1, tag2="", tag3=""):
    if not pid or not name or not price or not stock:
        return False
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        # Optional: Check if product belongs to vendor if we passed vid, but for now simple update
        cur.execute(
            "UPDATE Product SET product_name=%s, price=%s, stock=%s, tag1=%s, tag2=%s, tag3=%s WHERE product_id=%s",
            (name, float(price), int(stock), tag1, tag2, tag3, pid)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Update Product Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def delete_product(pid):
    if not pid:
        return False
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM order_item WHERE product_id=%s", (pid,))
        cur.execute("DELETE FROM Product WHERE product_id=%s", (pid,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete Product Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def search_products(keyword):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    like_key = f"%{keyword}%"
    sql = """
        SELECT * FROM Product 
        WHERE product_name LIKE %s 
        OR tag1 LIKE %s 
        OR tag2 LIKE %s 
        OR tag3 LIKE %s
    """
    cur.execute(sql, (like_key, like_key, like_key, like_key))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

# -------------------- Cart --------------------
def add_to_cart(cid, pid_str, qty_str):
    try:
        pid = int(pid_str)
        qty = int(qty_str)
    except ValueError:
        return False

    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT stock FROM Product WHERE product_id = %s", (pid,))
        stock_result = cur.fetchone()
        if not stock_result:
            return False
        if int(stock_result[0]) < qty:
            messagebox.showwarning("Warning", "Insufficient stock")
            return False

        cur.execute("SELECT quantity FROM cart_item WHERE customer_id=%s AND product_id=%s", (cid, pid))
        item = cur.fetchone()
        if item:
            new_qty = int(item[0]) + qty
            if int(stock_result[0]) < new_qty:
                 messagebox.showwarning("Warning", "Insufficient stock for total quantity")
                 return False
            cur.execute("UPDATE cart_item SET quantity=%s WHERE customer_id=%s AND product_id=%s", (new_qty, cid, pid))
        else:
            cur.execute("INSERT INTO cart_item (customer_id, product_id, quantity) VALUES (%s,%s,%s)", (cid, pid, qty))
        conn.commit()
        return True
    except Exception as e:
        print(f"Add to Cart Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_cart(cid):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT ci.cart_id, ci.product_id, p.product_name, p.price, ci.quantity,
                   (p.price * ci.quantity) AS subtotal
            FROM cart_item ci
            JOIN Product p ON ci.product_id = p.product_id
            WHERE ci.customer_id = %s
        """, (cid,))
        res = cur.fetchall()
        return res
    except Exception as e:
        print(f"Get Cart Error: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()

def update_cart_item(cart_id, new_qty):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.stock, ci.product_id 
            FROM cart_item ci 
            JOIN Product p ON ci.product_id = p.product_id 
            WHERE ci.cart_id = %s
        """, (cart_id,))
        res = cur.fetchone()
        if not res:
            return False
        stock, pid = res
        if int(stock) < int(new_qty):
            messagebox.showwarning("Warning", "Insufficient stock")
            return False
            
        cur.execute("UPDATE cart_item SET quantity = %s WHERE cart_id = %s", (new_qty, cart_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Update Cart Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def remove_cart_item(cart_id):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cart_item WHERE cart_id = %s", (cart_id,))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# -------------------- Orders --------------------
def create_order_from_cart(cid):
    cart_items = get_cart(cid)
    if not cart_items:
        return False

    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()

    try:
        total = sum(float(item[5]) for item in cart_items)

        cur.execute("""
            INSERT INTO orders (customer_id, total_price, status, order_time)
            VALUES (%s, %s, 'pending', CURRENT_TIMESTAMP)
        """, (cid, total))
        order_id = cur.lastrowid

        for item in cart_items:
            pid = item[1]
            qty = item[4]
            price = item[3] 
            
            cur.execute("""
                INSERT INTO order_item (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, pid, qty, price))
            
            cur.execute("UPDATE Product SET stock = stock - %s WHERE product_id = %s", (qty, pid))

        cur.execute("DELETE FROM cart_item WHERE customer_id = %s", (cid,))

        conn.commit()
        return True

    except Exception as e:
        print("ERROR:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_user_orders(cid):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT order_id, total_price, status, order_time FROM orders WHERE customer_id=%s ORDER BY order_time DESC", (cid,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def get_vendor_orders(vid):
    """Get all orders that contain at least one product from this vendor"""
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    # Distinct orders because an order might have multiple items from same vendor
    cur.execute("""
        SELECT DISTINCT o.order_id, o.total_price, o.status, o.order_time 
        FROM orders o
        JOIN order_item oi ON o.order_id = oi.order_id
        JOIN Product p ON oi.product_id = p.product_id
        WHERE p.vendor_id = %s
        ORDER BY o.order_time DESC
    """, (vid,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def get_order_full_details(order_id):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT p.product_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS subtotal, p.vendor_id
        FROM order_item oi
        INNER JOIN Product p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
    """, (order_id,))
    details = cur.fetchall()
    cur.close()
    conn.close()
    return details

def cancel_order(oid):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT status FROM orders WHERE order_id=%s", (oid,))
        status_res = cur.fetchone()
        if not status_res or status_res[0] != "pending":
            messagebox.showwarning("Warning", "Only pending orders can be cancelled")
            return False

        cur.execute("SELECT product_id, quantity FROM order_item WHERE order_id=%s", (oid,))
        items = cur.fetchall()
        for pid, qty in items:
            cur.execute("UPDATE Product SET stock = stock + %s WHERE product_id=%s", (qty, pid))

        cur.execute("DELETE FROM order_item WHERE order_id=%s", (oid,))
        cur.execute("DELETE FROM orders WHERE order_id=%s", (oid,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Cancel Order Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_order_items_for_customer(oid, cid):
    """Get order items for a specific order and customer, ensuring ownership"""
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    try:
        # Verify order belongs to customer first
        cur.execute("SELECT customer_id, status FROM orders WHERE order_id=%s", (oid,))
        order_info = cur.fetchone()
        if not order_info or order_info[0] != cid:
            return [] # Not found or not owned
        
        status = order_info[1]
        
        cur.execute("""
            SELECT oi.item_id, p.product_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS subtotal, p.product_id
            FROM order_item oi
            INNER JOIN Product p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (oid,))
        items = cur.fetchall()
        return items, status
    except Exception as e:
        print(f"Get Order Items Error: {str(e)}")
        return [], None
    finally:
        cur.close()
        conn.close()

def remove_order_item(oid, pid, cid):
    """Remove a specific item from an order and restore stock. Only if pending."""
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        # Check ownership and status
        cur.execute("SELECT customer_id, status FROM orders WHERE order_id=%s", (oid,))
        order_info = cur.fetchone()
        if not order_info or order_info[0] != cid:
            messagebox.showerror("Error", "Unauthorized access")
            return False
        if order_info[1] != 'pending':
            messagebox.showwarning("Warning", "Only pending orders can be modified")
            return False

        # Get quantity to restore stock
        cur.execute("SELECT quantity FROM order_item WHERE order_id=%s AND product_id=%s", (oid, pid))
        item_res = cur.fetchone()
        if not item_res:
            return False
        
        qty = item_res[0]
        
        # Restore stock
        cur.execute("UPDATE Product SET stock = stock + %s WHERE product_id=%s", (qty, pid))
        
        # Delete item
        cur.execute("DELETE FROM order_item WHERE order_id=%s AND product_id=%s", (oid, pid))
        
        # Recalculate Total Price for the order
        cur.execute("SELECT SUM(quantity * unit_price) FROM order_item WHERE order_id=%s", (oid,))
        new_total_res = cur.fetchone()
        new_total = new_total_res[0] if new_total_res[0] is not None else 0.0
        
        cur.execute("UPDATE orders SET total_price=%s WHERE order_id=%s", (new_total, oid))
        
        # Optional: If no items left, delete the order? 
        # For now, we leave it with 0 total. Or we could call cancel_order if new_total == 0.
        if new_total == 0:
             cur.execute("DELETE FROM orders WHERE order_id=%s", (oid,))

        conn.commit()
        return True
    except Exception as e:
        print(f"Remove Order Item Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
def get_customer_profile(cid):
    """Retrieve customer profile details"""
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, contact_number, shipping_address FROM Customer WHERE customer_id=%s", (cid,))
        res = cur.fetchone()
        return res
    except Exception as e:
        print(f"Get Profile Error: {str(e)}")
        return None
    finally:
        cur.close()
        conn.close()

def update_customer_profile(cid, name, contact, address):
    """Update customer profile details"""
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Customer SET name=%s, contact_number=%s, shipping_address=%s WHERE customer_id=%s",
            (name, contact, address, cid)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Update Profile Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()