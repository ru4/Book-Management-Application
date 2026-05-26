import unittest
from unittest.mock import patch
import tempfile
import os
import json
import io
import main



# ============================================================
# Integration Tests - IT-01 to IT-05
# ============================================================

class TestIntegration(unittest.TestCase):
    """Integration Tests - IT-01 to IT-05"""

    def setUp(self):
        """Create temporary files and redirect constants"""
        # Create temp files for JSON and CSV
        self.temp_dir = tempfile.mkdtemp()
        self.json_file = os.path.join(self.temp_dir, "books.json")
        self.titles_csv = os.path.join(self.temp_dir, "titles.csv")
        self.years_csv = os.path.join(self.temp_dir, "years.csv")

        # Patch the constants
        self.patch_json = patch('main.BOOKS_JSON_FILE', self.json_file)
        self.patch_titles = patch('main.TITLES_CSV_FILE', self.titles_csv)
        self.patch_years = patch('main.YEARS_CSV_FILE', self.years_csv)
        
        self.patch_json.start()
        self.patch_titles.start()
        self.patch_years.start()

        # Start with an empty book list
        self.book_list = []

    def tearDown(self):
        """Stop patching and clean up temp files"""
        self.patch_json.stop()
        self.patch_titles.stop()
        self.patch_years.stop()
        
        # Remove temp directory
        for f in [self.json_file, self.titles_csv, self.years_csv]:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(self.temp_dir)
        
        
    
    @patch('main.get_valid_input')
    def test_add_then_search(self, mock_input):
        """IT-01: Add a book, then search for it - book found and displayed"""
        # Simulate adding a book
        mock_input.side_effect = [
            "The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 12.99
        ]
        main.add_book(self.book_list)

        # Verify book is in the list
        self.assertEqual(len(self.book_list), 1)

        # search for it
        mock_input.side_effect = ["The Hobbit"]
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.search_book(self.book_list)
        output = fake_out.getvalue()
        self.assertIn("The Hobbit", output)
        self.assertIn("J.R.R. Tolkien", output)

        # verify the JSON file contains the book
        with open(self.json_file, 'r') as f:
            saved_books = json.load(f)
        self.assertEqual(len(saved_books), 1)
        self.assertEqual(saved_books[0]['title'], "The Hobbit")
        
        
    
    @patch('main.get_valid_input')
    def test_add_then_sort(self, mock_input):
        """IT-02: Add multiple books, then sort - correct alphabetical order"""
        # Add three books in non-alphabetical order
        books_data = [
            ("Zebra", "A", "G", 2000, 1.0),
            ("Apple", "B", "G", 2001, 2.0),
            ("Mango", "C", "G", 2002, 3.0)
        ]
        for title, author, genre, year, price in books_data:
            mock_input.side_effect = [title, author, genre, year, price]
            main.add_book(self.book_list)

        self.assertEqual(len(self.book_list), 3)

        # Sort
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.sort_books(self.book_list)
        output = fake_out.getvalue()

        # Check display order
        self.assertIn("Apple", output)
        # Check actual list order
        self.assertEqual(self.book_list[0]['title'], "Apple")
        self.assertEqual(self.book_list[1]['title'], "Mango")
        self.assertEqual(self.book_list[2]['title'], "Zebra")

        # Confirm JSON is sorted
        with open(self.json_file, 'r') as f:
            saved = json.load(f)
        self.assertEqual(saved[0]['title'], "Apple")
        self.assertEqual(saved[1]['title'], "Mango")
        self.assertEqual(saved[2]['title'], "Zebra")


    
    @patch('main.get_valid_input')
    def test_add_then_export(self, mock_input):
        """IT-03: Add books, then export - CSV files contain correct data"""
        # Add two books
        books_data = [
            ("1984", "Orwell", "Dystopian", 1949, 9.99),
            ("Dune", "Herbert", "Sci-Fi", 1965, 14.99)
        ]
        for data in books_data:
            mock_input.side_effect = list(data)
            main.add_book(self.book_list)

        # Export titles
        main.export_titles_csv(self.book_list)
        with open(self.titles_csv, 'r') as f:
            titles_content = f.read()
        self.assertIn("1984", titles_content)
        self.assertIn("Dune", titles_content)

        # Export years
        main.export_years_csv(self.book_list)
        with open(self.years_csv, 'r') as f:
            years_content = f.read()
        self.assertIn("1949", years_content)
        self.assertIn("1965", years_content)
        
        
    @patch('main.get_valid_input')
    def test_data_persistence(self, mock_input):
        """IT-04: Add books, save, reload - data persists correctly"""
        mock_input.side_effect = [
            "The Hobbit", "Tolkien", "Fantasy", 1937, 12.99
        ]
        main.add_book(self.book_list)

        # Simulate program restart by loading books into a new list
        fresh_list = main.load_books()

        self.assertEqual(len(fresh_list), 1)
        self.assertEqual(fresh_list[0]['title'], "The Hobbit")
        
    
    @patch('main.get_valid_input')
    def test_full_workflow(self, mock_input):
        """IT-05: Full workflow - add, search, sort, oldest, newest, export, count"""
       
        # Add three books
        books_data = [
            ("Zebra", "A", "G", 2000, 1.0),
            ("Apple", "B", "G", 1990, 2.0),   # oldest
            ("Mango", "C", "G", 2020, 3.0)    # newest
        ]
        for data in books_data:
            mock_input.side_effect = list(data)
            main.add_book(self.book_list)

        # Search for a book
        mock_input.side_effect = ["Apple"]
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.search_book(self.book_list)
        self.assertIn("Apple", fake_out.getvalue())

        # Sort the books
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.sort_books(self.book_list)
        self.assertIn("Apple", fake_out.getvalue())
        self.assertEqual(self.book_list[0]['title'], "Apple")

        # Find the oldest book
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_oldest_book(self.book_list)
        self.assertIn("Apple", fake_out.getvalue())  # 1990

        # Find the newest book
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.find_newest_book(self.book_list)
        self.assertIn("Mango", fake_out.getvalue())  # 2020

        # Export titles & years
        main.export_titles_csv(self.book_list)
        main.export_years_csv(self.book_list)
        with open(self.titles_csv) as f:
            titles = f.read()
        self.assertIn("Apple", titles)
        self.assertIn("Zebra", titles)
        with open(self.years_csv) as f:
            years = f.read()
        self.assertIn("2000", years)

        # Count books by author "C"
        mock_input.side_effect = ["C"]
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main.count_books_by_author(self.book_list)
        self.assertIn("1", fake_out.getvalue())
        
        
        
# ============================================================
# Run the tests
# ============================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)