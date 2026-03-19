import sqlite3
import datetime

# ========== 关键修改：改成你的项目绝对路径 ==========
DB_PATH = "C:/Users/86186/Desktop/ecommerce_project/ecommerce.db"
# ==================================================
STATUS_PENDING = "PENDING"
STATUS_SHIPPED = "SHIPPED"
STATUS_CANCELLED = "CANCELLED"

def force_rebuild_database():
    # 强制创建/连接数据库（绝对路径，确保生成到指定文件夹）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"✅ 连接数据库成功，路径：{DB_PATH}")

    # 第一步：强制删除所有旧表（彻底清空）
    tables = ['transactions', 'orders', 'customers', 'products', 'vendors', 'cart', 'user_accounts']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"✅ 删除旧表 {table}")

    # 第二步：按顺序重建所有表（确保外键关联正确）
    # 1. 用户账号表（先建，因为 orders 关联它）
    cursor.execute('''
        CREATE TABLE user_accounts (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            contact TEXT,
            shipping_addr TEXT
        )
    ''')

    # 2. 商家表
    cursor.execute('''
        CREATE TABLE vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            avg_rating REAL NOT NULL CHECK(avg_rating BETWEEN 0 AND 5),
            geography TEXT NOT NULL
        )
    ''')

    # 3. 商品表
    cursor.execute('''
        CREATE TABLE products (
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

    # 4. 客户表
    cursor.execute('''
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT NOT NULL UNIQUE,
            shipping_addr TEXT NOT NULL
        )
    ''')

    # 5. 订单表（明确包含 user_id，放在客户表后）
    cursor.execute('''
        CREATE TABLE orders (
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

    # 6. 购物车表
    cursor.execute('''
        CREATE TABLE cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            FOREIGN KEY (user_id) REFERENCES user_accounts(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, product_id)
        )
    ''')

    # 7. 交易明细表
    cursor.execute('''
        CREATE TABLE transactions (
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

    print("✅ 所有表已强制重建（包含 user_id）")

    # 插入测试数据（字段顺序100%匹配）
    # 1. 用户
    cursor.execute('''
        INSERT INTO user_accounts (username, password, contact, shipping_addr)
        VALUES ('user1', '123456', '+1234567890', '123 Main St, New York, NY 10001')
    ''')
    # 2. 商家
    cursor.executemany('''
        INSERT INTO vendors (business_name, avg_rating, geography)
        VALUES (?, ?, ?)
    ''', [
        ("Tech Electronics Ltd", 4.8, "New York, USA"),
        ("Fashion Hub Inc", 4.5, "Los Angeles, USA"),
        ("Home Goods Store", 4.2, "Chicago, USA")
    ])
    # 3. 商品
    cursor.executemany('''
        INSERT INTO products (vendor_id, product_name, listed_price, stock_quantity, tag1, tag2, tag3)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (1, "iPhone 15 Pro", 999.99, 50, "Electronics", "Phone", "Apple"),
        (1, "MacBook Air M3", 1199.99, 30, "Electronics", "Laptop", "Apple"),
        (2, "Nike Air Max 270", 129.99, 100, "Fashion", "Shoes", "Sports"),
        (2, "Levi's 501 Jeans", 69.99, 80, "Fashion", "Clothing", "Denim"),
        (3, "Kitchen Blender", 79.99, 40, "Home", "Kitchen", "Appliance"),
        (3, "Cotton Bed Sheet Set", 49.99, 60, "Home", "Bedding", "Textile")
    ])
    # 4. 客户
    cursor.executemany('''
        INSERT INTO customers (contact, shipping_addr)
        VALUES (?, ?)
    ''', [
        ("+1234567890", "123 Main St, New York, NY 10001"),
        ("+1987654321", "456 Oak Ave, Los Angeles, CA 90001"),
        ("+1122334455", "789 Pine Rd, Chicago, IL 60001")
    ])
    # 5. 订单（字段顺序：customer_id, user_id, total_price, status, create_time）
    cursor.executemany('''
        INSERT INTO orders (customer_id, user_id, total_price, status, create_time)
        VALUES (?, ?, ?, ?, ?)
    ''', [
        (1, 1, 999.99, STATUS_PENDING, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        (2, 1, 129.99, STATUS_SHIPPED, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        (3, 1, 129.98, STATUS_CANCELLED, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ])
    # 6. 交易明细
    cursor.executemany('''
        INSERT INTO transactions (order_id, product_id, vendor_id, buy_quantity, single_total)
        VALUES (?, ?, ?, ?, ?)
    ''', [
        (1, 1, 1, 1, 999.99),
        (2, 3, 2, 1, 129.99),
        (3, 5, 3, 1, 79.99),
        (3, 6, 3, 1, 49.99)
    ])

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\n🎉 数据库强制重建成功！文件已生成到：{DB_PATH}")

if __name__ == "__main__":
    force_rebuild_database()