"""
4-stream_ages.py - Stream user ages from database using a generator

CONCEPT: Streaming Specific Data
=================================
Instead of fetching entire user objects, we can stream just the data we need.
This is even MORE memory efficient!

Full user object: {user_id, name, email, age} = ~200 bytes
Just age: 25.50 = ~8 bytes

For 1 million users:
- Full objects: ~200 MB in memory
- Just ages: ~8 MB in memory
That's 25x less memory!"""
import mysql


def stream_user_ages():
    """
    Generator function that streams only user ages from the database.
    
    Instead of fetching entire user records, this only fetches the age field,
    making it even more memory efficient.
    
    Yields:
        float: User age one at a time
    
    How it works:
    1. Connect to database
    2. SELECT only the age column
    3. Loop through results
    4. YIELD each age value (not the whole user object!)
    5. Clean up when done
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
            # Create cursor with buffered=False for streaming
            cursor = connection.cursor(buffered=False)
            
            # Query ONLY the age column - more efficient!
            query = "SELECT age FROM user_data"
            cursor.execute(query)
            
            # ONE LOOP - yield ages one by one
            for (age,) in cursor:  # Note: (age,) unpacks the tuple
                yield age  # Yield just the age value
                
    except Error as e:
        print(f"Database error: {e}")
        
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

