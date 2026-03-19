import sqlite3
from config import DB_PATH, STATUS_PENDING, STATUS_CANCELLED, STATUS_SHIPPED

def get_db_conn():
    """Create and return database connection and cursor"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None, None

def close_db_conn(conn, cursor):
    """Close database connection and cursor"""
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# ------------------------------ Vendor Operations ------------------------------
def query_all_vendors():
    """Query all vendors"""
    conn, cursor = get_db_conn()
    if not conn:
        return []
    try:
        cursor.execute("SELECT * FROM vendors ORDER BY vendor_id")
        vendors = [dict(row) for row in cursor.fetchall()]
        return vendors
    except sqlite3.Error as e:
        print(f"Query vendors error: {e}")
        return []
    finally:
        close_db_conn(conn, cursor)

def add_vendor(business_name, avg_rating, geography):
    """Add a new vendor"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, "Failed to connect to database"
    try:
        cursor.execute(
            """INSERT INTO vendors (business_name, avg_rating, geography) 
               VALUES (?, ?, ?)""",
            (business_name, avg_rating, geography)
        )
        conn.commit()
        return True, f"Vendor '{business_name}' added successfully"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Add vendor failed: {e}"
    finally:
        close_db_conn(conn, cursor)

# ------------------------------ Customer Operations ------------------------------
def add_customer(contact, shipping_addr):
    """Add a new customer (return customer_id if success)"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, 0, "Failed to connect to database"
    try:
        # Check if customer already exists
        cursor.execute("SELECT customer_id FROM customers WHERE contact = ?", (contact,))
        existing = cursor.fetchone()
        if existing:
            return True, existing["customer_id"], "Customer already exists (using existing ID)"
        
        # Insert new customer
        cursor.execute(
            """INSERT INTO customers (contact, shipping_addr) 
               VALUES (?, ?)""",
            (contact, shipping_addr)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        return True, customer_id, "Customer added successfully"
    except sqlite3.Error as e:
        conn.rollback()
        return False, 0, f"Add customer failed: {e}"
    finally:
        close_db_conn(conn, cursor)

# ------------------------------ Product Operations ------------------------------
def query_products_by_vendor(vendor_id):
    """Query products by vendor ID"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, "Failed to connect to database"
    try:
        cursor.execute("SELECT * FROM products WHERE vendor_id = ? ORDER BY product_id", (vendor_id,))
        products = [dict(row) for row in cursor.fetchall()]
        return True, products
    except sqlite3.Error as e:
        return False, f"Query products failed: {e}"
    finally:
        close_db_conn(conn, cursor)

