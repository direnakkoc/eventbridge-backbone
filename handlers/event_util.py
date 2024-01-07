import json
from multiprocessing import process

import boto3
from aws_lambda_powertools import Logger

logger = Logger()
logger._get_logger("event-sender")
events_client = boto3.client("events")


BUS_ARN = process.env  # check this???


class EventSender:
    service_name: str

    def __init__(self, service_name):
        self.service_name = service_name

    def send(self, detail_type, data):
        params = events_client.put_events(
            Entries=[
                {
                    "EventBusName": BUS_ARN,
                    "Source": self.service_name,
                    "DetailType": detail_type,
                    "Detail": json.dumps({"data": data, "meta": {}}),
                }
            ]
        )
        logger.info(params, "Sending events")
        # return client.put_events(params)
        return params
