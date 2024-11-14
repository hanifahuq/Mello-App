import streamlit as st
import pandas as pd


def display_dashboard():

     # Add custom CSS to center the title and change font size
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 50px;
            margin-bottom: 20px;
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
        </style>
        """,
        unsafe_allow_html=True
    )
       
    # Use the class to center the title
    st.markdown('<h1 class="title"> Dashboard </h1>', unsafe_allow_html=True)

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

        st.subheader('Emotion Trends')
        st.bar_chart(emotions_data.set_index('Emotion'))

    else:
        st.write('No emotion data available to display.')

    