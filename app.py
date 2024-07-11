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

def import_fireworks_data():
  df = pd.read_csv("show_planner_2024.csv")
  
  # Select only the specified columns
  df = df[["Firework Name", "Effect Duration", "Effect Time"]]
  
  # Rename the columns
  df.rename(columns={
    "Firework Name": "firework_name", 
    "Effect Duration": "duration",
    "Effect Time": "start_time"}, 
    inplace=True)
  
  # Convert columns to datetime
  df['duration'] = pd.to_timedelta(pd.to_numeric(pd.to_datetime(df['duration'], format='%M:%S').dt.strftime("%S"), errors='coerce').fillna(0), unit='s')
  df['start_time'] = pd.to_datetime(df['start_time'], format='%M:%S')#.dt.strftime("%M:%S")
  df['end_time'] = df['start_time'] + df['duration']

  return df

def main(): 
    # Initialization
    if 'fireworks_df' not in st.session_state:
        st.session_state['fireworks_df'] = import_fireworks_data()

    st.header("Richard's Fireworks Timeline!")
    
    st.session_state['fireworks_df'] =st.data_editor(st.session_state['fireworks_df'], 
                #    column_config=column_config,
                   key="updated_df",
                   num_rows="dynamic")
    
    chart = alt.Chart(st.session_state['fireworks_df']).mark_bar().encode(
        x='start_time',
        x2='end_time',
        y='firework_name',
    )
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


    st.write(st.session_state)


if __name__ == "__main__":
    main()