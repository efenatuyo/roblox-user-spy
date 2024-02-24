import json

def read():
    return json.loads(open("spy/database/database.json", "r").read())

def write(content, return_content=False):
    open("spy/database/database.json", "w").write(json.dumps(content, indent=2))
    if return_content:
        return read()