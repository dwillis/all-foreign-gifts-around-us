import json
from collections import OrderedDict

def check_missing_objects(combined_file, combined_with_names_file):
    # Load the JSON data from the files
    with open(combined_file, 'r') as file:
        combined_data = json.load(file, object_pairs_hook=OrderedDict)

    with open(combined_with_names_file, 'r') as file:
        combined_with_names_data = json.load(file, object_pairs_hook=OrderedDict)

    # Create dictionaries to store objects from both files
    combined_objects = {}
    combined_with_names_objects = {}

    # Create keys for the dictionaries using the specified keys
    for obj in combined_data:
        key = tuple((obj.get(k) for k in ['name_and_title', 'gift_description', 'received', 'estimated_value', 'foreign_donor']))
        combined_objects[key] = obj

    for obj in combined_with_names_data:
        key = tuple((obj.get(k) for k in ['name_and_title', 'gift_description', 'received', 'estimated_value', 'foreign_donor']))
        combined_with_names_objects[key] = obj

    # Find missing objects
    missing_objects = [obj for key, obj in combined_objects.items() if key not in combined_with_names_objects]

    # Print missing objects
    if missing_objects:
        print("The following objects are present in combined.json but not in combined_json_with_names.json:")
        for obj in missing_objects:
            print(obj)
    else:
        print("All objects in combined.json are present in combined_json_with_names.json.")

# Example usage
combined_file = 'combined.json'
combined_with_names_file = 'combined_json_with_names.json'
check_missing_objects(combined_file, combined_with_names_file)