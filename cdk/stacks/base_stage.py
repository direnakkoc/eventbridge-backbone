from aws_cdk import StackProps, Stage
from constructs import Construct

from cdk.stacks.base_stack import BaseStack


class BaseStageProps(StackProps):
    bus_account: str
    identifier: str


class BaseStage(Stage):
    stack: BaseStack

    def __init__(self, scope: Construct, id: str, props: BaseStageProps) -> None:
        super().__init__(scope, id, props)
