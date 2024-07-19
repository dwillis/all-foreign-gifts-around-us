import json

def update_agency_employee_items(file_path):
    # Read the input file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Flag to check if any changes were made
    changes_made = False

    # Process each item in the data
    for item in data:
        if item.get('name_and_title') == "An Agency Employee":
            item['donor_name'] = ""
            item['donor_title'] = ""
            item['donor_country'] = ""
            changes_made = True

    # If changes were made, write the updated data back to the same file
    if changes_made:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Updates have been made to {file_path}")
    else:
        print("No items with 'An Agency Employee' were found. No changes were made.")

# File path
file_path = 'combined_json_with_both_names.json'

# Run the update function
update_agency_employee_items(file_path)