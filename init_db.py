import sqlite3
import datetime
from config import DB_PATH, STATUS_PENDING, STATUS_SHIPPED, STATUS_CANCELLED

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("✅ Connected to database successfully")

    # 用户账号表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_accounts (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            contact TEXT,
            shipping_addr TEXT
        )
    ''')

    # 购物车表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            FOREIGN KEY (user_id) REFERENCES user_accounts(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, product_id)
        )
    ''')

    # 商家表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            avg_rating REAL NOT NULL CHECK(avg_rating BETWEEN 0 AND 5),
            geography TEXT NOT NULL
        )
    ''')

    # 商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            listed_price REAL NOT NULL CHECK(listed_price > 0),
            stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
            tag1 TEXT,
            tag2 TEXT,
            tag3 TEXT,
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
        )
    ''')

    # 客户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT NOT NULL UNIQUE,
            shipping_addr TEXT NOT NULL
        )
    ''')

    # 订单表（已包含 user_id，修复字段缺失）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL CHECK(total_price >= 0),
            status TEXT NOT NULL CHECK(status IN ('PENDING', 'SHIPPED', 'CANCELLED')),
            create_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (user_id) REFERENCES user_accounts(user_id)
        )
    ''')

    # 交易明细表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            buy_quantity INTEGER NOT NULL CHECK(buy_quantity > 0),
            single_total REAL NOT NULL CHECK(single_total >= 0),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
        )
    ''')

    conn.commit()
    print("✅ All tables created/verified successfully")

    # 测试用户
    cursor.execute('''
        INSERT OR IGNORE INTO user_accounts (username, password, contact, shipping_addr)
        VALUES ('user1', '123456', '+1234567890', '123 Main St, New York, NY 10001')
    ''')
    print("✅ Inserted test user (user1 / 123456)")

    # 测试商家
    vendors_data = [
        ("Tech Electronics Ltd", 4.8, "New York, USA"),
        ("Fashion Hub Inc", 4.5, "Los Angeles, USA"),
        ("Home Goods Store", 4.2, "Chicago, USA")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO vendors (business_name, avg_rating, geography)
        VALUES (?, ?, ?)
    ''', vendors_data)
    print("✅ Inserted test vendors")

    # 测试商品
    products_data = [
        (1, "iPhone 15 Pro", 999.99, 50, "Electronics", "Phone", "Apple"),
        (1, "MacBook Air M3", 1199.99, 30, "Electronics", "Laptop", "Apple"),
        (2, "Nike Air Max 270", 129.99, 100, "Fashion", "Shoes", "Sports"),
        (2, "Levi's 501 Jeans", 69.99, 80, "Fashion", "Clothing", "Denim"),
        (3, "Kitchen Blender", 79.99, 40, "Home", "Kitchen", "Appliance"),
        (3, "Cotton Bed Sheet Set", 49.99, 60, "Home", "Bedding", "Textile")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO products (vendor_id, product_name, listed_price, stock_quantity, tag1, tag2, tag3)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products_data)
    print("✅ Inserted test products")

    # 测试客户
    customers_data = [
        ("+1234567890", "123 Main St, New York, NY 10001"),
        ("+1987654321", "456 Oak Ave, Los Angeles, CA 90001"),
        ("+1122334455", "789 Pine Rd, Chicago, IL 60001")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO customers (contact, shipping_addr)
        VALUES (?, ?)
    ''', customers_data)
    print("✅ Inserted test customers")

    # 测试订单（已带 user_id）
    orders_data = [
        (1, 1, 999.99, STATUS_PENDING, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        (2, 1, 129.99, STATUS_SHIPPED, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        (3, 1, 129.98, STATUS_CANCELLED, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO orders (customer_id, user_id, total_price, status, create_time)
        VALUES (?, ?, ?, ?, ?)
    ''', orders_data)
    print("✅ Inserted test orders")

    # 测试交易明细
    transactions_data = [
        (1, 1, 1, 1, 999.99),
        (2, 3, 2, 1, 129.99),
        (3, 5, 3, 1, 79.99),
        (3, 6, 3, 1, 49.99)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO transactions (order_id, product_id, vendor_id, buy_quantity, single_total)
        VALUES (?, ?, ?, ?, ?)
    ''', transactions_data)
    print("✅ Inserted test transactions")

    conn.commit()
    cursor.close()
    conn.close()
    print("\n🎉 Database initialization completed successfully!")

if __name__ == "__main__":
    init_database()