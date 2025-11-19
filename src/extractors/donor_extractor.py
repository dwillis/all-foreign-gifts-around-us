import json
import anthropic
import os

client = anthropic.Anthropic(
    api_key=os.environ.get("CLAUDE_API_KEY")
)

def extract_donor_details(foreign_donor):
    example = {
        "donor_name": "Michael Martin",
        "donor_title": "Prime Minister",
        "donor_country": "Ireland"
    }

    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=512,
        temperature=0.2,
        system="Extract the donor name (without honorifics), title, and country from the provided foreign_donor string and return ONLY a JSON object based on the provided example. Use double-quotes for everything. No yapping.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Given the following foreign_donor string:\n\n{foreign_donor}\n\nExtract the donor name, title, and country based on this example:\n\n{example}"
                    }
                ]
            }
        ]
    )

    try:
        response = message.content[0].text.strip()
        extracted_details = json.loads(response)
        return extracted_details
    except json.JSONDecodeError:
        print(f"Error: Could not parse the response for '{response}' as JSON.")
        return None

def item_exists(item, output_file):
    try:
        with open(output_file, 'r') as file:
            output_data = json.load(file)
            for existing_item in output_data:
                if all(item.get(key) == existing_item.get(key) for key in item.keys() if key != 'gift_description'):
                    return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    return False

def append_to_file(item, output_file):
    try:
        with open(output_file, 'r+') as file:
            file.seek(0, 2)  # Move to the end of the file
            if file.tell() == 0:  # File is empty
                json.dump([item], file, indent=2)
            else:
                file.seek(0)  # Move to the beginning of the file
                data = json.load(file)
                data.append(item)
                file.seek(0)  # Move back to the beginning of the file
                file.truncate()  # Clear the file content
                json.dump(data, file, indent=2)
    except FileNotFoundError:
        with open(output_file, 'w') as file:
            json.dump([item], file, indent=2)

def extract_and_merge_donor_details(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as file:
        input_data = json.load(file)

    # Process each item in the input data
    for item in input_data:
        # Check if the item (excluding gift_description) is already in the output data
        if not item_exists(item, output_file):
            print("adding item")
            foreign_donor = item.get('foreign_donor')
            if foreign_donor:
                extracted_details = extract_donor_details(foreign_donor)
                if extracted_details:
                    item.update(extracted_details)
                else:
                    # If there's an error, add null values
                    item.update({
                        "donor_name": None,
                        "donor_title": None,
                        "donor_country": None
                    })
            append_to_file(item, output_file)

# Example usage
input_file = 'combined.json'
output_file = 'combined_json_with_names.json'
extract_and_merge_donor_details(input_file, output_file)