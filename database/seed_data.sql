USE inventory;

INSERT INTO suppliers (supplier_name, contact_email, contact_phone, address) VALUES
('Tech Supplies Co', 'orders@techsupplies.com', '555-0100', '123 Tech Ave, Silicon Valley, CA'),
('Office World', 'supply@officeworld.com', '555-0101', '456 Business Rd, New York, NY'),
('Electronics Hub', 'sales@electronichub.com', '555-0102', '789 Circuit St, Austin, TX');

INSERT INTO products (product_name, category, qty, price, supplier_id, low_stock_threshold) VALUES
('Laptop', 'Electronics', 50, 999.99, 1, 5),
('Wireless Mouse', 'Electronics', 150, 29.99, 1, 20),
('Office Chair', 'Furniture', 30, 249.99, 2, 5),
('Notebook (A4)', 'Stationery', 500, 3.99, 2, 50),
('USB-C Cable', 'Electronics', 200, 12.99, 3, 30),
('Standing Desk', 'Furniture', 15, 599.99, 2, 3),
('Webcam HD', 'Electronics', 75, 89.99, 3, 10),
('Whiteboard', 'Office Supplies', 20, 149.99, 2, 5),
('Headphones', 'Electronics', 60, 149.99, 1, 10),
('Printer Ink', 'Office Supplies', 8, 39.99, 2, 15);
