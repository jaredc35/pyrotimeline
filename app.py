import streamlit as st
import altair as alt
import dataHandler as dh

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
        "Firework Name", help="The name of the firework", max_chars=100
    ),
    "duration": st.column_config.NumberColumn(
        "Duration",
        help="The duration of the firework in seconds",
        min_value=0,
        max_value=150,
    ),
    "start_time": st.column_config.NumberColumn(
        "Start Time",
        min_value=0,
        max_value=1440,
    ),
    "end_time": st.column_config.NumberColumn(
        "End Time",
        min_value=0,
        max_value=1440,
    ),
}


def add_new_firework(name, type, duration, display_start_time):
    """
    Add a new firework to the firework session state
    """
    dh.add_firework(
        {
            "firework_name": name,
            "type": type,
            "duration": duration,
            "display_start_time": display_start_time,
            "start_time": dh.convert_to_seconds(display_start_time),
            "end_time": dh.convert_to_seconds(display_start_time) + duration,
            "display_end_time": dh.convert_to_display_time(
                dh.convert_to_seconds(display_start_time) + duration
            ),
        }
    )
    st.session_state["fireworks_df"] = dh.get_fireworks_df()


def update_firework(id, name, type, duration, display_start_time):
    """
    Update a firework in the firework session state
    """
    dh.update_firework(id, name, type, duration, display_start_time)
    st.session_state["fireworks_df"] = dh.get_fireworks_df()


def remove_firework(id):
    """
    Delete a firework from the database and update session state
    """
    dh.delete_firework(id)
    st.session_state["fireworks_df"] = dh.get_fireworks_df()


def main():
    # Initialization
    st.set_page_config(
        page_title="Fireworks Show", page_icon=":fireworks:", layout="wide"
    )
    if "fireworks_df" not in st.session_state:
        st.session_state["fireworks_df"] = dh.get_fireworks_df()
    if "firework_action" not in st.session_state:
        st.session_state["firework_action"] = "Add New Firework"
    if "firework_types" not in st.session_state:
        st.session_state["firework_types"] = [
            "Rocket",
            "Cake",
            "Shells",
            "Sequencer",
            "Fireball",
            "Fountains",
        ]

    st.header("Richard's Fireworks Timeline!")

    with st.expander("Fireworks Data"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["firework_action"] = st.selectbox(
                "Select an action",
                [
                    "Edit Firework",
                    "Add New Firework",
                    "Remove Firework",
                    "Clear Fireworks",
                ],
            )

        with col2:
            if st.session_state["firework_action"] == "Edit Firework":
                firework_to_edit = st.selectbox(
                    "Select a firework",
                    st.session_state["fireworks_df"]["firework_name"],
                )
                old_firework = dh.get_firework_by_name(firework_to_edit)
                new_name = st.text_input(
                    "Firework Name", old_firework["firework_name"][0]
                )
                new_type = st.selectbox(
                    "Type",
                    st.session_state["firework_types"],
                    index=st.session_state["firework_types"].index(
                        old_firework["type"][0]
                    ),
                )
                new_duration = st.number_input(
                    "Duration (in seconds)",
                    min_value=0,
                    max_value=150,
                    value=old_firework["duration"][0],
                )
                new_start_time = st.text_input(
                    "Start Time",
                    placeholder="Please enter a time in MM:SS format",
                    value=old_firework["display_start_time"][0],
                )
                st.button(
                    "Update Firework",
                    on_click=lambda: update_firework(
                        old_firework["_id"][0],
                        new_name,
                        new_type,
                        new_duration,
                        new_start_time,
                    ),
                )

            if st.session_state["firework_action"] == "Add New Firework":
                new_name = st.text_input("Firework Name")
                type = st.selectbox(
                    "Type",
                    ["Rocket", "Cake", "Shells", "Sequencer", "Fireball", "Fountains"],
                )
                duration = st.number_input(
                    "Duration (in seconds)", min_value=0, max_value=150
                )
                start_time = st.text_input(
                    "Start Time", placeholder="Please enter a time in MM:SS format"
                )
                st.button(
                    "Add New Firework",
                    on_click=lambda: add_new_firework(
                        new_name, type, duration, start_time
                    ),
                )

            if st.session_state["firework_action"] == "Remove Firework":
                firework_to_delete = st.selectbox(
                    "Select a firework",
                    st.session_state["fireworks_df"]["firework_name"],
                )
                st.button(
                    "Remove Firework",
                    on_click=lambda: remove_firework(
                        dh.get_firework_by_name(firework_to_delete)["_id"][0]
                    ),
                )

            if st.session_state["firework_action"] == "Clear Fireworks":
                st.button("Clear Fireworks")

    with st.container():
        st.dataframe(
            st.session_state["fireworks_df"],
            use_container_width=True,
            column_order=[
                "firework_name",
                "type",
                "duration",
                "display_start_time",
                "display_end_time",
            ],
        )

    chart = (
        alt.Chart(st.session_state["fireworks_df"])
        .mark_bar()
        .encode(
            x="start_time",
            x2="end_time",
            y="firework_name",
        )
        .interactive()
    )
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


if __name__ == "__main__":
    main()
