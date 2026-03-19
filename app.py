# 导入所有必要库
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import datetime

# ========== 基础配置 ==========
app = Flask(__name__)
# 登录必须的secret_key，不能删！
app.secret_key = "ecommerce_web_2026_en"
# 数据库绝对路径（替换成你的项目路径）
DB_PATH = "C:/Users/86186/Desktop/ecommerce_project/ecommerce.db"
# 订单状态常量
STATUS_PENDING = "PENDING"
STATUS_SHIPPED = "SHIPPED"
STATUS_CANCELLED = "CANCELLED"

# ========== 登录装饰器（确保需要登录的页面必须登录） ==========
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ========== 数据库连接工具函数 ==========
def get_db_conn():
    """获取数据库连接和游标"""
    conn = sqlite3.connect(DB_PATH)
    # 让查询结果返回字典格式
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

# ========== 管理端路由 ==========
@app.route('/')
def index():
    """管理端首页"""
    return render_template('index.html')

@app.route('/vendors')
def vendors():
    """商家管理页面"""
    conn, cursor = get_db_conn()
    cursor.execute("SELECT * FROM vendors ORDER BY vendor_id DESC")
    vendors = cursor.fetchall()
    conn.close()
    return render_template('vendors.html', vendors=vendors)

@app.route('/products')
def products():
    """商品管理页面"""
    conn, cursor = get_db_conn()
    # 查询商品+关联商家名称
    cursor.execute("""
        SELECT p.*, v.business_name 
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
        ORDER BY p.product_id DESC
    """)
    products = cursor.fetchall()
    # 查询所有商家（供新增商品选择）
    cursor.execute("SELECT * FROM vendors")
    vendors = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products, vendors=vendors)

@app.route('/orders')
def orders():
    """订单管理页面（修复查询逻辑，确保显示所有订单）"""
    conn, cursor = get_db_conn()
    order_list = []
    
    try:
        # 查询所有订单 + 关联客户信息
        cursor.execute("""
            SELECT o.*, c.contact, c.shipping_addr
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_id DESC
        """)
        orders = cursor.fetchall()

        # 给每个订单补充交易明细（商品信息）
        for order in orders:
            cursor.execute("""
                SELECT t.*, p.product_name 
                FROM transactions t
                LEFT JOIN products p ON t.product_id = p.product_id
                WHERE t.order_id = ?
            """, (order['order_id'],))
            transactions = cursor.fetchall()
            # 转成普通字典，方便前端渲染
            order_dict = dict(order)
            order_dict['transactions'] = [dict(t) for t in transactions]
            order_list.append(order_dict)
    except Exception as e:
        print(f"查询订单失败: {e}")
        flash(f"查询订单出错: {str(e)}", "error")
    finally:
        conn.close()

    # 查询可下单的商品（供左侧创建订单用）
    conn, cursor = get_db_conn()
    cursor.execute("SELECT product_id, product_name, listed_price FROM products WHERE stock_quantity > 0")
    products = cursor.fetchall()
    product_list = [dict(p) for p in products]
    conn.close()

    return render_template('orders.html', orders=order_list, products=product_list)

