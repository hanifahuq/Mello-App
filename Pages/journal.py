import streamlit as st
import time
from playsound import playsound

def display_journal():

    # Add header
    st.title("How was your day?")

    # Create journal entry form to add to table
    with st.form(key = "Journal Entry"):
        
        # Journal entry
        st.text_area("How was your day?")

        # Habit tracking
        ## Temporary habits variable
        habits = ['Meditation', 'Nature walk', 'Reading']
        selected_habits = []

        # If any habits are expected for the day, create a section
        if habits:
            st.write("Habit Tracking")
            for habit in habits:
                if st.checkbox(habit):  # Creates a checkbox for each emotion
                    selected_habits.append(habit)  # Add checked emotion to the list

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
        chat_ready = False # Set chat ready to false 
        with submitted_container:
            st.success("Journal for today submitted!")

        # TODO: Add in AI code here (Maybe make mimi page a class) and check with abby
        chat_ready = True
        if chat_ready:
            with col3:
                # Load and display the image from the assets folder
                image_path = "assets/mimi-notification.png"  # Adjust the path if necessary
                st.image(image_path, use_column_width=False, width = 85)
            
            # Create a button to play the audio
            playsound('assets/cat-meow.mp3')