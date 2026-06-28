# NOTES

## How to run

This project uses Python standard libraries only. No external packages are required.

From the project root folder, run:

```bash
python transform.py
```

The script reads the source CSV file from:

```text
source_data/legacy_crm_export.csv
```

It creates the following output files:

```text
output/transformed_records.json
output/rejected_records.json
output/summary.json
```

## What the script does

The script reads each record from the legacy CRM export and transforms it into the target Rates system format.

For each record, it:

* Cleans whitespace and inconsistent casing
* Splits `FullName` into `firstName` and `lastName`
* Converts dates into ISO format: `YYYY-MM-DD`
* Validates and normalises email values
* Carries over phone numbers in a consistent cleaned format
* Converts address fields into the nested `address` object
* Maps account status values into the target status values
* Validates required fields and postcode format
* Separates valid transformed records from rejected records
* Flags potential duplicate records based on matching name and date of birth

## Assumptions and judgement calls

### Email handling

If an email address is missing or malformed, I chose to transform the record with:

```json
"email": null
```

instead of rejecting the whole record.

My reasoning is that email is not the only way to contact a ratepayer. The record may still contain a valid phone number and address, so rejecting the entire record only because of email could cause unnecessary data loss.

### Status mapping

Clear variants of active, inactive, and pending are mapped to:

```text
ACTIVE
INACTIVE
PENDING
```

Any account status that does not clearly match these values is mapped to:

```text
NEEDS_REVIEW
```

I chose this approach because guessing an unclear status could incorrectly change a ratepayer's account state. Mapping uncertain statuses to `NEEDS_REVIEW` keeps the record usable while still flagging it for human review.

### Rejected records

I rejected records that failed required structural or business validation.

In this implementation, records are rejected if:

* The name is missing or cannot be split into first and last name
* The date of birth is missing or invalid
* The postcode is missing
* The postcode is not exactly 4 digits
* The `LastUpdated` value cannot be parsed into a valid date

I also rejected invalid `LastUpdated` values because the target schema expects `lastUpdated` to be a valid ISO date. I did not guess or default this value because it is important for auditability.

### Duplicate detection

Potential duplicates are detected using:

```text
firstName + lastName + dateOfBirth
```

If two records have the same cleaned name and date of birth, they are flagged in `summary.json`.

I did not merge duplicate records automatically because that could accidentally combine two records that should remain separate. Instead, I flagged them for human review.

### Address handling

Some address values may have small formatting inconsistencies in the source data. I cleaned leading and trailing whitespace but did not attempt advanced address correction, because guessing address changes could introduce incorrect data. With more time, I would use a proper address validation service.

## Output summary

The script processed 18 source records.

```text
Total records processed: 18
Successfully transformed: 13
Rejected: 5
Potential duplicate groups flagged: 2
```

The rejected records were:

```text
REC003 - Invalid postcode format
REC005 - Missing first name or last name
REC007 - Invalid postcode format
REC011 - Missing postcode
REC018 - Invalid or missing last updated date
```

The potential duplicate groups flagged were:

```text
REC001 and REC006 - Same name and date of birth
REC002 and REC015 - Same name and date of birth
```

## What I would improve with more time

With more time, I would add:

* Unit tests for date parsing, postcode validation, status mapping, and duplicate detection
* Stronger phone number normalisation
* More detailed validation reporting for malformed email addresses
* Address validation using a trusted external service
* Better logging for larger files
* A configuration file for accepted date formats and status mappings

