import streamlit as st
import mello_functions as mf
import base64


def display_about():

    mf.show_username_in_corner()


    # Add page title

    mf.page_title("About", "assets/mimi-icons/about-mimi.png")

     # Create a layout with columns
    col1, col2, col3 = st.columns(3)


    with col2:
        st.markdown("""
            <div style="text-align: center;">
                <p>
                    This app is designed to enhance mental well-being through psychological prinicples, by helping users organise their often stressful daily lives, track moods and manage habits.
                </p>
                <h3>Our Mission</h3>
                <p>To help users manage stress, stay organised, and maintain a balanced mindset!.</p>
                <h3>How it works:</h3>
                <p> Input your journal entry each day, noting down both positive and negative parts. Once this is completed you will get a response from Mimi, your AI CBT therapist.
                    You can also navigate to the Habits page where you can create habits you want to track, you can then mark these on the journal page when they have been completed. 
                    Now the journal entry has been submitted you can talk to Mimi and ask her for some guidance and support.
                    The dashboard tracks your moods and habits overtime.
                    Mimi will also suggests some events to help you which you can schedule into the calendar. 
                </p>
                <h4> Have fun! </h4>
            </div>
        """, unsafe_allow_html=True)


 
        with open("assets/txt-files/Privacy policy.txt", "r", encoding="utf-8") as file:
                file_content = file.read()


        with st.expander('View Privacy Policy'):
                st.text(file_content)
                    