@app.route('/create_order', methods=['POST'])
def create_order():
    """管理端手动创建订单"""
    try:
        contact = request.form.get('contact').strip()
        shipping_addr = request.form.get('shipping_addr').strip()
        product_id = request.form.get('product_id')
        buy_quantity = int(request.form.get('buy_quantity'))

        if not contact or not shipping_addr or not product_id or buy_quantity < 1:
            flash('All fields are required!', 'error')
            return redirect(url_for('orders'))

        conn, cursor = get_db_conn()
        # 检查商品库存
        cursor.execute("SELECT stock_quantity, listed_price, vendor_id FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            flash('Product not found!', 'error')
            conn.close()
            return redirect(url_for('orders'))
        
        if product['stock_quantity'] < buy_quantity:
            flash(f'Not enough stock! Current stock: {product["stock_quantity"]}', 'error')
            conn.close()
            return redirect(url_for('orders'))

        # 查找/创建客户
        cursor.execute("SELECT customer_id FROM customers WHERE contact = ?", (contact,))
        customer = cursor.fetchone()
        if customer:
            customer_id = customer['customer_id']
        else:
            cursor.execute("INSERT INTO customers (contact, shipping_addr) VALUES (?, ?)", (contact, shipping_addr))
            customer_id = cursor.lastrowid

        # 计算总价
        total_price = product['listed_price'] * buy_quantity

        # 开启事务
        conn.execute("BEGIN TRANSACTION")
        # 扣库存
        cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?", (buy_quantity, product_id))
        # 创建订单（默认user_id=1，测试用）
        cursor.execute("""
            INSERT INTO orders (customer_id, user_id, total_price, status, create_time)
            VALUES (?, 1, ?, ?, datetime('now', 'localtime'))
        """, (customer_id, total_price, STATUS_PENDING))
        order_id = cursor.lastrowid
        # 创建交易明细
        cursor.execute("""
            INSERT INTO transactions (order_id, product_id, vendor_id, buy_quantity, single_total)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, product_id, product['vendor_id'], buy_quantity, total_price))
        
        conn.commit()
        flash(f'Order #{order_id} created successfully!', 'success')
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"创建订单失败: {e}")
        flash(f'Failed to create order: {str(e)}', 'error')
    finally:
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('orders'))

@app.route('/orders/ship/<int:order_id>')
def ship_order(order_id):
    """标记订单为已发货"""
    try:
        conn, cursor = get_db_conn()
        cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (STATUS_SHIPPED, order_id))
        conn.commit()
        flash(f'Order #{order_id} marked as shipped!', 'success')
    except Exception as e:
        flash(f'Failed to ship order: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('orders'))

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    """取消订单"""
    try:
        conn, cursor = get_db_conn()
        # 回滚库存
        cursor.execute("""
            SELECT t.product_id, t.buy_quantity 
            FROM transactions t 
            WHERE t.order_id = ?
        """, (order_id,))
        transactions = cursor.fetchall()
        for t in transactions:
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE product_id = ?", (t['buy_quantity'], t['product_id']))
        
        # 更新订单状态
        cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (STATUS_CANCELLED, order_id))
        conn.commit()
        flash(f'Order #{order_id} cancelled! Stock restored.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to cancel order: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('orders'))

@app.route('/get_order_details/<int:order_id>')
def get_order_details(order_id):
    """获取订单详情（供模态框）"""
    try:
        conn, cursor = get_db_conn()
        # 查询订单基本信息
        cursor.execute("""
            SELECT o.*, c.contact, c.shipping_addr
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
        """, (order_id,))
        order_info = cursor.fetchone()
        if not order_info:
            return jsonify({'error': 'Order not found!'})
        
        # 查询交易明细
        cursor.execute("""
            SELECT t.*, p.product_name 
            FROM transactions t
            LEFT JOIN products p ON t.product_id = p.product_id
            WHERE t.order_id = ?
        """, (order_id,))
        transactions = cursor.fetchall()
        
        conn.close()
        return jsonify({
            'order_info': dict(order_info),
            'transactions': [dict(t) for t in transactions]
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# ========== 用户端路由 ==========
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """用户登录页"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('user_login.html', error='Username and password are required!')
        
        # 验证账号密码
        conn, cursor = get_db_conn()
        cursor.execute("SELECT user_id, username FROM user_accounts WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # 登录成功，保存session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('user_shop'))
        else:
            return render_template('user_login.html', error='Invalid username or password!')
    
    # GET请求，显示登录页
    return render_template('user_login.html')

@app.route('/user/logout')
def user_logout():
    """用户退出登录"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('user_login'))

@app.route('/user/shop')
@login_required
def user_shop():
    """用户商品浏览页"""
    conn, cursor = get_db_conn()
    # 支持搜索
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        cursor.execute("""
            SELECT * FROM products 
            WHERE product_name LIKE ? AND stock_quantity > 0
            ORDER BY product_id DESC
        """, (f'%{keyword}%',))
    else:
        cursor.execute("SELECT * FROM products WHERE stock_quantity > 0 ORDER BY product_id DESC")
    
    products = cursor.fetchall()
    product_list = [dict(p) for p in products]
    conn.close()
    
    return render_template('user_shop.html', 
                           products=product_list, 
                           keyword=keyword,
                           user={'username': session['username']},
                           cart_count=len(get_user_cart(session['user_id'])))

@app.route('/user/cart')
@login_required
def cart_view():
    """用户购物车页"""
    user_id = session['user_id']
    cart_items = get_user_cart(user_id)
    # 计算总价
    total_price = sum(item['total'] for item in cart_items)
    
    return render_template('user_cart.html', 
                           cart_items=cart_items,
                           total_price=total_price,
                           user={'username': session['username']})

@app.route('/user/cart/add', methods=['POST'])
@login_required
def cart_add():
    """添加商品到购物车"""
    try:
        user_id = session['user_id']
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        
        if quantity < 1:
            flash('Quantity must be at least 1!', 'error')
            return redirect(url_for('user_shop'))
        
        conn, cursor = get_db_conn()
        # 检查商品库存
        cursor.execute("SELECT stock_quantity, product_name, listed_price FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            flash('Product not found!', 'error')
            conn.close()
            return redirect(url_for('user_shop'))
        
        if product['stock_quantity'] < quantity:
            flash(f'Not enough stock for {product["product_name"]}! Current stock: {product["stock_quantity"]}', 'error')
            conn.close()
            return redirect(url_for('user_shop'))
        
        # 检查购物车是否已有该商品
        cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        existing = cursor.fetchone()
        if existing:
            # 更新数量
            new_quantity = existing['quantity'] + quantity
            cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?", (new_quantity, user_id, product_id))
        else:
            # 新增购物车项
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (user_id, product_id, quantity))
        
        conn.commit()
        flash(f'Added {quantity} x {product["product_name"]} to cart!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to add to cart: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('user_shop'))

@app.route('/user/cart/update', methods=['POST'])
@login_required
def cart_update():
    """更新购物车商品数量"""
    try:
        user_id = session['user_id']
        cart_id = request.form.get('cart_id')
        quantity = int(request.form.get('quantity', 1))
        
        if quantity < 1:
            flash('Quantity must be at least 1!', 'error')
            return redirect(url_for('cart_view'))
        
        conn, cursor = get_db_conn()
        # 检查商品库存
        cursor.execute("""
            SELECT p.stock_quantity 
            FROM cart c
            LEFT JOIN products p ON c.product_id = p.product_id
            WHERE c.cart_id = ? AND c.user_id = ?
        """, (cart_id, user_id))
        product = cursor.fetchone()
        if not product:
            flash('Cart item not found!', 'error')
            conn.close()
            return redirect(url_for('cart_view'))
        
        if product['stock_quantity'] < quantity:
            flash(f'Not enough stock! Current stock: {product["stock_quantity"]}', 'error')
            conn.close()
            return redirect(url_for('cart_view'))
        
        # 更新数量
        cursor.execute("UPDATE cart SET quantity = ? WHERE cart_id = ? AND user_id = ?", (quantity, cart_id, user_id))
        conn.commit()
        flash('Cart updated!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to update cart: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('cart_view'))

@app.route('/user/cart/delete/<int:cart_id>')
@login_required
def cart_delete(cart_id):
    """删除购物车商品"""
    try:
        user_id = session['user_id']
        conn, cursor = get_db_conn()
        cursor.execute("DELETE FROM cart WHERE cart_id = ? AND user_id = ?", (cart_id, user_id))
        conn.commit()
        flash('Item removed from cart!', 'success')
    except Exception as e:
        flash(f'Failed to remove item: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('cart_view'))

@app.route('/user/cart/checkout', methods=['POST'])
@login_required
def cart_checkout():
    """购物车结算（核心修复：确保订单能写入数据库）"""
    user_id = session['user_id']
    conn, cursor = get_db_conn()
    
    try:
        print("✅ 接收到结算请求，开始处理...")
        # 1. 获取用户购物车
        cart_items = get_user_cart(user_id)
        if not cart_items:
            flash('Your cart is empty!', 'error')
            conn.close()
            return redirect(url_for('cart_view'))
        
        # 2. 获取用户收货信息
        cursor.execute("SELECT contact, shipping_addr FROM user_accounts WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        if not user_info or not user_info['contact'] or not user_info['shipping_addr']:
            flash('Please complete your contact and shipping address first!', 'error')
            conn.close()
            return redirect(url_for('cart_view'))
        contact, shipping_addr = user_info['contact'], user_info['shipping_addr']
        
        # 3. 查找/创建客户
        cursor.execute("SELECT customer_id FROM customers WHERE contact = ?", (contact,))
        customer = cursor.fetchone()
        if customer:
            customer_id = customer['customer_id']
        else:
            cursor.execute("INSERT INTO customers (contact, shipping_addr) VALUES (?, ?)", (contact, shipping_addr))
            customer_id = cursor.lastrowid
        
        # 4. 计算总价
        total_price = sum(item['total'] for item in cart_items)
        print(f"✅ 订单总价：{total_price}，客户ID：{customer_id}")
        
        # 5. 开启事务（确保原子性）
        conn.execute("BEGIN TRANSACTION")
        
        # 6. 扣减库存 + 验证库存
        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']
            # 再次检查库存（防止并发问题）
            cursor.execute("SELECT stock_quantity, vendor_id FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()
            if product['stock_quantity'] < quantity:
                raise Exception(f'Not enough stock for {item["product_name"]}! Current stock: {product["stock_quantity"]}')
            # 扣库存
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?", (quantity, product_id))
            item['vendor_id'] = product['vendor_id']  # 保存商家ID，用于交易明细
        
        # 7. 创建订单
        cursor.execute("""
            INSERT INTO orders (customer_id, user_id, total_price, status, create_time)
            VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
        """, (customer_id, user_id, total_price, STATUS_PENDING))
        order_id = cursor.lastrowid
        print(f"✅ 生成订单ID：{order_id}")
        
        # 8. 创建交易明细
        for item in cart_items:
            cursor.execute("""
                INSERT INTO transactions (order_id, product_id, vendor_id, buy_quantity, single_total)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item['product_id'], item['vendor_id'], item['quantity'], item['total']))
        
        # 9. 清空购物车
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        
        # 提交事务
        conn.commit()
        print(f"✅ 订单 {order_id} 创建成功！")
        flash(f'Order #{order_id} created successfully! Thank you for your purchase!', 'success')
        return redirect(url_for('user_shop'))
    
    except Exception as e:
        # 出错回滚所有操作
        conn.rollback()
        print(f"❌ 结算失败：{str(e)}")
        flash(f'Failed to create order: {str(e)}', 'error')
        return redirect(url_for('cart_view'))
    finally:
        conn.close()

# ========== 工具函数：获取用户购物车 ==========
def get_user_cart(user_id):
    """获取用户购物车（带商品详情和总价）"""
    conn, cursor = get_db_conn()
    cursor.execute("""
        SELECT c.cart_id, c.product_id, c.quantity, p.product_name, p.listed_price, p.stock_quantity
        FROM cart c
        LEFT JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ?
    """, (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    
    # 转换格式 + 计算每个商品总价
    result = []
    for item in cart_items:
        item_dict = dict(item)
        item_dict['total'] = item_dict['listed_price'] * item_dict['quantity']
        result.append(item_dict)
    return result

# ========== 调试路由（可选） ==========
@app.route('/debug/orders')
def debug_orders():
    """调试用：查看所有订单原始数据"""
    conn, cursor = get_db_conn()
    cursor.execute("SELECT * FROM orders ORDER BY order_id DESC")
    orders = cursor.fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])

@app.route('/test/create_order')
@login_required
def test_create_order():
    """手动创建测试订单（快速验证）"""
    user_id = session['user_id']
    conn, cursor = get_db_conn()
    
    try:
        # 创建测试订单（商品ID=1，数量=1）
        cursor.execute("INSERT INTO orders (customer_id, user_id, total_price, status, create_time) VALUES (1, ?, 999.99, 'PENDING', datetime('now'))", (user_id,))
        order_id = cursor.lastrowid
        cursor.execute("INSERT INTO transactions (order_id, product_id, vendor_id, buy_quantity, single_total) VALUES (?, 1, 1, 1, 999.99)", (order_id,))
        conn.commit()
        flash(f'Test order #{order_id} created!', 'success')
    except Exception as e:
        flash(f'Failed to create test order: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('orders'))

# ========== 启动应用 ==========
if __name__ == '__main__':
    # 开启调试模式，修改代码自动重启
    app.run(debug=True, host='0.0.0.0', port=5000)