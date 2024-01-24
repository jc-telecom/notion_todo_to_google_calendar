from scripts.read_settings import read_defaut_properties_scheme
from tools.utils import check_attributes
import json


class PropertyScheme:
    col_types = read_defaut_properties_scheme().keys()
    print_to_locations = ["summary", "description"]

    def __init__(self, name, col_type, print_to, path, method=None, order=1, prefix="", suffix="", character_limit=None, inner_separator="", title="", show_title=False, title_suffix="", title_prefix=""):
        self.name = str(name)

        if col_type not in self.col_types:
            raise ValueError(
                f"col_type must be one of : [{', '.join(self.col_types)}]")
        self.col_type = col_type

        if col_type == "date":
            self.print_to = "date"
        elif print_to in self.print_to_locations:
            self.print_to = print_to

        else:
            raise ValueError(
                f"print_to must be one of : [{', '.join(self.print_to_locations)}]. {print_to} passed")
        self.path = [name] + path
        self.method = method

        self.order = check_attributes(order, "order", int, 1)
        self.character_limit = check_attributes(
            character_limit, "character_limit", int, None)
        self.prefix = check_attributes(prefix, "prefix", str, "")
        self.suffix = check_attributes(suffix, "suffix", str, "")
        self.title = check_attributes(title, "title", str, "")
        self.show_title = check_attributes(
            show_title, "show_title", bool, False)
        self.title_prefix = check_attributes(
            title_prefix, 'title_prefix', str, "")
        self.title_suffix = check_attributes(
            title_suffix, 'title_suffix', str, "")
        self.inner_separator = check_attributes(
            inner_separator, 'inner_separator', str, " ")

    def check_col_type(self):
        if self.get('col_type') not in PropertyScheme.col_types:
            raise ValueError(
                f"col_type must be one of : [{', '.join(PropertyScheme.col_types)}]. '{self.get('col_type')}' passed")
