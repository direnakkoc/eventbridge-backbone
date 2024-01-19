import os

from aws_cdk import App, Stage
from boto3 import client, session
from constructs import Construct

from .bus_stack import BusStack

account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name
app = App()

ORDER_SERVICE_IDENTIFIER = "order-service"
DELIVERY_SERVICE_IDENTIFIER = "delivery-service"
order_account = os.environ.get("order-service-account")
delivery_account = os.environ.get("delivery-service-account")


class BusStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        BusStack(
            self,
            "DirenBusStack",
            application_account_by_identifier={
                ORDER_SERVICE_IDENTIFIER: order_account,
                DELIVERY_SERVICE_IDENTIFIER: delivery_account,
            },
        )
