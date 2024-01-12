import os

from aws_cdk import App, Environment
from boto3 import client, session
from constructs import Construct

from .base_stage import BaseStage
from .order_stack import OrderServiceStack

account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name
app = App()


class OrderStage(BaseStage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        bus_account: str,
        identifier: str,
        env: Environment,
    ) -> None:
        super().__init__(scope, id, bus_account, identifier, env)

        OrderServiceStack(
            app,
            "DirenOrderServiceStack",
            bus_account=self.bus_account,
            identifier="order-service",
            env=Environment(
                account=os.environ.get("order-service-account", account),
                region=os.environ.get("AWS_DEFAULT_REGION", region),
            ),
        )
