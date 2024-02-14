from aws_cdk import Stage
from constructs import Construct

from ..constants import BUS_ACCOUNT, DELIVERY_SERVICE_IDENTIFIER
from .delivery_stack import DeliveryServiceStack


class DeliveryStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        DeliveryServiceStack(
            self,
            "DirenDeliveryServiceStack",
            bus_account=BUS_ACCOUNT,
            identifier=DELIVERY_SERVICE_IDENTIFIER,
        )
