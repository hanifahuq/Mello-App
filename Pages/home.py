import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime

def display_home():
    

  # Add custom CSS to center the title and change font size
  st.markdown(
      """
      <style>
      .title {
          text-align: center;
          font-size: 200px;  /* Increased font size for the title */
      }
      blockquote {
          font-size: 40px;  /* Increased font size for the quote */
          padding: 20px;
          line-height: 1.6; /* Adjust line height for better readability */
      }
      </style>
      """, unsafe_allow_html=True
  )

  # Use the class to center the title
  st.markdown('<h1 class="title">😺 Mello 😺</h1>', unsafe_allow_html=True)


 # Function to fetch the quote
  def fetch_quote():
      url = 'https://www.louisehay.com/affirmations/'
      page = requests.get(url)

      # Check if the request was successful
      if page.status_code != 200:
          return 'Unsuccessful'

      # Parse the HTML content
      soup = BeautifulSoup(page.text, 'lxml')

      # Extract the quote
      quote = soup.find('div', {'class': 'da-quote'}).text.strip()
      return quote


  # Fetch and display the quote
  quote = fetch_quote()

  # Center the title and quote in the app
  if quote != 'Unsuccessful':
      st.markdown(
          """
        <div style="text-align: center; font-family: 'Arial', sans-serif; font-size: 40px;">
            <blockquote style="font-size: 50px; font-weight: bold; color: #333;">"{}"</blockquote>
        </div>
          """.format(quote), unsafe_allow_html=True
      ) 
  else:
      st.write("Could not retrieve the quote.")




  
  # Get the current time and date
  now = datetime.now()
  current_time = now.strftime("%I:%M %p")  # Format: 11:11 AM/PM
  current_date = now.strftime("%A, %B %d")  # Format: Wednesday, June 15th
  am_pm = now.strftime("%p") #Format: AM or PM
 

  # HTML for the card component
  time_card_html = f"""
  <div style="display: flex; justify-content: center; align-items: center; height: 20vh;">
        <div style="border-radius: 10px; border: 1px solid #ccc; padding: 30px; width: 400px; text-align: center; box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);">
            <p style="margin: 0; font-size: 3em; font-weight: bold;">
                <span>{current_time.split()[0]}</span><span style="font-size: 0.5em; vertical-align: top;">{am_pm}</span>
            </p>
            <p style="margin: 0; font-size: 1.5em; color: #555;">{current_date}</p>
            <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 16 16" fill="currentColor" stroke="currentColor" style="color: #FFD700; margin-top: 10px;">
                <path d="M6 .278a.768.768 0 0 1 .08.858 7.208 7.208 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277.527 0 1.04-.055 1.533-.16a.787.787 0 0 1 .81.316.733.733 0 0 1-.031.893A8.349 8.349 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.752.752 0 0 1 6 .278z"></path>
                <path d="M10.794 3.148a.217.217 0 0 1 .412 0l.387 1.162c.173.518.579.924 1.097 1.097l1.162.387a.217.217 0 0 1 0 .412l-1.162.387a1.734 1.734 0 0 0-1.097 1.097l-.387 1.162a.217.217 0 0 1-.412 0l-.387-1.162A1.734 1.734 0 0 0 9.31 6.593l-1.162-.387a.217.217 0 0 1 0-.412l1.162-.387a1.734 1.734 0 0 0 1.097-1.097l.387-1.162zM13.863.099a.145.145 0 0 1 .274 0l.258.774c.115.346.386.617.732.732l.774.258a.145.145 0 0 1 0 .274l-.774.258a1.156 1.156 0 0 0-.732.732l-.258.774a.145.145 0 0 1-.274 0l-.258-.774a1.156 1.156 0 0 0-.732-.732l-.774-.258a.145.145 0 0 1 0-.274l.774-.258c.346-.115.617-.386.732-.732L13.863.1z"></path>
            </svg>
        </div>
    </div>
        """
  
   # Use Streamlit to render the card
  #st.markdown(time_card_html, unsafe_allow_html=True)



