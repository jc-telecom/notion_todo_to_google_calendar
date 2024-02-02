from tools.utils import property_value_from_path
from scripts.notion_API import GetNotionInfo
from dateutil.parser import parse
from datetime import datetime, timedelta, date
import json


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


def create_date_field(db_entry_properties, properties_scheme):
    date_properties = {key: value for key,
                       value in properties_scheme.items() if value.col_type == "date"}
    date_properties = date_properties.get(
        list(date_properties.keys())[0], None)
    date = property_value_from_path(
        db_entry_properties, date_properties.path)
    date_start = date.get("start")
    date_end = date.get("end")
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


def create_field(print_to, db_entry_properties, properties_scheme, fields_formats):
    field_properties = {key: value for key, value in properties_scheme.items(
    ) if value.print_to == print_to}
    field_properties = dict(
        sorted(field_properties.items(), key=lambda item: item[1].order))

    # Format the field
    field_format = fields_formats[print_to]
    prefix = getattr(field_format, "prefix", "")
    suffix = getattr(field_format, "suffix", "")
    inner_separator = getattr(field_format, "inner_separator", " ")
    # Retrieve the information for each property that is part of the field
    fields_text = []
    for field_property in field_properties.values():
        if field_property.print_to == print_to and field_property.name in db_entry_properties.keys():
            values = property_value_from_path(
                db_entry_properties, field_property.path, field_property.inner_separator)
            if isinstance(values, list):
                for idx, value in enumerate(values):
                    if field_property.method is not None and getattr(GetNotionInfo(), field_property.method, None):
                        method = getattr(
                            GetNotionInfo(), field_property.method)
                        method_value = method(value)
                        value = method_value if method_value is not None else value
                    if field_property.character_limit is not None:
                        value = value[:field_property.character_limit]
                    values[idx] = value
                values = field_property.inner_separator.join(values)
            value = str(values)
            if not value:
                continue
            title = (
                field_property.title_prefix
                + field_property.title
                + field_property.title_suffix
                if field_property.show_title
                else ""
            )
            fields_text.append(field_property.prefix +
                               title + value + field_property.suffix)

    field_content = prefix
    field_content += inner_separator.join(list(fields_text))
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
        self.colorId = colorId

    def db_entry_to_google_event(self, DbEntry, properties_scheme, fields_formats):
        properties = DbEntry.properties
        event_id = DbEntry.id.replace("-", "")
        # Create summary
        summary = create_field(
            "summary", properties, properties_scheme, fields_formats)

        # Create description
        description = create_field(
            "description", properties, properties_scheme, fields_formats)

        # Create date
        date_start, date_end, full_day = create_date_field(
            properties, properties_scheme)
        return CalendarEvent(event_id=event_id,
                             summary=summary,
                             start=date_start,
                             end=date_end,
                             description=description,
                             full_day=full_day,
                             )

    def db_entries_to_google_events(self, db_entries, properties_scheme, fields_formats):
        google_events = {}
        for key, db_entry in db_entries.items():
            event_id = key.replace("-", "")
            google_events[event_id] = self.db_entry_to_google_event(self,
                                                                    db_entry, properties_scheme, fields_formats)
        return google_events
