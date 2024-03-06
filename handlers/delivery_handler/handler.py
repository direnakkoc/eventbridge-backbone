import os
import uuid

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from event_util import EventSender

SERVICE_IDENTIFIER = os.environ["SERVICE_IDENTIFIER"]
if not SERVICE_IDENTIFIER:
    raise ValueError("SERVICE_IDENTIFIER env var is required")

SERVICE = os.environ["SERVICE"]
POWERTOOLS_NAMESPACE_NAME = os.environ["POWERTOOLS_NAMESPACE_NAME"]
ENVIRONMENT = os.environ["ENVIRONMENT"]

logger = Logger()
tracer = Tracer(service=SERVICE)

metrics = Metrics(service=SERVICE, namespace=POWERTOOLS_NAMESPACE_NAME)
metrics.set_default_dimensions(environment=ENVIRONMENT)

event_sender = EventSender(SERVICE_IDENTIFIER)


@logger.inject_lambda_context(log_event=True)
@metrics.log_metrics()
@tracer.capture_lambda_handler()

# Order Delivery processing - handle EventBridge events for Order.Created
# and emit a Delivery.UpdatedEvent
def handle_order_created(event: dict, context: LambdaContext) -> dict:
    logger.info(event)

    order = event["detail"]["data"]

    import time

    # Sleep to simulate some delivery processing
    time.sleep(5)

    delivery_update = {
        "order": order,
        "delivered_at": int(time.time() * 1000),
        "delivery_id": str(uuid.uuid4()),
    }
    event_sender.send("Delivery.Updated", delivery_update)
