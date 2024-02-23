import json
import os

import boto3
from aws_lambda_powertools import Logger

logger = Logger()
logger.info("event-sender")
events_client = boto3.client("events")

BUS_ARN = os.environ["BUS_ARN"]


class EventSender:
    def __init__(self, service_name):
        self.service_name = service_name

    def send(self, detail_type: str, data: str):
        params = {
            "Entries": [
                {
                    "EventBusName": BUS_ARN,
                    "Source": self.service_name,
                    "DetailType": detail_type,
                    "Detail": json.dumps({"data": data, "meta": {}}),
                }
            ]
        }

        logger.info(params, "Sending events")
        try:
            response = events_client.put_events(Entries=params["Entries"])
            logger.info(response, "PutEventsCommand response")
            return response
        except Exception as e:
            logger.error(e, "Error sending events to EventBridge")
