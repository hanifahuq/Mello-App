import streamlit as st
from streamlit_option_menu import option_menu
import mello_functions as mf
import pandas as pd

from pages.home import display_home
from pages.journal import display_journal
from pages.mimi import display_mimi
from pages.habit import display_habit
from pages.dashboard import display_dashboard
from pages.about import display_about

# Set the page configuration to wide layout
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def check_user_exists(username):
    table = mf.query_select("user_accounts", username = username, columns = ("user_id", 'password_hash'))
    return table if len(table) > 0 else None

def set_session_user(username):

    user_info = mf.query_select("user_accounts", username = username, columns = ("name", "user_id"))

    st.session_state['username'] = username[0]
    st.session_state['user_id'] = user_info['user_id'.upper()][0]
    st.session_state['name'] = user_info['name'.upper()][0]

    st.rerun()


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
            password = st.text_input("Password", type='password')
            login_button = st.button("Login")

            if login_button:
                user_data = check_user_exists(username)
                if user_data:
                    stored_hashed_password = user_data[0]['password']
                    if mf.verify_password(password, stored_hashed_password):
                        st.success("Success! Logging in...")
                        set_session_user(username)
                    else:
                        st.error("Invalid password")
        
                else:
                    st.error("Username does not exist")
        else:
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
                if not data_permission:
                    st.error("Please accept our terms and conditions to make an account.")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif check_user_exists(username):
                    st.error("Username already exists, try logging in")
                else:
                    mf.hashed_password = mf.hash_password(password) 
                    print((username, mf.hashed_password.decode("utf-8"), name, data_permission))
                    print(len((username, mf.hashed_password.decode("utf-8"), name, data_permission)))
                    try:
                            # create_user(username, name, data_permission)
                            mf.insert_data("user_accounts", columns = ('username','password_hash', 'name', 'data_permission'), data = (username, mf.hashed_password.decode("utf-8"), name, data_permission))

                            st.success("Account created! Logging in...")
                            set_session_user(username)

                    except Exception as e:
                            st.error("Error creating account. Contact developers.")
                            print(e)
                          
else:
    page_container = st.container()

    selected = option_menu(
        None,
        ["Home", "Journal", "Mimi", "Dashboard", "Habits/Calendar", "About"],
        default_index = 0,
        icons = [],
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

