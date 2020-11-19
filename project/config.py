from typing import Callable, Any
import os
import json

config_mode = os.getenv("FLASK_ENV", "development")


def read_properties(setting, filename="db.properties"):
    """Get secret setting or fail with ImproperlyConfigured"""
    with open(filename) as f:
        secrets = json.load(f)
        try:
            return secrets[setting]
        except KeyError:
            print("Set the {} setting".format(setting))
            raise


def config_properties(env: str) -> Callable[[str], Any]:
    filename = "db"
    if env is not None:
        filename += "." + env
    filename += "." + "properties"
    return lambda name: read_properties(name, filename)


get_config = config_properties(config_mode)
