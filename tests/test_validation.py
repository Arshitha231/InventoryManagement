import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from unittest.mock import patch, MagicMock
import io

class TestInputValidation(unittest.TestCase):

    @patch('builtins.input', side_effect=['abc', '-1', '5'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_positive_int_rejects_invalid(self, mock_stdout, mock_input):
        from inventory import get_positive_int
        result = get_positive_int("Enter: ")
        self.assertEqual(result, 5)

    @patch('builtins.input', side_effect=['abc', '-1.5', '9.99'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_positive_float_rejects_invalid(self, mock_stdout, mock_input):
        from inventory import get_positive_float
        result = get_positive_float("Enter: ")
        self.assertEqual(result, 9.99)

    @patch('builtins.input', side_effect=['', '   ', 'Valid Name'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_non_empty_string_rejects_blank(self, mock_stdout, mock_input):
        from inventory import get_non_empty_string
        result = get_non_empty_string("Enter: ")
        self.assertEqual(result, 'Valid Name')

    @patch('builtins.input', return_value='a' * 200)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_non_empty_string_rejects_too_long(self, mock_stdout, mock_input):
        from inventory import get_non_empty_string
        # Should keep asking, so we patch to eventually give valid input
        with patch('builtins.input', side_effect=['a' * 200, 'Valid']):
            result = get_non_empty_string("Enter: ")
            self.assertEqual(result, 'Valid')

if __name__ == '__main__':
    unittest.main()
