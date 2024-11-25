import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd
import os
import base64
import bcrypt
import json 
import re
import openai
from pygame import mixer
import requests
from bs4 import BeautifulSoup

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


# # Hash a password
# def hash_password(password) -> str:
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     print('SHOULD BE BYTE: ', type(hashed_password))
#     hashed_password_base64 = base64.b64encode(hashed_password).decode('utf-8')
#     print('SHOULD BE STR:', type(hashed_password_base64))

#     try:
#         base64.b64decode(hashed_password_base64)
#         print('IS IN BASE64')
#     except Exception:
#         print('IS --NOT-- IN BASE64')
    
#     return hashed_password_base64

def hash_password(password):
    password_hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return password_hashed

def verify_password(entered_password, stored_hash_password):
    is_correct = bcrypt.checkpw(entered_password.encode(), stored_hash_password.encode())
    return is_correct

# # Verify a password
# def verify_password(password, hashed_password_base64: str) -> bool:
#     try:
#         # Decode the base64-encoded hashed password
#         decoded_password = base64.b64decode(hashed_password_base64)
        
#         # Verify the password using bcrypt
#         return bcrypt.checkpw(password.encode('utf-8'), decoded_password)
#     except Exception as e:
#         print(f"Error during password verification: {e}")
#         return False


def extract_json(response_content):
        try:
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON object found in the response.")
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON format.") from e
        



def extract_json_to_python(response_content):
    try:
        # Find the first valid JSON array in the response content
        print("Raw Response Content for JSON Extraction:", response_content)
        
        json_match = re.search(r"\[.*\]", response_content, re.DOTALL)
        if json_match:
            extracted_json = json.loads(json_match.group(0))  # Convert the JSON string to Python object
            return extracted_json
        else:
            raise ValueError("No valid JSON object found in the response.")
    
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        raise ValueError("Invalid JSON format.") from e
        

def analyze_emotions(journal_entry):
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that analyzes journal entries. Respond strictly with a JSON object containing percentages for the emotions Angry, Fear, Happy, Sad, Surprise. Ensure the percentages sum to 100%. Do not include any additional text."
            },
            {
                "role": "user",
                "content": f"Journal Entry: {journal_entry}"
            }
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0
        )
        
        raw_content = response['choices'][0]['message']['content']
        print("Raw Response:", raw_content)  # Debugging step
        return extract_json(raw_content)

def meow():
    filepath = "assets\cat-meow.mp3"

    mixer.init()
    mixer.music.load(filepath)
    mixer.music.play() 


# Function to send the prompt and get a CBT-specific response
def get_completion(prompt, model="gpt-4o-mini", temperature=0.7):
    """
    Sends a prompt to the specified language model and returns the model's CBT-based response.
    
    Parameters:
    - prompt (str): The input prompt containing the user's statement or question.
    - model (str): The model to be used for generating the completion.
    - temperature (float): Controls the randomness of the output.
    
    Returns:
    - str: The content of the response generated by the model, based on CBT principles.
    """
    messages = [
        {"role": "system", "content": """
            You are a therapist specialized in Cognitive Behavioral Therapy (CBT). 
            Your goal is to help the user manage negative thoughts and emotions by 
            applying CBT principles. Offer supportive, thoughtful responses and help the user 
            reframe unhelpful thoughts.
        """},
        {"role": "user", "content": prompt}
    ]

    for role, message in st.session_state['chat_history']:
        api_role = 'assistant' if role == 'Mimi' else 'user'
        messages.append({"role": api_role, "content": message})


    # Add the latest user input
    messages.append({'role' : 'user' , 'content' : prompt})

    # Sends a request to the OpenAI API with the specified parameters
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    # Returns the content of the response generated by the model
    return response.choices[0].message['content']




def generate_suggested_events(chat_history):


    prompt = f"""
    Based on the following chat history, suggest exactly two personalized activities the user can schedule:

    Chat History:
    {chat_history}

    Suggestions:
    Provide actionable events (e.g., 'Schedule a walk')
    Ensure they align with the user's goals.  

    Respond strictly with a JSON object with two entries, each having a title and a description. Do not include any extra information. 

    Example:
    [
        {{"title": "Event 1", "description": "Description of event 1"}},
        {{"title": "Event 2", "description": "Description of event 2"}}
    ]
    """

    response = openai.ChatCompletion.create(
        model = "gpt-4o-mini",
            messages=[
        {"role": "system", "content": "You are a helpful assistant providing CBT-based activity suggestions."},
        {"role": "user", "content": prompt}
        ],
        temperature = 0
    )

    raw_content = response.choices[0].message['content']
    return extract_json_to_python(raw_content)



# Function to fetch the quote
def fetch_quote():
    url = 'https://www.louisehay.com/affirmations/'
    page = requests.get(url)

    # Check if the request was successful
    if page.status_code != 200:
        return 'Unsuccessful'

    # Parse the HTML content
    soup = BeautifulSoup(page.text, 'lxml')

    # Extract the quote
    quote = soup.find('div', {'class': 'da-quote'}).text.strip()
    return quote


def show_username_in_corner():
    """
    Displays the logged-in user's username in the top-right corner of the app.
    """
    if 'username' in st.session_state:
        username = st.session_state['username']
        # Display username using custom HTML and CSS
        st.markdown(
            f"""
            <style>
                .username-display {{
                    top: 5px;
                    left: 5px;
                    background-color: #ab9ee2;
                    padding: 8px 20px;
                    border-radius: 10px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                    font-size: 20px;
                    font-weight: bold;
                    color: #272665;
                    z-index: 1000;
                    min-width: 150px; /* Ensures the box has a minimum width */
                    height: auto; /* Adjust height automatically based on content */
                    display: inline-block; /* Automatically adjust width based on content */
                    white-space: nowrap; /* Prevents text from wrapping to the next line */
                }}
            </style>
            <div class="username-display">
                Logged in as: {username}
            </div>
            """,
            unsafe_allow_html=True
        )
