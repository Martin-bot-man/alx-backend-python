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
          '''Loads data from users.csv into the users table in ALX_prodev database.'''
          data = []
          try :
          with open(csv_file_path,'r', encoding='utf-8') as csv_file 
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                 if 'user_id' in row and row['user_id']:
                      user_id = row['user_id']
                 else:
                      user_id = str['uuid.uuid4']     