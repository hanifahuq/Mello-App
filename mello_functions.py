import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import os


def get_db_connection():

    """
    Establishes connection with snowflake using credentials set up in env

    Params: 
        None

    Returns: 
        None
    """

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
    
def query_select(user_id, table_title: str,  *columns: str):

    """
    Extracts dataframe based on specific user using SELECT SQL function from snowflake data. 

    Params:
        user_id: User logged in
        table_title (str): Title of snowflake table to select information from
        columns: Column data to extract
        
    Returns:
        pd.DataFrame
    """

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

def insert_data(table_title: str, columns: tuple, data: tuple):
    """
    Inserts a row of data into snowflake table

    Params:
        table_title (str): Title of snowflake table to select information from
        columns (list): List of column titles 
        data (str): 

    Returns:
        None

    """

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

def check_login():
    """
    Checks if user has logged in to the session

    Params:
        None
    
    Returns:
        Bool
    """

    if 'username' in st.session_state:
        return True
    else: return False