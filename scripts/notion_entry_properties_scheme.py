import json
from tools.utils import property_value_from_path


class PropertyScheme:
    information_types = ["summary", "date_start",
                         "date_end", "location", "description"]

    def __init__(self, name, path, title=None, information_type=None, order=1, prefix=None, suffix=None, character_limit=None, inner_separators="", property_item=None, show_title=False):
        try:
            if not isinstance(name, str):
                raise ValueError("name must be a string")
            self.name = name

            self.title = name if title is None else title
            if not isinstance(path, list):
                raise ValueError("path must be a list")
            self.path = path

            if information_type not in self.information_types:
                raise ValueError(
                    f"information_type must be one of : [{', '.join(information_types)}]")
            self.information_type = information_type

            if not isinstance(order, int):
                raise ValueError(
                    "order must be a boolean")
            self.order = order

            self.prefix = prefix
            self.suffix = suffix
            self.character_limit = character_limit
            self.inner_separators = inner_separators
            self.show_title = show_title

        except ValueError as error:
            # print(f"-> Error: {error}")
            traceback.print_exc()
            if property_item is not None:
                print(f"JSON block: {property_item}\n")


def retrieve_property_scheme(file_path="project_settings.json"):
    with open(file_path, 'r') as file:
        settings = json.load(file)
    properties = settings.get("properties.scheme")
    properties_dict = {}
    for key, property_item in properties.items():
        if property_item.get("property_path") is None:
            raise ValueError(
                f"-> Error: The 'property_path' key is required in the properties.scheme file for the '{key}' property")
        if property_item.get("information_type") is None:
            raise ValueError(
                f"-> Error: The 'information_type' key is required in the properties.scheme file for the '{key}' property")
        properties_dict[key] = PropertyScheme(
            name=key,
            title=property_item.get("title"),
            path=property_item.get("property_path"),
            information_type=property_item.get("information_type"),
            order=property_item.get("order", 1),
            character_limit=property_item.get("character_limit"),
            prefix=property_item.get("prefix", ""),
            suffix=property_item.get("suffix", ""),
            inner_separators=property_item.get("inner_separators", ""),
            show_title=property_item.get("show_title", False),
            property_item=f"{key} : {json.dumps(property_item)}"
        )
    with open('config/config.json', 'r') as f:
        required_keys = json.load(f).get("properties.mandatory")
    for key in required_keys:
        if key not in properties_dict:
            raise ValueError(
                f"-> Error: The '{key}' property is required in the properties.scheme file")
    return properties_dict


def get_properties_from_db_entry(db_entry, properties_scheme):
    properties = db_entry.properties
    event_properties_dict = {}
    for key, property_item in properties_scheme.items():
        # values can be a string or a list
        values = property_value_from_path(
            properties, property_item.path)
        if not isinstance(values, list):
            values = [values]

        prefix = getattr(property_item, "prefix", "")
        suffix = getattr(property_item, "suffix", "")
        for index, value in enumerate(values):
            if value is not None:
                value = None if value == "None" else value
                if getattr(property_item, "character_limit") is not None:
                    value = value[:int(property_item.character_limit)]
                values[index] = value
            else:
                values[index] = ""
        inner_separators = getattr(property_item, "inner_separators", " ")
        event_properties_dict[key] = prefix + \
            inner_separators.join(values) + suffix

    return event_properties_dict


class FieldFormat:
    def __init__(self, name, suffix=None, prefix=None, inner_separators=None):
        self.name = name
        self.suffix = suffix
        self.prefix = prefix
        self.inner_separators = inner_separators


def retrieve_field_format(file_path="project_settings.json"):
    with open(file_path, 'r') as file:
        settings = json.load(file)
    fields_format = settings.get("fields.format", {})
    return {
        key: FieldFormat(
            name=key,
            suffix=field_format.get("suffix"),
            prefix=field_format.get("prefix"),
            inner_separators=field_format.get("inner_separators"),
        )
        for key, field_format in fields_format.items()
    }
