import configparser


class Config:
    def __init__(self, filename):
        self._config = configparser.ConfigParser()
        # ensure a file exists and is actually read
        if filename:
            try:
                with open(filename, "r") as _:
                    self._config.read(filename)
                    for section in self._config.sections():
                        for key, val in self._config.items(section):
                            if val.isdigit():
                                val = float(val)
                            setattr(self, key, val)
            except FileNotFoundError:
                raise (f"Config file {filename} not found.")

    def __getattr__(self, _):
        # Return None if the attribute is not found
        return None
