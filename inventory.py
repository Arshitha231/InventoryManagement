import os
import sys
import logging
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
from colorama import Fore, Style, init

load_dotenv()
init(autoreset=True)

logging.basicConfig(
    filename='inventory.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'inventory')
}


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            return self
        except Error as e:
            logging.error(f"Database connection failed: {e}")
            print(Fore.RED + f"Error: Could not connect to database. {e}")
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.connection.rollback()
            logging.error(f"Transaction rolled back due to: {exc_val}")
        else:
            self.connection.commit()
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        return False


def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print(Fore.YELLOW + "Value must be non-negative. Try again.")
                continue
            return value
        except ValueError:
            print(Fore.YELLOW + "Invalid input. Please enter a whole number.")


def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print(Fore.YELLOW + "Value must be greater than zero. Try again.")
                continue
            return value
        except ValueError:
            print(Fore.YELLOW + "Invalid input. Please enter a number.")


def get_non_empty_string(prompt, max_length=100):
    while True:
        value = input(prompt).strip()
        if not value:
            print(Fore.YELLOW + "This field cannot be empty.")
        elif len(value) > max_length:
            print(Fore.YELLOW + f"Input too long. Max {max_length} characters.")
        else:
            return value


def log_action(db, prod_id, action, qty_changed, old_qty, new_qty, notes=''):
    try:
        db.cursor.execute("""
            INSERT INTO inventory_log (prod_id, action, quantity_changed, old_quantity, new_quantity, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (prod_id, action, qty_changed, old_qty, new_qty, notes))
    except Error as e:
        logging.error(f"Failed to log action: {e}")


def add_product(db):
    print(Fore.CYAN + "\n--- Add New Product ---")
    product_name = get_non_empty_string("Product Name: ")
    category = get_non_empty_string("Category: ")
    qty = get_positive_int("Quantity in Stock: ")
    price = get_positive_float("Price: ")
    supplier_id_input = input("Supplier ID (leave blank if none): ").strip()
    supplier_id = int(supplier_id_input) if supplier_id_input.isdigit() else None
    low_stock_threshold = get_positive_int("Low Stock Threshold (default 10): ") or 10

    query = """INSERT INTO products (product_name, category, qty, price, supplier_id, low_stock_threshold)
               VALUES (%s, %s, %s, %s, %s, %s)"""
    try:
        db.cursor.execute(query, (product_name, category, qty, price, supplier_id, low_stock_threshold))
        prod_id = db.cursor.lastrowid
        log_action(db, prod_id, 'ADD', qty, 0, qty, 'Product added to inventory')
        print(Fore.GREEN + f"Product '{product_name}' added successfully with ID {prod_id}.")
        logging.info(f"Product added: {product_name} (ID: {prod_id})")
    except Error as e:
        print(Fore.RED + f"Failed to add product: {e}")
        logging.error(f"Failed to add product: {e}")


def show_products(db):
    print(Fore.CYAN + "\n--- All Products ---")
    try:
        db.cursor.execute("""
            SELECT prod_id, product_name, category, qty, price, supplier_id, low_stock_threshold, updated_at
            FROM products ORDER BY prod_id
        """)
        rows = db.cursor.fetchall()
        if not rows:
            print(Fore.YELLOW + "No products found in inventory.")
            return
        headers = ["ID", "Name", "Category", "Qty", "Price", "Supplier ID", "Low Stock Alert", "Last Updated"]
        formatted = []
        for row in rows:
            qty = row[3]
            threshold = row[6]
            qty_display = f"{Fore.RED}{qty}{Style.RESET_ALL}" if qty <= threshold else str(qty)
            formatted.append((row[0], row[1], row[2], qty_display, f"${row[4]:.2f}", row[5] or "N/A", threshold, row[7]))
        print(tabulate(formatted, headers=headers, tablefmt="grid"))
        print(Fore.CYAN + f"\nTotal products: {len(rows)}")
    except Error as e:
        print(Fore.RED + f"Error fetching products: {e}")
        logging.error(f"Error fetching products: {e}")


def update_stock(db):
    print(Fore.CYAN + "\n--- Update Stock ---")
    prod_id = get_positive_int("Enter Product ID to update: ")
    db.cursor.execute("SELECT product_name, qty FROM products WHERE prod_id = %s", (prod_id,))
    result = db.cursor.fetchone()
    if not result:
        print(Fore.YELLOW + f"No product found with ID {prod_id}.")
        return
    product_name, old_qty = result
    print(f"Current stock for '{product_name}': {old_qty}")
    new_qty = get_positive_int("Enter new quantity: ")
    try:
        db.cursor.execute("UPDATE products SET qty = %s WHERE prod_id = %s", (new_qty, prod_id))
        log_action(db, prod_id, 'UPDATE', new_qty - old_qty, old_qty, new_qty, 'Stock updated')
        print(Fore.GREEN + f"Stock updated: '{product_name}' {old_qty} → {new_qty}")
        logging.info(f"Stock updated for product ID {prod_id}: {old_qty} -> {new_qty}")
    except Error as e:
        print(Fore.RED + f"Failed to update stock: {e}")
        logging.error(f"Failed to update stock: {e}")


def delete_product(db):
    print(Fore.CYAN + "\n--- Delete Product ---")
    prod_id = get_positive_int("Enter Product ID to delete: ")
    db.cursor.execute("SELECT product_name FROM products WHERE prod_id = %s", (prod_id,))
    result = db.cursor.fetchone()
    if not result:
        print(Fore.YELLOW + f"No product found with ID {prod_id}.")
        return
    product_name = result[0]
    confirm = input(Fore.YELLOW + f"Are you sure you want to delete '{product_name}'? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Deletion cancelled.")
        return
    try:
        db.cursor.execute("DELETE FROM products WHERE prod_id = %s", (prod_id,))
        print(Fore.GREEN + f"Product '{product_name}' deleted successfully.")
        logging.info(f"Product deleted: {product_name} (ID: {prod_id})")
    except Error as e:
        print(Fore.RED + f"Failed to delete product: {e}")
        logging.error(f"Failed to delete product: {e}")


def search_product(db):
    print(Fore.CYAN + "\n--- Search Products ---")
    print("Search by:\n1. Product Name\n2. Category\n3. Product ID")
    choice = input("Choose (1-3): ").strip()
    if choice == '1':
        term = get_non_empty_string("Enter product name (partial ok): ")
        query = "SELECT prod_id, product_name, category, qty, price FROM products WHERE product_name LIKE %s"
        db.cursor.execute(query, (f"%{term}%",))
    elif choice == '2':
        term = get_non_empty_string("Enter category: ")
        query = "SELECT prod_id, product_name, category, qty, price FROM products WHERE category LIKE %s"
        db.cursor.execute(query, (f"%{term}%",))
    elif choice == '3':
        prod_id = get_positive_int("Enter Product ID: ")
        query = "SELECT prod_id, product_name, category, qty, price FROM products WHERE prod_id = %s"
        db.cursor.execute(query, (prod_id,))
    else:
        print(Fore.YELLOW + "Invalid choice.")
        return
    rows = db.cursor.fetchall()
    if not rows:
        print(Fore.YELLOW + "No products found matching your search.")
        return
    headers = ["ID", "Name", "Category", "Qty", "Price"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(Fore.CYAN + f"Found {len(rows)} result(s).")


def low_stock_alert(db):
    print(Fore.CYAN + "\n--- Low Stock Alert ---")
    try:
        db.cursor.execute("""
            SELECT prod_id, product_name, qty, low_stock_threshold
            FROM products
            WHERE qty <= low_stock_threshold
            ORDER BY qty ASC
        """)
        rows = db.cursor.fetchall()
        if not rows:
            print(Fore.GREEN + "All products are adequately stocked!")
            return
        headers = ["ID", "Product Name", "Current Qty", "Min Threshold"]
        print(Fore.RED + f"\nWARNING: {len(rows)} product(s) are low on stock!\n")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        logging.warning(f"Low stock alert: {len(rows)} products below threshold")
    except Error as e:
        print(Fore.RED + f"Error checking stock levels: {e}")
        logging.error(f"Error in low_stock_alert: {e}")


def inventory_report(db):
    print(Fore.CYAN + "\n--- Inventory Report ---")
    try:
        db.cursor.execute("SELECT COUNT(*), SUM(qty), SUM(qty * price), AVG(price) FROM products")
        stats = db.cursor.fetchone()
        total_products, total_qty, total_value, avg_price = stats
        print(f"\n{'='*40}")
        print(f"  Total Products:       {total_products}")
        print(f"  Total Units in Stock: {total_qty or 0}")
        print(f"  Total Inventory Value: ${total_value or 0:.2f}")
        print(f"  Average Product Price: ${avg_price or 0:.2f}")
        print(f"{'='*40}")

        db.cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(qty) as total_qty, SUM(qty*price) as value
            FROM products GROUP BY category ORDER BY value DESC
        """)
        categories = db.cursor.fetchall()
        if categories:
            print(Fore.CYAN + "\nBy Category:")
            headers = ["Category", "Products", "Total Qty", "Value"]
            print(tabulate(categories, headers=headers, tablefmt="grid"))
        logging.info("Inventory report generated")
    except Error as e:
        print(Fore.RED + f"Error generating report: {e}")
        logging.error(f"Error in inventory_report: {e}")


