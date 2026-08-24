"""Expire temporary nonprofit records while preserving audit-relevant objects."""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone

if __package__:
    from .infrai_storage import StorageClient, infrai_client
else:
    from infrai_storage import StorageClient, infrai_client


TTL_DAYS = {"donor_receipt": 30, "volunteer_reminder": 14, "campaign_report": 90}


@dataclass(frozen=True)
class ExpiryDecision:
    key: str
    object_type: str
    expires: bool


def expiry_decision(key: str, object_type: str, created_at: datetime, now: datetime) -> ExpiryDecision:
    age_days = (now - created_at).total_seconds() / 86400
    return ExpiryDecision(key, object_type, object_type in TTL_DAYS and age_days >= TTL_DAYS[object_type])


def run(bucket: str, now: datetime, client: StorageClient) -> list[str]:
    infrai = client
    infrai.storage.bucket.create(name=bucket)
    listing = infrai.storage.object.list(bucket) or {}
    removed: list[str] = []
    for item in listing.get("items", []):
        key = item["key"]
        object_type = item.get("object_type", "")
        created_at = datetime.fromisoformat(item["created_at"]).astimezone(timezone.utc)
        decision = expiry_decision(key, object_type, created_at, now)
        if decision.expires:
            infrai.storage.object.delete(bucket, key)
            removed.append(key)
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove expired nonprofit throwaway objects.")
    parser.add_argument("--bucket", default="nonprofit-throwaway-records")
    args = parser.parse_args()
    removed = run(args.bucket, datetime.now(timezone.utc), infrai_client())
    print("expired objects:", ", ".join(removed) if removed else "none")


if __name__ == "__main__":
    main()
