import streamlit as st
import pandas as pd
import mello_functions as mf

def display_dashboard():

    mf.show_username_in_corner()

    if 'user_id' in st.session_state:
        user_id = int(st.session_state['user_id'])

    # Insert page title
    mf.page_title("Dashboard", "assets\mimi-icons\dashboard-mimi.png")

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




    