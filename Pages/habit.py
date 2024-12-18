import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import mello_functions as mf

def display_habit():

    mf.show_username_in_corner()

    # Retrieve the user id from the session state
    user_id = int(st.session_state['user_id'])
    
    # Insert page title
    mf.page_title("Calendar", "assets/mimi-icons/habit-mimi.png")

    # Insert subheader
    st.subheader("Create a new habit")

    # Define how regular habits can be tracked
    habit_regularity = [
        "Daily", 
        "Weekly"
    ]

    # Retrieve todays date
    today = datetime.today()

    # Allow users to create a new habit
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



