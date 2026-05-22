"""
Unit Tests for Book Management Application
===========================================
Tests for all functional requirements (UT01 to UT16)
plus validation helper tests.
"""

import unittest
from unittest.mock import patch, mock_open, call
import json
import io

import main 


# ============================================================
# UT01, UT02, UT03 / EH04, EH05: load_books() Tests
# ============================================================

class TestLoadBooks(unittest.TestCase):
    """UT01 - UT03 /EH04 - EH05: Tests for loading books from JSON file"""
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=100)
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([
        {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "year": 1949, "price": 9.99}
    ]))
    def test_UT01_load_valid_json(self, mock_file, mock_getsize, mock_exists):
        """UT01: Load from existing books.json with valid data returns list of dicts"""
        result = main.load_books()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], "1984")
        self.assertEqual(result[0]['author'], "George Orwell")

    @patch('os.path.exists', return_value=False)
    def test_UT02_EH05_load_file_not_exist(self, mock_exists):
        """UT02 / EH05: Load when books.json does not exist returns empty list without crashing"""
        result = main.load_books()
        
        self.assertEqual(result, [])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=0)
    def test_UT03_load_empty_file(self, mock_getsize, mock_exists):
        """UT03: Load from empty books.json returns empty list"""
        result = main.load_books()
        
        self.assertEqual(result, [])


    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=100)
    @patch('builtins.open', new_callable=mock_open, read_data="This is not valid JSON{{{")
    def test_EH04_corrupted_json_file(self, mock_file, mock_getsize, mock_exists):
        """EH04: Corrupted JSON file - graceful error, empty collection returned"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.load_books()
        
        output = fake_out.getvalue()
        self.assertEqual(result, [])
        self.assertIn("Couldn't load", output)
    
# ============================================================
# UT04: save_books() Test
# ============================================================

class TestSaveBooks(unittest.TestCase):
    """Tests for saving books to JSON file"""

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_UT04_save_writes_correct_json(self, mock_json_dump, mock_file):
        """UT04: Save list to books.json - file created with correct JSON format"""
        books = [
            {"title": "Test", "author": "A", "genre": "G", "year": 2000, "price": 5.0}
        ]
        
        main.save_books(books)

        # Check open called with correct filename and mode
        mock_file.assert_called_once_with(main.BOOKS_JSON_FILE, 'w')
        
        # Check json.dump called with correct data and file handle
        mock_json_dump.assert_called_once_with(books, mock_file(), indent=4)


# ============================================================
# UT05, UT06, UT07: add_book() Tests
# ============================================================

class TestAddBook(unittest.TestCase):
    """Tests for adding books"""

    def setUp(self):
        """Reset book list before each test"""
        self.book_list = []

    @patch('main.save_books')
    @patch('main.get_valid_input')
    def test_UT05_add_valid_book(self, mock_input, mock_save):
        """UT05: Add valid book data - book appended to list, file saved"""
        mock_input.side_effect = ["The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 12.99]
        
        main.add_book(self.book_list)
        
        self.assertEqual(len(self.book_list), 1)
        book = self.book_list[0]
        self.assertEqual(book['title'], "The Hobbit")
        self.assertEqual(book['author'], "J.R.R. Tolkien")
        self.assertEqual(book['genre'], "Fantasy")
        self.assertEqual(book['year'], 1937)
        self.assertEqual(book['price'], 12.99)
        mock_save.assert_called_once_with(self.book_list)

    @patch('main.save_books')
    @patch('main.get_valid_input')
    def test_UT06_correct_prompts_used(self, mock_input, mock_save):
        """UT06: Add book uses correct prompts and types for each field"""
        mock_input.side_effect = ["Title", "Author", "Genre", 2000, 9.99]
        
        main.add_book(self.book_list)
        
        # Verify each call to get_valid_input has correct arguments
        calls = mock_input.call_args_list
        self.assertEqual(calls[0], call("\nEnter book title: "))
        self.assertEqual(calls[1], call("\nEnter book author: "))
        self.assertEqual(calls[2], call("\nEnter book genre: "))
        self.assertEqual(calls[3], call("\nEnter book published year: ", int, 
                                         "\nThe year must be a whole number! (e.g., 1999)"))
        self.assertEqual(calls[4], call("\nEnter book price: ", float, 
                                         "\nThe price must be a number! (e.g., 19.99)"))


# ============================================================
# UT07 / EH01 - EH03: get_valid_input() Validation Tests
# (Tests the validation that add_book relies on)
# ============================================================

class TestGetValidInput(unittest.TestCase):
    """UT07 / EH01 - EH03: Tests for input validation helper"""

    
    @patch('builtins.input')
    def test_UT07a_valid_string_accepted(self, mock_input):
        """UT07: Valid string returned without error"""
        mock_input.return_value = "The Hobbit"
        
        result = main.get_valid_input("Enter title: ")
        self.assertEqual(result, "The Hobbit")

    @patch('builtins.input')
    def test_UT07b_valid_int_accepted(self, mock_input):
        """UT07: Valid integer converted and returned"""
        mock_input.return_value = "1999"
        
        result = main.get_valid_input("Enter year: ", int)
        self.assertEqual(result, 1999)
        self.assertIsInstance(result, int)

    @patch('builtins.input')
    def test_UT07c_valid_float_accepted(self, mock_input):
        """UT07: Valid float converted and returned"""
        mock_input.return_value = "19.99"
        
        result = main.get_valid_input("Enter price: ", float)
        self.assertEqual(result, 19.99)
        self.assertIsInstance(result, float)


   
    @patch('builtins.input')
    def test_UT07d_whitespace_rejected(self, mock_input):
        """UT07: Whitespace-only input treated as empty"""
        mock_input.side_effect = ["   ", "Valid Title"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter title: ")
        
        self.assertEqual(result, "Valid Title")
        self.assertIn("This field cannot be empty!", fake_out.getvalue())

    @patch('builtins.input')
    def test_EH01_non_numeric_year_rejected(self, mock_input):
        """EH01: Non-numeric year input rejected with error"""
        
        mock_input.side_effect = ["abc", "1999"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter year: ", int, "Must be a number!")
        
        output = fake_out.getvalue()
        self.assertEqual(result, 1999)
        self.assertIn("Must be a number!", output)

    @patch('builtins.input')
    def test_EH02_non_numeric_price_rejected(self, mock_input):
        """EH02: Non-numeric price input rejected with error"""
        mock_input.side_effect = ["xyz", "19.99"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter price: ", float, "Must be a number!")
        
        output = fake_out.getvalue()
        self.assertEqual(result, 19.99)
        self.assertIn("Must be a number!", output)

    @patch('builtins.input')
    def test_EH03_empty_string_rejected(self, mock_input):
        """EH03: Empty input rejected with error message"""
        mock_input.side_effect = ["", "Valid Title"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter title: ")
        
        output = fake_out.getvalue()
        self.assertEqual(result, "Valid Title")
        self.assertIn("This field cannot be empty!", output)



