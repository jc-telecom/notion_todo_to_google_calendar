from scripts.db_entries import DbEntry
from tools.utils import property_value_from_path
import os
import requests
from dotenv import load_dotenv
load_dotenv()


headers = {
    "Authorization": "Bearer " + os.environ['NOTION_TOKEN'],
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


# Retrieve the database entries from notion AP
def get_notion_entries(page_id, num_pages=None, filters=None):

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


class GetNotionInfo(object):
    def get_page_name(self, page_id):
        if page_id is None:
            return None
        url = f"https://api.notion.com/v1/pages/{page_id}/properties/title"
        response = requests.get(url, headers=headers)
        results = response.json().get("results")[0]
        title = property_value_from_path(
            results, ["title", "plain_text"], in_separator=" ")

        return title

    def get_user_name(self, user_id):
        if user_id is None:
            return None
        url = f"https://api.notion.com/v1/users/{user_id}"
        response = requests.get(url, headers=headers)
        return response.json().get("name")
