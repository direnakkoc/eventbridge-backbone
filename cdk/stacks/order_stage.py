from aws_cdk import Stage
from constructs import Construct

from ..constants import BUS_ACCOUNT
from .order_stack import OrderServiceStack


class OrderStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        OrderServiceStack(
            self,
            "DirenOrderServiceStack",
            bus_account=BUS_ACCOUNT,
            identifier="order-service",
        )
