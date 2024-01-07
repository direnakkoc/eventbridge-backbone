import uuid

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from handlers.event_util import EventSender

SERVICE_IDENTIFIER = "delivery-service"
if not SERVICE_IDENTIFIER:
    raise ValueError("SERVICE_IDENTIFIER env var is required")

logger = Logger()

event_sender = EventSender(SERVICE_IDENTIFIER, logger)


@logger.inject_lambda_context(log_event=True, service_identifier=SERVICE_IDENTIFIER)

# Order Delivery processing - handle EventBridge events for Order.Created
# and emit a Delivery.UpdatedEvent
def handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)

    order = event["detail"]["data"]

    import time

    time.sleep(5)

    delivery_update = {
        "order": order,
        "delivered_at": int(time.time() * 1000),
        "delivery_id": str(uuid.uuid4()),
    }
    event_sender.send("Delivery.Updated", delivery_update)
