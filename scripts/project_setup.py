import json
from datetime import datetime, timedelta, timezone
import pytz


def retrieve_starting_date(file_path="project_settings.json"):
    with open(file_path, 'r') as file:
        settings = json.load(file)
    day_rev_limit = settings.get("day_rev_limit", 5)
    if not isinstance(day_rev_limit, int):
        raise ValueError(
            "-> Error: The day_rev_limit property in the project_settings.json most be an integer"
        )

    starting_date = datetime.now(pytz.timezone(
        'Europe/Paris')) - timedelta(days=day_rev_limit)
    return starting_date.isoformat()
