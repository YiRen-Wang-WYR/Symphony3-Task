import csv
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
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%B %d, %Y",
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
        return "NEED_REVIEW"
    
    status = status.strip().lower()

    if status == "active":
        return "ACTIVE"
    elif status == "inactive":
        return "INACTIVE"
    elif status == "pending":
        return "PENDING"
    else:
        return "NEED_REVIEW"

def transform_record(row):
    first_name, last_name = clean_name(row.get("Full Name"))
    date_of_birth = parse_date(row.get("Date of Birth"))
    last_update = parse_date(row.get("Last Update"))
    email = validate_email(row.get("Email"))
    phone = normalise_phone(row.get("Phone Number"))
    status = map_status(row.get("Status"))

    transformed = {
        "ratepayerID": row.get("RecordID", "").strip() if row.get("RecordID") else None,
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
        "lastUpdate": last_update,
    }

    return transformed


def main():
    input_file = "source_data/legacy_crm_export.csv"
    print("Starting to read the CSV file...")
    with open(input_file, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            transformed = transform_record(row)
            print(transformed)

if __name__ == "__main__":
    main()