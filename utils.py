from datetime import datetime, timedelta, timezone
import pytz

notion_date_formats = ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d"]
paris_tz = pytz.timezone('Europe/Paris')


def add_time(start_date, added_min=30):
    return start_date + timedelta(minutes=added_min)


def convert_notion_date_to_iso(date_str):
    for date_format in notion_date_formats:
        try:
            date = datetime.strptime(date_str, date_format)
            return add_time_zone(date)
        except:
            pass
    return ""


def add_time_zone(date):
    return date.replace(tzinfo=timezone(timedelta(hours=1))).isoformat()


def avoid_none(row, path):
    try:
        for p in path:
            row = row[p]
        if row is None:
            return ""
        else:
            return row

    except:
        return ""
# print("yeajfr")
