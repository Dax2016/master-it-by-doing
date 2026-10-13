import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lambda_function import lambda_handler, process_order


class OrderNotificationTests(unittest.TestCase):
    def test_valid_order_creates_notification(self):
        result = process_order({
            "orderId": "ORD-1001",
            "status": "confirmed",
        })
        self.assertEqual(result["orderId"], "ORD-1001")
        self.assertEqual(
            result["message"],
            "Order ORD-1001 is now confirmed.",
        )

    def test_missing_order_id_is_rejected(self):
        with self.assertRaises(ValueError):
            process_order({"status": "confirmed"})

    def test_sqs_success_returns_no_failed_messages(self):
        event = {
            "Records": [{
                "messageId": "msg-001",
                "body": json.dumps({
                    "orderId": "ORD-1001",
                    "status": "confirmed",
                }),
            }]
        }
        with patch("builtins.print"):
            result = lambda_handler(event, None)
        self.assertEqual(result, {"batchItemFailures": []})

    def test_invalid_message_is_reported_as_failed(self):
        event = {
            "Records": [{
                "messageId": "msg-bad",
                "body": json.dumps({"status": "confirmed"}),
            }]
        }
        with patch("builtins.print"):
            result = lambda_handler(event, None)
        self.assertEqual(
            result,
            {"batchItemFailures": [{"itemIdentifier": "msg-bad"}]},
        )


if __name__ == "__main__":
    unittest.main()
