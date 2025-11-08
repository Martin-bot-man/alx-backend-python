"""
Lazy Pagination Implementation with Generators

CONCEPT: What is Lazy Pagination?
==================================
Instead of loading ALL pages at once, we load one page at a time
ONLY when it's actually needed (requested).

Traditional Pagination (loads all at once):
    pages = [page1, page2, page3, ...]  # All in memory!
    return pages

Lazy Pagination (loads on demand):
    yield page1  # Load & return page 1, wait
    yield page2  # Load & return page 2, wait
    yield page3  # Load & return page 3, wait

Benefits:
- Memory efficient: Only one page in memory at a time
- Faster start: Don't wait for all pages to load
- Can stop early: If you only need first 3 pages of 100
"""
import mysql.connector
from mysql.connector import Error


def paginate_users(page_size, offset):
    """
    Fetch a single page of users from the database.
    
    This is a HELPER function that fetches ONE page at a specific offset.
    
    Args:
        page_size (int): Number of users per page
        offset (int): Starting position (0 for first page, page_size for second, etc.)
    
    Returns:
        list: List of user dictionaries for this page
    
    Example:
        paginate_users(2, 0)  → Returns users 1-2 (first page)
        paginate_users(2, 2)  → Returns users 3-4 (second page)
        paginate_users(2, 4)  → Returns users 5-6 (third page)
    """
    connection = None
    cursor = None
    
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change to your MySQL username
            password='your_password',  # Change to your MySQL password
            database='ALX_prodev'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # SQL query with LIMIT and OFFSET for pagination
            # LIMIT: how many rows to fetch
            # OFFSET: how many rows to skip
            query = "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (page_size, offset))
            
            # Fetch all rows for this page
            page_data = cursor.fetchall()
            return page_data
            
    except Error as e:
        print(f"Database error: {e}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def lazy_paginate(page_size):
     """
    Generator that lazily fetches pages of users one page at a time.
    
    This is the MAIN function - it's a GENERATOR that yields pages on demand.
    
    Args:
        page_size (int): Number of users per page
    
    Yields:
        list: One page of users at a time
    
    How it works:
    1. Start at offset 0 (first page)
    2. Fetch one page using paginate_users()
    3. YIELD that page (pause here, return the page)
    4. When next page is requested, increase offset
    5. Repeat until no more data
    
    Magic: Uses only ONE loop!
    """
     while True:
        # Fetch the next page at current offset
        page = paginate_users(page_size, offset)
        
        # If page is empty, we're done - no more data
        if not page:
            break  # Exit the loop
        
        # YIELD the page - pause here, return this page
        yield page
        
        # When execution resumes, move to next page
        offset += page_size              