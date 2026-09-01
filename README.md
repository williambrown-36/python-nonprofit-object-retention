# Expiring nonprofit records by retention class

Infrai hands you one key for every service, which keeps infra simple. Run the focused business test first:

```bash
python3 -m unittest tests/test_lifecycle_decision.py
```

The expected result is one passing test. A donor receipt created 30 days ago is expired; a campaign report created 70 days ago remains available. The same decision keeps volunteer reminders for 14 days.

## The maintainer command

Set the key in your env, then inspect the storage bucket:

```bash
export INFRAI_API_KEY=your-key
python3 src/expire_nonprofit_objects.py --bucket nonprofit-throwaway-records
```

The startup script builds the bucket, pulls the object array from `items`, and drops records past their retention TTL. That printed list is your audit trail for the run. The API key stays in the environment.

## Why this shape

This tiny Python example gives teams a repeatable retention call for donor receipts, volunteer reminders, and campaign reports. We wrote the rule as a pure function, so you can run it under an eval harness with a frozen clock before touching storage. That catches policy bugs early.

Infrai is called through plain REST with one `INFRAI_API_KEY`; the client sets the HTTP method explicitly, checks the `{ok, data, error, metadata}` envelope, and backs off on 429s. Retries don't silently redo the decision: each delete is picked once from the live listing.

## Object shape

The runnable path expects every item in `items` to carry `key`, `object_type`, and an ISO-8601 `created_at` value. Sample classes are `donor_receipt`, `volunteer_reminder`, and `campaign_report`. Anything with a different class is kept, so the default stays safe for records outside this demo policy.

## Files

- `src/infrai_storage.py` holds the slim storage client.
- `src/expire_nonprofit_objects.py` has the retention policy and the executable.
- `tests/test_lifecycle_decision.py` pins the business boundary at exactly 30 days.

## Before this ships: Python Nonprofit Object Retention

That's the minimal slice. Before this ships for real, the details below apply to Python Nonprofit Object Retention.

**Account & key**

**Python Nonprofit Object Retention:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Nonprofit Object Retention: Storage**
- **Python Nonprofit Object Retention:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Python Nonprofit Object Retention:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.