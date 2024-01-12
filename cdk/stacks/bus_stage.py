import os
from typing import Dict

from aws_cdk import App, Environment, Stage
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
        identifier: Dict,
        env: Environment,
    ) -> None:
        super().__init__(scope, id, identifier, env)

        BusStack(
            app,
            "DirenBusStack",
            identifier={
                ORDER_SERVICE_IDENTIFIER: order_account,
                DELIVERY_SERVICE_IDENTIFIER: delivery_account,
            },
            env=Environment(
                account=os.environ.get("bus-account", account),
                region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
            ),
        )
