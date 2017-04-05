#!/usr/bin/python3
import requests
import sys
import os
import shutil
import json

#
# first parameter is the url of the API
# if nothingis given, http://localhost:8080 is used.
#

HERE = os.path.dirname(__file__) or "."
TESTS = os.path.join(HERE, "tests")
DOWNLOADED_FILE_START = "downloaded_api_"
DOWNLOADED_FILE_TEMPLATE = DOWNLOADED_FILE_START + "{}.json"
NUMBER_OF_EXAMPLES = 3


API = (sys.argv[1] if len(sys.argv) >= 2 else "http://localhost:8080")
if not API.startswith("http"):
    API = "http://" + API
    
print("deleting files")
for dirpath, dirnames, filenames in os.walk(TESTS):
    for file in filenames:
        if file.startswith(DOWNLOADED_FILE_START):
            os.remove(os.path.join(dirpath, file))

print("querying", API)

downloaded = 0
def download_file(url, file_name):
    # from http://stackoverflow.com/a/39217788/1320237
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return r

def download_for_schema(schema, path):
    global downloaded
    downloaded += 1
    url = API + path
    file_name = os.path.join(TESTS, schema, "works", DOWNLOADED_FILE_TEMPLATE.format(downloaded))
    print(schema, url)
    print(" " * (len(schema) - 4), "->", file_name)
    r = download_file(url, file_name)
    if r.status_code == 200:
        with open(file_name, "r") as f:
            return json.load(f)
    else:
        with open(file_name, "w") as f:
            json.dump(None, f)
    return {}

def download_collection(plural, singular):
    collection = download_for_schema(plural, "/{}.json".format(plural))
    for i, instance in enumerate(collection.values()):
        download_for_schema(singular, instance["urls"]["json"])
        if i >= NUMBER_OF_EXAMPLES:
            break
    return collection

organizations = download_collection("organizations", "organization")
i = 0
for organization in organizations.values():
    for repository in organization["repositories"].values():
        download_for_schema("repository", repository["urls"]["json"])
        i += 1
    if i >= NUMBER_OF_EXAMPLES:
        break

