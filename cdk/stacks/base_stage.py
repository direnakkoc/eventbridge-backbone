from aws_cdk import Stage
from constructs import Construct

from cdk.stacks.base_stack import BaseStack


class BaseStage(Stage):
    stack: BaseStack

    def __init__(
        self, scope: Construct, id: str, bus_account: str, identifier: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.bus_account = bus_account
        self.identifier = identifier
