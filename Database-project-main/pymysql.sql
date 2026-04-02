DROP DATABASE IF EXISTS ecommerce_platform;
CREATE DATABASE ecommerce_platform;
USE ecommerce_platform;

CREATE SCHEMA `ecommerce_platform`;

CREATE TABLE IF NOT EXISTS admin (
    admin_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL
);

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


CREATE TABLE cart_item (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
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

INSERT INTO admin (admin_id, name, password) 
VALUES ('admin', 'Super Admin', '123456');

SHOW TABLES;

USE ecommerce_platform;

DELIMITER //
CREATE PROCEDURE safe_drop_column(
    IN table_name VARCHAR(64),
    IN column_name VARCHAR(64)
)
BEGIN
    DECLARE column_count INT;
    SELECT COUNT(*) INTO column_count
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = table_name
      AND COLUMN_NAME = column_name;
    
    IF column_count > 0 THEN
        SET @sql = CONCAT('ALTER TABLE ', table_name, ' DROP COLUMN ', column_name);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

CALL safe_drop_column('Product', 'tag2');
CALL safe_drop_column('Product', 'tag3');

ALTER TABLE Product CHANGE COLUMN tag1 tag VARCHAR(50);

DROP PROCEDURE IF EXISTS safe_drop_column;


USE ecommerce_platform;
DESC Product;

USE ecommerce_platform;

ALTER TABLE orders ADD COLUMN total DECIMAL(10,2) NOT NULL AFTER customer_id;


ALTER TABLE orders ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending' AFTER total;

ALTER TABLE orders ADD COLUMN order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER status;
