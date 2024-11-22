import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd
import os
import base64
import bcrypt


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

def import_html_media(media_path: str):
    # Encode the image in base64
    with open(media_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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
        width: 120px;  /* Set the width of the image */
        height: 120px;  /* Set the height of the image */
        margin-bottom: 30px; /* Set the margin for soe white space */
        }
        </style>
        """,
        unsafe_allow_html=True
        )
    
    # Get title image
    # Encode the image in base64
    title_image = import_html_media(img_path)
    
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

def hash_password(password):
    password_hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return password_hashed

def verify_password(entered_password, stored_hash_password):
    is_correct = bcrypt.checkpw(entered_password.encode(), stored_hash_password.encode())
    return is_correct

def kpi_card(img_path, top_emotion: str, percent_value):
    
    # Encoding image as base64 (for demonstration purpose)
    encoded_icon = import_html_media(img_path)

    # Inject custom CSS for Google Fonts
    st.markdown(
        """
        <style>
            /* Import DM Serif Display and Pacifico from Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Pacifico&display=swap');

            /* Apply font classes */
            .dm-serif-display {
                font-family: 'DM Serif Display', serif;
            }

            .pacifico {
                font-family: 'Pacifico', cursive;
            }

            /* Center text styling for demonstration */
            .center-text {
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # HTML and CSS content to render in Streamlit
    st.markdown(
        f"""
        <style>
        /* Flexbox container to center content */
        .flex-container {{
            display: flex;
            justify-content: center; /* Center horizontally */
            align-items: center; /* Center vertically */
            width: 100%;
            height: auto; /* Adjust height if needed */
        }}

        .card {{
            cursor: pointer;
            width: 380px;
            height: 150px;
            background: rgb(255, 255, 255);
            border-radius: 15px;
            border: 2px solid rgba(0, 0, 255, .2);
            transition: all .2s;
            box-shadow: 12px 12px 2px 1px rgba(0, 0, 255, .2);
            display: flex;
            align-items: center; /* Align vertically */
            justify-content: flex-start; /* Align items to the left */
            padding: 10px;
            text-align: left;
            font-family: Arial, sans-serif;
            color: rgb(50, 50, 50);
            margin: 20px;
        }}

        .card:hover {{
            box-shadow: -12px 12px 2px -1px rgba(0, 0, 255, .2);
        }}

        .card img {{
            width: 100px;
            height: 100px;
            object-fit: contain;
            margin-right: 20px;
            margin-left: 20px;
        }}

        .card .subtitle {{
            font-size: 20px;
            font-family: 'DM Serif Display', serif;
            font-weight: 600;
            margin-top: 7px;
        }}

        .card .emotion {{
            font-size: 30px;
            font-family: 'Pacifico', cursive;
            margin-bottom: -5px;
        }}

        .card .percentage {{
            font-size: 50px;
            font-family: 'DM Serif Display', serif;
            font-weight: 600;
        }}
        </style>

        <!-- Flexbox container wrapping the card -->
        <div class="flex-container">
            <div class="card">
                <img src="data:image/png;base64,{encoded_icon}">
                <div>
                    <div class="subtitle">{top_emotion}</div>
                    <div class="percentage">{percent_value}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def html_graph(image_base64, title=""):
    """
    Generates HTML content for displaying an image in Streamlit.

    Args:
    image_base64 (str): Base64 encoded image of the plot.
    title (str): Title of the HTML container.
    
    Returns:
    None
    """
    html_content = f"""
    <div style="
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 60vh;
        background: transparent;">
        <div style="
            border: 2px solid rgba(0, 0, 255, .2);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            background-color: #ffffff;
            width: 85%;
            box-shadow: 12px 12px 2px 1px rgba(0, 0, 255, .2);
            margin-bottom: 40px;">
            <img src="data:image/png;base64,{image_base64}" alt="{title}" style="width: 100%; border-radius: 10px;"/>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def mimicon_path(state:str):
    return f"assets\mimi-icons\{state.lower()}-mimi.png"