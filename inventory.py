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
