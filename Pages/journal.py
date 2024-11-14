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

def display_journal():

    if'journal_text' not in st.session_state:
        st.session_state['journal_text'] = ''

    if'habits' not in st.session_state:
        st.session_state['habits'] = []

    # Load environment variables from the .env file
    load_dotenv()

    # Access the OpenAI API key
    api_key = os.getenv('API_KEY')

    if api_key:
        print(f"API Key loaded successfully!")
    else:
        print("Error:API Key not found!")

    # Add header
    st.title("How was your day?")


    # Create journal entry form to add to table
    with st.form(key = "Journal Entry"):
        
        # Journal entry
        journal_entry = st.text_area("How was your day?", value=st.session_state.get('journal_text', ''))

        # Create a form submit button
        submit_button = st.form_submit_button("Submit")
    
    # Initialise container that will contain the success message
    submitted_container = st.container()

    # Initialise the container that will have the mimi notification
    notif_container = st.container()

    # Create columns equal to the number of pages
    # TODO: make this more dynamic and look at the number of py files in pages folder
    with notif_container:
        col1, col2, col3, col4, col5 = st.columns(5, gap = "large")

    # Show success when information is stored
    # Show notification and play sound when mimi is ready to chat
    if submit_button:
        st.session_state['journal_text'] = journal_entry #save the journal entry
        #chat_ready = False # Set chat ready to false 
        with submitted_container:
            st.success("Journal for today submitted!")

            # TODO: Add in AI code here (Maybe make mimi page a class) and check with abby
            chat_ready = True
            if chat_ready:
                # Display the image centered using `st.image`
                with notif_container:
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image("assets/mimi-notification.png", width=85)
                    st.markdown("</div>", unsafe_allow_html=True)

                # Create a button to play the audio
                #playsound('assets/cat-meow.mp3')



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
            
                for emotion, score in result.items():
                    print(f"{emotion}: {score}")
            else:
                # Print error message if the request failed
                print(f"Error: Unable to process the request. Status Code: {status_code}")


     # Display and Track Habit Completion
    st.subheader("Habit Tracker")
    today = date.today()
    if st.session_state['habits']:
        for habit in st.session_state['habits']:
            st.write(f"**{habit['title']}**")
            completed_today = today in habit['completed_dates']
            if st.checkbox(f"Mark '{habit['title']}' as completed for {today}", value=completed_today, key=f"{habit['title']}_{today}"):
                if today not in habit['completed_dates']:
                    habit['completed_dates'].append(today)
                    st.success(f"'{habit['title']}' marked as completed for today.")
            else:
                if today in habit['completed_dates']:
                    habit['completed_dates'].remove(today)
                    st.info(f"'{habit['title']}' marked as incomplete.")
    else:
        st.write("No habits created yet.")