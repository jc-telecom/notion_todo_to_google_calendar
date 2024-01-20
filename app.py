from scripts.notification import show_notification
from tools.utils import update_meta_file
from scripts.project_setup import retrieve_starting_date
from scripts.notion_API_entries import get_notion_entries
from scripts.notion_entry_properties_scheme import retrieve_property_scheme, retrieve_field_format
from scripts.google_event import db_entries_to_google_events
from scripts.google_calendar_API import CalendarAPI
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


# Retrieve the starting date
starting_date = retrieve_starting_date()

# Retrieve the properties scheme
properties_scheme = retrieve_property_scheme()

# Retrieve the events fields formats
fields_formats = retrieve_field_format()

# Retrieve the notion database entries
filters = {
    "property": "Date",
    "date": {
        "after": starting_date
    }}
notion_db_entries = get_notion_entries(
    os.environ['DATABASE_ID'], filters=filters)

# Convert db entries to google events
events = db_entries_to_google_events(
    notion_db_entries, properties_scheme, fields_formats)

# Connect to google calendar API
google_calendar = CalendarAPI(os.environ['GOOGLE_CALENDAR_ID'])

# Retrieve existing events from google calendar
google_past_events_dict = CalendarAPI.get_events(
    google_calendar, starting_date)


# Modify the google calendar events
if google_past_events_dict is None:
    new_events = events
    delete_events = None
    update_events = None
else:
    # Identify new events
    new_events = {key: value for key, value in events.items(
    ) if key not in google_past_events_dict.keys()}

    # Identify events to be deleted
    delete_events = {key: value for key, value in google_past_events_dict.items(
    ) if key not in events.keys()}

    # Identify events to be updated
    update_events = {}
    for key, event in events.items():
        if key in google_past_events_dict:
            prev_event = google_past_events_dict[key]
            if event.summary != prev_event.summary or event.description != prev_event.description or event.colorId != prev_event.colorId or event.date_start.date != prev_event.date_start.date or event.date_end.date != prev_event.date_end.date:
                update_events[key] = event

nb_new_events = len(new_events) if new_events is not None else 0
nb_updated_events = len(update_events) if update_events is not None else 0
nb_deleted_events = len(delete_events) if delete_events is not None else 0

# Add, delete and update events
CalendarAPI.send_event(google_calendar, new_events, "add")
print(f"{nb_new_events} new events added")
CalendarAPI.send_event(google_calendar, delete_events, "delete")
print(f"{nb_deleted_events} events deleted")
CalendarAPI.send_event(google_calendar, update_events, "update")
print(f"{nb_updated_events} events updated")

# Append the results to a JSON file
update_meta_file(nb_new_events, nb_updated_events, nb_deleted_events)


# Send a notification
show_notification(nb_new_events, nb_updated_events, nb_deleted_events)
