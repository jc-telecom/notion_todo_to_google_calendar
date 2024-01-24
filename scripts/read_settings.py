import json
from datetime import datetime, timedelta
import pytz


def get_starting_date(days_before_today):
    return (datetime.now(pytz.timezone('Europe/Paris')) - timedelta(days=days_before_today)).isoformat()


def read_user_settings(file_path="project_settings.json"):
    with open(file_path, "r") as f:
        user_settings = json.load(f)
    if user_settings is None:
        raise AttributeError("Settings file is empty")
    return user_settings


def read_defaut_properties_scheme(file_path="config/properties_sheme.json"):
    with open(file_path, "r") as f:
        defaut_properties_scheme = json.load(f)
    return defaut_properties_scheme


def read_user_properties_scheme(settings_json):
    user_properties_scheme = settings_json.get("properties.scheme", None)
    if user_properties_scheme is None:
        raise AttributeError(
            "No properties scheme found in project_settings file")
    col_types = [
        value.get("col_type") for key, value in user_properties_scheme.items()
    ]
    if "date" not in col_types:
        raise AttributeError(
            "No date property found in properties scheme in project_settings file"
        )
    return user_properties_scheme


def get_properties_scheme(defaut_properties_scheme, user_properties_scheme):
    properties_scheme = {}
    from scripts.properties_scheme import PropertyScheme
    for key, property_scheme in user_properties_scheme.items():
        PropertyScheme.check_col_type(property_scheme)
        defaut_property = defaut_properties_scheme[property_scheme.get(
            "col_type")]
        properties_scheme[key] = PropertyScheme(
            name=key,
            col_type=property_scheme.get("col_type"),
            print_to=property_scheme.get(
                "print_to", property_scheme),
            path=defaut_property.get("path", None),
            method=defaut_property.get("method", None),
            order=property_scheme.get("order"),
            prefix=property_scheme.get("prefix"),
            suffix=property_scheme.get("suffix"),
            character_limit=property_scheme.get("character_limit"),
            inner_separator=property_scheme.get("inner_separator"),
            title=property_scheme.get("title"),
            show_title=property_scheme.get("show_title", False),
            title_suffix=property_scheme.get("title_suffix"),
            title_prefix=property_scheme.get("title_prefix")
        )
    return properties_scheme


def get_fields_format(fields_format):
    from scripts.properties_scheme import PropertyScheme
    from scripts.fields_format import FieldFormat
    # Add the possibility to check that each keys are in the print_to fields
    if any(
        key not in PropertyScheme.print_to_locations
        for key in fields_format.keys()
    ):
        raise ValueError(
            f"fields_format keys must be one of : [{', '.join(PropertyScheme.print_to_locations)}]")
    return {
        key: FieldFormat(
            name=key,
            prefix=value.get("prefix", ""),
            suffix=value.get("suffix", ""),
            inner_separator=value.get("inner_separator", ""),
        )
        for key, value in fields_format.items()
    }


def read_project_settings(user_settings_file_path="project_settings.json", defaut_properties_scheme_file_path="config/properties_sheme.json"):
    user_settings = read_user_settings(user_settings_file_path)

    # get the starting date
    try:
        days_before_today = user_settings.get("days_before_today", 5)
    except ValueError as e:
        raise ValueError(
            "days_before_today must be a int : {days_before_today} passed"
        ) from e
    starting_date = get_starting_date(days_before_today)

    # get the properties scheme
    defaut_properties_scheme = read_defaut_properties_scheme(
        defaut_properties_scheme_file_path)

    user_properties_scheme = read_user_properties_scheme(user_settings)
    properties_scheme = get_properties_scheme(
        defaut_properties_scheme, user_properties_scheme)

    # get fields format
    fields_format = user_settings.get("fields.format", None)
    fields_format = get_fields_format(fields_format)

    return starting_date, properties_scheme, fields_format
