import os
import json
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("CLAUDE_API_KEY")
)

example_json = {
                "name_and_title": "name and title of the recipient",
                "gift_description": "the gift",
                "received": "the date received in yyyy-mm-dd format",
                "estimated_value": "the dollar value only, no dollar sign",
                "disposition": "the disposition of the gift, not including 'Disposition-'",
                "foreign_donor": "name and title of foreign donor",
                "circumstances": "why the gift was accepted"
            }

def extract_info(text, example):
    if "Honorable" in text:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0,
            system=f"create only a valid JSON object based only on the provided text. Always use double-quotes for every key and value. No yapping, no hallucinations.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract all Tangible Gifts contained in {text} into individual JSON objects with no text before or after the object based on {example}. Do NOT include the example in the results and do NOT group any gifts together into a list. Remove any linebreaks or similar whitespace characters that aren't literal spaces. Don't repeat any gifts."
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
    else:
        return ""

def read_text_and_extract_data(input_txt_path, output_json_path):
    # Read the input text file
    with open(input_txt_path, 'r') as file:
        content = file.read()

    # Split the text into sections
    sections = content.split('Federal Register / Vol. ')

    # Iterate over the sections and extract data
    all_data = []
    for section in sections:
        if section.strip():  # Skip empty sections
            extracted_info = extract_info(section, example_json)
            if extracted_info:  # Check if extracted_info is not an empty string
                try:
                    section_json = json.loads(extracted_info)
                    all_data.append(section_json)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print(f"extracted_info: {extracted_info}")

    # Convert the list of data to JSON
    with open(output_json_path, 'w', newline='') as jsonfile:
        json.dump(all_data, jsonfile, indent=4)

# Example usage

input_txt_path = 'text/2024-03129.txt'
output_json_path = 'json/2024-03129.json'
read_text_and_extract_data(input_txt_path, output_json_path)