from scripts.google_event import CalendarEvent
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import sys


def get_token():

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

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


class CalendarAPI:
    def __init__(self, calendar_id):
        self.creds = get_token()
        self.service = build("calendar", "v3", credentials=self.creds)
        self.calendar_id = calendar_id

    def event_class_to_json(self):
        event_json = {
            "id": self.id,
            "summary": self.summary,
            "description": self.description,
            "colorId": self.colorId,
        }
        date_start, date_end = self.date_start.date, self.date_end.date
        if self.full_day:
            event_json_dates = {
                "start": {
                    "date": date_start,
                    "timeZone": "Europe/Paris",
                },
                "end": {
                    "date": date_end,
                    "timeZone": "Europe/Paris",
                }}
        else:
            event_json_dates = {
                "start": {
                    "dateTime": date_start,
                    "timeZone": "Europe/Paris",
                },
                "end": {
                    "dateTime": date_end,
                    "timeZone": "Europe/Paris",
                }, }
        event_json |= event_json_dates
        return event_json

    def add_event(self, event_json):
        try:
            event = self.service.events().insert(calendarId=self.calendar_id,
                                                 body=event_json).execute()
        except HttpError as error:
            self._extracted_from_send_event_6(error, event_json)

    def delete_event(self, event_id):
        try:
            event = self.service.events().delete(calendarId=self.calendar_id,
                                                 eventId=event_id).execute()
        except HttpError as error:
            print("An error occurred: ", error)

    def update_event(self, event_json):
        try:
            event = self.service.events().update(calendarId=self.calendar_id, eventId=event_json.get('id'),
                                                 body=event_json).execute()
        except HttpError as error:
            print("An error occurred: ", error)

    def send_event(self, calendar_event_dic, method):
        if calendar_event_dic is None:
            return None
        if method not in ["add", "delete", "update"]:
            raise ValueError(
                "-> Error: The method must be either 'add', 'delete' or 'update'"
            )
        events_json = [CalendarAPI.event_class_to_json(event)
                       for key, event in calendar_event_dic.items()]

        for event_json in events_json:
            try:
                if method == "add":
                    self.add_event(event_json)
                elif method == "update":
                    self.update_event(event_json)
                elif method == "delete":
                    self.delete_event(event_json.get("id"))
            except HttpError as error:
                self._extracted_from_send_event_6(error, calendar_event_dic)

    # TODO Rename this here and in `add_event` and `send_event`
    def _extracted_from_send_event_6(self, error, arg1):
        print("An error occurred: ", error)
        print(arg1)
        sys.exit()

    def get_event(self, event_id):
        try:
            return (
                self.service.events()
                .get(calendarId=self.calendar_id, eventId=event_id)
                .execute()
            )
        except HttpError as error:
            print("An error occurred: ", error)

    def get_events(self, start_date):
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
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
            return {
                event["id"]: CalendarEvent(
                    event_id=event["id"],
                    summary=event["summary"],
                    start=event["start"].get(
                        "dateTime", event["start"].get("date")),
                    end=event["end"].get("dateTime", event["end"].get("date")),
                    description=event["description"],
                    colorId=event.get("colorId"),
                )
                for event in events
            }
        except HttpError as error:
            print(f"An error occurred: {error}")
