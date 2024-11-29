# Importing the necessary packages
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import openai
import mello_functions as mf


def display_journal():

    mf.show_username_in_corner()

    # Add page title
    mf.page_title("Journal", "assets/mimi-icons/journal-mimi.png")


    # Initializing session states
    if'journal_text' not in st.session_state:
        st.session_state['journal_text'] = ''

    if'habits' not in st.session_state:
        st.session_state['habits'] = []

    if'submitted' not in st.session_state:
        st.session_state['submitted'] = False

    if 'user_id' in st.session_state:
        user_id = int(st.session_state['user_id'])

    if'journal_entries' not in st.session_state:
        st.session_state['journal_entries'] = []

    if'habit_status' not in st.session_state:
        st.session_state['habit_status'] = {}

    #  # Load environment variables from the .env file
    # load_dotenv()

    # # Access the OpenAI API key
    # openai.api_key = os.getenv('OPENAI_API_KEY')

    # if openai.api_key:
    #     print(f"OpenAI API Key loaded successfully!")
    # else:
    #     print("Error: OpenAI API Key not found!")

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    
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
    

    # Example prompts for the user
    example_questions = """Here are some prompts to help you get started
    
    1. What was the best part of your day today?
    2. Did you experience any challenges today? How did you deal with them?
    3. How are you feeling right now? Why do you think that is?
    4. What are you grateful for today?
    5. Is there anything you wish you could have done differently today?
    
    Feel free to express yourself freely and reflect on your emotions and experiences.
    """

    # # Create journal entry form to add to table
    # if not st.session_state['submitted']:

    with st.form(key = "Journal Entry"):
        
        # Journal entry text area
        journal_entry = st.text_area("How was your day? (Feel free to reflect on any thoughts or emotions you had today)",
                                    value=st.session_state.get('journal_text', ''),
                                    height=250,
                                    placeholder=example_questions,
                                    key = "journal_input")
        
        # Add mic recorder
        # st.subheader("Record your journal:")
        # audio_data = st_mic_recorder()

        # if st.form_submit_button("Transcribe Audio"):
        #     if audio_data:
        #         with st.spinner("Transcribing audio..."):
        #             transcribed_text = mf.transcribe_audio(audio_data)
        #             if transcribed_text:
        #                 st.session_state['journal_text'] = transcribed_text
        #                 st.success("Audio transcribed successfully! Text added to your journal entry")
        
        # submit_button = st.form_submit_button("Submit")
    
        # Adds the habits to the Journal page which can be ticked when completed
        st.subheader("To Do:")
        if not todays_events.empty:
            for index, event in todays_events.iterrows():
                checkbox_key = f'eventcheck_{index}'
                is_checked = st.session_state['habit_status'].get(checkbox_key)
                completed = st.checkbox(label = event["EVENT_TITLE"], key=checkbox_key, value=is_checked)
                st.session_state['habit_status'][checkbox_key] = completed
        else:
            st.write("No habits created")
            st.info("Head to the Calendar page to create your habits!")

        # Create a form submit button
        submit_button = st.form_submit_button("Submit")

    # When the submit button is pressed and the journal entry completed, process the journal
    if submit_button:
        st.session_state['journal_text'] = journal_entry
        st.session_state['submitted'] =  True
        st.session_state['journal_entries'].append(journal_entry)

        with st.spinner('Processing your Journal...'):

            # Update the events database to show these have been completed in the calendar
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
            
            # Get the date of when the journal is written
            journal_date = datetime.now().date()

            # Analyze the journal entry to extract emotions using the analyze emotions function
            result = mf.analyze_emotions(journal_entry)

            # Store the result in the emotions session state
            st.session_state['emotions'] = result

            # Extract the emotion scores from the journal entry
            angry_score = result.get('Angry', 0.0)
            fear_score = result.get('Fear', 0.0)
            happy_score = result.get('Happy', 0.0)
            sad_score = result.get('Sad', 0.0)
            surprise_score = result.get('Surprise', 0.0)

            # Insert the emotions extracted into the journal entries table to use in the dashboard
            try:
                mf.insert_data("JOURNAL_ENTRIES", columns = ('user_id', 'date_created', 'journal_entry', 'angry', 'fear', 'happy', 'sad', 'surprise'), data = (str(user_id), journal_date, journal_entry, angry_score, fear_score, happy_score, sad_score, surprise_score))
            except Exception as e:
                st.error(f"Error submitting journal entry: {e}")

                    
            # Change the events loaded session state to false
            st.session_state['events_loaded'] = False

            # Play meow when the journal has been processed
            #mf.meow()

            # Success message
            # Inject CSS styles
            st.markdown(
                """
                <style>
                /* From Uiverse.io by andrew-demchenk0 */ 
                .success {
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    width: 320px;
                    padding: 12px;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: start;
                    background: #EDFBD8;
                    border-radius: 8px;
                    border: 1px solid #84D65A;
                    box-shadow: 0px 0px 5px -3px #111;
                    margin-bottom: 20px;
                }

                .success__icon {
                    width: 35px;
                    height: 35px;
                    transform: translateY(-2px);
                    margin-right: 8px;
                }

                .success__icon path {
                    fill: #84D65A;
                }

                .success__title {
                    font-weight: 500;
                    font-size: 14px;
                    color: #2B641E;
                    margin-left: 10px;
                }

                .success__close {
                    width: 20px;
                    height: 20px;
                    cursor: pointer;
                    margin-left: auto;
                }

                .success__close path {
                    fill: #2B641E;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            super_mimi = mf.import_html_media("assets/mimi-icons/super-mimi.png")

            st.markdown(
                f"""
                <div class="success">
                    <div class="success__icon">
                        <img src="data:image/png;base64,{super_mimi}" alt="Success Icon" style="width: 35px; height: 35px; margin-right: 8px;" />
                    </div>
                    <div class="success__title">Journal submitted - Head to Mimi!</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# else:
#     # Only one journal can be submitted each day
#     st.success("You've already submitted your journal for today!")

        
