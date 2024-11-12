import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import os


def get_db_connection():

    load_dotenv()

    # Setting up env and connection variables:
    ACCOUNT = os.getenv('ACCOUNT')
    USER = os.getenv('USER')
    PASSWORD =  os.getenv('PASSWORD')
    WAREHOUSE =  os.getenv('WAREHOUSE')
    DATABASE = "MELLOAPPLICATIONDATA"
    SCHEMA = "APP_SCHEMA"

    ##Establishing the connection and cursor to be used to execute the API requests:
    ctx = snowflake.connector.connect(
            user=USER,
            password=PASSWORD,
            account=ACCOUNT,
            warehouse=WAREHOUSE,
            database=DATABASE,
            schema =SCHEMA
        )
    
def query_select(table_title: str, columns: list, user_id):

    # Create connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Join column names into a single string for the SELECT statement
    columns_str = ", ".join(columns)
    query = "SELECT " + columns_str + " FROM " + table_title + " WHERE user_id = " + str(user_id)

    # Get data
    cursor.execute(query)
    data = cursor.fetch_pandas_all()

    # Close connection
    cursor.close()
    conn.close()

    return data  # Returns None if not found, else returns (user_id, name)

def insert_data(table_title: str, columns: list, *data):
    # Validate the length of data matches columns
    if len(columns) != len(data):
        raise ValueError("The number of columns and data values must match.")

    # Join column names and create placeholders dynamically
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))  # Create a placeholder for each column

    # Construct the query string
    insert_query = f"INSERT INTO {table_title} ({columns_str}) VALUES ({placeholders})"

    # Set up the connection and execute the query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(insert_query, data)  # Pass data as parameters
        conn.commit()
    except Exception as e:
        print("Error inserting data:", e)
        conn.rollback()  # Roll back in case of error
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
