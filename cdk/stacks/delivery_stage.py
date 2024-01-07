import os

from aws_cdk import Environment
from boto3 import client, session
from constructs import Construct

from .base_stage import BaseStage, BaseStageProps
from .delivery_stack import DeliveryServiceStack

account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name


class DeliveryStage(BaseStage):
    def __init__(self, scope: Construct, id: str, props: BaseStageProps) -> None:
        super().__init__(scope, id, props)

        DeliveryServiceStack(
            self,
            "DirenDeliveryServiceStack",
            env=Environment(
                account=os.environ.get("delivery-service-account", account),
                region=os.environ.get("eu-west-1", region),
            ),
            identifier="delivery-service",
            bus_account=props.bus_account,
        )
