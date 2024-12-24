import json


def read_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)