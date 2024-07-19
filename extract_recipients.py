import json
import anthropic
import os

client = anthropic.Anthropic(
    api_key=os.environ.get("CLAUDE_API_KEY")
)

def extract_recipient_details(name_and_title):
    example = {
        "recipient_name": "Joseph R. Biden Jr.",
        "recipient_title": "President of the United States"
    }

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        temperature=0.2,
        system="Extract the recipient name (without honorifics) and title from the provided name_and_title string and return ONLY a JSON object based on the provided example. Use double-quotes for everything. No yapping.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Given the following name_and_title string:\n\n{name_and_title}\n\nExtract the recipient name and title based on this example:\n\n{example}"
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

def extract_and_merge_recipient_details(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as file:
        input_data = json.load(file)

    # Process each item in the input data
    for item in input_data:
        # Check if the item (excluding gift_description) is already in the output data
        if not item_exists(item, output_file):
            print("adding item")
            name_and_title = item.get('name_and_title')
            if name_and_title:
                extracted_details = extract_recipient_details(name_and_title)
                if extracted_details:
                    item.update(extracted_details)
                else:
                    # If there's an error, add null values
                    item.update({
                        "recipient_name": None,
                        "recipient_title": None
                    })
            append_to_file(item, output_file)

# Example usage
input_file = 'combined_json_with_names.json'
output_file = 'combined_json_with_both_names.json'
extract_and_merge_recipient_details(input_file, output_file)