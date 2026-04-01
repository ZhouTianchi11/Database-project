
CREATE SCHEMA `ecommerce_platform` ;


CREATE TABLE Customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL
);


CREATE TABLE Vendor (
    vendor_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL
);


CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    tag1 VARCHAR(50),
    tag2 VARCHAR(50),
    tag3 VARCHAR(50),
    image_path VARCHAR(255),
    FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id)
);


CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Order_Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);


insert into Customer values ('zhan3', '张三', '123456');
insert into Customer values ('li4', '李四', '123456');  
insert into Customer values ('wang5', '王五', '123456');
insert into Customer values ('zhao6', '赵六', '123456');
insert into Customer values ('sun7', '孙七', '123456');
insert into Customer values ('qian8', '钱八', '123456');


insert into Vendor values ('xiaomi', 'xiaomi', '123456');
insert into Vendor values ('huawei', 'huawei', '123456');


-- 1. Customer
-- customer_id：客户账号（登录用）
-- name：客户姓名
-- password：密码

-- 2. Vendor
-- vendor_id：商家账号（登录用）
-- name：商家名称
-- password：密码

-- 3. Product
-- product_id：商品 ID
-- vendor_id：所属商家
-- product_name：商品名
-- price：价格
-- stock：库存
-- tag1/tag2/tag3：标签
-- image_path：图片路径

-- 4. Orders
-- order_id：订单号
-- customer_id：下单客户
-- order_time：下单时间
-- total_price：订单总价
-- status：订单状态（pending）

-- 5. Order_Item
-- item_id：明细 ID
-- order_id：属于哪个订单
-- product_id：哪个商品
-- quantity：购买数量