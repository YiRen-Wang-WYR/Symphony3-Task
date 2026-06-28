from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import os
import uuid


app = FastAPI()

EVENTS_FILE = "event_api/events.json"

ALLOWED_EVENT_TYPES = [
    "NEW_FINE",
    "PAYMENT_RECEIVED",
    "OVERDUE"
]


class EventRequest(BaseModel):
    eventType: str
    customerId: str
    amount: float
    timestamp: str


def load_events():
    if not os.path.exists(EVENTS_FILE):
        return []

    with open(EVENTS_FILE, mode="r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_events(events):
    with open(EVENTS_FILE, mode="w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)


def validate_timestamp(timestamp):
    try:
        if timestamp.endswith("Z"):
            timestamp = timestamp.replace("Z", "+00:00")

        parsed_timestamp = datetime.fromisoformat(timestamp)
        return parsed_timestamp.isoformat()
    except ValueError:
        return None


@app.post("/events")
def create_event(event: EventRequest):
    if event.eventType not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid event type"
        )

    if event.customerId.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Customer ID is required"
        )

    if event.amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Amount cannot be negative"
        )

    parsed_timestamp = validate_timestamp(event.timestamp)

    if parsed_timestamp is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid timestamp format"
        )

    new_event = {
        "eventId": str(uuid.uuid4()),
        "eventType": event.eventType,
        "customerId": event.customerId.strip(),
        "amount": event.amount,
        "timestamp": parsed_timestamp
    }

    events = load_events()
    events.append(new_event)
    save_events(events)

    return {
        "message": "Event created successfully",
        "event": new_event
    }


@app.get("/events/{customer_id}")
def get_events_by_customer(customer_id: str):
    events = load_events()

    customer_events = []

    for event in events:
        if event["customerId"] == customer_id:
            customer_events.append(event)

    return {
        "customerId": customer_id,
        "events": customer_events
    }


@app.get("/")
def root():
    return {
        "message": "Fine Event Ingestion API is running"
    }