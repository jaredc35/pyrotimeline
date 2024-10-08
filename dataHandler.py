import pymongo
import pandas as pd
import streamlit as st

MONGODB_KEY = st.secrets["MONGODB_KEY"]

myclient = pymongo.MongoClient(
    "mongodb+srv://admin-jared:"
    + MONGODB_KEY
    + "@cluster0-42f7w.mongodb.net/test?retryWrites=true&w=majority"
)
pyroDB = myclient["PyroTimeline"]
fireworkCollection = pyroDB["fireworkCollection"]

blank_firework = {
    "name": "",
    "type": "Rocket",
    "duration": 0,
    "display_start_time": "",
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
    if sec < 10:
        sec = "0" + str(sec)
    return f"{min}:{sec}"


def import_fireworks_data_from_csv():
    df = pd.read_csv("show_planner_2024.csv")

    # Select only the specified columns
    df = df[["Firework Name", "Type", "Effect Duration", "Effect Time"]]

    # Rename the columns
    df.rename(
        columns={
            "Firework Name": "firework_name",
            "Effect Duration": "duration",
            "Type": "type",
            "Effect Time": "start_time",
        },
        inplace=True,
    )

    df.dropna(inplace=True)

    # Convert columns to usable time
    df["duration"] = pd.to_numeric(
        pd.to_datetime(df["duration"], format="%M:%S").dt.strftime("%S"),
        errors="coerce",
    ).fillna(0)
    df["display_start_time"] = pd.to_datetime(
        df["start_time"], format="%M:%S"
    ).dt.strftime("%M:%S")
    df["start_time"] = df["display_start_time"].apply(convert_to_seconds)
    df["end_time"] = df["start_time"] + df["duration"]
    df["display_end_time"] = df["end_time"].apply(convert_to_display_time)
    import_fireworks_data_to_mongo(df)
    return get_fireworks_df()


def import_fireworks_data_to_mongo(fireworks_df):
    result = fireworkCollection.insert_many(fireworks_df.to_dict("records"))
    print(len(result.inserted_ids), " records inserted.")


def delete_items(query, printResult=True):
    """
    Deletes all items that match the query
    query: dictionary object (example: {"type":"Rocket"} or "{}" to delete all records)
    """
    result = fireworkCollection.delete_many(query)
    if printResult:
        print(result.deleted_count, " records deleted.")
    return result


def add_firework(name, type, duration, display_start_time):
    """
    Adds a firework to the firework collection
    """
    firework_dict = {
        "firework_name": name,
        "type": type,
        "duration": duration,
        "display_start_time": display_start_time,
        "start_time": convert_to_seconds(display_start_time),
        "end_time": convert_to_seconds(display_start_time) + duration,
        "display_end_time": convert_to_display_time(
            convert_to_seconds(display_start_time) + duration
        ),
    }
    result = fireworkCollection.insert_one(firework_dict)
    st.session_state["fireworks_df"] = get_fireworks_df()
    st.session_state["user_input_firework"] = blank_firework
    return result


def delete_firework(firework_name):
    """
    Deletes a firework based on the id
    """
    id = get_firework_by_name(firework_name)["_id"][0]
    result = fireworkCollection.delete_one({"_id": id})
    st.session_state["fireworks_df"] = get_fireworks_df()
    return result.deleted_count


def get_fireworks_df():
    """
    Used to get fireworks collection into a pandas dataframe
    """
    cursor = fireworkCollection.find({})
    df = pd.DataFrame(list(cursor))
    if df.empty:
        return pd.DataFrame()
    df = df.astype({"_id": "string"})
    df = df.sort_values(by="start_time")
    return df


def get_firework_by_name(name):
    """
    Used to get a firework by its name
    """
    query = {"firework_name": name}
    cursor = fireworkCollection.find(query)
    df = pd.DataFrame(list(cursor))
    return df


def update_firework(id, name, type, duration, display_start_time):
    """
    Used to update a firework
    """
    query = {"_id": id}
    new_values = {
        "$set": {
            "firework_name": name,
            "type": type,
            "duration": duration,
            "display_start_time": display_start_time,
            "start_time": convert_to_seconds(display_start_time),
            "end_time": convert_to_seconds(display_start_time) + duration,
            "display_end_time": convert_to_display_time(
                convert_to_seconds(display_start_time) + duration
            ),
        }
    }
    result = fireworkCollection.update_one(query, new_values)
    st.session_state["fireworks_df"] = get_fireworks_df()
    st.session_state["firework_to_edit"] = None
    return result


def findItems(query, printHead=True):
    """
    Use to find/return/print everything that matches a certain query
    query [Dict (JSON-type)]: What we want to filter based on
    Ex: { "UpdateDate": {"$gte" : dt.datetime(2020, 1, 1), "$lt": dt.datetime(2020, 7, 1)}}
    --> Finds all items that were updated between January 1st 2020 and
        July 1st 2020
    """
    cursor = fireworkCollection.find(query)
    df = pd.DataFrame(list(cursor))
    print(df.head())
    print(df.describe())
    print(df.info())
    return df


if __name__ == "__main__":
    firework_df = import_fireworks_data_from_csv()
    import_fireworks_data_to_mongo(firework_df)
    # delete_items({})
