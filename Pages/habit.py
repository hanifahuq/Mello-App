import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Save the original sys.path
original_sys_path = sys.path.copy()

# Add the utils directory to sys.path temporarily
utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, utils_dir)

# Import the functions from mello_functions.py
import utils.mello_functions as mf

# Restore the original sys.path
sys.path = original_sys_path

def display_habit():

    user_id = int(st.session_state['user_id'])

    # Initialize calendar events if they don't exist in session state
    if'calendar_events' not in st.session_state:
        st.session_state['calendar_events'] = []

    if'habits' not in st.session_state:
        st.session_state['habits'] = []

    st.title("Create a new habit")

    habit_regularity = [
        "Daily", 
        "Weekly", 
        # "Monthly"
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

        # TODO put this line in mimi:
        # st.time_input("what time?", step = 1800)

        frequency = st.selectbox("How often?", options = habit_regularity, index= 0)

        # Display additional input fields based on the frequency selected
        # if frequency == "Monthly":
        #     day_of_month = st.number_input("On which day of the month would you like to repeat this habit?", 
        #                                     min_value=1, max_value=31, value=1, step=1)
        #     st.write(f"Repeating on the {day_of_month} day of each month.")

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
                # weeks = duration // 7 + 1
                # for _ in range(weeks):
                #     # Adjust to the next occurrence of the target day
                #     while current_date.weekday() != target_day:
                #         current_date += timedelta(days=1)
                #     if len(dates) < duration:
                #         dates.append(current_date)
                #         current_date += timedelta(days=7)

                while current_date <= end_date:
                    # If the date does not land on the target weekday, then increase the day till it reaches target
                    if current_date.weekday() != target_day:
                        current_date += timedelta(days = 1)
                    else:
                        # Record the date if same as target weekday and change date to the week after
                        dates.append(current_date)
                        current_date += timedelta(days=7)
                    
            # elif frequency == "Monthly":
            #     current_date = start_date
            #     months = duration // 30 + 1
            #     for _ in range(months):
            #         try:
            #             new_date = current_date.replace(day=day_of_month)
            #             if new_date >= start_date and len(dates) < duration:
            #                 dates.append(new_date)
            #         except ValueError:
            #             # Handle cases where the day doesn't exist in the month
            #             pass
            #         # Move to next month
            #         if current_date.month == 12:
            #             current_date = current_date.replace(year=current_date.year + 1, month=1)
            #         else:
            #             current_date = current_date.replace(month=current_date.month + 1)

            # Structure the data for insertion
            habit_data = [(user_id, title, date) for date in dates]

            mf.insert_multiple_data("events", 
                           columns = ("user_id", "event_title", "assigned_date"),
                           data = habit_data)
            
            # Display the generated dates
            st.write("Generated habit tracking dates:")
            st.dataframe(habit_data)
            
            # Here you could save the habit_data to a database or file
            # For example:
            # habit_data.to_csv('habits.csv', index=False)


        # Ensure calendar_events is a list before passing to the calendar widget
        # if isinstance(st.session_state['calendar_events'], list):
        #     selected_date = calendar(events=st.session_state['calendar_events'])
        # else:
        #     st.error("Error: calendar_events should be a list of event dictionaries.")
        #     selected_date = None
    
    # Show the list of upcoming events
    # if st.session_state['calendar_events']:
    #     st.write("Upcoming Events:")
    #     for event in st.session_state['calendar_events']:
    #         # Ensure each event is a dictionary with the expected keys
    #         if isinstance(event, dict) and "title" in event:
    #             event_datetime = datetime.fromisoformat(event['datetime'])
    #             st.write(f"- {event['title']} on {event_datetime.strftime('%Y-%m-%d %H:%M')}")
    #         else:
    #             st.error("Error: Invalid event format detected.")
    # else:
    #     st.write("No events scheduled yet.")




