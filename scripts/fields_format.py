from tools.utils import check_attributes


class FieldFormat:
    def __init__(self, name, prefix="", suffix="", inner_separator=""):
        self.name = check_attributes(name, "name", str, "")
        self.prefix = check_attributes(prefix, "prefix", str, "")
        self.suffix = check_attributes(suffix, "suffix", str, "")
        self.inner_separator = check_attributes(
            inner_separator, "inner_separator", str, "")
