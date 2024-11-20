import streamlit as st
import pandas as pd
import mello_functions as mf
import base64

def display_dashboard():

    if 'user_id' in st.session_state:
        user_id = int(st.session_state['user_id'])

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
        .card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: 300px;
            margin: 0 auto; /* Center the card */
        }
        .card-text {
            font-size: 24px;
            font-weight: bold;
            color: #333;
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
        """,
        unsafe_allow_html=True
        )
       
        # Encode the image in base64
    with open("assets/mimi-icons/dashboard-mimi.png", "rb") as file:
        image_base64 = base64.b64encode(file.read()).decode()
    
        # Embed the HTML structure with the image in base64
    st.markdown(
        f"""
        <div class="title-container">
            <img class="title-image" src = "data:image/png;base64,{image_base64}">
            <h1 class="title">Dashboard</h1>
            <img class="title-image" src="data:image/png;base64,{image_base64}">
        </div>
        """,
        unsafe_allow_html=True
        )


    if'emotions' in st.session_state and st.session_state['emotions']:
        emotions_data = pd.DataFrame(list(st.session_state['emotions'].items()), columns=['Emotion', 'Count'])

        top_emotion = emotions_data.loc[emotions_data['Count'].idxmax()]

        # Display the top emotion as a centered card
        st.markdown(
            f"""
            <div class="card">
                <div class="card-text">Top Emotion: {top_emotion['Emotion']} ({top_emotion['Count']}%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader('Emotion Trends For Today')
        st.bar_chart(emotions_data.set_index('Emotion'))

    else:
        st.write('No emotion data available to display.')


    emotions_overtime = mf.query_select('journal_entries', user_id = user_id, columns = ('Angry', 'Fear', 'Happy', 'Sad', 'Surprise'))
    mean_emotions = emotions_overtime.mean()
    st.subheader('Mean Emotions From All Journal Entries.')
    st.bar_chart(mean_emotions)




    