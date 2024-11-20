import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd
import os
import base64


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
            user_id = int(st.session_state['user_id'])
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

def insert_multiple_data(table_title: str, columns: tuple, data: list):
    """
    Inserts multiple rows of data into a Snowflake table.

    Params:
        table_title (str): Title of Snowflake table to insert data into.
        columns (tuple): Tuple of column names in the table.
        data (list of tuples): List of tuples where each tuple represents a row to insert.

    Returns:
        None
    """

    # Validate that data is a list of tuples
    if not isinstance(data, list):
        raise ValueError("Data must be a list of tuples.")
    
    if not all(isinstance(row, tuple) for row in data):
        raise ValueError("Each element in data must be a tuple representing a row.")
    
    # Validate that each row of data matches the number of columns
    if not all(len(columns) == len(row) for row in data):
        raise ValueError("Each row of data must have the same number of elements as columns.")

    # Join column names and create placeholders dynamically
    columns_str = ', '.join(columns)
    placeholders = ', '.join(["%s"] * len(columns))  # Create a placeholder for each column

    # Construct the query string
    insert_query = 'INSERT INTO ' + table_title + ' (' + columns_str + ')  VALUES (' + placeholders + ')'

    # Set up the connection and execute the query
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Execute the insert for all rows in data
        cursor.executemany(insert_query, data)  # Use executemany for inserting multiple rows
        conn.commit()
    except Exception as e:
        print(f"Error inserting data into {table_title}: {e}")
        conn.rollback()  # Roll back in case of error
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def update_data(table_name: str, column_to_update: str, new_value: bool, condition_column: str, condition_value):
    """
    Updates a column value in Snowflake based on a condition.

    Params:
        table_name (str): Name of the Snowflake table.
        column_to_update (str): Column to update.
        new_value (bool): The new value to set (True or False).
        condition_column (str): The column used to filter the rows.
        condition_value: The value to match in the condition column.

    Returns:
        None
    """
    # Create the SQL UPDATE query
    update_query = f"""
    UPDATE {table_name}
    SET {column_to_update} = %s
    WHERE {condition_column} = %s
    """

    # Set up the connection and execute the query
    conn = get_db_connection() 
    cursor = conn.cursor()
    
    try:
        # Execute the update query with parameters
        cursor.execute(update_query, (new_value, condition_value))
        conn.commit()
        print(f"Successfully updated {column_to_update} to {new_value} where {condition_column} = {condition_value}.")
    except Exception as e:
        print(f"Error updating data: {e}")
        conn.rollback()  # Roll back in case of error
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def import_html_img(path):
    # Encode the image in base64
    with open(path, "rb") as file:
        image_base64 = base64.b64encode(file.read()).decode()

    return image_base64

def page_title(title:str, img_path):
    # Add custom CSS to center the title and change font size
    st.markdown(
        """
        <style>
        .title {
          text-align: center;
          font-size: 100px;  /* Increased font size for the title */
          font-weight: 550;
          font-style: normal;
          margin-bottom: 20px; /* Optional: Add space below the title */
        }
        .card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: 300px;
            margin: 0 auto; /* Center the card */
        }
        .card-text {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .title-container {
            display: flex;
            justify-content: center;
            align-items: center;  /* Vertically align items in the center */
        }
        .title-image {
        width: 200px;  /* Set the width of the image */
        height: 200px;  /* Set the height of the image */
        }
        </style>
        """,
        unsafe_allow_html=True
        )
    
    # Get title image
    # Encode the image in base64
    title_image = import_html_img(img_path)
    
    # Embed the HTML structure with the image in base64
    st.markdown(
        f"""
        <div class="title-container">
            <img class="title-image" style = "margin-right: 50px" src = "data:image/png;base64,{title_image}">
            <h1 class="dm-serif-display"style="font-size: 100px; font-weight: 600">{title}</h1>
            <img class="title-image" style = "margin-left: 10px" src="data:image/png;base64,{title_image}">
        </div>
        """,
        unsafe_allow_html=True
    )

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