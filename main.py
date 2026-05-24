"""
Book Management Application
============================
A console-based book management system.

This program allows library staff to:
    - Add new books to the collection
    - Search for books by title
    - Sort books alphabetically
    - Find the oldest and newest books
    - Export book titles to a CSV file defined by TITLES_CSV_FILE
    - Export book publication years to a CSV file defined by YEARS_CSV_FILE
    - Count books by a specific author

Data is stored persistently in a JSON file defined by BOOKS_JSON_FILE.

Author: Rami Olaqi
Date: 25-05-2026
Version: 1.0
"""

#=========================
# IMPORTS
#=========================

import json
import csv
import os


#=========================
# CONSTANTS
#=========================

MENU = """
===== BOOK MANAGEMENT SYSTEM =====
1. Add Book
2. Search Book
3. Sort Books
4. Find Oldest Book
5. Find Newest Book
6. Export Titles to CSV
7. Export Years to CSV
8. Count Books by Author
9. Exit
"""

BOOKS_JSON_FILE = "books.json"
TITLES_CSV_FILE = "titles.csv"
YEARS_CSV_FILE = "years.csv"

#=========================
# HELPER FUNCTIONS
#=========================

def get_valid_input(prompt, input_type=str, error_message="Invalid input! Please try again."):
    """
    A helper function to get and validate user input
    
    Args:
        prompt: The input prompt to display
        input_type: Expected type (str, int, float)
        error_message: Custom error message for invalid input
    
    Returns:
        Validated input value
    """
    while True:
        user_input = input(prompt).strip()
        
        # Check for empty input
        if not user_input:
            print("\nThis field cannot be empty!")
            continue
        
        # For string input, just return it
        if input_type == str:
            return user_input
        
        # For numeric input, try conversion
        try:
            value = input_type(user_input)
            return value
        except ValueError:
            print(error_message)
           

def display_book(book):
    """
    Display a single book's details
    
    Args:
        book (dict): The book dictionary to display
    """
    print(f"Title: {book['title']}")
    print(f"Author: {book['author']}")
    print(f"Genre: {book['genre']}")
    print(f"Year: {book['year']}")
    print(f"Price: {book['price']}")
    

def display_all_books(book_list):
    """
    Display all books in a numbered list
    
    Args:
        book_list (list): The list of books to display
    """
    for i, book in enumerate(book_list, 1):
        print(f"{i}. {book['title']} by {book['author']} ({book['year']})")


#=========================
# DATA MANAGEMENT
#=========================

def load_books():
    """
    Load book data from BOOKS_JSON_FILE
    
    Returns: 
        list: A list of books loaded from the JSON file
    """
   
    if not os.path.exists(BOOKS_JSON_FILE) or os.path.getsize(BOOKS_JSON_FILE) == 0:
        return []

    try:
        with open(BOOKS_JSON_FILE, "r") as file:
            books = json.load(file)
        return books
    except json.JSONDecodeError:
        print(f"\nCouldn't load {BOOKS_JSON_FILE}! Starting with an empty collection.")
        return []
    
        
    
 
def save_books(book_list):
    """
    Save book data to BOOKS_JSON_FILE
    
    Args:
        book_list (list): The list of books to save
    """
    try:
        with open(BOOKS_JSON_FILE, "w") as json_books:
            json.dump(book_list , json_books,  indent=4)
    except:
        print(f"\nError saving books to {BOOKS_JSON_FILE}!")


def write_to_csv(books_details, file_name):
    """
    Write details to a CSV file
    
    Args:
        books_details (list): The list of book details to write
        file_name (str): The name of the CSV file to write to
    """
    
    try:
        with open(file_name, "w", newline="") as file:
            
            # Create a writer object
            writer = csv.writer(file)

            writer.writerow(books_details)
    except:
        print(f"\nError writing to {file_name}!")


# =========================
# MENU SYSTEM
# =========================

def get_user_choice():
    """
    Get validated menu choice from user
    
    returns: 
        str - the user's menu choice
    """
    choice = input("Enter your choice: ")
    return choice


# =========================
# CORE FEATURES
# =========================

