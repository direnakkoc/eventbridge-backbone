import json
import os
import time
from uuid import uuid4

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    EventBridgeEvent,
)
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
def handle_order_create(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:
    logger.info(event)

    order_id = str(uuid4())
    order = {"order_id": order_id, "created_at": int(time.time() * 1000)}

    event_sender.send("Order.Created", order)  # type: ignore

    return {"statusCode": 201, "body": json.dumps(order)}


def handle_delivery_update(event: EventBridgeEvent, context: LambdaContext) -> dict:
    logger.info(event)

    order = event["detail"]["data"]
    delivered_at = event["detail"]["data"]["delivered_at"]

    updated_order = {
        "order": order,
        "delivered_at": delivered_at,
        "updated_at": int(time.time() * 1000),
    }

    event_sender.send("Order.Updated", updated_order)  # type: ignore

    return updated_order
