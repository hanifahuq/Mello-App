import streamlit as st
from streamlit_option_menu import option_menu
import mello_functions as mf
import pandas as pd


from Pages.home import display_home
from Pages.journal import display_journal
from Pages.mimi import display_mimi
from Pages.habit import display_habit
from Pages.dashboard import display_dashboard
from Pages.about import display_about

# Set the page configuration to wide layout
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def set_session_user(username):

    user_info = mf.query_select("user_accounts", username = username, columns = ("name", "user_id"))

    st.session_state['username'] = username#[0]
    st.session_state['user_id'] = user_info['user_id'.upper()][0]
    st.session_state['name'] = user_info['name'.upper()][0]

    st.rerun()

def get_user(username, check_exists = True):
    user_details = mf.query_select("user_accounts", username=username, columns=("user_id", "username", "name", "password_hash"))
    if check_exists:
        return user_details, len(user_details) > 0
    else:
        return user_details

# Inject custom CSS for Google Fonts
st.markdown(
    """
    <style>
        /* Import DM Serif Display and Pacifico from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Pacifico&display=swap');

        /* Apply font classes */
        .dm-serif-display {
            font-family: 'DM Serif Display', serif;
        }

        .pacifico {
            font-family: 'Pacifico', cursive;
        }

        /* Center text styling for demonstration */
        .center-text {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# User authentication
if 'username' not in st.session_state:
    
    # Add changing mimi gif at the top
    changing_mimi = mf.import_html_media("assets/changing-mimi.gif")
    st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; height: 400px;">
                        <img src="data:image/gif;base64,{changing_mimi}" style="width: 300px; height: 300px;" />
                    </div>
                    """,
                    unsafe_allow_html=True,
                )    

    # App content with styled text
    st.markdown(
        """
        <div class="center-text">
            <span class="dm-serif-display" style="font-size: 100px; font-weight: 600">Welcome to </span>
            <span class="pacifico" style="font-size: 100px;">Mello</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Create a layout with columns
    col1, col2, col3 = st.columns(3)
    
    with col2:
        login_create_options = ["Login", "Create an account"]
        login_create = st.selectbox("", options = login_create_options, index = 1)

        username = st.text_input("Username").lower()

        if login_create == login_create_options[0]:

            # Setting up the form layout
            password = st.text_input("Password", type='password')
            login_button = st.button("Login")

            if login_button:
                
                # Get user details and whether the user exists
                user_details, user_exists = get_user(username, check_exists= True)
                stored_hash = user_details['PASSWORD_HASH'][0]

                if user_exists:
                    # Verify login details
                    correct_password = mf.verify_password(password, stored_hash)

                    if correct_password:

                        st.success("Success! Logging in...")
                        set_session_user(username)

                    else:
                        "Incorrect password. Try again"
                else:
                    st.error("User does not exist, create an account")
            
        else:

            # Set up form layout
            name = st.text_input("Name")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type='password')
            data_permission = st.checkbox("I comply with the terms and conditions")

            with open("assets/txt-files/Terms and Conditions.txt", "r", encoding="utf-8") as file:
                file_content = file.read()

            with st.expander('View Terms and Conditions'):
                st.text(file_content)


            create_account_button = st.button("Create Account")

            if create_account_button:
                # Has the individual given permission?
                if not data_permission:
                    st.error("Please accept our terms and conditions to make an account.")
                else:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        # insert the user details
                        hashed = mf.hash_password(password)
                        mf.insert_data("user_accounts", columns = ('USERNAME', 'NAME', 'DATA_PERMISSION', 'PASSWORD_HASH'), data = (username, name, data_permission, hashed))

                        st.success("Account created! Logging in...")

                        set_session_user(username)

else:
    page_container = st.container()

    selected = option_menu(
        None,
        ["Home", "Journal", "Mimi", "Dashboard", "Habits/Calendar", "About"],
        default_index = 0,
        icons = ["house", "journal-bookmark-fill", "chat-right-heart", "bar-chart-line", "calendar-event", "question"],
        orientation = "horizontal"
    )

    if selected == "Home":
        with page_container:
            display_home()
    elif selected == "Journal":
        with page_container:
            display_journal()
    elif selected == "Mimi":
        with page_container:
            display_mimi()
    elif selected == 'Dashboard':
        with page_container:
            display_dashboard()
    elif selected == "Habits/Calendar":
        with page_container:
            display_habit()
    elif selected == "About":
        with page_container:
            display_about()
