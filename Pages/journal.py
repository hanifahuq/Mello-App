import streamlit as st
import time
from playsound import playsound
import requests
from pprint import pprint
import json
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import date
import mello_functions as mf
from datetime import datetime

def display_journal():

    if'journal_text' not in st.session_state:
        st.session_state['journal_text'] = ''

    if'habits' not in st.session_state:
        st.session_state['habits'] = []

    if'submitted' not in st.session_state:
        st.session_state['submitted'] = False

    if 'user_id' in st.session_state:
        user_id = int(st.session_state['user_id'])

    # Load environment variables from the .env file
    load_dotenv()

    # Access the OpenAI API key
    api_key = os.getenv('API_KEY')

    if api_key:
        print(f"API Key loaded successfully!")
    else:
        print("Error:API Key not found!")
    
    # TODO put this into mello functions -- repeated code from habit.py
    # Get all events due for today
    if ('events_loaded' not in st.session_state) or (st.session_state['events_loaded'] == False):
        events = mf.query_select("events", columns = ("event_id", "event_title", "assigned_date", "completed"))

        # Cache the grouped events and mark as loaded
        st.session_state['events'] = events
        st.session_state['events_loaded'] = True
    else:
        # Retrieve cached grouped events
        events = st.session_state['events']

    todays_events = events[events['ASSIGNED_DATE'] == datetime.today().date()]

    # Add header
    st.title("How was your day?")

    
    # Example prompts for the user
    example_questions = """Here are some prompts to help you get started
    
    1. What was the best part of your day today?
    2. Did you experience any challenges today? How did you deal with them?
    3. How are you feeling right now? Why do you think that is?
    4. What are you grateful for today?
    5. Is there anything you wish you could have done differently today?
    
    Feel free to express yourself freely and reflect on your emotions and experiences.
    """
   


    # Create journal entry form to add to table
    if not st.session_state['submitted']:

        with st.form(key = "Journal Entry"):
            
            # Journal entry
            journal_entry = st.text_area("How was your day? (Feel free to reflect on any thoughts or emotions you had today)",
                                        value=st.session_state.get('journal_text', ''),
                                        height=150,
                                        placeholder=example_questions)
            
            st.write("**Todays Habits**")
            if not todays_events.empty:
                for index, event in todays_events.iterrows():
                    st.checkbox(label = event["EVENT_TITLE"], key= 'eventcheck_' + str(index))
            else:
                st.write("No habits created yet")

            # Create a form submit button
            submit_button = st.form_submit_button("Submit")


        if submit_button:
            st.session_state['journal_text'] = journal_entry
            st.session_state['submitted'] = True

            with st.spinner('Processing your Journal...'):
 
                 # Update the events database
                for index, event in todays_events.iterrows():
                    checkbox_key = f'eventcheck_{index}'
                    if st.session_state.get(checkbox_key):  # Check if the checkbox is checked
                        mf.update_data(
                            table_name="events",
                            column_to_update="completed",
                            new_value=True,
                            condition_column="event_id",
                            condition_value=event['EVENT_ID']
                        )
              
              
              
                journal_date = datetime.now().date()
                submitted_container = st.container()

                with submitted_container:
                    st.success('Journal for today submitted!')
        
                # Define the API URL
                url = "https://api.apilayer.com/text_to_emotion"

                # Convert the journal entry to bytes (utf-8 encoded)
                payload = journal_entry.encode("utf-8")

                # Define headers with API key (replace with your actual API key)
                headers = {
                    "apikey": api_key
                }

                # Make the POST request to the API
                response = requests.request("POST", url, headers=headers, data=payload)

                # Get the status code of the response
                status_code = response.status_code

                # Check if the request was successful
                if status_code == 200:
                    # Parse the response to a dictionary
                    result = json.loads(response.text)
                    st.session_state['emotions'] = result

                    # Extract the emotion scores
                    angry_score = result.get('Angry', 0.0)
                    fear_score = result.get('Fear', 0.0)
                    happy_score = result.get('Happy', 0.0)
                    sad_score = result.get('Sad', 0.0)
                    surprise_score = result.get('Surprise', 0.0)

                    try:
                        # insert journal into journal entries table
                        mf.insert_data("JOURNAL_ENTRIES", columns = ('user_id', 'date_created', 'entry_text', 'angry', 'fear', 'happy', 'sad', 'surprise'), data = (str(user_id), journal_date, str(journal_entry), angry_score, fear_score, happy_score, sad_score, surprise_score))
                    except Exception as e:
                        st.error(f"Error submitting journal entry: {e}")

                else:
                    # Print error message if the request failed
                    print(f"Error: Unable to process the request. Status Code: {status_code}")

                st.session_state['calendar_rerun'] = True
                
                st.success('Head over to Mimi!')
    else:
        st.success("You've already submitted your journal for today!")

           
