import streamlit as st
from streamlit_option_menu import option_menu

from pages.home import display_home
from pages.journal import display_journal
from pages.mimi import display_mimi
from pages.habit import display_habit
from pages.dashboard import display_dashboard

# Set the page configuration to wide layout
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

page_container = st.container()

selected = option_menu(
    None,
    ["Home", "Journal", "Mimi", "Dashboard", "Habits"],
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
elif selected == "Habits":
    with page_container:
        display_habit()

