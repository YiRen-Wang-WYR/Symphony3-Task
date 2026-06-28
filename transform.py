import csv
import json
import os
from datetime import datetime
import re

def clean_name(full_name):
    if full_name is None:
        return None, None
    full_name = full_name.strip()

    if full_name == "":
        return None, None

    parts = full_name.split()

    if len(parts) < 2:
        return None, None
    
    first_name = parts[0].capitalize()
    last_name = " ".join(parts[1:]).title()

    return first_name, last_name

def parse_date(date_value):
    if date_value is None:
        return None
    
    date_value = date_value.strip()
    
    if date_value == "":
        return None
    
    possible_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%d-%b-%Y",
        "%B, %d, %Y",
    ]

    for date_format in possible_formats:
        try:
            parsed_date = datetime.strptime(date_value, date_format)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None

def validate_email(email):
    if email is None:
        return None
    
    email = email.strip()

    if email == "":
        return None

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if re.match(pattern, email):
        return email.lower()
    
    return None

def normalise_phone(phone):
    if phone is None:
        return None
    
    phone = phone.strip()

    if phone == "":
        return None
    
    return phone

def map_status(status):
    if status is None:
        return "NEEDS_REVIEW"
    
    status = status.strip().lower()

    if status == "active":
        return "ACTIVE"
    elif status == "inactive":
        return "INACTIVE"
    elif status == "pending":
        return "PENDING"
    else:
        return "NEEDS_REVIEW"

def transform_record(row):
    first_name, last_name = clean_name(row.get("FullName"))
    date_of_birth = parse_date(row.get("DOB"))
    last_updated = parse_date(row.get("LastUpdated"))
    email = validate_email(row.get("Email"))
    phone = normalise_phone(row.get("Phone"))
    status = map_status(row.get("AccountStatus"))

    transformed = {
        "ratepayerId": row.get("RecordID", "").strip() if row.get("RecordID") else None,
        "firstName": first_name,
        "lastName": last_name,
        "dateOfBirth": date_of_birth,
        "email": email,
        "phone": phone,
        "address": {
            "line1": row.get("Address", "").strip() if row.get("Address") else None,
            "suburb": row.get("Suburb", "").strip() if row.get("Suburb") else None,
            "postcode": row.get("Postcode", "").strip() if row.get("Postcode") else None,
        },
        "status": status,
        "lastUpdated": last_updated,
    }

    return transformed

def validate_record(record):
    reasons = []

    if record["firstName"] is None or record["lastName"] is None:
        reasons.append("Missing first name or last name")

    if record["dateOfBirth"] is None:
        reasons.append("Invalid or missing date of birth")

    postcode = record["address"]["postcode"]

    if postcode is None:
        reasons.append("Missing postcode")
    elif not re.match(r"^\d{4}$", postcode):
        reasons.append("Invalid postcode format")
    
    if record["lastUpdated"] is None:
        reasons.append("Invalid or missing last updated date")

    if len(reasons) > 0:
        return False, reasons
    
    return True, []

def find_potential_duplicates(records):
    seen = {}
    duplicates = []

    for record in records:
        first_name = record["firstName"]
        last_name = record["lastName"]
        date_of_birth = record["dateOfBirth"]

        key = (
            first_name.lower(),
            last_name.lower(),
            date_of_birth
        )

        if key in seen:
            duplicates.append({
                "matchedRecords": [seen[key], record["ratepayerId"]],
                "reason": "Same name and date of birth"
            })
        else:
            seen[key] = record["ratepayerId"]

    return duplicates

def main():
    input_file = "source_data/legacy_crm_export.csv"
    output_folder = "output"

    valid_records = []
    rejected_records = []

    print("Starting to read the CSV file...")

    with open(input_file, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transformed = transform_record(row)
            is_valid, reasons = validate_record(transformed)

            if is_valid:
                valid_records.append(transformed)
            else:
                rejected_records.append({
                    "recordId": row.get("RecordID"),
                    "reasons": reasons,
                    "originalRecord": row
                })

    potential_duplicates = find_potential_duplicates(valid_records)

    summary = {
        "totalRecordsProcessed": len(valid_records) + len(rejected_records),
        "successfullyTransformed": len(valid_records),
        "rejected": len(rejected_records),
        "potentialDuplicateGroupsFlagged": len(potential_duplicates),
        "potentialDuplicates": potential_duplicates
    }

    os.makedirs(output_folder, exist_ok=True)

    with open("output/transformed_records.json", mode="w", encoding="utf-8") as file:
        json.dump(valid_records, file, indent=2)

    with open("output/rejected_records.json", mode="w", encoding="utf-8") as file:
        json.dump(rejected_records, file, indent=2)

    with open("output/summary.json", mode="w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("Total records processed:", summary["totalRecordsProcessed"])
    print("Successfully transformed:", summary["successfullyTransformed"])
    print("Rejected:", summary["rejected"])
    print("Potential duplicates flagged:", summary["potentialDuplicateGroupsFlagged"])
    print("Output files created:")
    print("- output/transformed_records.json")
    print("- output/rejected_records.json")
    print("- output/summary.json")
if __name__ == "__main__":
    main()