def search_products(keyword):
    """Search products by keyword (name/tag)"""
    conn, cursor = get_db_conn()
    if not conn:
        return []
    try:
        cursor.execute(
            """SELECT * FROM products 
               WHERE product_name LIKE ? OR tag1 LIKE ? OR tag2 LIKE ? OR tag3 LIKE ? 
               ORDER BY product_id""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        products = [dict(row) for row in cursor.fetchall()]
        return products
    except sqlite3.Error as e:
        print(f"Search products error: {e}")
        return []
    finally:
        close_db_conn(conn, cursor)

def add_product(vendor_id, product_name, listed_price, stock_quantity, tag1=None, tag2=None, tag3=None):
    """Add a new product"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, "Failed to connect to database"
    try:
        cursor.execute(
            """INSERT INTO products (vendor_id, product_name, listed_price, stock_quantity, tag1, tag2, tag3) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (vendor_id, product_name, listed_price, stock_quantity, tag1, tag2, tag3)
        )
        conn.commit()
        return True, f"Product '{product_name}' added successfully"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Add product failed: {e}"
    finally:
        close_db_conn(conn, cursor)

def update_product_stock(product_id, quantity):
    """Update product stock (reduce by quantity, return success status)"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, "Failed to connect to database"
    try:
        # Check current stock
        cursor.execute("SELECT stock_quantity FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            return False, "Product does not exist"
        
        current_stock = product["stock_quantity"]
        if current_stock < quantity:
            return False, f"Insufficient stock (current: {current_stock}, required: {quantity})"
        
        # Update stock
        cursor.execute(
            "UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
            (quantity, product_id)
        )
        conn.commit()
        return True, "Stock updated successfully"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Update stock failed: {e}"
    finally:
        close_db_conn(conn, cursor)

# ------------------------------ Order Operations ------------------------------
def create_order(customer_id, product_list):
    """
    Create a new order
    product_list: list of dict, e.g. [{"product_id": 1, "buy_quantity": 2}]
    """
    conn, cursor = get_db_conn()
    if not conn:
        return False, "Failed to connect to database"
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Calculate total price
        total_price = 0
        for item in product_list:
            product_id = item["product_id"]
            buy_quantity = item["buy_quantity"]
            
            # Get product info
            cursor.execute("SELECT listed_price FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()
            if not product:
                conn.rollback()
                return False, f"Product ID {product_id} does not exist"
            
            # Update stock first
            stock_success, stock_msg = update_product_stock(product_id, buy_quantity)
            if not stock_success:
                conn.rollback()
                return False, f"Failed to update stock for product {product_id}: {stock_msg}"
            
            # Accumulate total price
            total_price += product["listed_price"] * buy_quantity
        
        # Insert order
        cursor.execute(
            """INSERT INTO orders (customer_id, total_price, status) 
               VALUES (?, ?, ?)""",
            (customer_id, total_price, STATUS_PENDING)
        )
        order_id = cursor.lastrowid
        
        # Insert transaction records
        for item in product_list:
            cursor.execute(
                """INSERT INTO transactions (order_id, product_id, vendor_id, buy_quantity, single_total) 
                   VALUES (?, ?, (SELECT vendor_id FROM products WHERE product_id = ?), ?, ?)""",
                (order_id, item["product_id"], item["product_id"], item["buy_quantity"], 
                 item["buy_quantity"] * cursor.execute("SELECT listed_price FROM products WHERE product_id = ?", (item["product_id"],)).fetchone()["listed_price"])
            )
        
        conn.commit()
        return True, f"Order {order_id} created successfully (Total: ${total_price:.2f})"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Create order failed: {e}"
    finally:
        close_db_conn(conn, cursor)

def cancel_order(order_id):
    """Cancel an order (only pending orders can be cancelled)"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, "Failed to connect to database"
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Check order status
        cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            conn.rollback()
            return False, f"Order {order_id} does not exist"
        
        if order["status"] != STATUS_PENDING:
            conn.rollback()
            return False, f"Cannot cancel order (current status: {order['status']})"
        
        # Get transaction records to restore stock
        cursor.execute("SELECT product_id, buy_quantity FROM transactions WHERE order_id = ?", (order_id,))
        transactions = cursor.fetchall()
        if not transactions:
            conn.rollback()
            return False, f"No transaction records for order {order_id}"
        
        # Restore product stock
        for trans in transactions:
            product_id = trans["product_id"]
            buy_quantity = trans["buy_quantity"]
            cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                (buy_quantity, product_id)
            )
        
        # Update order status to cancelled
        cursor.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            (STATUS_CANCELLED, order_id)
        )
        
        conn.commit()
        return True, f"Order {order_id} cancelled successfully (stock restored)"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Cancel order failed: {e}"
    finally:
        close_db_conn(conn, cursor)

def query_order_details(order_id):
    """Query order details (order info + transaction records)"""
    conn, cursor = get_db_conn()
    if not conn:
        return False, {}
    
    try:
        # Get order info
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        order = dict(cursor.fetchone()) if cursor.fetchone() else None
        if not order:
            return False, {"error": f"Order {order_id} does not exist"}
        
        # Get transaction records
        cursor.execute("""
            SELECT t.*, p.product_name, p.listed_price 
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            WHERE t.order_id = ?
        """, (order_id,))
        transactions = [dict(row) for row in cursor.fetchall()]
        
        return True, {
            "order_info": order,
            "transactions": transactions
        }
    except sqlite3.Error as e:
        return False, {"error": f"Query order failed: {e}"}
    finally:
        close_db_conn(conn, cursor)