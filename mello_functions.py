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

    #load_dotenv(dotenv_path='pages/.env')

    # Setting up env and connection variables:
    # ACCOUNT = os.getenv('ACCOUNT')
    # USER = os.getenv('USER')
    # PASSWORD =  os.getenv('PASSWORD')
    # WAREHOUSE =  os.getenv('WAREHOUSE')
    # DATABASE = "MELLOAPPLICATIONDATA"
    # SCHEMA = "APP_SCHEMA"

    ACCOUNT = st.secrets["ACCOUNT"]
    USER = st.secrets['USER']
    PASSWORD = st.secrets['PASSWORD']
    WAREHOUSE = st.secrets['WAREHOUSE']
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

# def import_html_media(media_path: str):
#     # Encode the image in base64
#     with open(media_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode()


def import_html_media(media_path: str):
    """
    Encodes a media file (image, video, etc.) to Base64 for embedding in HTML.

    Args:
        media_path (str): Relative path to the media file.

    Returns:
        str: Base64-encoded string of the media file.
    """
    # Construct the absolute path to the media file
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, media_path)

    # Check if the file exists
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Media file not found: {full_path}")

    # Encode the file in Base64
    with open(full_path, "rb") as media_file:
        return base64.b64encode(media_file.read()).decode()


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
    return f"assets/mimi-icons/{state.lower()}-mimi.png"

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


# def meow():
#     filepath = "assets/cat-meow.mp3"
#     # Use Streamlit's built-in audio playback
#     with open(filepath, "rb") as audio_file:
#         st.audio(audio_file.read(), format="audio/mp3") 


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


def transcribe_audio(audio_data):

    api_key = st.secrets['API_KEY']
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    # Upload audio to AssemblyAI
    response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=headers,
        data=audio_data
    )
    upload_url = response.json()['upload_url']

    # Transcribe the audio
    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers=headers,
        json={"audio_url": upload_url}
    )
    transcript_id = transcript_response.json()['id']

    # Poll the API to get the result
    while True:
        result = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        ).json()
        if result['status'] == 'completed':
            return result['text']  # Return the transcribed text
        elif result['status'] == 'failed':
            st.error("Transcription failed.")
            return None
