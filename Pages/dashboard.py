import streamlit as st
import pandas as pd
import mello_functions as mf
import base64
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import io

def display_dashboard():

    mf.show_username_in_corner()

    if 'user_id' in st.session_state:
        user_id = int(st.session_state['user_id'])

    ## LAYOUT ##
    # Insert page title
    mf.page_title("Dashboard", "assets/mimi-icons/dashboard-mimi.png")

    info_container = st.container()

    # Show the KPI's
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    bargraph_container = st.container()

    timeline_container = st.container()

    ## LOGIC ##

    NA_str = "--"
    min_entries = 3

    if 'emotions' in st.session_state and st.session_state['emotions']:

        # Turn all emotions into df for today
        emotions_data = pd.DataFrame(list(st.session_state['emotions'].items()), columns=['Emotion', 'Count'])

        # Get top emotion values
        emotion_count = emotions_data.loc[emotions_data['Count'].idxmax()]
        top_emotion = emotion_count['Emotion']
        top_emotion_value = emotion_count['Count']

    else:
        top_emotion = NA_str
        top_emotion_value = NA_str
        st.info('Submit your Journal to get more insights!')


    ## TODO repeated code from journal - maybe turn into a function
    if ('events_loaded' not in st.session_state) or (st.session_state['events_loaded'] == False):
        events = mf.query_select("events", columns = ("event_id", "event_title", "assigned_date", "completed"))

        # Cache the grouped events and mark as loaded
        st.session_state['events'] = events
        st.session_state['events_loaded'] = True
    else:
        # Retrieve cached grouped events
        events = st.session_state['events']

    # Get the length of people 
    todays_uncompleted_tasks = events[(events['ASSIGNED_DATE'] == datetime.today().date()) & (events['COMPLETED'] != True)]

    remaining_tasks = len(todays_uncompleted_tasks)

    if remaining_tasks > 0:
        todo_emoticon = "coffee"
    else:
        todo_emoticon = "spa"

    with kpi4:
            mf.kpi_card(mf.mimicon_path(todo_emoticon), "Todo's Today", remaining_tasks)
    

    alt_emoticon = mf.mimicon_path("about")

    if 'emotions' in st.session_state and st.session_state['emotions']:
        # Set up the plot
        sns.set(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10, 2))

        # Custom color palette for emotions
        purple_palette = sns.color_palette(["#7D7DDA", "#8C8CDA", "#9A9AD9", "#A9A9D9", "#B7B7D8"])

        # Bar plot for emotions
        sns.barplot(x="Emotion", y="Count", data=emotions_data, palette=purple_palette, ax=ax)

        # Add labels
        ax.set_title("Today's Emotions", fontsize=16)
        ax.set_xlabel("")
        ax.set_ylabel("Percentage (%)", fontsize=12)

        # Save the plot to a BytesIO buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)

        # Encode the image to base64
        emotion_graph = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

        # Render the HTML in Streamlit
        with bargraph_container:
            mf.html_graph(emotion_graph)

    if 'all_entries' not in st.session_state:
        journal_entries = mf.query_select("journal_entries", 
                                            ("date_created", "angry", "fear", "happy", "sad", "surprise"), 
                                            user_id = user_id)
        st.session_state['all_entries'] = journal_entries
    else:
        journal_entries = st.session_state['all_entries']

    if not journal_entries.empty:
        journal_entries['DATE'] = pd.to_datetime(journal_entries['DATE_CREATED'], format='%Y-%m-%d')

        # Group any identical dates together (multiple entries in same day)
        entries_grouped = journal_entries.groupby('DATE').mean().reset_index().sort_values(by = 'DATE')

        # Find consecutive date groups
        entries_grouped['GROUP'] = (entries_grouped['DATE'].diff().dt.days != 1).cumsum()

        # Calculate streak lengths
        streaks = entries_grouped.value_counts('GROUP').reset_index()

        best_streak = streaks['count'].max()

        with kpi3:
            # TODO Change the journal streak by extracting data and calculate the best streak
            mf.kpi_card(f"assets/trophy-icon.png", "Best Streak", best_streak)


        # Current streak (if today is included in the latest streak)
        today = pd.Timestamp.now().normalize()
        if today in entries_grouped['DATE'].values:
            current_streak = streaks.iloc[-1]['count']
        else:
            current_streak = 0

        with kpi2:
            # TODO Change the journal streat by extracting data and calculating current streak
            mf.kpi_card(f"assets/fire-icon.png", "Journal Streak", current_streak)

        if len(entries_grouped) > min_entries:

            # Melt the DataFrame to use seaborn lineplot for time series
            entries_melted = entries_grouped.melt(id_vars=['DATE'], value_vars=entries_grouped[['ANGRY', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE']].columns, 
                            var_name="EMOTION", value_name="PERCENTAGE")
            # Rename EMOTION values in entries_melted to capitalize the first letter
            entries_melted['EMOTION'] = entries_melted['EMOTION'].str.capitalize()

            sns.set(style="whitegrid")
            line_color = sns.color_palette(["#cdb4db", "#ffc8dd", "#ffafcc", "#bde0fe", "#a2d2ff"])

            fig, ax = plt.subplots(figsize=(10, 2))

            # Line plot for emotions over time
            sns.lineplot(data=entries_melted, x="DATE", y="PERCENTAGE", hue="EMOTION", marker='o', ax=ax, palette=line_color, linewidth = 10)

            # Add labels and title
            ax.set_title("Emotion Percentages Over Time", fontsize=16)
            ax.set_ylabel("Percentage (%)", fontsize=12)
            ax.set_xlabel("")

            ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Emotions")
            
            ax.set_xticks(entries_grouped['DATE'])  # Set ticks explicitly to match the string dates
            ax.set_xticklabels([d.strftime("%d-%m-%Y") for d in entries_grouped['DATE']])

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)

            # Save the plot to a BytesIO buffer
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            # Encode the image to base64
            timeline_graph = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()

            # Render the HTML in Streamlit
            with timeline_container:
                mf.html_graph(timeline_graph)
        else:
            st.info(f"Submit at least {min_entries} journals to see data!")
    else:
        st.info(f"Submit at least {min_entries} journals to see data!")

        with kpi1:
            mf.kpi_card(
                mf.mimicon_path(top_emotion) if top_emotion != NA_str else alt_emoticon, 
                f"Feeling: {top_emotion}", 
                f"{top_emotion_value}%"
            )
        # with kpi2:
        #     # TODO Change the journal streat by extracting data and calculating current streak
        #     mf.kpi_card(f"assets/fire-icon.png", "Journal Streak", current_streak)
        # with kpi3:
        #     # TODO Change the journal streak by extracting data and calculate the best streak
        #     mf.kpi_card(f"assets/trophy-icon.png", "Best Streak", best_streak)
        # with kpi4:
        #     mf.kpi_card(mf.mimicon_path(todo_emoticon), "Todo's Today", remaining_tasks)





