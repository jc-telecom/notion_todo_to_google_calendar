from notion import notion_db_entries_to_event_df
from calendar_api import delete_event, get_events, add_event, update_event
from utils import paris_tz

import pandas as pd
from datetime import datetime, timedelta, timezone
import json
import os


update_threshold = 5  # days
update_start_date = (datetime.now(paris_tz) -
                     timedelta(days=update_threshold)).isoformat()


def update_meta_file():
    # update the meta file
    if os.path.exists('meta.json') and os.path.getsize('meta.json') > 0:
        with open('meta.json', 'r') as f:
            metacontent = json.load(f)
    else:
        metacontent = {}
    metacontent[datetime.now(paris_tz).isoformat()] = {
        "last_updated_time": datetime.now(paris_tz).isoformat(),
        "new_events": df_new_events.shape[0] if df_prev_events is not None else df_events.shape[0],
        "updated_events": df_updated_events.shape[0] if df_prev_events is not None else df_events.shape[0],
        "deleted_events": df_deleted_events.shape[0] if df_prev_events is not None else 0}
    with open("meta.json", "w") as meta:
        json.dump(metacontent, meta)


# Get all the dataframe with the events information
df_events = notion_db_entries_to_event_df()

# Keep only the events that have a date and a summary
df_events = df_events[(df_events["start_date"] != "") & (
    df_events["end_date"] != "") & (df_events["summary"] != "")]

# Keep only the events with edited time higher that date threshold
df_events = df_events[df_events["start_date"] > update_start_date]


# Get all the events from two the threshold date
df_prev_events = get_events(update_start_date)

# New : create the event
if df_prev_events is not None:
    df_new_events = df_events[~df_events["id"].isin(df_prev_events["id"])]
else:
    df_new_events = df_events
for index, row in df_new_events.iterrows():
    add_event(row["id"], row["summary"], row["start_date"],
              row["end_date"], description=row["description"])


# Update get the event and update it
if df_prev_events is not None:
    df_merged = pd.merge(df_events, df_prev_events, on='id',
                         suffixes=('_current', '_prev'))
    df_updated_events = df_merged[
        (df_merged['summary_current'] != df_merged['summary_prev']) |
        (df_merged['start_date_current'] != df_merged['start_date_prev']) |
        (df_merged['end_date_current'] != df_merged['end_date_prev']) |
        (df_merged['description_current'] != df_merged['description_prev'])
    ]
    for index, row in df_updated_events.iterrows():
        update_event(row["id"], row["summary_current"], row["start_date_current"],
                     row["end_date_current"], description=row["description_current"])

    # Delete the event
    df_deleted_events = df_prev_events[~df_prev_events["id"].isin(
        df_events["id"])]
    for index, row in df_deleted_events.iterrows():
        delete_event(row["id"])


update_meta_file()
