# All Foreign Gifts Around Us

This project aims to extract structured data from unstructured text published in the Federal Register about gifts provided to U.S. officials by foreign government officials.

## Overview

The Federal Register is the official journal of the United States government, which publishes various notices, rules, and regulatory information. Among these publications are reports detailing gifts received by U.S. government officials from foreign sources. Some presidential administrations are [better than others](https://oversightdemocrats.house.gov/news/press-releases/oversight-democrats-release-evidence-showing-trump-first-family-failed-to) about reporting these gifts. The current minimum value of reportable gifts is [$480](https://www.gsa.gov/policy-regulations/policy/personal-property-policy-overview/special-programs/foreign-gifts).

This project uses Large Language Models (LLMs), specifically Claude 3 Sonnet and Claude 3 Haiku, to extract structured information from these unstructured text reports and convert it into JSON format. The [JSON data](https://raw.githubusercontent.com/dwillis/all-foreign-gifts-around-us/main/combined_with_names.json) can then be used for further analysis, visualization, or integration with other systems.

## Data Source

The source data for this project is a text file containing excerpts from the Federal Register, specifically the sections related to gift reports. The text file is structured with sections separated by the string "Federal Register / Vol.".

## Data Extraction Process

The data extraction process involves the following steps:

1. **Splitting the Text**: The source text file is split into sections based on the "Federal Register / Vol." separator.
2. **AI-Assisted Extraction**: Each section is passed to an LLM (Claude 3 Sonnet) for extracting structured information in JSON format. The LLM is provided with an example JSON structure and instructions to extract relevant gift details from the text.
3. **Parsing and Error Handling**: The output from the LLM is parsed as JSON, with error handling and recovery mechanisms in place to handle invalid or problematic JSON output.
4. **Deduplication and Merging**: The extracted JSON objects from different sections are combined, removing duplicates based on specific keys. The 'disposition' key is handled as an array, merging values from duplicate entries.
5. **Output Generation**: The final merged and deduplicated JSON data is saved to an output file (`combined.json`).
6. **Donor Information Extraction**: A separate process uses Claude 3 Sonnet to extract structured donor information (name, title, country) from the 'foreign_donor' field.
7. **Recipient Information Extraction**: Another process uses Claude 3 Haiku to extract structured recipient information (name, title) from the 'name_and_title' field.
8. **Agency Employee Anonymization**: For items where the recipient is listed as "An Agency Employee", the donor information (name, title, country) is set to empty strings to maintain anonymity.

## Code Overview

The project consists of Python scripts that handle the data extraction, deduplication, and merging processes. The LLMs (Claude 3 Sonnet and Claude 3 Haiku) are integrated using the Anthropic API, and their roles include:

1. Extracting structured JSON objects from unstructured text sections.
2. Extracting donor and recipient information from specific fields.
3. Assisting in writing and refining the Python code for organizing and running the extraction process.

The main scripts in the project are:

- `extract_data.py`: Handles the text splitting, AI-assisted extraction, parsing, and error handling.
- `combine_json.py`: Combines the extracted JSON objects from different sections, handles deduplication, and merges the 'disposition' values.
- `extract_donors.py`: Extracts structured donor information from the 'foreign_donor' field.
- `extract_recipients.py`: Extracts structured recipient information from the 'name_and_title' field.
- `agency_employees.py`: Sets donor information to empty strings for items where the recipient is "An Agency Employee".

## Data Updates

The Federal Register publishes gift reports annually (and sometimes provides updates to previous records), and this project will be updated periodically to incorporate new data as it becomes available.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## Dependencies

For text extraction from PDFs on Linux systems, you can run the following commands: