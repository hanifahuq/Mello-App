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

            with st.expander('View Terms and Conditions'):
                st.markdown("""
                            ### Terms and Conditions

                            Last Updated: 19/11/2024
                            Welcome to Mello. By accessing or using the App, you agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use the App.

                            1. Introduction
                            Mello is a mental health application designed to provide journaling, AI-based advice, emotional tracking, habit creation, event scheduling, and calendar management. The App does not replace professional mental health advice or therapy.

                            2. Eligibility
                            To use the App, you must:
                            •	Be at least 16 years old (or the minimum age required in your country for data processing consent under GDPR).
                            •	Agree to provide accurate and truthful information during registration.

                            3. Use of the App
                            You agree to use the App for personal, non-commercial purposes only. You must not:
                            •	Use the App in a manner that violates any laws or regulations.
                            •	Attempt to disrupt or harm the functionality of the App or other users’ experiences.

                            4. Data Collection and GDPR Compliance
                            We value your privacy and comply with the General Data Protection Regulation (GDPR).
                            4.1 Data We Collect
                            •	Personal Information: Name and Username
                            •	Journaling and habit data, calendar events, and emotional tracking logs.
                            4.2 How We Use Your Data
                            •	To provide personalized services and recommendations.
                            •	To improve and maintain the App’s functionality.
                            •	For anonymized research and analytics purposes.
                            4.3 Your Rights
                            Under GDPR, you have the right to:
                            •	Access, correct, or delete your personal data.
                            •	Withdraw your consent to data processing.
                            •	Request data portability.
                            You can exercise these rights by contacting us at Abbyparker@rockborne.com / Hanifahuq@rockborne.com .

                            5. AI Advice and Limitations
                            The App’s AI chatbot provides general advice based on your inputs. This advice is:
                            •	For informational purposes only.
                            •	Not a substitute for professional mental health advice or treatment. We strongly recommend consulting a qualified healthcare provider for any mental health concerns.

                            6. Account Security
                            You are responsible for maintaining the confidentiality of your login credentials. Notify us immediately if you suspect unauthorized use of your account.

                            7. Limitation of Liability
                            To the fullest extent permitted by law:
                            •	Mello is not liable for any indirect, incidental, or consequential damages arising from your use of the App.
                            •	The App is provided “as-is” without warranties of any kind.

                            8. Third-Party Services
                            The App may integrate with third-party services (e.g., payment processors). We are not responsible for the practices or terms of these third parties.

                            9. Termination
                            We reserve the right to suspend or terminate your account if you violate these Terms and Conditions.

                            10. Changes to These Terms
                            We may update these Terms from time to time. Significant changes will be communicated via email or within the App. Continued use of the App after updates constitutes acceptance of the revised Terms.

                            11. Contact Information
                            If you have questions about these Terms or your data, contact us at:
                            Mello
                            Email: Abbyparker@rockborne.com / Hanifahuq@rockborne.com 

                            12. Governing Law
                            These Terms are governed by the laws of the United Kingdom, without regard to conflict of laws principles.

                            13. Consent
                            By using Mello, you confirm that you have read and agree to these Terms and Conditions, including our Privacy Policy.

                            """)
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