def view_logs(db):
    print(Fore.CYAN + "\n--- Inventory Action Log ---")
    try:
        db.cursor.execute("""
            SELECT l.log_id, p.product_name, l.action, l.quantity_changed,
                   l.old_quantity, l.new_quantity, l.notes, l.logged_at
            FROM inventory_log l
            LEFT JOIN products p ON l.prod_id = p.prod_id
            ORDER BY l.logged_at DESC LIMIT 50
        """)
        rows = db.cursor.fetchall()
        if not rows:
            print(Fore.YELLOW + "No log entries found.")
            return
        headers = ["Log ID", "Product", "Action", "Qty Changed", "Old Qty", "New Qty", "Notes", "Timestamp"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Error as e:
        print(Fore.RED + f"Error fetching logs: {e}")
        logging.error(f"Error in view_logs: {e}")


def add_supplier(db):
    print(Fore.CYAN + "\n--- Add New Supplier ---")
    name = get_non_empty_string("Supplier Name: ")
    email = input("Contact Email (optional): ").strip() or None
    phone = input("Contact Phone (optional): ").strip() or None
    address = input("Address (optional): ").strip() or None
    try:
        db.cursor.execute(
            "INSERT INTO suppliers (supplier_name, contact_email, contact_phone, address) VALUES (%s, %s, %s, %s)",
            (name, email, phone, address)
        )
        supplier_id = db.cursor.lastrowid
        print(Fore.GREEN + f"Supplier '{name}' added with ID {supplier_id}.")
        logging.info(f"Supplier added: {name} (ID: {supplier_id})")
    except Error as e:
        print(Fore.RED + f"Failed to add supplier: {e}")


def show_suppliers(db):
    print(Fore.CYAN + "\n--- All Suppliers ---")
    try:
        db.cursor.execute("SELECT supplier_id, supplier_name, contact_email, contact_phone, address FROM suppliers")
        rows = db.cursor.fetchall()
        if not rows:
            print(Fore.YELLOW + "No suppliers found.")
            return
        headers = ["ID", "Name", "Email", "Phone", "Address"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    except Error as e:
        print(Fore.RED + f"Error fetching suppliers: {e}")


import csv
from datetime import datetime


def export_to_csv(db):
    print(Fore.CYAN + "\n--- Export Inventory to CSV ---")
    try:
        db.cursor.execute("SELECT prod_id, product_name, category, qty, price, supplier_id, low_stock_threshold FROM products")
        rows = db.cursor.fetchall()
        if not rows:
            print(Fore.YELLOW + "No products to export.")
            return
        filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Product Name", "Category", "Quantity", "Price", "Supplier ID", "Low Stock Threshold"])
            writer.writerows(rows)
        print(Fore.GREEN + f"Exported {len(rows)} products to '{filename}'.")
        logging.info(f"Inventory exported to {filename}")
    except Error as e:
        print(Fore.RED + f"Export failed: {e}")
        logging.error(f"Export failed: {e}")


def update_price(db):
    print(Fore.CYAN + "\n--- Update Product Price ---")
    prod_id = get_positive_int("Enter Product ID: ")
    db.cursor.execute("SELECT product_name, price FROM products WHERE prod_id = %s", (prod_id,))
    result = db.cursor.fetchone()
    if not result:
        print(Fore.YELLOW + f"No product found with ID {prod_id}.")
        return
    product_name, old_price = result
    print(f"Current price for '{product_name}': ${old_price:.2f}")
    new_price = get_positive_float("Enter new price: $")
    try:
        db.cursor.execute("UPDATE products SET price = %s WHERE prod_id = %s", (new_price, prod_id))
        print(Fore.GREEN + f"Price updated: '{product_name}' ${old_price:.2f} → ${new_price:.2f}")
        logging.info(f"Price updated for product ID {prod_id}: {old_price} -> {new_price}")
    except Error as e:
        print(Fore.RED + f"Failed to update price: {e}")
        logging.error(f"Failed to update price: {e}")


def restock_product(db):
    print(Fore.CYAN + "\n--- Restock Product ---")
    prod_id = get_positive_int("Enter Product ID to restock: ")
    db.cursor.execute("SELECT product_name, qty FROM products WHERE prod_id = %s", (prod_id,))
    result = db.cursor.fetchone()
    if not result:
        print(Fore.YELLOW + f"No product found with ID {prod_id}.")
        return
    product_name, current_qty = result
    print(f"Current stock for '{product_name}': {current_qty}")
    add_qty = get_positive_int("Quantity to add: ")
    new_qty = current_qty + add_qty
    try:
        db.cursor.execute("UPDATE products SET qty = %s WHERE prod_id = %s", (new_qty, prod_id))
        log_action(db, prod_id, 'RESTOCK', add_qty, current_qty, new_qty, f'Restocked +{add_qty} units')
        print(Fore.GREEN + f"Restocked '{product_name}': {current_qty} → {new_qty} (+{add_qty})")
        logging.info(f"Product {prod_id} restocked: {current_qty} -> {new_qty}")
    except Error as e:
        print(Fore.RED + f"Failed to restock: {e}")
        logging.error(f"Failed to restock: {e}")


def sell_product(db):
    print(Fore.CYAN + "\n--- Record Sale ---")
    prod_id = get_positive_int("Enter Product ID: ")
    db.cursor.execute("SELECT product_name, qty FROM products WHERE prod_id = %s", (prod_id,))
    result = db.cursor.fetchone()
    if not result:
        print(Fore.YELLOW + f"No product found with ID {prod_id}.")
        return
    product_name, current_qty = result
    print(f"Available stock for '{product_name}': {current_qty}")
    if current_qty == 0:
        print(Fore.RED + "Product is out of stock!")
        return
    sell_qty = get_positive_int("Quantity to sell: ")
    if sell_qty > current_qty:
        print(Fore.RED + f"Cannot sell {sell_qty} units. Only {current_qty} available.")
        return
    new_qty = current_qty - sell_qty
    try:
        db.cursor.execute("UPDATE products SET qty = %s WHERE prod_id = %s", (new_qty, prod_id))
        log_action(db, prod_id, 'SELL', -sell_qty, current_qty, new_qty, f'Sold {sell_qty} units')
        print(Fore.GREEN + f"Sale recorded: '{product_name}' {current_qty} → {new_qty} (-{sell_qty})")
        if new_qty <= 10:
            print(Fore.YELLOW + f"WARNING: Low stock alert for '{product_name}'! Only {new_qty} units remaining.")
        logging.info(f"Product {prod_id} sold: {sell_qty} units, remaining: {new_qty}")
    except Error as e:
        print(Fore.RED + f"Failed to record sale: {e}")
        logging.error(f"Failed to record sale: {e}")
