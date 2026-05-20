"""
Unit Tests for Book Management Application
===========================================
Tests for all functional requirements (UT-01 to UT-16)
plus validation helper tests.
"""

import unittest
from unittest.mock import patch, mock_open, call, MagicMock
import json
import os
import io
import sys

import main 


# ============================================================
# UT-01, UT-02, UT-03: load_books() Tests
# ============================================================

class TestLoadBooks(unittest.TestCase):
    """Tests for loading books from JSON file"""

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=100)
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([
        {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "year": 1949, "price": 9.99}
    ]))
    def test_UT_01_load_valid_json(self, mock_file, mock_getsize, mock_exists):
        """UT-01: Load from existing books.json with valid data returns list of dicts"""
        result = main.load_books()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], "1984")
        self.assertEqual(result[0]['author'], "George Orwell")

    @patch('os.path.exists', return_value=False)
    def test_UT_02_load_file_not_exist(self, mock_exists):
        """UT-02: Load when books.json does not exist returns empty list without crashing"""
        result = main.load_books()
        
        self.assertEqual(result, [])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=0)
    def test_UT_03_load_empty_file(self, mock_getsize, mock_exists):
        """UT-03: Load from empty books.json returns empty list"""
        result = main.load_books()
        
        self.assertEqual(result, [])

