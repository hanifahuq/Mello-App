import streamlit as st
import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import mello_functions as mf

def display_mimi():

    mf.show_username_in_corner()

    # Add page title
    mf.page_title("Mimi", "assets\mimi-icons\mimi-mimi.png")

    # Retrieve the user id from session state
    user_id = int(st.session_state['user_id'])
    
    # Load environment variables from the .env file
    load_dotenv()

    # Access the OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    if openai.api_key:
        print(f"OpenAI API Key loaded successfully!")
    else:
        print("Error: OpenAI API Key not found!")

    # Initialize session states
 
    if 'question_count' not in st.session_state:
        st.session_state['question_count'] = 0

    if'journal_responded' not in st.session_state:
        st.session_state['journal_responded'] = False

    if'journal_response' not in st.session_state:
        st.session_state['journal_response'] = ''

    if'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    if'user_input' not in st.session_state:
        st.session_state['user_input'] = ''

    # Retrieve the chat history from session state
    chat_history = st.session_state.get('chat_history', [])
    


    st.write("Mimi provides guidance based on Cognitive Behavioral Therapy (CBT) techniques.")
    # Disclaimer
    st.write("Disclaimer: This chatbot is for educational purposes only and is not a substitute for professional mental health treatment.")


    # Check if there is a journal entry
    journal_text = st.session_state.get('journal_text', '')


    # Default prompt if no journal entry
    if not journal_text:
        st.info('Please go to the Journal page and enter your notes for today. Mimi will respond once you have submitted a journal entry.')
    else:
        if not st.session_state['journal_responded']:
            #Generate a response to the journal entry
            initial_prompt = f"Based on the user's journal entry today:\n\n'{journal_text}'\n\nAct as a therapist and provide supportive adivce and guidance using CBT techniques."
            st.session_state['journal_response'] = mf.get_completion(prompt=initial_prompt, model='gpt-4o-mini', temperature=0.7)


            #Add Mimi's response to chat history
            st.session_state['chat_history']. append(('Mimi', st.session_state['journal_response']))
            #Mark that Mimi has responded to the journal entry
            st.session_state['journal_responded'] = True


    # Add chat interface with scrollable history
    st.markdown(
        """
        <style>
            .chat-history {
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .chat-history .message {
                margin-bottom: 15px;
            }
            .chat-history .user {
                text-align: right;
                color: #333;
            }
            .chat-history .mimi {
                text-align: left;
                color: #444;
            }
        </style>
        """, unsafe_allow_html=True
    )

    # After journal response, allow the user to ask questions
    if journal_text and st.session_state['journal_responded']:
            # Check if the user has asked fewer than 10 questions
            if st.session_state['question_count'] < 10:

                # Detect any suggested events from Mimi's response
                if st.session_state['question_count'] >= 3:

                    # Generate events to add to the calendar based on the chat history
                    if 'selected_events' not in st.session_state:
                        try:
                            formatted_chat_history = "\n".join([message for _, message in chat_history])
                            st.session_state['selected_events'] = mf.generate_suggested_events(formatted_chat_history)
                        except Exception as e:
                            st.error(f"Error generating suggestions: {e}")
                            st.session_state['selected_events'] = []

                    # Allow the user to add these events to the calendar
                    st.markdown ('### Suggested Events:  <br>Please select an event you would like to add to the calender', unsafe_allow_html=True)
                    with st.form("event_schedule_form"):
                        for idx, event in enumerate(st.session_state['selected_events']):
                            with st.expander(event['title']):
                                st.write(event['description'])

                                # Date input for scheduling the event
                                event_date = st.date_input(f"Select a date for {event['title']}'",min_value=datetime.now().date(), key=f"date_{idx}")

                                if st.form_submit_button(f"Add '{event['title']}' to calendar"):
                                    st.success('Event added to Calendar')

                                    try:
                                        # insert events into the events table
                                        mf.insert_data("EVENTS", columns = ('user_id', 'event_title', 'assigned_date'), data = (str(user_id), event['title'], event_date))
                                    except Exception as e:
                                        st.error(f"Error submitting event entry: {e}")

                                    st.session_state['events_loaded'] = False
        
                # User input field
            
                user_input = st.chat_input("How can I help you today?", max_chars=500)
        
                # Check if the question was previously asked
                if user_input:

                    st.session_state['question_count'] += 1
                    st.session_state['chat_history'].append(('user', user_input))


                    # Get the chatbot's response using the OpenAI API
                    response = mf.get_completion(prompt=user_input, model="gpt-4o-mini", temperature=0.7)
                        
                    
                    # Save the new question and response to history
                    st.session_state['chat_history'].append(('Mimi', response))


                    # Display the journal entry at the top of the page
                if journal_text:
                    st.markdown(
                        f"""
                        <div style="background-color: #dbfeff; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 80%; margin-left: auto; margin-right: 0;">
                            <h3>Journal Entry:</h3>
                            <p>{journal_text}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )


                for role, message in st.session_state['chat_history']:
                    if role == 'user':
                        st.markdown(
                                    f"""
                                    <div style="background-color: #dbfeff; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 80%; margin-left: auto; margin-right: 0;">
                                        <span style="font-size: 18px;">💬</span> <b>You:</b> {message}
                                    </div>
                                    """, unsafe_allow_html=True
                                )
                    elif role == 'Mimi':
                        st.markdown(
                                    f"""
                                    <div style="background-color: #F1F0F0; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 80%; margin-left: 0; margin-right: auto;">
                                        <span style="font-size: 18px;">🐱</span> <b>Mimi:</b> {message}
                                    </div>
                                    """, unsafe_allow_html=True
                                )

                st.markdown('</div>', unsafe_allow_html=True)


                # Show how many questions the user has left
                st.write(f"Questions left: {10 - st.session_state['question_count']}")
                
            else:
                # Display a message if the user has reached the question limit
                st.write("You have reached the limit of 10 questions for this session. Thank you for talking with me today! I look forward to talking to you tomorrow")


    