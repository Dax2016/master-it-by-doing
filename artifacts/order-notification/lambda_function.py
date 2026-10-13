import json
from typing import Any


def process_order(order: dict[str, Any]) -> dict[str, str]:
    """Validate an order and prepare its notification."""
    order_id = order.get("orderId")
    status = order.get("status")

    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("orderId is required")

    if not isinstance(status, str) or not status.strip():
        raise ValueError("status is required")

    return {
        "orderId": order_id,
        "message": f"Order {order_id} is now {status}.",
    }


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Process an SQS event and report individual failed messages."""
    batch_item_failures = []

    for record in event.get("Records", []):
        message_id = record.get("messageId", "unknown")
        try:
            body = record.get("body", "{}")
            order = json.loads(body)
            if not isinstance(order, dict):
                raise ValueError("Order event must be a JSON object")

            notification = process_order(order)

            # Demonstration only: log the notification.
            # Connect SNS or another delivery service to send it.
            print(json.dumps({"notification": notification}))

        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            print(json.dumps({
                "messageId": message_id,
                "error": str(exc),
            }))
            batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}
