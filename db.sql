CREATE DATABASE IF NOT EXISTS ecommerce_platform;
USE ecommerce_platform;

-- Admin Table
CREATE TABLE admin (
    admin_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL
);

-- Vendor Table
CREATE TABLE Vendor (
    vendor_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    location VARCHAR(255)
);

-- Customer Table
CREATE TABLE Customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL,
    contact_number VARCHAR(20),
    shipping_address TEXT
);

-- Product Table
CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    tag1 VARCHAR(50),
    tag2 VARCHAR(50),
    tag3 VARCHAR(50),
    image_path VARCHAR(255),
    FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id) ON DELETE CASCADE
);

-- Cart Item Table
CREATE TABLE cart_item (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE
);

-- Orders Table
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, shipped, cancelled, completed
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Order Item Table
CREATE TABLE Order_Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- -------------------- Initial Data --------------------

-- 1. Admins
INSERT INTO admin (admin_id, name, password) VALUES 
('admin', 'Super Admin', '123456'),
('manager', 'Store Manager', '123456');

-- 2. Vendors (Expanded)
INSERT INTO Vendor (vendor_id, name, password, rating, location) VALUES 
('xiaomi', 'Xiaomi Official', '123456', 4.8, 'Beijing, China'),
('huawei', 'Huawei Store', '123456', 4.7, 'Shenzhen, China'),
('apple_auth', 'Apple Authorized Reseller', '123456', 4.9, 'Shanghai, China'),
('nike_store', 'Nike Official', '123456', 4.6, 'Guangzhou, China'),
('book_world', 'Book World Inc.', '123456', 4.5, 'Nanjing, China'),
('home_goods', 'Home & Living', '123456', 4.3, 'Hangzhou, China');

-- 3. Customers (Expanded)
INSERT INTO Customer (customer_id, name, password, contact_number, shipping_address) VALUES 
('zhan3', 'Zhang San', '123456', '13800138000', 'No.1 Street, Beijing'),
('li4', 'Li Si', '123456', '13900139000', 'No.2 Avenue, Shanghai'),
('wang5', 'Wang Wu', '123456', '13700137000', 'Room 303, Building A, Shenzhen'),
('zhao6', 'Zhao Liu', '123456', '13600136000', 'No.88 West Lake Road, Hangzhou'),
('sun7', 'Sun Qi', '123456', '13500135000', 'Unit 502, Tech Park, Nanjing');

-- 4. Products (Expanded Variety)

-- Xiaomi Products
INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES 
('xiaomi', 'Mi Band 7', 299.00, 100, 'Electronics', 'Wearable', 'Fitness'),
('xiaomi', 'Redmi Note 12', 1599.00, 50, 'Electronics', 'Smartphone', '5G'),
('xiaomi', 'Xiaomi Air Purifier 4', 1299.00, 30, 'Home', 'Appliance', 'Health'),
('xiaomi', 'Mi Robot Vacuum', 2499.00, 20, 'Home', 'Robot', 'Cleaning'),
('xiaomi', 'Redmi Buds 4 Pro', 599.00, 80, 'Audio', 'Earbuds', 'Wireless');

-- Huawei Products
INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES 
('huawei', 'MateBook D14', 4999.00, 30, 'Electronics', 'Laptop', 'Office'),
('huawei', 'P60 Pro', 6999.00, 25, 'Electronics', 'Smartphone', 'Camera'),
('huawei', 'FreeBuds 5i', 499.00, 100, 'Audio', 'Earbuds', 'Noise Cancelling'),
('huawei', 'Watch GT 3', 1488.00, 40, 'Electronics', 'Wearable', 'Sports'),
('huawei', 'Router AX3 Pro', 329.00, 60, 'Network', 'WiFi', 'Home');

