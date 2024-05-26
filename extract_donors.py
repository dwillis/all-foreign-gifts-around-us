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

def extract_and_merge_donor_details(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    for item in data:
        foreign_donor = item.get('foreign_donor')
        if foreign_donor:
            extracted_details = extract_donor_details(foreign_donor)
            if extracted_details:
                item.update(extracted_details)

    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
input_file = 'combined.json'
output_file = 'combined_json_with_names.json'
extract_and_merge_donor_details(input_file, output_file)