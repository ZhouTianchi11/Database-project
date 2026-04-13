🌟 E-Commerce Management System (Dual Role: User + Super Admin)
A complete e-commerce system with merchant, product, cart, and order management.
📖 Project Overview
This is a full-stack e-commerce management system supporting two roles: User and Super Admin. It implements merchant management, product management, shopping cart, order management, and personal account functions in a clean, easy-to-use interface.
🎯 Features
🔐 Login Page
Unified login for User and Super Admin
Auto redirect to corresponding dashboard based on role
🔑 Super Admin
Merchant Management
Merchant list on the left
Add / delete merchants on the right
Product Catalog
Switch merchants via dropdown
View products under each merchant
Add products: name, price, stock, 3 tags
Delete products
Order Management
View all orders placed by users
🧑‍💻 User Side
Product Browse & Search
Display all products
Search by product name or tag
Add to cart
Shopping Cart
Update quantity
Remove items
Checkout to place order
My Orders
View all personal orders
Remove single item from order
Delete entire order
Account Info
View personal account details
🛠️ Tech Stack
Frontend: Vue3, HTML, CSS, JavaScript
Backend: Node.js / Java / Python (fill in yours)
Database: MySQL
Tools: Git, IDE, Node.js
🚀 Quick Start
bash
运行
# Clone the project
git clone https://github.com/your-username/your-repo.git

# Enter directory
cd your-repo-name

# Install dependencies
npm install

# Run locally
npm run dev

# Build for production
npm run build
📂 Project Structure
plaintext
├── src/
│   ├── api/          # API requests
│   ├── components/   # Common components
│   ├── views/
│   │   ├── admin/    # Super Admin pages
│   │   ├── user/     # User pages
│   │   └── Login.vue # Login page
│   ├── router/       # Routes
│   └── main.js       # Entry file
├── public/
└── package.json
📌 Highlights
Dual-role permission control
Product search by name & tags
Complete cart & order flow
Clean UI, suitable for class project / graduation project
📄 License
MIT License
✉ Contact
GitHub: your-github-url
Email: your-email@example.com