def add_book(book_list):
    """
    Add a new book to the list
    
    Args:
        book_list (list): The list of books
    """
    
    # A dictionary to store book details
    book ={}
    
    # Get validated input for each book detail
    book["title"] = get_valid_input("\nEnter book title: ")
    book["author"] = get_valid_input("\nEnter book author: ")
    book["genre"] = get_valid_input("\nEnter book genre: ")
    book["year"]=  get_valid_input("\nEnter book published year: ",
                                   int, "\nThe year must be a whole number! (e.g., 1999)")       
    book["price"] = get_valid_input("\nEnter book price: ", 
                                    float, "\nThe price must be a number! (e.g., 19.99)")
    
    
    book_list.append(book)

    save_books(book_list)
    print("\nBook added successfully!")

def search_book(book_list):
    """
    Search for a book by title (linear search)
    
    Args:
        book_list (list): The list of books
    """
   
    if not book_list: 
        print("\nThere are no books yet!")
        return

    term = get_valid_input("\nEnter book title to search: ")
    for book in book_list:
        if book["title"].lower() == term.lower():
            print("\nThe Book you are looking for:")
            display_book(book) 
            return
    print("\nBook not found")



def sort_books(book_list):
    """
    Sort books alphabetically by title
    
    Args:
        book_list (list): The list of books
    """
   
    if not book_list: 
        print("\nThere are no books yet!")
        return
    
    book_list.sort(key = lambda book: book["title"] )
    save_books(book_list)
    print("\nBooks sorted by title:")
    display_all_books(book_list)  

    
def find_oldest_book(book_list):
    """
    Find book with earliest publication year
    
    Args:
        book_list (list): The list of books
    """
    if not book_list: 
        print("\nThere are no books yet!")
        return
    
    book = min(book_list, key= lambda book: int(book["year"]))
    

    print("\nThe Oldest Book:")
    display_book(book)
   



def find_newest_book(book_list):
    """
    Find book with latest publication year
    
    Args:
        book_list (list): The list of books
    """
    if not book_list: 
        print("\nThere are no books yet!")
        return
    
    book = max(book_list, key= lambda book: int(book["year"]))
    

    print("\nThe Newest Book:")
    display_book(book)


def export_titles_csv(book_list):
    """
    Export all book titles to titles.csv
    
    Args:
        book_list (list): The list of books
    """
    
    if not book_list:
        print("\nThere are no books to export!")
        return
    
   
    titles = [book["title"] for book in book_list]

    write_to_csv(titles, TITLES_CSV_FILE)
    print("\nBook titles exported to titles.csv successfully!")

def export_years_csv(book_list):
    """
    Export all publication years to years.csv
    
    Args:
        book_list (list): The list of books
    """
    
    if not book_list:
        print("\nThere are no books to export!")
        return
    
    
    years = [book["year"] for book in book_list]
    
    write_to_csv(years, YEARS_CSV_FILE)
    print("\nPublication years exported to years.csv successfully!")

def count_books_by_author(book_list):
    """
    Count number of books by a given author
    """
    if not book_list:
        print("\nThere are no books yet!")
        return
    
    author_name = get_valid_input("\nEnter author name: ")
    count = 0
    
    for book in book_list:
        if book["author"].lower() == author_name.lower():
            count += 1
    
    if count == 0:
        print(f"\nNo books found by {author_name}")

    else:
        print(f"\nNumber of books by {author_name}: {count}")

# =========================
# MAIN PROGRAM
# =========================

def main():
    """
    Main program loop
    """
    book_list = load_books()

    while True:
        print(MENU)

        choice = get_user_choice()

        if choice == "1":
            add_book(book_list)
            input("\nPress Enter to return to menu...")
            
        elif choice == "2":
            search_book(book_list)
            input("\nPress Enter to return to menu...")
            
        elif choice == "3":
            sort_books(book_list)
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            find_oldest_book(book_list)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            find_newest_book(book_list)
            input("\nPress Enter to return to menu...")

        elif choice == "6":
            export_titles_csv(book_list)
            input("\nPress Enter to return to menu...")

        elif choice == "7":
            export_years_csv(book_list)
            input("\nPress Enter to return to menu...")

        elif choice == "8":
            count_books_by_author(book_list)
            input("\nPress Enter to return to menu...")

        elif choice == "9":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid choice. Please try again.")


# =========================
# PROGRAM ENTRY POINT
# =========================

if __name__ == "__main__":
    main()


