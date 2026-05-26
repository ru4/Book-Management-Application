"""
Unit Tests for Book Management Application
===========================================
Tests for all functional requirements (UT-01 to UT-16)
plus validation helper tests.
"""

import unittest
from unittest.mock import patch, mock_open, call
import json
import io

import main 


# ============================================================
# UT-01, UT-02, UT-03 / EH-04, EH-05: load_books() Tests
# ============================================================

class TestLoadBooks(unittest.TestCase):
    """UT-01 - UT-03 /EH-04 - EH-05: Tests for loading books from JSON file"""
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=100)
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([
        {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "year": 1949, "price": 9.99}
    ]))
    def test_load_valid_json(self, mock_file, mock_getsize, mock_exists):
        """UT-01: Load from existing books.json with valid data returns list of dicts"""
        result = main.load_books()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], "1984")
        self.assertEqual(result[0]['author'], "George Orwell")

    @patch('os.path.exists', return_value=False)
    def test_load_file_not_exist(self, mock_exists):
        """UT-02 / EH-05: Load when books.json does not exist returns empty list without crashing"""
        result = main.load_books()
        
        self.assertEqual(result, [])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=0)
    def test_load_empty_file(self, mock_getsize, mock_exists):
        """UT-03: Load from empty books.json returns empty list"""
        result = main.load_books()
        
        self.assertEqual(result, [])


    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=100)
    @patch('builtins.open', new_callable=mock_open, read_data="This is not valid JSON{{{")
    def test_corrupted_json_file(self, mock_file, mock_getsize, mock_exists):
        """EH-04: Corrupted JSON file - graceful error, empty collection returned"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.load_books()
        
        output = fake_out.getvalue()
        self.assertEqual(result, [])
        self.assertIn("Couldn't load", output)
    
# ============================================================
# UT-04: save_books() Test
# ============================================================

class TestSaveBooks(unittest.TestCase):
    """Tests for saving books to JSON file"""

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_writes_correct_json(self, mock_json_dump, mock_file):
        """UT-04: Save list to books.json - file created with correct JSON format"""
        books = [
            {"title": "Test", "author": "A", "genre": "G", "year": 2000, "price": 5.0}
        ]
        
        main.save_books(books)

        # Check open called with correct filename and mode
        mock_file.assert_called_once_with(main.BOOKS_JSON_FILE, 'w')
        
        # Check json.dump called with correct data and file handle
        mock_json_dump.assert_called_once_with(books, mock_file(), indent=4)


# ============================================================
# UT-05: add_book() Tests
# ============================================================

class TestAddBook(unittest.TestCase):
    """Tests for adding books"""

    def setUp(self):
        """Reset book list before each test"""
        self.book_list = []

    @patch('main.save_books')
    @patch('main.get_valid_input')
    def test_add_valid_book(self, mock_input, mock_save):
        """UT-05: Add valid book data - book appended to list, file saved"""
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



# ============================================================
# UT-06, UT-07 / EH-01 - EH-03: get_valid_input() Validation Tests
# (Tests the validation that add_book relies on)
# ============================================================

class TestGetValidInput(unittest.TestCase):
    """UT-06, UT-07 / EH-01 - EH-03: Tests for input validation helper
        which add_book relies on for user input
    """

    @patch('builtins.input')
    def test_empty_string_rejected(self, mock_input):
        """UT-06 / EH-03: Empty input rejected with error message"""
        mock_input.side_effect = ["", "Valid Title"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter title: ")
        
        output = fake_out.getvalue()
        self.assertEqual(result, "Valid Title")
        self.assertIn("This field cannot be empty!", output)




    @patch('builtins.input')
    def test_valid_string_accepted(self, mock_input):
        """UT-07: Valid string returned without error"""
        mock_input.return_value = "The Hobbit"
        
        result = main.get_valid_input("Enter title: ")
        self.assertEqual(result, "The Hobbit")

    @patch('builtins.input')
    def test_valid_int_accepted(self, mock_input):
        """UT-07: Valid integer converted and returned"""
        mock_input.return_value = "1999"
        
        result = main.get_valid_input("Enter year: ", int)
        self.assertEqual(result, 1999)
        self.assertIsInstance(result, int)

    @patch('builtins.input')
    def test_valid_float_accepted(self, mock_input):
        """UT-07: Valid float converted and returned"""
        mock_input.return_value = "19.99"
        
        result = main.get_valid_input("Enter price: ", float)
        self.assertEqual(result, 19.99)
        self.assertIsInstance(result, float)


   
    @patch('builtins.input')
    def test_whitespace_rejected(self, mock_input):
        """UT-07: Whitespace-only input treated as empty"""
        mock_input.side_effect = ["   ", "Valid Title"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter title: ")
        
        self.assertEqual(result, "Valid Title")
        self.assertIn("This field cannot be empty!", fake_out.getvalue())

    @patch('builtins.input')
    def test_non_numeric_year_rejected(self, mock_input):
        """EH-01: Non-numeric year input rejected with error"""
        
        mock_input.side_effect = ["abc", "1999"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter year: ", int, "Must be a number!")
        
        output = fake_out.getvalue()
        self.assertEqual(result, 1999)
        self.assertIn("Must be a number!", output)

    @patch('builtins.input')
    def test_non_numeric_price_rejected(self, mock_input):
        """EH-02: Non-numeric price input rejected with error"""
        mock_input.side_effect = ["xyz", "19.99"]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = main.get_valid_input("Enter price: ", float, "Must be a number!")
        
        output = fake_out.getvalue()
        self.assertEqual(result, 19.99)
        self.assertIn("Must be a number!", output)



# ============================================================
# UT-08, UT-09: search_book() Tests
# ============================================================

class TestSearchBook(unittest.TestCase):
    """Tests for searching books by title"""

    def setUp(self):
        self.books = [
            {"title": "1984", "author": "George Orwell", "genre": "Dystopian", 
             "year": 1949, "price": 9.99},
            {"title": "Animal Farm", "author": "George Orwell", "genre": "Satire", 
             "year": 1945, "price": 7.99}
        ]

    @patch('main.get_valid_input', return_value="1984")
    def test_search_book_found(self, mock_input):
        """UT-08: Search for existing book - details displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.search_book(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("1984", output)
        self.assertIn("George Orwell", output)
        self.assertIn("Dystopian", output)
        self.assertIn("1949", output)
        self.assertIn("9.99", output)

    @patch('main.get_valid_input', return_value="1984")
    def test_case_insensitive_search(self, mock_input):
        """UT-08: Search should be case-insensitive"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.search_book(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("1984", output)

    @patch('main.get_valid_input', return_value="Nonexistent Book")
    def test_search_book_not_found(self, mock_input):
        """UT-09: Search for non-existent book - 'not found' message displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.search_book(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("Book not found", output)

    def test_search_empty_collection(self):
        """UT-09: Search in empty collection shows appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.search_book([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books yet!", output)


# ============================================================
# UT-10: sort_books() Test
# ============================================================

class TestSortBooks(unittest.TestCase):
    """Tests for sorting books alphabetically"""

    def setUp(self):
        self.books = [
            {"title": "Zebra", "author": "X", "genre": "G", "year": 2000, "price": 1.0},
            {"title": "Apple", "author": "Y", "genre": "G", "year": 2000, "price": 1.0},
            {"title": "Mango", "author": "Z", "genre": "G", "year": 2000, "price": 1.0}
        ]

    @patch('main.save_books')
    def test_sort_alphabetically(self, mock_save):
        """UT-10: Sort multiple books - alphabetical order by title"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.sort_books(self.books)
        
        output = fake_out.getvalue()
        
        # Check list is sorted
        self.assertEqual(self.books[0]['title'], "Apple")
        self.assertEqual(self.books[1]['title'], "Mango")
        self.assertEqual(self.books[2]['title'], "Zebra")
        
        # Check display output
        self.assertIn("Apple", output)
        self.assertIn("Mango", output)
        self.assertIn("Zebra", output)
        
        # Check save was called
        mock_save.assert_called_once_with(self.books)

    def test_sort_empty_collection(self):
        """UT-10: Sort empty collection shows appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.sort_books([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books yet!", output)


# ============================================================
# UT-11: find_oldest_book() Test
# ============================================================

class TestFindOldestBook(unittest.TestCase):
    """Tests for finding the oldest book"""

    def setUp(self):
        self.books = [
            {"title": "Book A", "author": "A", "genre": "G", "year": 2000, "price": 5.0},
            {"title": "Book B", "author": "B", "genre": "G", "year": 1950, "price": 5.0},
            {"title": "Book C", "author": "C", "genre": "G", "year": 2020, "price": 5.0}
        ]

    def test_find_oldest_book(self):
        """UT-11: Find oldest book - earliest year displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_oldest_book(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("Book B", output)
        self.assertIn("1950", output)

    def test_find_oldest_book_single(self):
        """UT-11: Single book collection - that book is the oldest"""
        single_book = [{"title": "Only", "author": "X", "genre": "G", "year": 2000, "price": 5.0}]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_oldest_book(single_book)
        
        output = fake_out.getvalue()
        self.assertIn("Only", output)

    def test_find_oldest_book_empty_collection(self):
        """UT-11: Empty collection shows appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_oldest_book([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books yet!", output)


# ============================================================
# UT-12: find_newest_book() Test
# ============================================================

class TestFindNewestBook(unittest.TestCase):
    """Tests for finding the newest book"""

    def setUp(self):
        self.books = [
            {"title": "Book A", "author": "A", "genre": "G", "year": 2000, "price": 5.0},
            {"title": "Book B", "author": "B", "genre": "G", "year": 1950, "price": 5.0},
            {"title": "Book C", "author": "C", "genre": "G", "year": 2020, "price": 5.0}
        ]

    def test_find_newest_book(self):
        """UT-12: Find newest book - latest year displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_newest_book(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("Book C", output)
        self.assertIn("2020", output)

    def test_find_newest_book_single(self):
        """UT-12: Single book collection - that book is the newest"""
        single_book = [{"title": "Only", "author": "X", "genre": "G", "year": 2000, "price": 5.0}]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_newest_book(single_book)
        
        output = fake_out.getvalue()
        self.assertIn("Only", output)

    def test_find_newest_book_empty_collection(self):
        """UT-12: Empty collection shows appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_newest_book([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books yet!", output)


# ============================================================
# UT-13, UT-14: count_books_by_author() Tests
# ============================================================

class TestCountBooksByAuthor(unittest.TestCase):
    """Tests for counting books by author"""

    def setUp(self):
        self.books = [
            {"title": "1984", "author": "George Orwell", "genre": "Dystopian", 
             "year": 1949, "price": 9.99},
            {"title": "Animal Farm", "author": "George Orwell", "genre": "Satire", 
             "year": 1945, "price": 7.99},
            {"title": "Brave New World", "author": "Aldous Huxley", "genre": "Dystopian", 
             "year": 1932, "price": 8.99}
        ]

    @patch('main.get_valid_input', return_value="George Orwell")
    def test_count_existing_author(self, mock_input):
        """UT-13: Author with multiple books - correct count displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.count_books_by_author(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("2", output)
        self.assertIn("George Orwell", output)

    @patch('main.get_valid_input', return_value="Aldous Huxley")
    def test_count_single_book_author(self, mock_input):
        """UT-13: Author with one book - count of 1 displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.count_books_by_author(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("1", output)
        self.assertIn("Aldous Huxley", output)

    @patch('main.get_valid_input', return_value="Unknown Author")
    def test_count_no_author(self, mock_input):
        """UT-14: Author with no books - zero/not found message displayed"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.count_books_by_author(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("No books found", output)

    @patch('main.get_valid_input', return_value="george orwell")
    def test_case_insensitive_search(self, mock_input):
        """UT-14: Author search should be case-insensitive"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.count_books_by_author(self.books)
        
        output = fake_out.getvalue()
        self.assertIn("2", output)

    def test_count_empty_collection(self):
        """UT-14: Empty collection shows appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.count_books_by_author([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books yet!", output)


# ============================================================
# UT-15: export_titles_csv() Test
# ============================================================

class TestExportTitlesCSV(unittest.TestCase):
    """Tests for exporting book titles to CSV"""

    def setUp(self):
        self.books = [
            {"title": "Book A", "year": 2000},
            {"title": "Book B", "year": 2005},
            {"title": "Book C", "year": 2010}
        ]

    @patch('main.write_to_csv')
    def test_export_titles(self, mock_write):
        """UT-15: Export titles - write_to_csv called with correct titles"""
        main.export_titles_csv(self.books)
        
        expected_titles = ["Book A", "Book B", "Book C"]
        mock_write.assert_called_once_with(expected_titles, main.TITLES_CSV_FILE)

    @patch('main.write_to_csv')
    def test_export_titles_empty_list(self, mock_write):
        """UT-15: Empty list - no export, appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.export_titles_csv([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books to export!", output)
        mock_write.assert_not_called()


# ============================================================
# UT-16: export_years_csv() Test
# ============================================================

class TestExportYearsCSV(unittest.TestCase):
    """Tests for exporting publication years to CSV"""

    def setUp(self):
        self.books = [
            {"title": "Book A", "year": 2000},
            {"title": "Book B", "year": 2005},
            {"title": "Book C", "year": 2010}
        ]

    @patch('main.write_to_csv')
    def test_export_years(self, mock_write):
        """UT-16: Export years - write_to_csv called with correct years"""
        main.export_years_csv(self.books)
        
        expected_years = [2000, 2005, 2010]
        mock_write.assert_called_once_with(expected_years, main.YEARS_CSV_FILE)

    @patch('main.write_to_csv')
    def test_export_years_empty_list(self, mock_write):
        """UT-16: Empty list - no export, appropriate message"""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.export_years_csv([])
        
        output = fake_out.getvalue()
        self.assertIn("There are no books to export!", output)
        mock_write.assert_not_called()


# ============================================================
# Run the tests
# ============================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)