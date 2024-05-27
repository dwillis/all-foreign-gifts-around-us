# All Foreign Gifts Around Us

This project aims to extract structured data from unstructured text published in the Federal Register about gifts provided to U.S. officials by foreign government officials.

## Overview

The Federal Register is the official journal of the United States government, which publishes various notices, rules, and regulatory information. Among these publications are reports detailing gifts received by U.S. government officials from foreign sources. Some presidential administrations are [better than others](https://oversightdemocrats.house.gov/news/press-releases/oversight-democrats-release-evidence-showing-trump-first-family-failed-to) about reporting these gifts. The current minimum value of reportable gifts is [$480](https://www.gsa.gov/policy-regulations/policy/personal-property-policy-overview/special-programs/foreign-gifts).

This project uses a Large Language Model (LLM), specifically Claude 3 Sonnet, to extract structured information from these unstructured text reports and convert it into JSON format. The [JSON data](https://raw.githubusercontent.com/dwillis/all-foreign-gifts-around-us/main/combined_with_names.json) can then be used for further analysis, visualization, or integration with other systems.

## Data Source

The source data for this project is a text file containing excerpts from the Federal Register, specifically the sections related to gift reports. The text file is structured with sections separated by the string "Federal Register / Vol.".

## Data Extraction Process

The data extraction process involves the following steps:

1. **Splitting the Text**: The source text file is split into sections based on the "Federal Register / Vol." separator.
2. **AI-Assisted Extraction**: Each section is passed to an LLM (Claude 3 Sonnet) for extracting structured information in JSON format. The LLM is provided with an example JSON structure and instructions to extract relevant gift details from the text.
3. **Parsing and Error Handling**: The output from the LLM is parsed as JSON, with error handling and recovery mechanisms in place to handle invalid or problematic JSON output.
4. **Deduplication and Merging**: The extracted JSON objects from different sections are combined, removing duplicates based on specific keys. The 'disposition' key is handled as an array, merging values from duplicate entries.
5. **Output Generation**: The final merged and deduplicated JSON data is saved to an output file (`combined.json`).

## Code Overview

The project consists of Python scripts that handle the data extraction, deduplication, and merging processes. The LLM (Claude 3 Sonnet) is integrated using the Anthropic API, and its role includes:

1. Extracting structured JSON objects from unstructured text sections.
2. Assisting in writing and refining the Python code for organizing and running the extraction process.

The main scripts in the project are:

- `extract_data.py`: Handles the text splitting, AI-assisted extraction, parsing, and error handling.
- `combine_json.py`: Combines the extracted JSON objects from different sections, handles deduplication, and merges the 'disposition' values.

## Data Updates

The Federal Register publishes gift reports annually (and sometimes provides updates to previous records), and this project will be updated periodically to incorporate new data as it becomes available.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## Dependencies

For text extraction from PDFs on Linux systems, you can run the following commands:

```
sudo apt-get update
sudo apt-get install libpoppler-cpp-dev
sudo apt-get install poppler-utils
```

Python dependencies are listed in requirements.txt.
