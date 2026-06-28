# Rates System — Target Schema & Business Rules

The Rates system expects each ratepayer record as a JSON object with the following shape:

```json
{
  "ratepayerId": "string",
  "firstName": "string",
  "lastName": "string",
  "dateOfBirth": "YYYY-MM-DD",
  "email": "string or null",
  "phone": "string or null",
  "address": {
    "line1": "string",
    "suburb": "string",
    "postcode": "string (exactly 4 digits)"
  },
  "status": "ACTIVE | INACTIVE | PENDING | NEEDS_REVIEW",
  "lastUpdated": "YYYY-MM-DD"
}
```

## Field notes

- **ratepayerId** — carry over the source `RecordID`.
- **firstName / lastName** — split from the source `FullName`. Names should be in standard capitalisation (e.g. "John Smith", not "JOHN SMITH" or "john smith").
- **dateOfBirth / lastUpdated** — must be normalised to ISO 8601 (`YYYY-MM-DD`). The source export is not consistent about date format.
- **email** — should look like a valid email address. If it's missing or clearly malformed, that's worth a judgment call (see below).
- **phone** — no single required format is specified by the Rates system beyond "a phone number a human could dial." Normalise it sensibly and consistently.
- **postcode** — must be exactly 4 digits. Victorian postcodes in this dataset are all in the 3000s.
- **status** — must be one of `ACTIVE`, `INACTIVE`, `PENDING`, or `NEEDS_REVIEW`.

## Business rules

1. **Required fields**: a record without a name or without a date of birth cannot be transformed — reject it with a clear reason.
2. **Status mapping**: the source data isn't consistent about how it represents status. You can confidently map:
   - Variants of "active" → `ACTIVE`
   - Variants of "inactive" → `INACTIVE`
   - "Pending" → `PENDING`

   You'll encounter a few other values in the source data that don't map cleanly (e.g. abbreviations, or terms that don't appear in the list above). Don't guess silently — map anything you're not confident about to `NEEDS_REVIEW` and explain your reasoning in your notes.

3. **Postcode validity**: if the postcode isn't exactly 4 digits (or is missing), reject the record rather than guessing or truncating it.

4. **Email validity**: if an email is missing or malformed, that's a genuine judgment call — you could reject the record, or transform it with `email: null` and flag it some other way. Either is defensible. Pick one, and explain why in your notes.

5. **Duplicate detection**: a handful of records in the source data appear to represent the same person (matching name and date of birth, possibly with formatting differences). These shouldn't be silently merged or silently kept as separate ratepayers — flag them so a human can review, and reflect this in your summary output.

6. **Whitespace / casing**: the source data has some inconsistent capitalisation and stray whitespace. Output should be clean.

There's no single "correct" answer here for every edge case — we're more interested in seeing sensible, defensible decisions, applied consistently, and clearly explained.
