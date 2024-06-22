import json
import sqlite_utils

# Read JSON data from file
with open("combined_json_with_both_names.json", "r") as file:
    data = json.load(file)

# Create a SQLite database (or connect to it)
db = sqlite_utils.Database("gifts.db")

# Ensure the table schema
table = db["gifts"]
table.create({
    "id": int,
    "name_and_title": str,
    "gift_description": str,
    "received": str,
    "estimated_value": float,
    "disposition": str,
    "foreign_donor": str,
    "circumstances": str,
    "donor_name": str,
    "donor_title": str,
    "donor_country": str,
    "recipient_name": str,
    "recipient_title": str
}, pk="id", if_not_exists=True)

# Insert data into the table with a sequential ID
for idx, record in enumerate(data, start=1):
    if "donor_name" not in record:
        record["donor_name"] = ""
    if "donor_title" not in record:
        record["donor_title"] = ""
    if "donor_country" not in record:
        record["donor_country"] = ""
    if record["disposition"] == []:
        record["disposition"] = ["N/A"]
    disposition = next((d for d in record["disposition"] if d == "Transferred to NARA"), record["disposition"][0])
    
    # Process estimated_value
    if record["estimated_value"] is None:
        estimated_value = None
    elif (record["estimated_value"] == "Unknown" or
        record["estimated_value"] == "In appraisal process" or
        record["estimated_value"].lower().startswith("over")):
        estimated_value = None
    elif record["estimated_value"] == "1000-1500":
        estimated_value = 1000.0
    elif record["estimated_value"] == "300 to 400":
        estimated_value = 300.0
    elif record["estimated_value"] == "225 to 300":
        estimated_value = 225.0
    elif record["estimated_value"] == "":
        estimated_value = None
    else:
        estimated_value = float(record["estimated_value"].replace(",", ""))

    if record["donor_name"] == '':
        record["donor_country"] = None

    if record["donor_name"] == "Kingdom of Saudi Arabia" or record["donor_name"] == "Republic of Iraq":
        record["donor_country"] = record["donor_name"]
        record["donor_name"] = record["donor_title"]
        record["donor_title"] = None

    record_to_insert = {
        "id": idx,
        "name_and_title": record["name_and_title"],
        "gift_description": record["gift_description"],
        "received": record["received"],
        "estimated_value": estimated_value,
        "disposition": disposition,
        "foreign_donor": record["foreign_donor"],
        "circumstances": record["circumstances"],
        "donor_name": record["donor_name"],
        "donor_title": record["donor_title"],
        "donor_country": record["donor_country"],
        "recipient_name": record["recipient_name"],
        "recipient_title": record["recipient_title"]
    }
    table.insert(record_to_insert, pk="id", replace=True)

print("Data successfully inserted into the gifts table.")
