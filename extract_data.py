import openai
import csv

def extract_info_with_openai(text, example):
    # This function uses the OpenAI API to extract structured information from the text
    prompt = f"Given the following text, extract structured information in CSV format:\n\n{text}\n\nExample CSV output:\n{example}\n\nFormat the above text as a CSV:"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.1  # Low temperature to promote consistency and less creativity in output
    )
    return response.choices[0].text.strip()

def read_text_and_extract_data(input_txt_path, output_csv_path):
    # Read the input text file
    with open(input_txt_path, 'r') as file:
        content = file.read()

    # Extract the relevant section of the text manually or programmatically
    section_start = content.find("Gifts to Federal Employees From Foreign Government Sources Reported to Employing Agencies")
    section_end = content.find("Next Section or End Marker")  # Adjust this accordingly
    section_text = content[section_start:section_end] if section_end != -1 else content[section_start:]

    # Provide an example of how the CSV should look
    example_csv = '"name_and_title","gift_description","foreign_donor","circumstances"\n"The Honorable Joseph R. Biden Jr., President of the United States.","Painting titled ‘At Parika Stelling (Guyana).’ Rec’d—3/2/2022. Est. Value—$650.00. Disposition —Pending Transfer to NARA.","His Excellency Michael Martin, Prime Minister of Ireland.","Non-acceptance would cause embarrassment to donor and U.S. Government."'

    # Use OpenAI API to parse the section with the example
    extracted_info = extract_info_with_openai(section_text, example_csv)

    # Convert the string to CSV
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line in extracted_info.split('\n'):
            writer.writerow(line.split(','))

# Setup your OpenAI API key
openai.api_key = 'your-openai-api-key'

# Example usage
input_txt_path = '2024-03129.txt'
output_csv_path = '2024-03129.csv'
read_text_and_extract_data(input_txt_path, output_csv_path)
