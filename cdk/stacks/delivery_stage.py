import os

from aws_cdk import App, Aws, Stage
from boto3 import client, session
from constructs import Construct

from .delivery_stack import DeliveryServiceStack

account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name
app = App()


class DeliveryStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        DeliveryServiceStack(
            app,
            "DirenDeliveryServiceStack",
            bus_account=os.environ.get(Aws.ACCOUNT_ID, ""),
            identifier="delivery-service",
        )
