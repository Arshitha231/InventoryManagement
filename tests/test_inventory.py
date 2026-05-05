import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestInventoryFunctions(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.cursor = MagicMock()
        self.mock_db.cursor.lastrowid = 1

    def test_add_product_success(self):
        from inventory import add_product
        self.mock_db.cursor.fetchone.return_value = None
        inputs = ['Widget', 'Electronics', '100', '29.99', '1', '10']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                add_product(self.mock_db)
        self.mock_db.cursor.execute.assert_called()

    def test_show_products_empty(self):
        from inventory import show_products
        self.mock_db.cursor.fetchall.return_value = []
        with patch('builtins.print') as mock_print:
            show_products(self.mock_db)
        output = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('No products found', output)

    def test_delete_product_not_found(self):
        from inventory import delete_product
        self.mock_db.cursor.fetchone.return_value = None
        with patch('builtins.input', return_value='999'):
            with patch('builtins.print') as mock_print:
                delete_product(self.mock_db)
        output = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('No product found', output)

    def test_sell_product_out_of_stock(self):
        from inventory import sell_product
        self.mock_db.cursor.fetchone.return_value = ('Widget', 0)
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                sell_product(self.mock_db)
        output = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('out of stock', output)

    def test_sell_product_exceeds_stock(self):
        from inventory import sell_product
        self.mock_db.cursor.fetchone.return_value = ('Widget', 5)
        with patch('builtins.input', side_effect=['1', '10']):
            with patch('builtins.print') as mock_print:
                sell_product(self.mock_db)
        output = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('Cannot sell', output)

    def test_low_stock_alert_all_good(self):
        from inventory import low_stock_alert
        self.mock_db.cursor.fetchall.return_value = []
        with patch('builtins.print') as mock_print:
            low_stock_alert(self.mock_db)
        output = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('adequately stocked', output)

if __name__ == '__main__':
    unittest.main()
