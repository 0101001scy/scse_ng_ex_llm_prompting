import json
import os


## Logic for loading and reading from a JSON file.
## The function must return only the items
def load_items(filename):
     with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # The JSON file may store items directly as a list, or under an "items" key
     if isinstance(data, dict):
        return data.get("items", [])
        return data

## Logic for getting only those items that are not yet claimed
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    unclaimed = []
    for item in items:
        # Accept either "claimed" (bool) or "status" (string) field
        if "claimed" in item:
            if not item["claimed"]:
                unclaimed.append(item)
        elif "status" in item:
            if str(item["status"]).lower() == "unclaimed":
                unclaimed.append(item)
        else:
            unclaimed.append(item)
    return unclaimed


## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
     directory = os.path.dirname(filename)
     if directory and not os.path.exists(directory):
        os.makedirs(directory)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

    