import json

GYM_MEM_FILE = "/home/sicko/projects/pyside_learning/gym_app/gym_members.json"
MEMBERSHIP_DICT_FILE = "/home/sicko/projects/pyside_learning/gym_app/membership_dict.json"
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
        """ If the file is empty it shows FileNotFoundError """
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
