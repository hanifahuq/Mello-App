import streamlit as st
import base64


def display_about():

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
    with open("assets/mimi-icons/about-mimi.png", "rb") as file:
        image_base64 = base64.b64encode(file.read()).decode()
    
        # Embed the HTML structure with the image in base64
    st.markdown(
        f"""
        <div class="title-container">
            <img class="title-image" src = "data:image/png;base64,{image_base64}">
            <h1 class="title">About</h1>
            <img class="title-image" src="data:image/png;base64,{image_base64}">
        </div>
        """,
        unsafe_allow_html=True
    )


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
           
