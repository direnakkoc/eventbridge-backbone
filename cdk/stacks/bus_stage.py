from aws_cdk import Stage
from constructs import Construct

from ..constants import DELIVERY_SERVICE_ACCOUNT, ORDER_SERVICE_ACCOUNT
from .bus_stack import BusStack

ORDER_SERVICE_IDENTIFIER = "order-service"
DELIVERY_SERVICE_IDENTIFIER = "delivery-service"


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
                ORDER_SERVICE_IDENTIFIER: ORDER_SERVICE_ACCOUNT,
                DELIVERY_SERVICE_IDENTIFIER: DELIVERY_SERVICE_ACCOUNT,
            },
        )
