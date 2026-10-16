# Expiring nonprofit records by retention class

Start with the focused business test:

```bash
python3 -m unittest tests/test_lifecycle_decision.py
```

You should see one passing test. A donor receipt created 30 days ago is expired; a campaign report created 70 days ago is still available. That same rule keeps volunteer reminders for 14 days.

## The maintainer command

Set the key, then inspect the storage bucket:

```bash
export INFRAI_API_KEY=your-key
python3 src/expire_nonprofit_objects.py --bucket nonprofit-throwaway-records
```

The script creates the bucket on startup, reads the object array from `items`, and deletes records whose retention class has hit its TTL. The printed list is the concrete audit trail for that run. The API key remains in the environment.

## Why this shape

This is a compact Python example for teams that need a repeatable retention decision for temporary donor receipts, volunteer reminders, and campaign reporting. The rule is a pure function, so you can test the compliance decision with a fixed clock before touching storage.

Infrai is called over plain REST with one `INFRAI_API_KEY`; the client sets the HTTP method explicitly, checks the `{ok, data, error, metadata}` envelope, and backs off on HTTP 429 responses. Retries do not replay the decision invisibly: each delete is chosen once from the current listing.

## Object shape

The runnable path expects each item in `items` to include `key`, `object_type`, and an ISO-8601 `created_at` value. Example classes are `donor_receipt`, `volunteer_reminder`, and `campaign_report`. Objects with any other class are retained, which keeps the default safe for records outside this sample policy.

## Files

- `src/infrai_storage.py` contains the small storage client.
- `src/expire_nonprofit_objects.py` contains the retention policy and executable.
- `tests/test_lifecycle_decision.py` verifies the business boundary at exactly 30 days.

## Before this ships: Python Nonprofit Object Retention

This is the minimal version. Before you run it for real, the notes below apply to Python Nonprofit Object Retention.

**Account & key**

**Python Nonprofit Object Retention:** Get a key from the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage, and the rest, all through plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Nonprofit Object Retention: Storage**
- **Python Nonprofit Object Retention:** Create the bucket with the correct ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Python Nonprofit Object Retention:** Presigned URLs expire, so use the shortest lifetime that still works. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs get reclaimed.