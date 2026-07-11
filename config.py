import json

# Loap the config file
def load_config():
    try:
        with open("config.json", "r") as file:
            configs = json.load(file)
        return configs
    except (FileNotFoundError, json.JSONDecodeError):
        return {"hide_completed": False, "initial_entry": False}
    

# Update the config file
def save_config(config):
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)