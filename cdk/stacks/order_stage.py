import os

from aws_cdk import Environment
from boto3 import client, session
from constructs import Construct

from .base_stage import BaseStage, BaseStageProps
from .order_stack import OrderServiceStack

account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name


class OrderStage(BaseStage):
    def __init__(self, scope: Construct, id: str, props: BaseStageProps) -> None:
        super().__init__(scope, id, props)

        OrderServiceStack(
            self,
            "DirenOrderServiceStack",
            env=Environment(
                account=os.environ.get("order-service-account", account),
                region=os.environ.get("AWS_DEFAULT_REGION", region),
            ),
            bus_account=props.bus_account,
            identifier="order-service",
        )
