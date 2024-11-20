import streamlit as st
import mello_functions as mf
import base64


def display_about():

    # Add page title
    mf.page_title("About", "assets/mimi-icons/about-mimi.png")

    st.markdown("""
        <div style="text-align: center;">
            <p>
                This app is designed to enhance mental well-being through psychological prinicples, by helping users organise their often stressful daily lives, track moods and manage habits.
            </p>
            <h3>Our Mission</h3>
            <p>To help users manage stress, stay organised, and maintain a balanced mindset!.</p>
            <h3>How it works:</h3>
            <p> Input your journal entry each day, noting down both positive and negative parts. Once this is completed you will get a response from Mimi, your AI CBT therapist.
                You can also navigate to the Habits page where you can create habits you want to track, you can then mark these on the journal page when they have been completed. 
                Now the journal entry has been submitted you can talk to Mimi and ask her for some guidance and support.
                The dashboard tracks your moods and habits overtime.
                Mimi will also suggests some events to help you which you can schedule into the calendar. 
            </p>
            <h4> Have fun! </h4>
        </div>
    """, unsafe_allow_html=True)


    with st.expander('View Privacy Policy'):
            st.markdown("""
                Last Updated: 19/11/2024
                Mello respects your privacy and is committed to protecting your personal data. This Privacy Policy explains how we collect, use, and safeguard your information in compliance with the General Data Protection Regulation (GDPR).

                1. Introduction
                This Privacy Policy applies to our mental health application, Mello, available via the Web. By using the App, you consent to the practices described in this Privacy Policy.

                2. Data Controller
                The data controllers responsible for your personal data is:
                Mello
                Email: Abbyparker@rockborne.com / Hanifahuq@rockborne.com 

                3. Data We Collect
                We collect the following types of data:
                3.1 Personal Data You Provide
                •	Account Information: Name and Username.
                •	Journal Entries: Text you input in the journaling feature.
                •	Emotional Tracking Data: Mood, emotional logs, and other self-reported data.
                •	Habits and Events: Scheduled activities and habits in the calendar.
                3.2 Automatically Collected Data
                •	Device information (e.g., IP address, operating system, and device type).
                •	App usage data (e.g., features accessed, session duration).
                3.3 Sensitive Personal Data
                The App may process sensitive mental health-related data as provided by you. By using the App, you explicitly consent to such processing.

                4. How We Use Your Data
                We use your data for the following purposes:
                •	To Provide and Improve Services: Personalize your experience, track emotional trends, and suggest habits or advice.
                •	For Analytics: Conduct anonymized statistical analyses to enhance the App’s features and usability.
                •	For Communication: Respond to your inquiries or notify you of updates.
                •	Legal Compliance: Fulfil legal obligations or respond to lawful requests.

                5. Legal Basis for Processing
                Under GDPR, we process your data based on the following legal bases:
                •	Consent: For journaling, emotional tracking, and habit creation data.
                •	Contractual Necessity: To provide the App’s core functionality.
                •	Legal Obligations: Compliance with applicable laws.
                •	Legitimate Interests: Anonymized analytics and App improvement.

                6. How We Share Your Data
                We do not sell your personal data. We may share your data:
                •	With Service Providers: Trusted third-party vendors who assist in hosting, analytics, and other operational functions.
                •	For Legal Reasons: To comply with applicable laws, regulations, or legal processes.

                7. Data Retention
                We retain your personal data only as long as necessary for the purposes described in this Policy, or as required by law. You may request deletion of your data at any time by contacting us at Abbyparker@rockborne.com / Hanifahuq@rockborne.com 

                8. Your GDPR Rights
                As a resident of the European Economic Area (EEA), you have the following rights under GDPR:
                •	Right to Access: Request access to your personal data.
                •	Right to Rectification: Correct inaccurate or incomplete data.
                •	Right to Erasure: Request deletion of your personal data.
                •	Right to Restriction: Limit how your data is processed.
                •	Right to Portability: Receive a copy of your data in a machine-readable format.
                •	Right to Object: Object to data processing for specific purposes.
                •	Right to Withdraw Consent: Withdraw consent at any time for data processing activities that rely on your consent.
                To exercise these rights, contact us at Abbyparker@rockborne.com / Hanifahuq@rockborne.com 

                9. Security Measures
                We implement industry-standard security measures to protect your data from unauthorized access, alteration, or disclosure. However, no method of transmission over the internet or electronic storage is 100% secure.

                10. Third-Party Services
                The App may integrate with third-party services (e.g., analytics providers, cloud storage). These third parties process your data in accordance with their own privacy policies.

                11. Children’s Privacy
                The App is not intended for individuals under 16 years old (or the minimum age in your country for data processing consent under GDPR). We do not knowingly collect personal data from children without parental consent.

                12. International Data Transfers
                Your data may be processed and stored outside the EEA. When transferring your data internationally, we ensure appropriate safeguards, such as standard contractual clauses, to protect your data.

                13. Changes to This Privacy Policy
                We may update this Privacy Policy from time to time. Significant changes will be communicated via email or within the App. Continued use of the App constitutes acceptance of the updated Policy.

                14. Contact Information
                If you have questions or concerns about this Privacy Policy, contact us at:
                Mello
                Email: Abbyparker@rockborne.com / Hanifahuq@rockborne.com 

                """)
