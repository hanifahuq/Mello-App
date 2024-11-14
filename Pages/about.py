import streamlit as st


def display_about():

     # Add custom CSS to center the title and change font size
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 50px;  /* Increased font size for the title */
        }
        blockquote {
            font-size: 28px;  /* Increased font size for the quote */
            padding: 20px;
            line-height: 1.6; /* Adjust line height for better readability */
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Use the class to center the title
    st.markdown('<h1 class="title">About Mello</h1>', unsafe_allow_html=True)

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