-- Apple Reseller Products
INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES 
('apple_auth', 'iPhone 15 Pro', 8999.00, 15, 'Electronics', 'Smartphone', 'Premium'),
('apple_auth', 'MacBook Air M2', 9499.00, 10, 'Electronics', 'Laptop', 'Portable'),
('apple_auth', 'AirPods Pro 2', 1899.00, 50, 'Audio', 'Earbuds', 'Apple'),
('apple_auth', 'iPad Air 5', 4799.00, 20, 'Electronics', 'Tablet', 'Study'),
('apple_auth', 'MagSafe Charger', 329.00, 200, 'Accessory', 'Charger', 'Apple');

-- Nike Products
INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES 
('nike_store', 'Air Max 270', 1299.00, 40, 'Shoes', 'Running', 'Sports'),
('nike_store', 'Dri-FIT T-Shirt', 199.00, 150, 'Clothing', 'T-Shirt', 'Summer'),
('nike_store', 'Sport Backpack', 399.00, 60, 'Accessory', 'Bag', 'Travel'),
('nike_store', 'Jordan 1 Low', 899.00, 25, 'Shoes', 'Basketball', 'Casual'),
('nike_store', 'Pro Compression Shorts', 249.00, 80, 'Clothing', 'Shorts', 'Gym');

-- Book World Products
INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES 
('book_world', 'Python Crash Course', 89.00, 100, 'Books', 'Programming', 'Education'),
('book_world', 'Clean Code', 75.00, 80, 'Books', 'Programming', 'Software'),
('book_world', 'The Three-Body Problem', 45.00, 200, 'Books', 'Sci-Fi', 'Novel'),
('book_world', 'Atomic Habits', 55.00, 150, 'Books', 'Self-Help', 'Psychology'),
('book_world', 'Kindle Paperwhite', 1099.00, 30, 'Electronics', 'E-reader', 'Reading');

-- Home Goods Products
INSERT INTO Product (vendor_id, product_name, price, stock, tag1, tag2, tag3) VALUES 
('home_goods', 'Cotton Bed Sheet Set', 299.00, 50, 'Home', 'Bedding', 'Cotton'),
('home_goods', 'LED Desk Lamp', 129.00, 100, 'Home', 'Lighting', 'Study'),
('home_goods', 'Ceramic Coffee Mug Set', 89.00, 120, 'Kitchen', 'Mug', 'Gift'),
('home_goods', 'Memory Foam Pillow', 159.00, 80, 'Home', 'Bedding', 'Comfort'),
('home_goods', 'Storage Box Large', 49.00, 200, 'Home', 'Organization', 'Plastic');

-- 5. Sample Orders (To test Order History)
-- Order 1: Zhang San buys a Mi Band and a Book
INSERT INTO Orders (order_id, customer_id, total_price, status, order_time) VALUES 
(1001, 'zhan3', 388.00, 'completed', '2023-10-01 10:00:00');

INSERT INTO Order_Item (order_id, product_id, quantity, unit_price) VALUES 
(1001, 1, 1, 299.00), -- Mi Band 7
(1001, 21, 1, 89.00);  -- Python Crash Course

-- Order 2: Li Si buys an iPhone
INSERT INTO Orders (order_id, customer_id, total_price, status, order_time) VALUES 
(1002, 'li4', 8999.00, 'shipped', '2023-10-05 14:30:00');

INSERT INTO Order_Item (order_id, product_id, quantity, unit_price) VALUES 
(1002, 11, 1, 8999.00); -- iPhone 15 Pro

-- Order 3: Wang Wu buys Shoes and Shirt (Pending - can be cancelled/modified)
INSERT INTO Orders (order_id, customer_id, total_price, status, order_time) VALUES 
(1003, 'wang5', 1498.00, 'pending', '2023-10-20 09:15:00');

INSERT INTO Order_Item (order_id, product_id, quantity, unit_price) VALUES 
(1003, 16, 1, 1299.00), -- Air Max 270
(1003, 17, 1, 199.00);  -- Dri-FIT T-Shirt