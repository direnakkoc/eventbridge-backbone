import json
import os
import time
from uuid import uuid4

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from event_util import EventSender

SERVICE_IDENTIFIER = os.environ["SERVICE_IDENTIFIER"]
if not SERVICE_IDENTIFIER:
    raise ValueError("SERVICE_IDENTIFIER env var is required")

logger = Logger()

event_sender = EventSender(SERVICE_IDENTIFIER, logger)


@logger.inject_lambda_context(log_event=True, service_identifier=SERVICE_IDENTIFIER)
def handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)

    order_id = str(uuid4())
    order = {"order_id": order_id, "created_at": int(time.time() * 1000)}

    event_sender.send("Order.Created", order)

    return {"statusCode": 201, "body": json.dumps(order)}


def handle_delivery_update(event: dict, context: LambdaContext) -> dict:
    logger.info(event)

    order = event["detail"]["data"]["order"]
    delivered_at = event["detail"]["data"]["delivered_at"]

    # how to convert spread operator for order in python
    updated_order = {
        "order": order,
        "delivered_at": delivered_at,
        "updated_at": int(time.time() * 1000),
    }

    event_sender.send("Order.Updated", updated_order)

    return updated_order
