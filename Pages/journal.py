import streamlit as st
import time
from playsound import playsound

def display_journal():

    st.title("How was your day?")

    with st.form(key = "Journal Entry"):
        st.text_input("Name")

        st.text_area("How was your day?")

        ## Temporary habits variable
        habits = ['Meditation', 'Nature walk', 'Reading']
        selected_habits = []

        for habit in habits:
            if st.checkbox(habit):  # Creates a checkbox for each emotion
                selected_habits.append(habit)  # Add checked emotion to the list

        submit_button = st.form_submit_button("Submit")
    
    submitted_container = st.container()

    notif_container = st.container()

    with notif_container:
        col1, col2, col3, col4, col5 = st.columns(5, gap = "large")

    # Display a button
    # Play sound when the button is clicked
    if submit_button:

        with submitted_container:
            st.success("Journal for today submitted!")

        time.sleep(1)

        with col3:
            # Load and display the image from the assets folder
            image_path = "assets/mimi-notification.png"  # Adjust the path if necessary
            st.image(image_path, use_column_width=False, width = 85)
        
        # Create a button to play the audio
        playsound('assets/cat-meow.mp3')