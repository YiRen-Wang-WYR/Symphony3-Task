import csv

def main():
    input_file = "source_data/legacy_crm_export.csv"
    print("Starting to read the CSV file...")
    with open(input_file, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        count = 0

        print("CSV columns:")
        print(reader.fieldnames)

        for row in reader:
            print(row)
            count += 1

        print("Total rows read:", count)

if __name__ == "__main__":
    main()