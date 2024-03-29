import json

import pretty_errors

pretty_errors.configure(
    separator_character="*",
    filename_display=pretty_errors.FILENAME_EXTENDED,
    line_number_first=True,
    display_link=True,
    lines_before=5,
    lines_after=2,
    line_color=pretty_errors.RED + "> " + pretty_errors.default_config.line_color,
    code_color="  " + pretty_errors.default_config.line_color,
    truncate_code=True,
    display_locals=True,
)


class Config:
    def __init__(self, filename):
        # ensure a file exists and is actually read
        if filename:
            try:
                with open(filename, "r") as f:
                    self._config = json.load(f)
                    for key, val in self._config.items():
                        if isinstance(val, dict):
                            for subkey, subval in val.items():
                                if str(subval).isdigit():
                                    subval = float(subval)
                                setattr(self, subkey, subval)
                        else:
                            if str(val).isdigit():
                                val = float(val)
                            setattr(self, key, val)
            except FileNotFoundError:
                raise (f"Config file {filename} not found.")

    def __getattr__(self, _):
        # Return None if the attribute is not found
        return None
