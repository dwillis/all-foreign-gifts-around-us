import os
import json
from collections import OrderedDict

def combine_json_files(directory):
    combined_data = []
    duplicate_keys = set()

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                data = json.load(file, object_pairs_hook=OrderedDict)

            for item in data:
                item_key = tuple((k, v) for k, v in item.items() if k != 'disposition')
                if item_key not in duplicate_keys:
                    if 'disposition' in item:
                        item['disposition'] = [item['disposition']]
                    else:
                        item['disposition'] = []
                    combined_data.append(item)
                    duplicate_keys.add(item_key)
                else:
                    existing_item = next(i for i in combined_data if tuple((k, v) for k, v in i.items() if k != 'disposition') == item_key)
                    if 'disposition' in item:
                        existing_item['disposition'].extend(item['disposition'] if isinstance(item['disposition'], list) else [item['disposition']])

    return combined_data

def save_combined_data(combined_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(combined_data, file, indent=4)

# Example usage
json_directory = 'json'
output_file = 'combined.json'

combined_data = combine_json_files(json_directory)
save_combined_data(combined_data, output_file)