# Book Management Application

A console-based book management system

## Features

- Add new books with input validation
- Search for books by title (case-insensitive)
- Sort books alphabetically by title
- Find oldest and newest books by publication year
- Export book titles to `titles.csv` defined by TITLES_CSV_FILE
- Export publication years to `years.csv` defined by YEARS_CSV_FILE
- Count books by a specific author
- Persistent storage using JSON `books.json` defined by BOOKS_JSON_FILE

## Book Structure

Each book is stored as a dictionary:

```json
{
    "title": "1984",
    "author": "George Orwell",
    "genre": "Dystopian",
    "year": 1949,
    "price": 9.99
}
```

## How to Run

1. Make sure you have **Python 3.x** installed
    
2. Clone this repository:
    
    ```bash
    git clone https://github.com/ru4/book-management-app.git
    ```
    
1. Navigate to the project folder:

	```bash
    cd book-management-app
    ```
    
2. Run the program:
    
    ```bash
    python main.py
    ```

## Requirements

- Python 3.x
- No external libraries needed (uses only standard library: `json`, `csv`)
    
## Menu Options

```
1. Add Book
2. Search Book
3. Sort Books
4. Find Oldest Book
5. Find Newest Book
6. Export Titles to CSV
7. Export Years to CSV
8. Count Books by Author
9. Exit
```

## Files

| File         | Description                               |
| ------------ | ----------------------------------------- |
| `main.py`    | Main program file                         |
| `books.json` | Book data storage (auto-created)          |
| `titles.csv` | Exported book titles (auto-created)       |
| `years.csv`  | Exported publication years (auto-created) |