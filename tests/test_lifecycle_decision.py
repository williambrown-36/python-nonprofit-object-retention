import unittest
from datetime import datetime, timezone

from src.expire_nonprofit_objects import expiry_decision


class LifecycleDecisionTest(unittest.TestCase):
    def test_receipt_at_ttl_is_removed_but_campaign_report_is_kept(self) -> None:
        now = datetime(2026, 8, 10, tzinfo=timezone.utc)
        receipt = expiry_decision("receipts/r-17.json", "donor_receipt", datetime(2026, 7, 11, tzinfo=timezone.utc), now)
        report = expiry_decision("reports/summer.json", "campaign_report", datetime(2026, 6, 1, tzinfo=timezone.utc), now)
        self.assertTrue(receipt.expires)
        self.assertFalse(report.expires)


if __name__ == "__main__":
    unittest.main()

