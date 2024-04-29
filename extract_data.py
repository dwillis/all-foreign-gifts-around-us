import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

def extract_info(text, example):
    completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "system",
            "content": f"create a JSON object containing the results based on the following example: {example}"
        },
        {
            "role": "user",
            "content": f"Given the following text, extract structured information in JSON format: {text}:"
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
)
    return completion.choices[0].message.content

def read_text_and_extract_data(input_txt_path, output_csv_path):
    # Read the input text file
    with open(input_txt_path, 'r') as file:
        content = file.read()

    # Extract the relevant section of the text manually or programmatically

    # Provide an example of how the CSV should look
    example_json = {
        "name_and_title": "The Honorable Joseph R. Biden Jr., President of the United States.",
        "gift_description": "Painting titled ‘At Parika Stelling (Guyana).’ Rec’d—3/2/2022. Est. Value—$650.00. Disposition —Pending Transfer to NARA.",
        "foreign_donor": "His Excellency Michael Martin, Prime Minister of Ireland.",
        "circumstances": "Non-acceptance would cause embarrassment to donor and U.S. Government."
    }
    
    extracted_info = extract_info(content, example_json)

    # Convert the string to json
    with open(output_json_path, 'w', newline='') as jsonfile:
        json.dump(extracted_info, jsonfile, indent=4)


# Example usage
input_txt_path = 'text/2024-03129.txt'
output_json_path = '2024-03129.json'
read_text_and_extract_data(input_txt_path, output_json_path)

