import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime


def display_habit():

    # Initialize calendar events if they don't exist in session state
    if'calendar_events' not in st.session_state:
        st.session_state['calendar_events'] = []

    st.title("Create a new habit")

    habit_regularity = ["Daily", "Weekly", "Monthly"]

    with st.expander("Add a new habit", expanded= False):

        st.text_input("Habit Title")
        st.number_input("How long do you want to track this habit?", min_value= 1, value = 30, step= 1)

        frequency = st.selectbox("How often?", options = habit_regularity, index= 0)

        # Display additional input fields based on the frequency selected
        if frequency == "Monthly":
            day_of_month = st.number_input("On which day of the month would you like to repeat this habit?", 
                                            min_value=1, max_value=31, value=1, step=1)
            st.write(f"Repeating on the {day_of_month} day of each month.")

        elif frequency == "Weekly":
            day_of_week = st.selectbox("On which day of the week would you like to repeat this habit?", 
                                        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            st.write(f"Repeating on {day_of_week} every week.")
        submitted = st.button("Create Habit")
                
        if submitted:
            st.success("New habit created")

    # Add temporary events
    events = [{
        "title": "Event 1",
        "color": "#AB9EE2",
        "start": "2024-10-24"
    }, {
        "title": "Event 1",
        "color": "#AB9EE2",
        "start": "2024-10-25"
    }, ]

    # Create a calendar widget
    #selected_date = calendar(events=st.session_state.get("events", events))

    #st.write(selected_date)


    # Ensure calendar_events is a list before passing to the calendar widget
    if isinstance(st.session_state['calendar_events'], list):
        selected_date = calendar(events=st.session_state['calendar_events'])
    else:
        st.error("Error: calendar_events should be a list of event dictionaries.")
        selected_date = None

    #if selected_date:
        #st.write(f"Selected date: {selected_date}")

    # Show the list of upcoming events
    if st.session_state['calendar_events']:
        st.write("Upcoming Events:")
        for event in st.session_state['calendar_events']:
            # Ensure each event is a dictionary with the expected keys
            if isinstance(event, dict) and "title" in event:
                event_datetime = datetime.fromisoformat(event['datetime'])
                st.write(f"- {event['title']} on {event_datetime.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.error("Error: Invalid event format detected.")
    else:
        st.write("No events scheduled yet.")




