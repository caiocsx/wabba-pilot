import json
import os

from paths import DATA_PATH


def load_clicked(path=DATA_PATH):
    if not os.path.exists(path):
        return set()

    with open(path, "r", encoding="utf-8") as f:
        return set(tuple(x) for x in json.load(f))


def save_clicked(clicked, path=DATA_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([list(x) for x in clicked], f)
