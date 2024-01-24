import json

# Your JSON data
json_data = '''
{
  "checkbox": { "path": ["checkbox"] },
  "date": { "path": ["date"] },
  "email": { "path": ["email"] },
  "last_edited_by": { "path": ["id"], "method": "get_user_name" },
  "multi_select": { "path": ["multi_select", "name"] },
  "number": { "path": ["number"] },
  "people": { "path": ["people", "id"], "method": "get_user_name" },
  "phone_number": { "path": ["phone_number"] },
  "rich_text": { "path": ["rich_text", "plain_text"] },
  "select": { "path": ["select", "name"] },
  "status": { "path": ["status", "name"] },
  "title": { "path": ["title", "plain_text"] },
  "url": { "path": ["url"] },
  "relation": { "path": ["relation", "id"], "method": "get_page_name" }
}
'''

# Parse the JSON data
parsed_data = json.loads(json_data)

# Get the keys as a list
keys_list = list(parsed_data.keys())

# Print the keys
print(keys_list)
