# Inventory Management System

A feature-rich CLI-based Inventory Management System built with Python and MySQL.

## Features

- **Product Management** — Add, view, update, delete products
- **Stock Control** — Restock products, record sales, update quantities
- **Price Management** — Update individual product prices
- **Supplier Management** — Track suppliers linked to products
- **Smart Alerts** — Low stock warnings based on configurable thresholds
- **Reporting** — Full inventory reports with category breakdowns
- **Audit Log** — Track every inventory change with timestamps
- **CSV Export** — Export full inventory to CSV for reporting
- **Search** — Search by name, category, or product ID

## Requirements

- Python 3.8+
- MySQL 8.0+

## Setup

1. Clone the repository:
   git clone https://github.com/Arshitha231/InventoryManagement.git
   cd InventoryManagement

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment variables:
   cp .env.example .env
   # Edit .env with your MySQL credentials

5. Set up the database:
   mysql -u root -p < database/schema.sql

6. Run the application:
   python inventory.py

## Environment Variables

| Variable    | Default   | Description         |
|-------------|-----------|---------------------|
| DB_HOST     | localhost | MySQL host          |
| DB_USER     | root      | MySQL username      |
| DB_PASSWORD |           | MySQL password      |
| DB_NAME     | inventory | Database name       |

## Running Tests

python -m pytest tests/ -v

## Menu Options

| Option | Description                    |
|--------|-------------------------------|
| 1      | Add new product                |
| 2      | View all products              |
| 3      | Update stock quantity          |
| 4      | Update product price           |
| 5      | Update product name/category   |
| 6      | Delete product                 |
| 7      | Search products                |
| 8      | Restock a product              |
| 9      | Record a sale                  |
| 10     | View low stock alerts          |
| 11     | View inventory report          |
| 12     | Supplier management            |
| 13     | View action log                |
| 14     | Export to CSV                  |
| 15     | Set low stock threshold        |

## License

MIT License
