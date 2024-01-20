from scripts.notion_entry_properties_scheme import get_properties_from_db_entry
from dateutil.parser import parse
from datetime import datetime, timedelta, date
import json


class EventDate:
    def __init__(self, date, timeZone="Europe/Paris"):
        self.date = date
        self.time_zone = timeZone


class CalendarEvent:
    def __init__(self, event_id, summary, start, end, timeZone="Europe/Paris", location=None, description=None, full_day=False, colorId=None):
        self.id = event_id
        self.summary = summary
        self.date_start = EventDate(start)
        self.date_end = EventDate(end)
        self.location = location
        self.description = description
        self.full_day = full_day
        self.colorId = int(colorId)


def format_date(date_start, date_end):
    full_day = False
    if date_start == "":
        return None
    date_start = parse(date_start)
    if date_end == "" or date_end is None:
        if date_start.hour == 0 and date_start.minute == 0:
            date_end = date_start + timedelta(days=1)
            date_end = date_end.date()
            date_start = date_start.date()
            full_day = True
        else:
            date_end = date_start + timedelta(minutes=30)
    else:
        date_end = parse(date_end)
    return date_start.isoformat(), date_end.isoformat(), full_day


def create_field(field, db_entry_properties, properties_scheme, fields_formats):
    field_properties = {key: value for key, value in properties_scheme.items(
    ) if value.information_type == field}
    field_properties = dict(
        sorted(field_properties.items(), key=lambda item: item[1].order))

    field_format = fields_formats.get(field)
    prefix = getattr(field_format, "prefix", "")
    suffix = getattr(field_format, "suffix", "")
    inner_separators = getattr(field_format, "inner_separators", " ")
    field_content = prefix
    field_content += inner_separators.join(
        [db_entry_properties.get(key) for key in field_properties]
    )
    field_content += suffix
    return field_content


def db_entries_to_google_events(db_entries, properties_scheme, fields_formats):
    google_events_dict = {}

    for key, db_entry in db_entries.items():
        db_entry_properties = get_properties_from_db_entry(
            db_entry, properties_scheme)
        # We remove "-" from the notion ID since it is not allowed in google calendar
        event_id = key.replace("-", "")
        summary = create_field(
            "summary", db_entry_properties, properties_scheme, fields_formats)
        description = create_field(
            "description", db_entry_properties, properties_scheme, fields_formats)

        with open('project_settings.json', 'r') as f:
            status_colors = json.load(f).get("status.colors")
        if status_colors is not None:
            colorId = status_colors.get(
                db_entry_properties.get("status"), None)
        else:
            colorId = None

        try:
            date_start, date_end, full_day = format_date(
                db_entry_properties.get("date_start"), db_entry_properties.get("date_end"),)
        except TypeError:
            continue
        google_events_dict[event_id] = CalendarEvent(
            event_id=event_id, summary=summary, start=date_start, end=date_end, description=description, full_day=full_day, colorId=colorId)

    return google_events_dict
