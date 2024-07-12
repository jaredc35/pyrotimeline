import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime as dt

_ = """
The purpose of this app is to allow someone
to import a CSV file of firework data or 
manually import a firework's name, duration, and start
time, then provide a visual representation of the fireworks
show.

Created by Jared Conway
7/10/24
"""
# @st.experimental_memo
# def get_chart_56029(use_container_width: bool):



column_config = {
    "firework_name": st.column_config.TextColumn(
        "Firework Name", help="The name of the firework",
         max_chars=100),
         "duration": st.column_config.NumberColumn(
        "Duration", help="The duration of the firework in seconds",
         min_value=0, max_value=150),
         "start_time": st.column_config.NumberColumn(
             "Start Time", 
             min_value=0,
             max_value=1440,
         ),
         "end_time": st.column_config.NumberColumn(
             "End Time", 
             min_value=0,
             max_value=1440,
         )
}

def convert_to_seconds(time_str):
    """
    Converts a time string to seconds
    """
    time_str = time_str.split(":")
    return int(time_str[0]) * 60 + int(time_str[1])

def convert_to_display_time(time_int):
    """
    Convert an integer of seconds
    to a display time string of
    the format 'MM:SS'
    """
    min = int(time_int / 60)
    sec = int(time_int % 60)
    return f"{min}:{sec}"

def import_fireworks_data():
  df = pd.read_csv("show_planner_2024.csv")
  
  # Select only the specified columns
  df = df[["Firework Name", "Type", "Effect Duration", "Effect Time"]]
  
  # Rename the columns
  df.rename(columns={
    "Firework Name": "firework_name", 
    "Effect Duration": "duration",
    "Type":"type",
    "Effect Time": "start_time"}, 
    inplace=True)
  
  df.dropna(inplace=True)
  
  # Convert columns to usable time
  df['duration'] = pd.to_numeric(pd.to_datetime(df['duration'], format='%M:%S').dt.strftime("%S"), errors='coerce').fillna(0)
  df['display_start_time'] = pd.to_datetime(df['start_time'], format='%M:%S').dt.strftime("%M:%S")
  df['start_time'] = df['display_start_time'].apply(convert_to_seconds)
  df['end_time'] = df['start_time'] + df['duration']
  df['display_end_time'] = df['end_time'].apply(convert_to_display_time)


  return df

def add_new_firework(name, type, duration, display_start_time):
    """
    Add a new firework to the firework session state
    """
    st.session_state['fireworks_df'] = st.session_state['fireworks_df'].append({
        "firework_name": name,
        "type": type,
        "duration": duration,
        "display_start_time": display_start_time,
        "start_time": convert_to_seconds(display_start_time),
        "end_time": convert_to_seconds(display_start_time) + duration,
        "display_end_time": convert_to_display_time(convert_to_seconds(display_start_time) + duration)
    }, ignore_index=True)

def main(): 
    # Initialization
    st.set_page_config(page_title="Fireworks Show", page_icon=":fireworks:", layout="wide")
    if 'fireworks_df' not in st.session_state:
        st.session_state['fireworks_df'] = import_fireworks_data()
    if 'firework_action' not in st.session_state:
        st.session_state['firework_action'] = "Add New Firework"

    st.header("Richard's Fireworks Timeline!")
    
    with st.expander("Fireworks Data"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state['firework_action'] = st.selectbox("Select an action", 
                         ["Edit Firework", "Add New Firework", "Remove Firework", "Clear Fireworks"],
                         )

        with col2:
            if st.session_state['firework_action'] == "Edit Firework":
                st.button("Edit Firework")
            if st.session_state['firework_action'] == "Add New Firework":
                new_name = st.text_input("Firework Name")
                type = st.selectbox("Type", ['Rocket', "Cake", "Shells", "Sequencer", "Fireball", "Fountains"])
                duration = st.number_input("Duration (in seconds)", min_value=0, max_value=150)
                start_time = st.text_input("Start Time", placeholder="Please enter a time in MM:SS format")
                st.button("Add New Firework",on_click=lambda: add_new_firework(new_name, type, duration, start_time))
            if st.session_state['firework_action'] == "Remove Firework":
                st.button("Remove Firework")
            if st.session_state['firework_action'] == "Clear Fireworks":
                st.button("Clear Fireworks")

    with st.container():
        st.dataframe(st.session_state['fireworks_df'], 
                    use_container_width=True,
                    )
        
    st.write(st.session_state['fireworks_df']['start_time'][0])
    chart = alt.Chart(st.session_state['fireworks_df']).mark_bar().encode(
        x='start_time',
        x2='end_time',
        y='firework_name',
    )
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


    st.write(st.session_state)


if __name__ == "__main__":
    main()