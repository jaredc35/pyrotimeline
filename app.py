import streamlit as st
import altair as alt
import dataHandler as dh
import components as co

_ = """
The purpose of this app is to allow someone
to import a CSV file of firework data or 
manually import a firework's name, duration, and start
time, then provide a visual representation of the fireworks
show.

Created by Jared Conway
7/10/24
"""


column_config = {
    "_id": st.column_config.TextColumn(
        "ID", help="The ID of the firework", max_chars=100
    ),
    "firework_name": st.column_config.TextColumn(
        "Firework Name", help="The name of the firework", max_chars=100
    ),
    "type": st.column_config.TextColumn(
        "Type", help="The type of the firework", max_chars=100
    ),
    "duration": st.column_config.NumberColumn(
        "Duration",
        help="The duration of the firework in seconds",
        min_value=0,
        max_value=150,
    ),
    "display_start_time": st.column_config.TextColumn(
        "Start Time",
        help="The start time of the firework in MM:SS format",
    ),
    "display_end_time": st.column_config.TextColumn(
        "End Time",
        help="The end time of the firework in MM:SS format",
    ),
}


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
    if "user_input_firework" not in st.session_state:
        st.session_state["user_input_firework"] = dh.blank_firework
    if "firework_to_edit" not in st.session_state:
        st.session_state["firework_to_edit"] = None

    st.header("Richard's Fireworks Timeline!")

    with st.expander("Fireworks Data"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["firework_action"] = st.selectbox(
                "Select an action",
                [
                    "Add New Firework",
                    "Edit Firework",
                    "Remove Firework",
                    "Clear Fireworks",
                    "Import Firework Data",
                ],
            )

        with col2:

            # Edit an existing firework
            if st.session_state["firework_action"] == "Edit Firework":
                st.session_state["firework_to_edit"] = st.selectbox(
                    "Select a firework",
                    st.session_state["fireworks_df"]["firework_name"],
                    index=None,
                )
                if st.session_state["firework_to_edit"]:
                    old_firework = dh.get_firework_by_name(
                        st.session_state["firework_to_edit"]
                    )
                    new_name = st.text_input(
                        "Firework Name",
                        old_firework["firework_name"][0],
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
                        on_click=lambda: dh.update_firework(
                            old_firework["_id"][0],
                            new_name,
                            new_type,
                            new_duration,
                            new_start_time,
                        ),
                    )

            # Add a new firework
            if st.session_state["firework_action"] == "Add New Firework":
                st.session_state["user_input_firework"]["name"] = st.text_input(
                    "Firework Name"
                )
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
                    on_click=lambda: dh.add_firework(
                        st.session_state["user_input_firework"]["name"],
                        type,
                        duration,
                        start_time,
                    ),
                )

            # Delete a firework
            if st.session_state["firework_action"] == "Remove Firework":
                firework_to_delete = st.selectbox(
                    "Select a firework",
                    st.session_state["fireworks_df"]["firework_name"],
                )
                st.button(
                    "Remove Firework",
                    on_click=lambda: dh.delete_firework(firework_to_delete),
                )

            if st.session_state["firework_action"] == "Clear Fireworks":
                st.button("Delete all Fireworks?", on_click=lambda: dh.delete_items({}))

            if st.session_state["firework_action"] == "Import Firework Data":
                st.button(
                    "Import all fireworks from original CSV?",
                    on_click=lambda: dh.import_fireworks_data_from_csv(),
                )

    def assign_firework(event):
        st.session_state["firework_action"] = "edit_firework"
        st.session_state["firework_to_edit"] = event.data["firework_name"]

    chart = (
        alt.Chart(
            st.session_state["fireworks_df"],
        )
        .mark_bar(cornerRadius=3, height=10)
        .encode(
            x=alt.X("start_time", title="Start Time"),
            x2=alt.X2("end_time", title="End Time"),
            y=alt.Y("firework_name", title="Firework Name").sort("x"),
            color=alt.Color("type", title="Type of Firework"),
        )
    )
    st.altair_chart(
        chart,
        theme="streamlit",
        # on_select=lambda event: assign_firework(event),
        use_container_width=True,
    )

    with st.container():
        st.dataframe(
            st.session_state["fireworks_df"],
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            column_order=[
                "firework_name",
                "type",
                "duration",
                "display_start_time",
                "display_end_time",
            ],
        )


if __name__ == "__main__":
    main()
