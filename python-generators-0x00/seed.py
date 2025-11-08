import mysql.connector
from mysql.connector import Error
import csv
import uuid
import os

def connect_db():
    '''Connects to the MySQL DB 
    Returns :connection  object or None if connection fails'''
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user ='root',
            password ='your_password')
        if connection.is_connected():
            print("Connection to MySQL successful")
            return connection
    except Error as e:
        print(f"Error while connecting to MYSQL: {e}")
        return None
    
    def create_database(connection):
        '''Creates a database named ALX_prodev if it does not exist.
        ARGS:
            connection: MySQL connection object
            '''
    try:
             cursor = connection.cursor()
             cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
             print("Database ALX_prodev created or already exists.")
             cursor.close()

    except Error as e:
              print(f"Error creating database: {e}")

def connect_to_prodev():
      '''Connects to the ALX_prodev database in MySQL.
    
    Returns:
        connection: MySQL connection object connected to ALX_prodev'''
      try:
          connection = mysql.connector.connect(
              host='localhost',
              user='root',
              password='your_password',
              database='ALX_prodev'
          )
          if connection.is_connected():
              print("Connection to ALX_prodev successful")
              return connection
      except Error as e:
          print(f"Error while connecting to ALX_prodev: {e}")
          return None
      
def create_tables(connection):
    '''Creates users  tables in the ALX_prodev database.
    
    ARGS:
        connection: MySQL connection object'''
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5, 2) NOT NULL,
                INDEX idx_user_id (user_id)
            )
        ''')
        connection.commit()
        print("Tables created successfully.")
        cursor.close()
    except Error as e:
        print(f"Error creating tables: {e}")

    def insert_data_from_csv(connection, csv_file):
        '''Inserts data into users table from a CSV file.    
        ARGS:
            connection: MySQL connection object
            csv_file: Path to the CSV file
        '''
        try:
            cursor = connection.cursor()
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    user_id = str(uuid.uuid4())
                    name = row['name']
                    email = row['email']
                    age = row['age']
                    cursor.execute('''
                        INSERT INTO users (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    ''', (user_id, name, email, age))
            connection.commit()
            print("Data inserted successfully.")
            cursor.close()
        except Error as e:
            print(f"Error inserting data from CSV: {e}")

    def load_csv_data():
          '''Loads data from users.csv into the users table in ALX_prodev database.
          ARGS: csv_file_path: path to the CSV file
          
          Returns: 
          list of tuples containing data from the CSV file'''
          data = []
          try:

            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
              csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                 if 'user_id' in row and row['user_id']:
                      user_id = row['user_id']
                 else:
                      user_id = str(uuid.uuid4())
                 name = row.get('name', '').strip()
                 email = row.get('email', '').strip()
                 age = float(row.get('age', 0))

                 if name and email and age > 0:
                        data.append((user_id, name, email,age))
                 else:
                      print(f"Skipping invalid row: {row}")
            print(f"Loaded {len(data)} rows from csv file.")
            return data
          except FileNotFoundError:
               print(f"Error: CSV file '{csv_file_path}' not found.")
               return []
          except Exception as e:
               print(f"Error reading CSV file: {e}")
               return[]
          
def main():
               '''Main function to setup database and populate with data'''
               csv_file_path = 'user_data.csv'
               #step 1 : Connect to MySQL server
               print("\n===step 1: Connecting to MySQL server ===")
               connection = connect_db()
               if not connection:
                    print("Failed to connect to MySQL server. Exiting...")
                    return
               
               #step2:Create ALX_prodev database
               print("\n===step 2: Creating ALX_prodev database ===")
               create_database(connection)
               connection.close()
                #step 3: Connect to ALX_prodev database
               print("\n===step 3: Connecting to ALX_prodev database ===")
               prodev_connection = connect_db(database="ALX_prodev")
               if not prodev_connection:
                   print("Failed to connect to ALX_prodev database. Exiting...")
                   return

               #step 4: Create users table
               print("\n===step 4: Creating users table ===")
               create_table(prodev_connection)

               #step 5: Load data from CSV
               print("\n===step 5: Loading data from CSV ===")
               if not os.path.exists(csv_file_path):
                   print(f"CSV file '{csv_file_path}' not found. Creating a sample file.")
                   create_sample_csv(csv_file_path)
                   data = load_csv_data(csv_file_path)
               if data:
                   print("\n===step 6: Inserting data into database ===")
                   insert_data(prodev_connection, data)
               else:
                   print("No valid data to insert.")
                   #close connection and exit
                   prodev_connection.close()
                   print("\n=== Database setup completed successfully ===")


                   def create_sample_csv(file_path):
                        '''Creates a sample CSV file for testing purposes.
                        ARGS: 
                        file_path: path to the CSV file'''
                        sample_data = [
        {'user_id': str(uuid.uuid4()), 'name': 'John Doe', 'email': 'john.doe@example.com', 'age': '28.00'},
        {'user_id': str(uuid.uuid4()), 'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'age': '34.50'},
        {'user_id': str(uuid.uuid4()), 'name': 'Bob Johnson', 'email': 'bob.johnson@example.com', 'age': '45.25'},
        {'user_id': str(uuid.uuid4()), 'name': 'Alice Williams', 'email': 'alice.w@example.com', 'age': '29.75'},
        {'user_id': str(uuid.uuid4()), 'name': 'Charlie Brown', 'email': 'charlie.b@example.com', 'age': '52.00'},
    ]
                try:
                             with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
                                  fieldnames = ['user_id', 'name','email', 'age']
                                  writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                                  writer.writeheader()
                                  writer.writerows(sample_data)
                             print(f"sample CSV file created:{file_path}")

                except Exception as e:
                             print(f"Error creating sample CSV file:{e}")  
if __name__ =="__main__":
     main()                 
                                  
