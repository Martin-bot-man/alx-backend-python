"""
0-stream_users.py - Stream users from database using a generator

CONCEPT: What is a Generator?
=============================
A generator is a special function that produces values one at a time using 'yield'
instead of returning all values at once. This is memory-efficient!

Regular function (returns all at once):
    def get_all_users():
        users = [user1, user2, user3, ...]  # All in memory!
        return users

Generator function (returns one at a time):
    def stream_users():
        yield user1  # Return this, pause, wait
        yield user2  # Return this, pause, wait
        yield user3  # Return this, pause, wait

Why use generators?
- Memory efficient: Only one row in memory at a time
- Lazy evaluation: Data fetched only when needed
- Great for large datasets
"""
from time import time
import mysql.connector
from mysql.connector import Error

def stream_users():
     """
    Generator function that fetches rows one by one from user_data table.
    
    Uses yield to return one row at a time without loading all data into memory.
    
    Yields:
        dict: A dictionary containing one user's data (user_id, name, email, age)
    
    How it works:
    1. Connect to database
    2. Execute SELECT query
    3. Loop through cursor (cursor itself is an iterator!)
    4. YIELD each row one by one (this is the magic!)
    5. Clean up when done
    """
    connection = None
    cursor = None
 try:
     #step 1: Connect to ALX_prodev database
     connection = mysql.connector.connect(
            host='localhost',
            user='your_username',
            password='your_password',
            database='ALX_prodev'
     )
     if connection.is_connected():
            cursor = connection.cursor(dictionary=True, buffered=False)
            query = "SELECT user_id, name, email, age FROM users"
            cursor.execute(query)
            for row in cursor:
                yield row
  except Error as e:
            print(f"Error: {e}")
  finally:
            if cursor:
                    cursor.close()
            if connection and connection.is_connected():
                    connection.close()                  
                                     
  if __name__ == "__main__"                                       
