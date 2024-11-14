import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd
import os


def get_db_connection():

    """
    Establishes connection with snowflake using credentials set up in env

    Params: 
        None

    Returns: 
        None
    """

    load_dotenv(dotenv_path='pages/.env')

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
    
    return ctx

def query_select(table_title: str, columns: tuple, user_id: int = None, username: str = None) -> pd.DataFrame:
    """
    Extracts data from a Snowflake table based on specific user criteria using the SQL SELECT function.
    
    Params:
        table_title (str): Title of Snowflake table to select information from.
        user_id (int, optional): User ID to filter data.
        username (str, optional): Username to filter data.
        columns (str): Column data to extract.
        
    Returns:
        pd.DataFrame: Data retrieved from the query, or an empty DataFrame if no data is found.
    """

    table_title = table_title.upper()

    # Ensure at least one filter criterion is provided
    if not user_id and not username:
        try:
            user_id = st.session_state['user_id']
        except:
            raise ValueError("user_id in session state is not defined. Either user_id or username must be provided to filter the query.")

    # Check if columns is provided
    if columns:
        # Ensure that columns are treated as a list of strings (even if there's only one column)
        if isinstance(columns, str) or len(columns) == 1:
            # If columns is a single string, don't join
            columns_str = columns
        else:
            # Join the columns if it's a list of strings
            columns_str = ", ".join(columns)
    else:
        # If no columns, use '*' to select all columns
        columns_str = "*"

    # Start constructing the query
    query = 'SELECT ' + columns_str + ' FROM ' + table_title

    # Add the WHERE clause based on the available parameters
    filters = []
    params = []
    if user_id:
        filters.append("USER_ID = %s")
        params.append(user_id)
    if username:
        filters.append("USERNAME = %s")
        params.append(username)

    # Join filters with AND if both are provided
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)

    # Create connection
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Execute the query with parameters
        cursor.execute(query, params)
        data = cursor.fetch_pandas_all()
    except Exception as e:
        print(f"Error executing query: {query}", e)
        data = pd.DataFrame()  # Return an empty DataFrame on error
    finally:
        # Close connection
        cursor.close()
        conn.close()

    return data

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
    columns_str = ', '.join(columns)
    placeholders = ', '.join(["%s"] * len(columns))  # Create a placeholder for each column

    # Construct the query string
    insert_query = 'INSERT INTO ' + table_title + '(' + columns_str + ')' + ' VALUES ' + '(' + placeholders + ')'

    # Set up the connection and execute the query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(insert_query, data)  # Pass data as parameters
        conn.commit()
    except Exception as e:
        print(f"Error inserting data ({insert_query}):", e)
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