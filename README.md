# Symphony3 Backend Engineer Interview Task

This repository contains my solution for the Symphony3 Backend/API Engineer take-home task.

The project includes two parts:

1. Data conversion from a legacy CRM export into the Rates system target format
2. A simple Fine Event Ingestion API

---

## Project structure

```text
Symphony3-task/
│
├── source_data/
│   └── legacy_crm_export.csv
│
├── target_schema/
│   └── rates_system_schema.md
│
├── output/
│   ├── transformed_records.json
│   ├── rejected_records.json
│   └── summary.json
│
├── event_api/
│   ├── main.py
│   └── events.json
│
├── transform.py
├── NOTE.md
└── README.md
```

---

# Task 1 - Data Conversion

## How to run

From the project root folder, run:

```bash
python transform.py
```

The script reads:

```text
source_data/legacy_crm_export.csv
```

and writes the output files to:

```text
output/transformed_records.json
output/rejected_records.json
output/summary.json
```

## Output summary

The script processed 18 source records.

```text
Total records processed: 18
Successfully transformed: 13
Rejected: 5
Potential duplicate groups flagged: 2
```

## Main decisions

For the data conversion task, I made the following judgement calls:

* Missing or malformed email addresses are transformed to `null` rather than causing the whole record to be rejected.
* Unknown or ambiguous account statuses are mapped to `NEEDS_REVIEW`.
* Records with missing names, invalid dates of birth, or invalid postcodes are rejected.
* Records with invalid `LastUpdated` values are rejected because the target schema expects a valid ISO date.
* Potential duplicates are flagged in the summary rather than automatically merged.

More details about the data conversion assumptions and judgement calls are included in:

```text
NOTE.md
```

---

# Task 2 - Fine Event Ingestion API

This part implements a small backend API for receiving and retrieving fine events.

## How to run

Install dependencies:

```bash
pip install fastapi uvicorn
```

Run the API from the project root:

```bash
python -m uvicorn event_api.main:app --reload
```

Open the API documentation in the browser:

```text
http://127.0.0.1:8000/docs
```

---

## Endpoints

### POST /events

Creates a new fine event.

Example request:

```json
{
  "eventType": "NEW_FINE",
  "customerId": "REC001",
  "amount": 150.75,
  "timestamp": "2024-11-10T10:30:00Z"
}
```

Allowed event types are:

```text
NEW_FINE
PAYMENT_RECEIVED
OVERDUE
```

The API validates:

* event type
* customer ID
* amount
* timestamp

If the payload is valid, the API transforms it into an internal event model by adding an `eventId` and normalising the timestamp.

---

### GET /events/{customerId}

Returns all events for the given customer ID.

Example:

```text
GET /events/REC001
```

Example response:

```json
{
  "customerId": "REC001",
  "events": [
    {
      "eventId": "generated-id",
      "eventType": "NEW_FINE",
      "customerId": "REC001",
      "amount": 150.75,
      "timestamp": "2024-11-10T10:30:00+00:00"
    }
  ]
}
```

---

## Persistence

Events are stored in:

```text
event_api/events.json
```

I used JSON file storage because this is a small interview task and does not require a full database. This keeps the implementation simple and easy to run locally.

For a production system, I would use a database such as SQLite or PostgreSQL.

---

## Design decisions

* I used FastAPI because it is quick to build and provides automatic API documentation through Swagger UI.
* I used a request model to define the expected JSON structure.
* I used a fixed allow-list for event types so unknown event types are rejected.
* I added an `eventId` to each event to represent an internal model.
* I normalised timestamps into ISO format before saving.
* I used JSON file persistence to keep the implementation lightweight.

---

## Trade-offs

* JSON file storage is simple but not suitable for concurrent production writes.
* There is no authentication or authorisation.
* There is no database indexing.
* Validation is focused on the task requirements rather than being production-grade.
* The API does not currently check whether the customer ID exists in the transformed ratepayer data.

---

## What I would improve with more time

With more time, I would add:

* Unit tests for valid and invalid event payloads
* SQLite or PostgreSQL persistence
* Authentication and authorisation for API clients
* Structured logging and audit trails
* Pagination for customers with many events
* Customer ID validation against the transformed ratepayer records
* Better error response formatting for client applications
