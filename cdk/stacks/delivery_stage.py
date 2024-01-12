import os

from aws_cdk import App, Environment
from boto3 import client, session
from constructs import Construct

from .base_stage import BaseStage
from .delivery_stack import DeliveryServiceStack

account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name
app = App()


class DeliveryStage(BaseStage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        bus_account: str,
        identifier: str,
        env: Environment,
    ) -> None:
        super().__init__(scope, id, bus_account, identifier, env)

        DeliveryServiceStack(
            app,
            "DirenDeliveryServiceStack",
            bus_account=self.bus_account,
            identifier="delivery-service",
            env=Environment(
                account=os.environ.get("delivery-service-account", account),
                region=os.environ.get("AWS_DEFAULT_REGION", region),
            ),
        )
