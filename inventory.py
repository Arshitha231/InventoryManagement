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
