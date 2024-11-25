import streamlit as st
import base64
import mello_functions as mf

def display_home():
  
  mf.show_username_in_corner()
    
  # Add custom CSS to center the title and change font size
  st.markdown(
      """
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');

      .title {
          text-align: center;
          font-size: 200px;  /* Increased font size for the title */
          font-family: 'Pacifico', cursive;
          font-weight: 550;
          font-style: normal;
          margin-bottom: 20px; /* Optional: Add space below the title */
      }
      blockquote {
          font-size: 40px;  /* Increased font size for the quote */
          padding: 20px;
          line-height: 1.6; /* Adjust line height for better readability */
      }
      </style>
      """, unsafe_allow_html=True
  )

 # Custom CSS for styling
  st.markdown(
    """
    <style>
    .title-container {
        display: flex;
        justify-content: center;
        align-items: center;  /* Vertically align items in the center */
    }
    .title-image {
        width: 200px;  /* Set the width of the image */
        height: 200px;  /* Set the height of the image */
        margin-bottom: 30px
    }
    </style>
    """,
    unsafe_allow_html=True
  )
  
 # Encode the image in base64
  with open("assets/mimi-icons/flower-mimi.png", "rb") as file:
      image_base64 = base64.b64encode(file.read()).decode()
  
    # Embed the HTML structure with the image in base64
  st.markdown(
    f"""
    <div class="title-container">
        <img class="title-image" style = "margin-right: 30px"src = "data:image/png;base64,{image_base64}">
        <h1 class="title">Mello</h1>
        <img class="title-image" style = "margin-left: 30px" src="data:image/png;base64,{image_base64}">
    </div>
    """,
    unsafe_allow_html=True
  )
  # Fetch and display the quote
  quote = mf.fetch_quote()

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
  




