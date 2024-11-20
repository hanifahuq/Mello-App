import streamlit as st
import openai
import os
from dotenv import load_dotenv
from datetime import date, datetime
import random
import base64
import mello_functions as mf
from streamlit_calendar import calendar



def display_mimi():

    user_id = int(st.session_state['user_id'])
    
    # Load environment variables from the .env file
    load_dotenv()

    # Access the OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    if openai.api_key:
        print(f"OpenAI API Key loaded successfully!")
    else:
        print("Error: OpenAI API Key not found!")

    # Initialize question count and history in session state
    
    if'calendar_events' not in st.session_state:
        st.session_state['calendar_events'] = []

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
    
    # Function to generate suggested events based on previous inputs
    def generate_suggested_events():
        return [
        {"title": "Take a 10-minute break", "description": "A short break to relax and clear your mind."},
        {"title": "Try 10 minutes of meditation", "description": "A quick meditation session to calm your mind."},
        {"title": "Go for a walk", "description": "A short walk to get some fresh air and move your body."},
        {"title": "Journal for 5 minutes", "description": "Take a few minutes to jot down your thoughts or reflect on your day."},
        {"title": "Practice deep breathing", "description": "Spend 5 minutes on deep breathing exercises to reduce stress."},
        {"title": "Listen to relaxing music", "description": "Put on some calming music to help you unwind and relax."},
        {"title": "Read a chapter of a book", "description": "Spend some time reading something that interests you."},
        {"title": "Drink a glass of water", "description": "Hydrate yourself to stay refreshed and energized."},
        {"title": "Stretch for 5 minutes", "description": "Do some light stretching to relieve muscle tension."},
        {"title": "Plan your goals for tomorrow", "description": "Write down a few goals or priorities to set yourself up for a productive day."}
    ]

    
    # Streamlit app interface
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
        """, unsafe_allow_html=True
        )
    

     # Encode the image in base64
    with open("assets/mimi-icons/mimi-mimi.png", "rb") as file:
        image_base64 = base64.b64encode(file.read()).decode()
    
        # Embed the HTML structure with the image in base64
    st.markdown(
        f"""
        <div class="title-container">
            <img class="title-image" src = "data:image/png;base64,{image_base64}">
            <h1 class="title">Mimi</h1>
            <img class="title-image" src="data:image/png;base64,{image_base64}">
        </div>
        """,
        unsafe_allow_html=True
    )


    st.write("Mimi provides guidance based on Cognitive Behavioral Therapy (CBT) techniques.")

    # Check if there is a journal entry
    journal_text = st.session_state.get('journal_text', '')

    # Default prompt if no journal entry
    if not journal_text:
        st.info('Please go to the Journal page and enter your notes for today. Mimi will respond once you have submitted a journal entry.')
    else:
        if not st.session_state['journal_responded']:
            #Generate a response to the journal entry
            initial_prompt = f"Based on the user's journal entry today:\n\n'{journal_text}'\n\nAct as a therapist and provide supportive adivce and guidance using CBT techniques."
            st.session_state['journal_response'] = get_completion(prompt=initial_prompt, model='gpt-4o-mini', temperature=0.7)


            #Add Mimi's response to chat history
            st.session_state['chat_history']. append(('Mimi', st.session_state['journal_response']))
            #Mark that Mimi has responded to the journal entry
            st.session_state['journal_responded'] = True
            

    for role, message in st.session_state['chat_history']:
        if role == 'user':
            st.markdown(
            f"""
            <div style="background-color: #dbfeff; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 80%; margin-right: auto;">
                <span style="font-size: 18px;">💬</span> <b>You:</b> {message}
            </div>
            """, unsafe_allow_html=True
        )
        elif role == 'Mimi':
            st.markdown(
            f"""
            <div style="background-color: #F1F0F0; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 80%; margin-right: auto;">
                <span style="font-size: 18px;">🐱</span> <b>Mimi:</b> {message}
            </div>
            """, unsafe_allow_html=True
        )

    # After journal response, allow the user to ask questions
    if journal_text and st.session_state['journal_responded']:
            # Check if the user has asked fewer than 10 questions
            if st.session_state['question_count'] < 10:
                #st.write('You can now ask Mimi additional questions.')

                # Detect any suggested events from Mimi's response
                if st.session_state['question_count'] >= 3:

                    if 'selected_events' not in st.session_state:
                        suggested_events = generate_suggested_events()
                        st.session_state['selected_events'] = random.sample(suggested_events, 2)

                    st.markdown ('### Suggested Events:  <br>Please select an event you would like to add to the calender', unsafe_allow_html=True)
                    for idx, event in enumerate(st.session_state['selected_events']):
                        with st.expander(event['title']):
                            st.write(event['description'])

                            # Date input for scheduling the event
                            event_date = st.date_input(f"Select a date for {event['title']}'",min_value=datetime.now().date(), key=f"date_{idx}")

                            if st.button(f"Add '{event['title']}' to calendar", key=f"button_{idx}"):
                                st.success('Event added to Calendar')


                                try:
                                    # insert journal into journal entries table
                                    mf.insert_data("EVENTS", columns = ('user_id', 'event_title', 'assigned_date'), data = (str(user_id), event['title'], event_date))
                                except Exception as e:
                                    st.error(f"Error submitting event entry: {e}")

                                st.session_state['events_loaded'] = False
                                st.session_state['calendar_rerun'] = True

            

                    
                    # User input field
                with st.form(key='chat_form', clear_on_submit=True):
                    user_input = st.text_input("How can I help you today?", value=st.session_state['user_input'], max_chars=500)
                    submit_button = st.form_submit_button('Send')

               
                    # Check if the question was previously asked
                    if user_input and submit_button:

                        st.session_state['question_count'] += 1
                        st.session_state['chat_history'].append(('user', user_input))
        

                        # Get the chatbot's response using the OpenAI API
                        response = get_completion(prompt=user_input, model="gpt-4o-mini", temperature=0.7)
                            
                        
                        # Save the new question and response to history
                        st.session_state['chat_history'].append(('Mimi', response))

                        # Display the chatbot's response in the app
                        st.text_area("Mimi:", value=response, height=200)
                    
                        # Reset the input field after processing
                        st.session_state['user_input'] = ''

                # Show how many questions the user has left
                st.write(f"Questions left: {10 - st.session_state['question_count']}")
                    
                
            else:
                # Display a message if the user has reached the question limit
                st.write("You have reached the limit of 10 questions for this session. Thank you for talking with me today! I look forward to talking to you tomorrow")


    # Disclaimer
    st.write("Disclaimer: This chatbot is for educational purposes only and is not a substitute for professional mental health treatment.")
