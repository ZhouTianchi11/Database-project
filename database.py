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
    cur.execute("SELECT * FROM customer WHERE customer_id=%s AND password=%s", (cid, pwd))
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

# -------------------- Vendor  --------------------
def get_all_vendors():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT vendor_id, name FROM Vendor")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def add_vendor(vid, name, pwd):
    if not vid or not name or not pwd:
        print("Add Vendor Error: Missing required fields")
        return False

    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT vendor_id FROM Vendor WHERE vendor_id = %s", (vid,))
        if cur.fetchone():
            print(f"Add Vendor Error: Vendor ID {vid} already exists")
            messagebox.showerror("Error", f"Vendor ID {vid} already exists!")
            return False

        cur.execute(
            "INSERT INTO Vendor (vendor_id, name, password) VALUES (%s, %s, %s)",
            (vid, name, pwd)
        )
        conn.commit()
        print(f"Vendor {vid} added successfully")
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
        print("Delete Vendor Error: Missing vendor ID")
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

def add_product(vid, name, price, stock, tag):
    if not vid or not name or not price or not stock:
        print("Add Product Error: Missing required fields")
        return False

    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Product (vendor_id, product_name, price, stock, tag) VALUES (%s, %s, %s, %s, %s)",
            (vid, name, float(price), int(stock), tag)
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

def update_product(pid, name, price, stock, tag):
    if not pid or not name or not price or not stock:
        print("Update Product Error: Missing required fields")
        return False

    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Product SET product_name=%s, price=%s, stock=%s, tag=%s WHERE product_id=%s",
            (name, float(price), int(stock), tag, pid)
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
        print("Delete Product Error: Missing product ID")
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
    except:
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
    cur.execute("SELECT * FROM Product WHERE product_name LIKE %s OR tag LIKE %s", (like_key, like_key))
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
        print("Add to Cart Error: Invalid ID or Quantity")
        return False

    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT stock FROM Product WHERE product_id = %s", (pid,))
        stock_result = cur.fetchone()
        if not stock_result:
            print("Add to Cart Error: Product not found")
            return False
        if int(stock_result[0]) < qty:
            print("Add to Cart Error: Insufficient stock")
            return False

        cur.execute("SELECT quantity FROM cart_item WHERE customer_id=%s AND product_id=%s", (cid, pid))
        item = cur.fetchone()
        if item:
            new_qty = int(item[0]) + qty
            cur.execute("UPDATE cart_item SET quantity=%s WHERE customer_id=%s AND product_id=%s", (new_qty, cid, pid))
        else:
            cur.execute("INSERT INTO cart_item (customer_id, product_id, quantity) VALUES (%s,%s,%s)", (cid, pid, qty))
        conn.commit()
        return True
    except Exception as e:
        print(f"Add to Cart Error: {str(e)}")
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
        cur.execute("UPDATE cart_item SET quantity = %s WHERE cart_id = %s", (new_qty, cart_id))
        conn.commit()
        return True
    except:
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
        return False
    finally:
        cur.close()
        conn.close()

def clear_cart(cid):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cart_item WHERE customer_id=%s", (cid,))
        conn.commit()
        return True
    except:
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

def get_order_full_details(order_id):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    # Correct SQL: JOIN order_item + Product to get product details
    cur.execute("""
        SELECT p.product_name, oi.quantity, p.price, (oi.quantity * p.price) AS subtotal
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
        if cur.fetchone()[0] != "pending":
            return False

        cur.execute("SELECT product_id, quantity FROM order_item WHERE order_id=%s", (oid,))
        items = cur.fetchall()
        for pid, qty in items:
            cur.execute("UPDATE Product SET stock = stock + %s WHERE product_id=%s", (qty, pid))

        cur.execute("DELETE FROM order_item WHERE order_id=%s", (oid,))
        cur.execute("DELETE FROM orders WHERE order_id=%s", (oid,))
        conn.commit()
        return True
    except:
        return False
    finally:
        cur.close()
        conn.close()