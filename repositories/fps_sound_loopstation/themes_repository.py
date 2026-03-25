import json

def load(path):
    themes = None
    with open(path, "r") as f:
        themes = json.load(f)
    return themes
