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
