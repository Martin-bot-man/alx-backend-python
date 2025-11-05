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