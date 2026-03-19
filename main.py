import db_operate as db
from config import COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_RESET, STATUS_PENDING

def clear_screen():
    """Clear terminal screen (cross-platform)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    """Print main menu"""
    clear_screen()
    print(COLOR_GREEN + "="*40 + COLOR_RESET)
    print(COLOR_GREEN + "    Multi-Vendor E-Commerce Platform    " + COLOR_RESET)
    print(COLOR_GREEN + "="*40 + COLOR_RESET)
    print("1. Vendor Management Module")
    print("2. Product Catalog Module")
    print("3. Product Discovery Module (Search)")
    print("4. Order Creation Module")
    print("5. Order Management Module")
    print("0. Exit System")
    print(COLOR_GREEN + "="*40 + COLOR_RESET)

# ------------------------------ Vendor Management ------------------------------
def vendor_management():
    """Vendor management submenu"""
    while True:
        clear_screen()
        print(COLOR_YELLOW + "=== Vendor Management ===" + COLOR_RESET)
        print("1. View All Vendors")
        print("2. Add New Vendor")
        print("0. Return to Main Menu")
        
        choice = input("Please enter your choice (0-2): ")
        if choice == "0":
            break
        elif choice == "1":
            # View all vendors
            vendors = db.query_all_vendors()
            if not vendors:
                print(COLOR_RED + "No vendors found in database" + COLOR_RESET)
            else:
                print(COLOR_GREEN + "\n--- All Vendors ---" + COLOR_RESET)
                print(f"{'ID':<6} {'Name':<30} {'Rating':<8} {'Region':<20}")
                print("-"*70)
                for vendor in vendors:
                    print(f"{vendor['vendor_id']:<6} {vendor['business_name']:<30} {vendor['avg_rating']:<8} {vendor['geography']:<20}")
        elif choice == "2":
            # Add new vendor
            print(COLOR_YELLOW + "\n--- Add New Vendor ---" + COLOR_RESET)
            business_name = input("Enter vendor name: ")
            while True:
                try:
                    avg_rating = float(input("Enter vendor rating (0-5): "))
                    if 0 <= avg_rating <= 5:
                        break
                    else:
                        print(COLOR_RED + "Rating must be between 0 and 5" + COLOR_RESET)
                except ValueError:
                    print(COLOR_RED + "Invalid rating (must be a number)" + COLOR_RESET)
            geography = input("Enter vendor region: ")
            
            success, msg = db.add_vendor(business_name, avg_rating, geography)
            if success:
                print(COLOR_GREEN + msg + COLOR_RESET)
            else:
                print(COLOR_RED + msg + COLOR_RESET)
        else:
            print(COLOR_RED + "Invalid choice, please try again" + COLOR_RESET)
        
        input("\nPress Enter to continue...")

# ------------------------------ Product Catalog ------------------------------
def product_catalog():
    """Product catalog submenu"""
    while True:
        clear_screen()
        print(COLOR_YELLOW + "=== Product Catalog ===" + COLOR_RESET)
        print("1. View Products by Vendor")
        print("2. Add New Product")
        print("0. Return to Main Menu")
        
        choice = input("Please enter your choice (0-2): ")
        if choice == "0":
            break
        elif choice == "1":
            # View products by vendor
            vendors = db.query_all_vendors()
            if not vendors:
                print(COLOR_RED + "No vendors found, cannot view products" + COLOR_RESET)
                input("\nPress Enter to continue...")
                continue
            
            print(COLOR_YELLOW + "\n--- Select Vendor ---" + COLOR_RESET)
            for vendor in vendors:
                print(f"{vendor['vendor_id']}. {vendor['business_name']}")
            
            while True:
                try:
                    vendor_id = int(input("Enter vendor ID to view products: "))
                    break
                except ValueError:
                    print(COLOR_RED + "Invalid ID (must be a number)" + COLOR_RESET)
            
            success, res = db.query_products_by_vendor(vendor_id)
            if not success:
                print(COLOR_RED + res + COLOR_RESET)
            else:
                if not res:
                    print(COLOR_YELLOW + f"No products found for vendor ID {vendor_id}" + COLOR_RESET)
                else:
                    print(COLOR_GREEN + f"\n--- Products for Vendor ID {vendor_id} ---" + COLOR_RESET)
                    print(f"{'ID':<6} {'Name':<30} {'Price':<10} {'Stock':<8} {'Tags':<30}")
                    print("-"*90)
                    for product in res:
                        tags = f"{product['tag1'] or ''}, {product['tag2'] or ''}, {product['tag3'] or ''}".strip(", ")
                        print(f"{product['product_id']:<6} {product['product_name']:<30} ${product['listed_price']:<9.2f} {product['stock_quantity']:<8} {tags:<30}")
        elif choice == "2":
            # Add new product
            vendors = db.query_all_vendors()
            if not vendors:
                print(COLOR_RED + "No vendors found, cannot add products" + COLOR_RESET)
                input("\nPress Enter to continue...")
                continue
            
            print(COLOR_YELLOW + "\n--- Add New Product ---" + COLOR_RESET)
            print("Available Vendors:")
            for vendor in vendors:
                print(f"{vendor['vendor_id']}. {vendor['business_name']}")
            
            # Select vendor
            while True:
                try:
                    vendor_id = int(input("Enter vendor ID for this product: "))
                    # Validate vendor ID
                    vendor_ids = [v["vendor_id"] for v in vendors]
                    if vendor_id in vendor_ids:
                        break
                    else:
                        print(COLOR_RED + "Vendor ID does not exist" + COLOR_RESET)
                except ValueError:
                    print(COLOR_RED + "Invalid ID (must be a number)" + COLOR_RESET)
            
            # Product info
            product_name = input("Enter product name: ")
            while True:
                try:
                    listed_price = float(input("Enter product price: $"))
                    if listed_price > 0:
                        break
                    else:
                        print(COLOR_RED + "Price must be greater than 0" + COLOR_RESET)
                except ValueError:
                    print(COLOR_RED + "Invalid price (must be a number)" + COLOR_RESET)
            
            while True:
                try:
                    stock_quantity = int(input("Enter stock quantity: "))
                    if stock_quantity >= 0:
                        break
                    else:
                        print(COLOR_RED + "Stock quantity cannot be negative" + COLOR_RESET)
                except ValueError:
                    print(COLOR_RED + "Invalid quantity (must be a number)" + COLOR_RESET)
            
            tag1 = input("Enter tag 1 (optional): ") or None
            tag2 = input("Enter tag 2 (optional): ") or None
            tag3 = input("Enter tag 3 (optional): ") or None
            
            success, msg = db.add_product(vendor_id, product_name, listed_price, stock_quantity, tag1, tag2, tag3)
            if success:
                print(COLOR_GREEN + msg + COLOR_RESET)
            else:
                print(COLOR_RED + msg + COLOR_RESET)
        else:
            print(COLOR_RED + "Invalid choice, please try again" + COLOR_RESET)
        
        input("\nPress Enter to continue...")

# ------------------------------ Product Discovery ------------------------------
def product_discovery():
    """Product search module"""
    while True:
        clear_screen()
        print(COLOR_YELLOW + "=== Product Discovery ===" + COLOR_RESET)
        keyword = input("Enter search keyword (or '0' to return): ")
        if keyword == "0":
            break
        
        products = db.search_products(keyword)
        if not products:
            print(COLOR_RED + f"No products found for keyword: {keyword}" + COLOR_RESET)
        else:
            print(COLOR_GREEN + f"\n--- Search Results for '{keyword}' ({len(products)} items) ---" + COLOR_RESET)
            print(f"{'ID':<6} {'Name':<30} {'Vendor ID':<10} {'Price':<10} {'Stock':<8} {'Tags':<30}")
            print("-"*100)
            for product in products:
                tags = f"{product['tag1'] or ''}, {product['tag2'] or ''}, {product['tag3'] or ''}".strip(", ")
                print(f"{product['product_id']:<6} {product['product_name']:<30} {product['vendor_id']:<10} ${product['listed_price']:<9.2f} {product['stock_quantity']:<8} {tags:<30}")
        
        input("\nPress Enter to search again...")

# ------------------------------ Order Creation ------------------------------
def create_order():
    """Order creation module"""
    clear_screen()
    print(COLOR_YELLOW + "=== Create New Order ===" + COLOR_RESET)
    
    # Step 1: Add customer
    print("\nStep 1: Customer Information")
    contact = input("Enter customer phone number: ")
    shipping_addr = input("Enter customer shipping address: ")
    
    success, customer_id, msg = db.add_customer(contact, shipping_addr)
    if not success:
        print(COLOR_RED + f"Failed to add customer: {msg}" + COLOR_RESET)
        input("\nPress Enter to continue...")
        return
    print(COLOR_GREEN + f"Customer confirmed (ID: {customer_id})" + COLOR_RESET)
    
    # Step 2: Select products
    print("\nStep 2: Select Products (enter 0 to finish selection)")
    product_list = []
    while True:
        try:
            product_id = int(input("Enter product ID to add to order: "))
            if product_id == 0:
                break
            
            # Validate product exists
            conn, cursor = db.get_db_conn()
            cursor.execute("SELECT product_name FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()
            db.close_db_conn(conn, cursor)
            
            if not product:
                print(COLOR_RED + f"Product ID {product_id} does not exist" + COLOR_RESET)
                continue
            
            # Enter quantity
            while True:
                try:
                    buy_quantity = int(input(f"Enter quantity for product '{product['product_name']}': "))
                    if buy_quantity > 0:
                        break
                    else:
                        print(COLOR_RED + "Quantity must be greater than 0" + COLOR_RESET)
                except ValueError:
                    print(COLOR_RED + "Invalid quantity (must be a number)" + COLOR_RESET)
            
            product_list.append({"product_id": product_id, "buy_quantity": buy_quantity})
            print(COLOR_GREEN + f"Added product {product_id} (quantity: {buy_quantity}) to order" + COLOR_RESET)
        
        except ValueError:
            print(COLOR_RED + "Invalid product ID (must be a number)" + COLOR_RESET)
    
    if not product_list:
        print(COLOR_YELLOW + "No products selected, order creation cancelled" + COLOR_RESET)
        input("\nPress Enter to continue...")
        return
    
    # Step 3: Create order
    print("\nStep 3: Confirm Order Creation")
    confirm = input("Are you sure to create this order? (Y/N): ").upper()
    if confirm != "Y":
        print(COLOR_YELLOW + "Order creation cancelled" + COLOR_RESET)
        input("\nPress Enter to continue...")
        return
    
    success, msg = db.create_order(customer_id, product_list)
    if success:
        print(COLOR_GREEN + msg + COLOR_RESET)
    else:
        print(COLOR_RED + f"Failed to create order: {msg}" + COLOR_RESET)
    
    input("\nPress Enter to continue...")

# ------------------------------ Order Management ------------------------------
def order_management():
    """Order management submenu"""
    while True:
        clear_screen()
        print(COLOR_YELLOW + "=== Order Management ===" + COLOR_RESET)
        print("1. View Order Details")
        print("2. Cancel Pending Order")
        print("0. Return to Main Menu")
        
        choice = input("Please enter your choice (0-2): ")
        if choice == "0":
            break
        elif choice == "1":
            # View order details
            try:
                order_id = int(input("Enter order ID to view details: "))
                success, res = db.query_order_details(order_id)
                if not success:
                    print(COLOR_RED + res["error"] + COLOR_RESET)
                else:
                    order_info = res["order_info"]
                    transactions = res["transactions"]
                    
                    print(COLOR_GREEN + f"\n--- Order {order_id} Details ---" + COLOR_RESET)
                    print(f"Customer ID: {order_info['customer_id']}")
                    print(f"Total Price: ${order_info['total_price']:.2f}")
                    print(f"Status: {order_info['status']}")
                    print(f"Created Time: {order_info['create_time']}")
                    
                    print("\n--- Transaction Records ---")
                    print(f"{'Product ID':<10} {'Product Name':<30} {'Quantity':<10} {'Unit Price':<10} {'Subtotal':<10}")
                    print("-"*80)
                    for trans in transactions:
                        subtotal = trans["buy_quantity"] * trans["listed_price"]
                        print(f"{trans['product_id']:<10} {trans['product_name']:<30} {trans['buy_quantity']:<10} ${trans['listed_price']:<9.2f} ${subtotal:<9.2f}")
            except ValueError:
                print(COLOR_RED + "Invalid order ID (must be a number)" + COLOR_RESET)
        elif choice == "2":
            # Cancel order
            try:
                order_id = int(input("Enter order ID to cancel: "))
                success, msg = db.cancel_order(order_id)
                if success:
                    print(COLOR_GREEN + msg + COLOR_RESET)
                else:
                    print(COLOR_RED + f"Failed to cancel order: {msg}" + COLOR_RESET)
            except ValueError:
                print(COLOR_RED + "Invalid order ID (must be a number)" + COLOR_RESET)
        else:
            print(COLOR_RED + "Invalid choice, please try again" + COLOR_RESET)
        
        input("\nPress Enter to continue...")

# ------------------------------ Main Program ------------------------------
def main():
    """Main program entry"""
    print(COLOR_GREEN + "Welcome to Multi-Vendor E-Commerce Platform!" + COLOR_RESET)
    input("Press Enter to start...")
    
    while True:
        print_menu()
        choice = input("Please enter your choice (0-5): ")
        
        if choice == "0":
            print(COLOR_GREEN + "Thank you for using the system! Exiting..." + COLOR_RESET)
            break
        elif choice == "1":
            vendor_management()
        elif choice == "2":
            
            product_catalog()
        elif choice == "3":
            product_discovery()
        elif choice == "4":
            create_order()
        elif choice == "5":
            order_management()
        else:
            print(COLOR_RED + "Invalid choice, please enter a number between 0 and 5" + COLOR_RESET)
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()