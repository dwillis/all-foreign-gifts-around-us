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
            system=f"create only valid JSON objects based on the provided text and example. Never include any additional text or explanation. Always use double-quotes for every key and value. No yapping, no hallucinations.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract all Tangible Gifts contained in the following text into individual JSON objects based on this example: {example}\n\n{text}"
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
    else:
        return ""

import os

def read_text_and_extract_data(input_txt_path, output_json_path):
    # Read the input text file
    with open(input_txt_path, 'r') as file:
        content = file.read()

    # Split the text into sections
    sections = content.split('Federal Register / Vol. ')

    # Iterate over the sections and extract data
    all_data = []
    failed_extractions = []
    for section in sections:
        if section.strip():  # Skip empty sections
            extracted_info = extract_info(section, example_json)
            if extracted_info:  # Check if extracted_info is not an empty string
                try:
                    section_json = json.loads(extracted_info)
                    if isinstance(section_json, list):
                        all_data.extend(section_json)
                    else:
                        all_data.append(section_json)
                except json.JSONDecodeError:
                    # Try to recover from the error
                    if extracted_info.startswith('['):
                        # Try to parse as a JSON array
                        try:
                            section_json = json.loads(extracted_info[1:])
                            all_data.extend(section_json)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                            print(f"JSON string: {extracted_info}")
                            failed_extractions.append(extracted_info)
                    elif extracted_info.startswith('{'):
                        # Try to parse as a JSON object
                        try:
                            section_json = json.loads(extracted_info)
                            all_data.append(section_json)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                            print(f"JSON string: {extracted_info}")
                            failed_extractions.append(extracted_info)
                    else:
                        print(f"No JSON object found in string: {extracted_info}")
                        failed_extractions.append(extracted_info)

    # Convert the list of data to JSON
    with open(output_json_path, 'w', newline='') as jsonfile:
        json.dump(all_data, jsonfile, indent=4)

    # Save failed extractions to a text file
    save_failed_extractions_to_file(output_json_path, failed_extractions)

def save_failed_extractions_to_file(json_file_path, failed_extractions):
    if failed_extractions:
        txt_file_path = os.path.splitext(json_file_path)[0] + '.txt'
        with open(txt_file_path, 'a', encoding='utf-8') as file:
            for extraction in failed_extractions:
                file.write(f"Failed extraction:\n{extraction}\n\n")

# Example usage

files = [
    "2020-03722", "2021-16751", "2022-07641", "2023-03806"
    ]

for file in files:
    input_txt_path = f"text/{file}.txt"
    output_json_path = f"json/{file}.json"
    read_text_and_extract_data(input_txt_path, output_json_path)