"""
System Tests for Book Management Application
==============================================
Covers ST-01 to ST-05 from the Test Plan.
Simulates full program runs with mocked user input.
"""

import unittest
from unittest.mock import patch
import tempfile
import os
import json
import io
import sys

import main  # your main program file


class TestSystem(unittest.TestCase):
    """System tests - simulate real user sessions"""

    def setUp(self):
        """Create temporary files and redirect file constants."""
        self.temp_dir = tempfile.mkdtemp()

        # Temporary file paths
        self.json_path = os.path.join(self.temp_dir, "books.json")
        self.titles_path = os.path.join(self.temp_dir, "titles.csv")
        self.years_path = os.path.join(self.temp_dir, "years.csv")

        # Patch the file constants in main module
        self.patchers = [
            patch('main.BOOKS_JSON_FILE', self.json_path),
            patch('main.TITLES_CSV_FILE', self.titles_path),
            patch('main.YEARS_CSV_FILE', self.years_path),
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        """Stop patchers and remove temporary directory."""
        for p in self.patchers:
            p.stop()
        for f in [self.json_path, self.titles_path, self.years_path]:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(self.temp_dir)

    def _run_main(self, inputs):
        """
        Helper: run main() with a list of input strings.
        Returns captured stdout as a string.
        
        """
        with patch('builtins.input', side_effect=inputs), \
             patch('sys.stdout', new=io.StringIO()) as fake_out:
            
            main.main()
        return fake_out.getvalue()

    # ----------------------------------------------------------
    # ST-01: Empty collection operations (no crash, correct messages)
    # ----------------------------------------------------------
    def test_ST_01_empty_collection_operations(self):
        """ST-01: All menu options handle empty collection gracefully."""
        
        # After every menu choice 1-8, add an extra "" in the inputs list
        # to simulate the input pause. 
        inputs = [
            "2", "any", ""          # search -> "no books"
            "3", "",                # sort -> "no books"
            "4", "",                # oldest -> "no books"
            "5", "",                # newest -> "no books"
            "6", "",                # export titles -> "no books to export"
            "7", "",                # export years -> "no books to export"
            "8", "author", "",      # count -> "no books"
            "9"                     # exit
        ]
        output = self._run_main(inputs)
        self.assertIn("There are no books yet!", output)
        self.assertIn("There are no books to export!", output)
        self.assertIn("Goodbye!", output)

    # ----------------------------------------------------------
    # ST-02: Invalid menu choices
    # ----------------------------------------------------------
    def test_ST_02_invalid_menu_choices(self):
        """ST-02: Invalid choices show error and menu reappears."""
        inputs = [
            "0",       # invalid
            "abc",     # invalid
            "10",      # invalid
            "9"        # exit
        ]
        output = self._run_main(inputs)
        self.assertIn("Invalid choice. Please try again.", output)
        self.assertIn("Goodbye!", output)

    # ----------------------------------------------------------
    # ST-03: Full workflow - add, search, sort, oldest, newest, export, count
    # ----------------------------------------------------------
    def test_ST_03_full_workflow(self):
        """ST-03: Full sequence of operations works correctly."""
        inputs = [
            # Add 1st book
            "1", "The Hobbit", "J.R.R. Tolkien", "Fantasy", "1937", "12.99", "",
            # Add 2nd book
            "1", "1984", "George Orwell", "Dystopian", "1949", "9.99", "",
            # Add 3rd book
            "1", "Animal Farm", "George Orwell", "Satire", "1945", "7.99", "",
            # Search
            "2", "1984", "",
            # Sort
            "3", "",
            # Oldest
            "4", "",
            # Newest
            "5", "",
            # Export titles
            "6", "",
            # Export years
            "7", "",
            # Count by author
            "8", "George Orwell", "",
            # Exit
            "9"
        ]
        output = self._run_main(inputs)

        # Add success
        self.assertIn("Book added successfully!", output)

        # Search result
        self.assertIn("The Book you are looking for:", output)
        self.assertIn("1984", output)
        self.assertIn("George Orwell", output)

        # Sort
        self.assertIn("Books sorted by title:", output)
        self.assertIn("Animal Farm", output)

        # Oldest / Newest
        self.assertIn("The Oldest Book:", output)
        self.assertIn("The Newest Book:", output)

        # Count
        self.assertIn("Number of books by George Orwell: 2", output)

        # Goodbye
        self.assertIn("Goodbye!", output)

        # ----- File checks (the temp files) -----
        
        # books.json
        self.assertTrue(os.path.exists(self.json_path))
        with open(self.json_path, 'r') as f:
            books = json.load(f)
        self.assertEqual(len(books), 3)
        titles_in_file = [b['title'] for b in books]
        # After sort they should be alphabetical
        self.assertEqual(titles_in_file, ["1984", "Animal Farm", "The Hobbit"])

        # titles.csv
        self.assertTrue(os.path.exists(self.titles_path))
        with open(self.titles_path, 'r') as f:
            titles_csv = f.read()
        self.assertIn("1984", titles_csv)
        self.assertIn("Animal Farm", titles_csv)
        self.assertIn("The Hobbit", titles_csv)

        # years.csv
        self.assertTrue(os.path.exists(self.years_path))
        with open(self.years_path, 'r') as f:
            years_csv = f.read()
        self.assertIn("1937", years_csv)
        self.assertIn("1949", years_csv)
        self.assertIn("1945", years_csv)

    # ----------------------------------------------------------
    # ST-04: Data persistence between runs
    # ----------------------------------------------------------
    def test_ST_04_data_persistence(self):
        """ST-04: Data persists after program restart."""
        # First session: add a book and exit
        inputs_session1 = [
            "1", "Dune", "Frank Herbert", "Sci-Fi", "1965", "14.99", "",
            "9"
        ]
        self._run_main(inputs_session1)

        # Verify file exists and contains the book
        self.assertTrue(os.path.exists(self.json_path))
        with open(self.json_path, 'r') as f:
            books = json.load(f)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "Dune")

        # Second session: search for the book (should persist)
        inputs_session2 = [
            "2", "Dune", "",
            "9"
        ]
        output = self._run_main(inputs_session2)
        self.assertIn("Dune", output)
        self.assertIn("Frank Herbert", output)

if __name__ == '__main__':
    unittest.main(verbosity=2)