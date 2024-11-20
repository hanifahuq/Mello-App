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
    table = mf.query_select("user_accounts", username = username, columns = ("user_id"))
    return len(table) > 0

def set_session_user(username):

    user_info = mf.query_select("user_accounts", username = username, columns = ("name", "user_id"))

    st.session_state['username'] = username[0]
    st.session_state['user_id'] = user_info['user_id'.upper()][0]
    st.session_state['name'] = user_info['name'.upper()][0]

    st.rerun()


st.markdown(
        """
        <style>
        .title {
          text-align: center;
          font-size: 80px;  /* Increased font size for the title */
          font-weight: 550;
          font-style: normal;
          margin-bottom: 20px; /* Optional: Add space below the title */
        }
        </style>
        """, unsafe_allow_html=True
        )
    

# User authentication
if 'username' not in st.session_state:
    
    st.markdown(
        f"""
        <div>
            <h1 class="title">Welcome to Mello</h1>
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
            login_button = st.button("Login")
            if login_button:
                if check_user_exists(username):
                    st.success("Success! Logging in...")
                    set_session_user(username)
                    # show_user_access()

                else:
                    st.error("Username does not exist")
        else:
            name = st.text_input("Name")
            data_permission = st.checkbox("I comply with the terms and conditions")

            with open("assets/txt-files/Terms and Conditions.txt", "r", encoding="utf-8") as file:
                file_content = file.read()

            with st.expander('View Terms and Conditions'):
                st.text(file_content)


            create_account_button = st.button("Create Account")

            if create_account_button:
                if data_permission:
                    if check_user_exists(username):
                        st.error("Username already exists, try logging in")
                    else:
                        st.success("Account created! Logging in...")
                        
                        try:
                            # create_user(username, name, data_permission)
                            mf.insert_data("user_accounts", columns = ('username', 'name', 'data_permission'), data = (username, name, data_permission))
                            set_session_user(username)

                        except Exception as e:
                            st.error("Error creating account. Contact developers.")
                            print(e)
            
                else:
                    st.error("Please accept our terms and conditions to make an account")
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

