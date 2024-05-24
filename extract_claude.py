import os
import json
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("CLAUDE_API_KEY")
)

example_json = {
                "name_and_title": "name and title of the recipient",
                "gift_description": "the gift",
                "foreign_donor": "name and title of foreign donor",
                "circumstances": "why the gift was accepted"
            }

def extract_info(text, example):
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system=f"create only a valid JSON object. Always use double-quotes for every key and value. No yapping.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Extract all Tangible Gifts contained in {text} into JSON objects with no text before or after the object based on {example}. Do NOT include the example in the results and remove any linebreaks or similar whitespace characters that aren't literal spaces."
                    }
                ]
            }
        ]
    )
    return message.content[0].text

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
            print(extracted_info)
    
    # Convert the list of data to JSON
#    with open(output_json_path, 'w', newline='') as jsonfile:
#        json.dump(all_data, jsonfile, indent=4)

# Example usage
input_txt_path = 'test.txt'
output_json_path = 'test.json'
read_text_and_extract_data(input_txt_path, output_json_path)