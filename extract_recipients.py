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

def extract_and_merge_recipient_details(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    for item in data:
        name_and_title = item.get('name_and_title')
        if name_and_title:
            extracted_details = extract_recipient_details(name_and_title)
            if extracted_details:
                item.update(extracted_details)

    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
input_file = 'combined_json_with_names.json'
output_file = 'combined_json_with_both_names.json'
extract_and_merge_recipient_details(input_file, output_file)