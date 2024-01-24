The objective of this project is to synchronize any Notion Database to a Google Calendar Agenda

# Project architecture

The project is compposed of three main steps :
Retieve the info from the Notion API
Convert the info from the Notion database to an event format
Add the event to the Google Calendar

# Getting started

## 1. Install the packages

Install the required packages :

```
pip install -r requirements.txt
```

## 2. Setup Notion integration

First you need to set up your Notion integration. You can follow this [tutorial](https://developers.notion.com/docs/create-a-notion-integration) to find out how to do it.
Once your integration is created add your notion taken and the database id you want to retrieve the data from to a `.env` file as follows :

```
NOTION_TOKEN = "YOUR NOTION TOEKN"
DATABASE_ID = "YOUR DATABASE ID"
```

> See the [docs](https://developers.notion.com/docs/create-a-notion-integration#environment-variables) on Notion environment variables

## 3. Setup Google Calendar API

To set up the Google Calendar API, follow the [Google docs](https://developers.google.com/calendar/api/quickstart/python?hl=en)

If you want to add the events to your pirmary calendar add `GOOGLE_CALENDAR_ID` to your `.env` file :

```
GOOGLE_CALENDAR_ID = "primary"
```

Or you can create a custom agenda and add the agenda ID :

```
GOOGLE_CALENDAR_ID = "YOUR AGENDA ID"
```

## 4. Setup `project_setting.json` file

Each Notion database is different. The result received from the Notion API is a JSON object with the follwing keys :

- `id`
- `created_time`
- `last_edited_time`
- `properties`
- `url`
- `created_by`
- `last_edited_by`

Most information are stored in `properties`. To know how each property must be used, you need to fill in the `project_setting.json` file.

### 5. Fill the `day_rev_limit`

The `day_rev_limit` is the number of days prior to today whose data you want to retrieve.

`project_setting.json` :

```
{

  "day_rev_limit": 5,

  ...

```

### 6. Fill the `properties.scheme`

To know which information to retrieve from the database and how to use it you must fill the `properties.sheme`

The `date`, field is mandatory.

Each property must contain `col_type` which is the type of property. [See docs](https://developers.notion.com/reference/property-object)

| key               | Description                                                                                       | Type                                                                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `col_type`        | Databse column type                                                                               | _string_ in `['checkbox', 'date', 'email', 'last_edited_by', 'multi_select', 'number', 'people', 'phone_number', 'rich_text', 'select', 'status', 'title', 'url', 'relation']` |
| `print_to`        | Where the information should be used                                                              | _string_ in `"summary", "description"`                                                                                                                                         |
| `order`           |  order in which the information should be displayed inside the `information_type`                 | _int_                                                                                                                                                                          |
| `character_limit` | If the retrieve value must be trimmed                                                             | _int_                                                                                                                                                                          |
| `prefix`          | Text to be added before the retrieved value                                                       | _string_                                                                                                                                                                       |
| `suffix`          | Text to be added after the retrieved value                                                        | _string_                                                                                                                                                                       |
| `title`           | The title of the retrieved value                                                                  | _string_                                                                                                                                                                       |
| `show_title`      | if the title must be printed before the retrieved value                                           | _boolean_                                                                                                                                                                      |
| `title_prefix`    | Text to be added before the title                                                                 | _string_                                                                                                                                                                       |
| `title_suffix`    | Text to be added after the title                                                                  | _string_                                                                                                                                                                       |
| `inner_separator` | the inner separators is the retrieved values is a list (in the case of multi select for instance) | _string_                                                                                                                                                                       |

## 7. Run app.py file

Then just run the `app.py` file. The number of events added, deleted or updated are displayed in a push notification at the end of the script. The result is also stored in the `meta.json` file.
