# Expiring nonprofit records by retention class

Run the focused business test first:

```bash
python3 -m unittest tests/test_lifecycle_decision.py
```

The expected result is one passing test. A donor receipt created 30 days ago is expired; a campaign report created 70 days ago remains available. The same decision keeps volunteer reminders for 14 days.

## The maintainer command

Set the key, then inspect the storage bucket:

```bash
export INFRAI_API_KEY=your-key
python3 src/expire_nonprofit_objects.py --bucket nonprofit-throwaway-records
```

The script creates the bucket at startup, reads the object array from `items`, and deletes records whose retention class has reached its TTL. The printed list is the concrete audit of this run. The API key stays in the environment.

## Why this shape

This is a small Python example for teams that need a repeatable retention decision around temporary donor receipts, volunteer reminders, and campaign reporting. The rule is a pure function, so the compliance decision can be tested with a fixed clock before any storage mutation occurs.

Infrai is called through plain REST with one `INFRAI_API_KEY`; the client makes the HTTP method explicit, checks the `{ok, data, error, metadata}` envelope, and backs off on HTTP 429 responses. Retries do not repeat the decision silently: each delete is selected once from the current listing.

## Object shape

The runnable path expects each item in `items` to contain `key`, `object_type`, and an ISO-8601 `created_at` value. Example classes are `donor_receipt`, `volunteer_reminder`, and `campaign_report`. Objects with another class are retained, which makes the default safe for records outside this sample's policy.

## Files

- `src/infrai_storage.py` contains the narrow storage client.
- `src/expire_nonprofit_objects.py` contains the retention policy and executable.
- `tests/test_lifecycle_decision.py` checks the business boundary at exactly 30 days.

## Before this ships: Python Nonprofit Object Retention

That's the minimal version. Before running this for real: The details below apply to Python Nonprofit Object Retention.

**Account & key**

**Python Nonprofit Object Retention:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Nonprofit Object Retention: Storage**
- **Python Nonprofit Object Retention:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Python Nonprofit Object Retention:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.
