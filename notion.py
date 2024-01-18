from utils import avoid_none, add_time, convert_notion_date_to_iso, add_time_zone
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()


headers = {
    "Authorization": "Bearer " + os.environ['NOTION_TOKEN'],
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_page_name(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}/properties/title"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def get_pages(DATABASE_ID, num_pages=None):

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    results = data["results"]
    while data["has_more"]:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
    df = pd.DataFrame(results)
    return df


def get_parent_name(df, properties):
    parents_id = [parent["id"]
                  for parent in properties["Sous-élément"]["relation"]]
    parents_name = ""
    for parent_id in parents_id:
        parents_name += " ".join([parent_row["plain_text"]
                                 for parent_row in df.loc[df['id'] == parent_id, "properties"].iloc[0]["Nom"]["title"]])
    return parents_name


def get_end_date(df, row, start_date):
    if start_date == "":
        return ""
    else:
        if avoid_none(row, ["properties", "Date", "date", "end"]) == "":
            start_date = datetime.fromisoformat(start_date)
            if start_date.hour == 0 and start_date.minute == 0:
                return add_time_zone(add_time(start_date, 24*60))
            else:
                return add_time_zone(add_time(start_date, 30))
        else:
            return convert_notion_date_to_iso(avoid_none(row, ["properties", "Date", "date", "end"]))


def properties_to_df(df):
    df_event = pd.DataFrame()

    df_event["id"] = df["id"]
    df_event["last_edited_time"] = df["last_edited_time"].apply(
        lambda x: convert_notion_date_to_iso(x))
    df_event["last_edited_time"] = pd.to_datetime(
        df_event["last_edited_time"], format="ISO8601")

    # Get the name
    df_event["name"] = df.apply(lambda row: " ".join(
        [name_item["plain_text"] for name_item in row["properties"]["Nom"]["title"]]), axis=1)

    # Get the task's importance
    df_event["importance"] = df.apply(lambda row: avoid_none(
        row, ["properties", "Importance", "select", "name"]), axis=1)

    # Get the task's notes
    df_event["notes"] = df.apply(lambda row: " ".join(
        [note_item["plain_text"] for note_item in row["properties"]["Notes"]["rich_text"]]), axis=1)

    # Get dates
    df_event["start_date"] = df.apply(lambda row: convert_notion_date_to_iso(avoid_none(
        row, ["properties", "Date", "date", "start"])), axis=1)
    for index, row in df.iterrows():
        df_event.loc[index, "end_date"] = get_end_date(
            df, row, df_event.loc[index, "start_date"])
    # df_event["start_date"] = pd.to_datetime(df_event["start_date"])
    # df_event["end_date"] = pd.to_datetime(df_event["end_date"])

    # Get the task's project
    df_event["project"] = df.apply(lambda row: " ".join(
        [project_item["name"] for project_item in row["properties"]["Projet"]["multi_select"]]), axis=1)

    # Get parent_element
    df_event["parents_name"] = df.apply(
        lambda row: get_parent_name(df, row["properties"]), axis=1)
    return df_event


def create_description(row):
    description = ""
    if row["importance"] != "":
        description += f"Importance: {row['importance']}\n\n"
    if row["project"] != "":
        description += f"Project: {row['project']}\n\n"
    if row["notes"] != "":
        description += f"Notes: {row['notes']}\n\n"

    return description


def create_summary(row):
    summary = ""
    if row["project"] != "":
        summary += f"[{row['project'][0]}] "
    if row["parents_name"] != "":
        summary += f"{row['parents_name']} - "
    if row["name"] != "":
        summary += row['name']
    return summary


def notion_df_to_event_df(df):
    df["summary"] = df.apply(
        lambda row: create_summary(row), axis=1)
    df["description"] = df.apply(
        lambda row: create_description(row), axis=1)
    df["id"] = df["id"].apply(lambda x: x.replace("-", ""))
    df.drop(columns=["name", "importance",
            "project", "parents_name", "notes"], inplace=True)
    return df


def notion_db_entries_to_event_df():
    df = get_pages(os.environ['DATABASE_ID'])
    df_events = properties_to_df(df)
    df_events = notion_df_to_event_df(df_events)
    return df_events


# if __name__ == "__main__":
#     df = get_notion_db_entries()
#     print(df)
