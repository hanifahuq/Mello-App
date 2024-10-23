import requests
from bs4 import BeautifulSoup
import streamlit as st

def display_home():
    

  # Set the page config to use wide layout
  st.set_page_config(
      page_title="Mello", 
      layout="wide", 
      initial_sidebar_state="collapsed"
  )

  # Add custom CSS to center the title and change font size
  st.markdown(
      """
      <style>
      .title {
          text-align: center;
          font-size: 50px;  /* Increased font size for the title */
      }
      blockquote {
          font-size: 28px;  /* Increased font size for the quote */
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
          <div style="text-align: center;">
              <h2 style="margin-bottom: 20px;">Daily Affirmation Quote</h2>
              <blockquote>{}</blockquote>
          </div>
          """.format(quote), unsafe_allow_html=True
      ) 
  else:
      st.write("Could not retrieve the quote.")
