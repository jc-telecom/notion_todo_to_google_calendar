import pandas as pd
from datetime import datetime, timedelta
import os.path
from utils import paris_tz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_token():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "google_credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def create_event_dict(event_id, summary, start, end, location=None, description=None):
    event = {
        "id": event_id,
        "summary": summary,
        "location": location,
        "description": description}
    start_dateTime = datetime.fromisoformat(start)
    end_dateTime = datetime.fromisoformat(end)
    if start_dateTime.hour == 0 and start_dateTime.minute == 0 and end_dateTime.hour == 0 and end_dateTime.minute == 0:
        start_date = start_dateTime.date().isoformat()
        end_date = end_dateTime.date().isoformat()
        event_dates = {
            "start": {
                "date": start_date,
                "timeZone": "Europe/Paris",
            },
            "end": {
                "date": end_date,
                "timeZone": "Europe/Paris",
            }}
    else:
        event_dates = {
            "start": {
                "dateTime": start,
                "timeZone": "Europe/Paris",
            },
            "end": {
                "dateTime": end,
                "timeZone": "Europe/Paris",
            }, }

    event.update(event_dates)
    return event


def add_event(event_id, summary, start, end, location=None, description=None):
    creds = get_token()
    try:
        service = build("calendar", "v3", credentials=creds)
        event = create_event_dict(
            event_id, summary, start, end, location, description)
        event = service.events().insert(
            calendarId=os.environ['NOTION_CALENDAR_ID'], body=event).execute()

    except HttpError as error:
        print("An error occurred: ", error)


def delete_event(event_id):
    creds = get_token()
    try:
        service = build("calendar", "v3", credentials=creds)
        service.events().delete(
            calendarId=os.environ['NOTION_CALENDAR_ID'], eventId=event_id).execute()
    except HttpError as error:
        print("An error occurred: ", error)


def update_event(event_id, summary, start, end, location=None, description=None):
    creds = get_token()
    try:
        service = build("calendar", "v3", credentials=creds)
        event = create_event_dict(
            event_id, summary, start, end, location, description)
        event = service.events().update(
            calendarId=os.environ['NOTION_CALENDAR_ID'], eventId=event_id,  body=event).execute()
    except HttpError as error:
        print("An error occurred: ", error)


def get_events(start_date):
    creds = get_token()
    try:
        service = build("calendar", "v3", credentials=creds)
        # now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        # Call the Calendar API
        events_result = (
            service.events()
            .list(
                calendarId=os.environ['NOTION_CALENDAR_ID'],
                timeMin=start_date,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        df = pd.DataFrame()
        for event in events:
            idx = df.shape[0]
            df.loc[idx, "id"] = event["id"]
            df.loc[idx, "start_date"] = event["start"].get(
                "dateTime", event["start"].get("date"))
            df.loc[idx, "end_date"] = event["end"].get(
                "dateTime", event["end"].get("date"))
            df.loc[idx, "summary"] = event["summary"]
            df.loc[idx, "location"] = event["location"] if "location" in event else ""
            df.loc[idx, "description"] = event["description"] if "description" in event else ""
        return df
    except HttpError as error:
        print(f"An error occurred: {error}")
