import os
import requests
from dotenv import load_dotenv
load_dotenv()


# Declare the default database entry we shoud receive from notion API
class DbEntry:
    def __init__(self, id, created_time, last_edited_time, properties, url, created_by=None, last_edited_by=None):
        self.id = id
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.properties = properties
        self.url = url
        self.created_by = created_by
        self.last_edited_by = last_edited_by


# Retrieve the database entries from notion AP
def get_notion_entries(page_id, num_pages=None, filters=None):

    headers = {
        "Authorization": "Bearer " + os.environ['NOTION_TOKEN'],
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    url = f"https://api.notion.com/v1/databases/{page_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    if filters is not None:
        payload["filter"] = filters
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    results = data["results"]
    while data["has_more"]:
        payload["start_cursor"] = data["next_cursor"]
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
    return {
        result["id"]: DbEntry(
            result["id"],
            result["created_time"],
            result["last_edited_time"],
            result["properties"],
            result["url"],
            result["created_by"],
            result["last_edited_by"],
        )
        for result in results
    }


def get_page_name(page_id):
    if page_id is None:
        return None
    url = f"https://api.notion.com/v1/pages/{page_id}/properties/title"
    response = requests.get(url, headers=headers)
    return response.json()
