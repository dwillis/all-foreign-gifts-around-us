import os
import requests
import json
import pdftotext

def download_pdfs_from_json(json_path, pdf_directory='pdfs', text_directory='text'):
    # Create the directories if they don't exist
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)
    if not os.path.exists(text_directory):
        os.makedirs(text_directory)

    # Load the JSON file
    with open(json_path, 'r') as file:
        json_data = json.load(file)

    # Extract PDF URLs
    pdf_urls = [item['pdf_url'] for item in json_data['results'] if 'pdf_url' in item]

    # Download and save each PDF only if the corresponding text file does not exist
    for url in pdf_urls:
        filename = url.split('/')[-1]
        pdf_path = os.path.join(pdf_directory, filename)
        text_path = os.path.join(text_directory, filename.replace('.pdf', '.txt'))

        # Check if the text file already exists
        if not os.path.exists(text_path):
            try:
                # Download PDF if it doesn't exist
                if not os.path.exists(pdf_path):
                    response = requests.get(url)
                    response.raise_for_status()  # Ensure we stop at HTTP errors
                    with open(pdf_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded and saved: {pdf_path}")
                
                # Convert the PDF to text
                with open(pdf_path, "rb") as f:
                    pdf = pdftotext.PDF(f)
                
                with open(text_path, 'w') as f:
                    f.write("\n\n".join(pdf))
                print(f"Converted and saved: {text_path}")
            except requests.RequestException as e:
                print(f"Failed to download or convert {url}: {str(e)}")
        else:
            print(f"Text file already exists for {filename}, skipping...")

# Specify the path to your local JSON file
json_path = 'federal_register.json'
download_pdfs_from_json(json_path)
