from datetime import datetime, timedelta, timezone
import pytz
import os
import json
import traceback


def property_value_from_path(dict_obj, path, in_separator=" "):
    if not isinstance(path, list):
        path = [path]
    try:
        value = dict_obj
        for index, p in enumerate(path):
            if value is None:
                value = ""
            elif isinstance(value, list):
                value = [property_value_from_path(
                    v, path[index:]) for v in value]
            else:
                value = value.get(p)
        return value
    except Exception as error:
        traceback.print_exc()
        print(f"-> Dict: {dict_obj}")
        print(f"-> Path: {path}")
        return ""


def add_time(start_date, added_min=30):
    return start_date + timedelta(minutes=added_min)


def update_meta_file(nb_events_added, nb_updated_events, nb_deleted_events):
    if os.path.exists('meta.json') and os.path.getsize('meta.json') > 0:
        with open('meta.json', 'r') as f:
            metacontent = json.load(f)
    else:
        metacontent = {}
    metacontent[datetime.now(pytz.timezone(
        'Europe/Paris')).isoformat()] = {
        "new_events": nb_events_added,
        "updated_events": nb_updated_events,
        "deleted_events": nb_deleted_events}
    with open("meta.json", "w") as meta:
        json.dump(metacontent, meta)
