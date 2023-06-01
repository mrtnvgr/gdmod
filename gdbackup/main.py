#!/usr/bin/env python3

import json
import os
import shutil

import requests

API_URL = (
    lambda type: f"http://dinedi.net/api.php?action=read&type={type}&view=list&order=asc"
)


def check_dir(type: str, wipe=False):
    if wipe:
        shutil.rmtree(type, ignore_errors=True)
    os.mkdir(type)


def get_count(type: str):
    api_url = API_URL(type)
    return int(requests.get(api_url).json()["data"]["total"])


def new_uploads(type: str):
    new_count = get_count(type)
    local_count = len(os.listdir(type))
    return new_count > local_count - 1


def dump(type: str):
    try:
        check_dir(type)
    except FileExistsError:
        if new_uploads(type):
            print(f"Found new {type}! Redownloading...")
            check_dir(type, wipe=True)
        else:
            print(f"{type.title()} are up-to-date")
            return

    api_url = API_URL(type)
    count = get_count(type)

    schema = requests.get(f"{api_url}&limit={count}").json()
    schema_path = os.path.join(type, "schema.json")
    json.dump(schema, open(schema_path, "w"))

    for i, mod in enumerate(schema["data"]["list"]):
        id = mod["id"]

        if type == "tracks":
            file_url = mod["mrg"]
            file_name = f"{id}.mrg"
        else:
            file_url = mod["zip"]
            file_name = f"{id}.zip"

        file_path = os.path.join(type, file_name)
        content = requests.get(file_url, allow_redirects=True).content
        with open(file_path, "wb") as file:
            file.write(content)

        print(f"\r{type.title()}: [{i+1}/{count}]", end="")

    print()


if __name__ == "__main__":
    dump("tracks")
    dump("skins")
