The objective of this project is to create synchronize any Notion Database to a Google Calendar Agenda

# Project architecture

## Connect to Notion API

Fist we need to connect to the notion API to retrieve database entries.
Each entry is retrieved as a JSON response with the following keys :

- `id`
- `created_time`
- `last_edited_time`
- `properties`
- `url`
- `created_by`
- `last_edited_by`

Relavant data are stored in the properties' field, [more info](https://developers.notion.com/reference/property-object)

## Retrieve the information from the property field

Once databases entries have been retrieved, we need to retrieve the properties of each entry.

## Format the event

Each property contains information that could be used for the summary, the description or the date. Yet for each entry we create a class with those four sections.

## Connect to the Google Calendar API

## Add, delete or update the event

# Getting started

## Notifications :

https://jorricks.github.io/macos-notifications/faq/

# Exemple

# Schema to explain how it works

# Variable and functions naming :

db entry
notion event
google event

# Presentaion

# Improvements

CHANGE properties to properties SCHEME

- Add a messagebox with progression and validation when it's ok (push)
- Make it more custmomizable
- add child items to the description
- change color depending on the status
