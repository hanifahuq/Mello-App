import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime, timedelta, date
import mello_functions as mf
import base64

def display_habit():
    
    # if ('calendar_rerun' in st.session_state) or st.session_state['calendar_rerun'] == True:
    #     st.rerun()
    #     st.session_state['calendar_rerun'] = False

    user_id = st.session_state['user_id']

    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .title-container {
            display: flex;
            justify-content: center;
            align-items: center;  /* Vertically align items in the center */
        }
        .title-image {
            width: 200px;  /* Set the width of the image */
            height: 200px;  /* Set the height of the image */
        }
        .title {
          text-align: center;
          font-size: 100px;  /* Increased font size for the title */
          font-weight: 550;
          font-style: normal;
          margin-bottom: 20px; /* Optional: Add space below the title */
      }

        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Encode the image in base64
    with open("assets/mimi-icons/habit-mimi.png", "rb") as file:
        image_base64 = base64.b64encode(file.read()).decode()
    
        # Embed the HTML structure with the image in base64
    st.markdown(
        f"""
        <div class="title-container">
            <img class="title-image" src = "data:image/png;base64,{image_base64}">
            <h1 class="title">Calendar</h1>
            <img class="title-image" src="data:image/png;base64,{image_base64}">
        </div>
        """,
        unsafe_allow_html=True
    )


    st.subheader("Create a new habit")



    habit_regularity = [
        "Daily", 
        "Weekly"
    ]

    today = datetime.today()

    with st.expander("Add a new habit", expanded= False):

        title = st.text_input("Habit Title")

        # Get start date
        date_range = st.date_input("How long do you want to track this habit?",
                                   value = (today, today + timedelta(days = 7)),
                                   min_value = today)
        
        if len(date_range) == 1:
            st.warning("Make sure to add a beginning and end date!")
        else:
            start_date = date_range[0]
            end_date =  date_range[1]

        frequency = st.selectbox("How often?", options = habit_regularity, index= 0)

        if frequency == "Weekly":
            day_of_week = st.selectbox("On which day of the week would you like to repeat this habit?", 
                                        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            st.write(f"Repeating on {day_of_week} every week.")
        
        submitted = st.button("Create Habit")
                
        if submitted and title:
            dates = []
            
            # Generate dates only after form submission
            if frequency == "Daily":
                duration = (end_date - start_date).days  # Calculate the difference in days
                for i in range(duration):
                    dates.append(start_date + timedelta(days=i))
                    
            elif frequency == "Weekly":
                # Convert day name to number (0 = Monday, 6 = Sunday)
                day_numbers = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, 
                            "Friday": 4, "Saturday": 5, "Sunday": 6}
                target_day = day_numbers[day_of_week]
                
                current_date = start_date

                while current_date <= end_date:
                    # If the date does not land on the target weekday, then increase the day till it reaches target
                    if current_date.weekday() != target_day:
                        current_date += timedelta(days = 1)
                    else:
                        # Record the date if same as target weekday and change date to the week after
                        dates.append(current_date)
                        current_date += timedelta(days=7)

            # Structure the data for insertion
            habit_data = [(user_id, title, date) for date in dates]

            # Insert data into events database
            mf.insert_multiple_data("events", 
                           columns = ("user_id", "event_title", "assigned_date"),
                           data = habit_data)

            st.session_state['events_loaded'] = False
            st.rerun()

    # Extract all events
    if ('events_loaded' not in st.session_state) or (st.session_state['events_loaded'] == False):
        events = mf.query_select("events", columns = ("event_id", "event_title", "assigned_date", "completed"))

        # Cache the grouped events and mark as loaded
        st.session_state['events'] = events
        st.session_state['events_loaded'] = True
    else:
        # Retrieve cached grouped events
        events = st.session_state['events']

    formatted_events = [
        {
            "title" : row['EVENT_TITLE'], 
            "start": str(row['ASSIGNED_DATE']), 
            "end": str(row['ASSIGNED_DATE']),
            "backgroundColor": "#58855c" if row['COMPLETED'] else "#8479d9",
            "borderColor": "#58855c" if row['COMPLETED'] else "#8479d9"
            
            } for _, row in events.iterrows()]
    
    calendar(events = formatted_events)
    # st.rerun()



