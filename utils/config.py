import yaml
import os

CONFIG_PATH = "config.yml"

DEFAULT_CONFIG = {
    "TOKEN": "",
    "PREFIX": "!",
    "MYSQL": {
        "HOST": "",
        "PORT": 3306,
        "USER": "",
        "PASSWORD": "",
        "DATABASE": ""
    },
    "REDIS": {
        "HOST": "",
        "PORT": 6379,
        "USERNAME": "",
        "PASSWORD": "",
        "DB": 0
    },
    "LINKING": {
        "CODE_LENGTH": 6,
        "CODE_TTL_SECONDS": 300,
        "CODE_PREFIX": "linkcraft:code:"
    }
}

def merge_defaults(config, defaults):
    merged = defaults.copy()
    for key, value in config.items():
        if isinstance(value, dict) and isinstance(defaults.get(key), dict):
            merged[key] = merge_defaults(value, defaults[key])
        else:
            merged[key] = value
    return merged

class basicconfig:

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as file:
            file.write("# Your discord bot token get it by creating an application at https://discord.com/developers/applications\n")
            yaml.dump({"TOKEN": ""}, file, sort_keys=False)
            
            file.write("\n# Prefix is for the discord bot prefixed commands (such as !help, '!' is the prefix here)\n")
            yaml.dump({"PREFIX": "!"}, file, sort_keys=False)

            file.write("\n# MySQL connection credentials\n")
            yaml.dump({"MYSQL": DEFAULT_CONFIG["MYSQL"]}, file, sort_keys=False)

            file.write("\n# Redis-py connection credentials\n")
            yaml.dump({"REDIS": DEFAULT_CONFIG["REDIS"]}, file, sort_keys=False)

            file.write("\n# Temporary account-linking code settings\n")
            yaml.dump({"LINKING": DEFAULT_CONFIG["LINKING"]}, file, sort_keys=False)
            

    with open(CONFIG_PATH, "r") as file:
        try:
            _config = yaml.safe_load(file)
            if not isinstance(_config, dict):
                raise ValueError("Invalid configuration structure.")
            _config = merge_defaults(_config, DEFAULT_CONFIG)
        except (yaml.YAMLError, ValueError):
            _config = DEFAULT_CONFIG.copy()
            with open(CONFIG_PATH, "w") as reset_file:
                # Manually add comments and the default configuration when resetting
                reset_file.write("# Your discord bot token get it by creating an application at https://discord.com/developers/applications\n")
                yaml.dump({"TOKEN": _config["TOKEN"]}, reset_file, sort_keys=False)
                
                
                reset_file.write("\n# Prefix is for the discord bot prefixed commands (such as !help, '!' is the prefix here)\n")
                yaml.dump({"PREFIX": _config["PREFIX"]}, reset_file, sort_keys=False)

                reset_file.write("\n# MySQL connection credentials\n")
                yaml.dump({"MYSQL": _config["MYSQL"]}, reset_file, sort_keys=False)

                reset_file.write("\n# Redis-py connection credentials\n")
                yaml.dump({"REDIS": _config["REDIS"]}, reset_file, sort_keys=False)

                reset_file.write("\n# Temporary account-linking code settings\n")
                yaml.dump({"LINKING": _config["LINKING"]}, reset_file, sort_keys=False)
                

    TOKEN = _config.get("TOKEN", "")
    PREFIX = _config.get("PREFIX", "!")
    MYSQL = _config.get("MYSQL", DEFAULT_CONFIG["MYSQL"])
    REDIS = _config.get("REDIS", DEFAULT_CONFIG["REDIS"])
    LINKING = _config.get("LINKING", DEFAULT_CONFIG["LINKING"])
