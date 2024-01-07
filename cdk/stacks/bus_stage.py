from typing import Dict

from aws_cdk import Stage, StageProps
from constructs import Construct

from .bus_stack import BusStack


class BusStageProps(StageProps):
    application_account_by_identifier: Dict[str, str]


class BusStage(Stage):
    def __init__(self, scope: Construct, id: str, props: BusStageProps) -> None:
        super().__init__(scope, id, props)

        BusStack(
            self,
            "DirenBusStack",
            application_account_by_identifier=props.application_account_by_identifier,
        )
