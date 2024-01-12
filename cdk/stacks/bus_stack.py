from typing import Dict

from aws_cdk import (
    Aws,
    CfnOutput,
    Environment,
    Stack,
    aws_events_targets,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk.aws_events_targets import CloudWatchLogGroup
from constructs import Construct

"""
 Stack to create a global EventBus. All applications post
 cross-domain events to this bus.
 This bus also has rules to forward global events to local
 buses in each application account
 where rules can be created to handle events in each application.
"""


class BusStack(Stack):
    def __init__(
        self, scope: Construct, id: str, identifier: Dict, env: Environment
    ) -> None:
        super().__init__(scope, id, identifier, env)

        bus_log_group = logs.LogGroup(
            self, "GlobalBusLogs", retention=logs.RetentionDays.ONE_WEEK
        )

        bus = events.EventBus(self, "Bus", event_bus_name="global-bus")

        CfnOutput(self, "globalBusName", value=bus.event_bus_name)

        events.CfnEventBusPolicy(
            self,
            "BusPolicy",
            event_bus_name=bus.event_bus_name,
            statement_id="global-bus-policy-stmt",
            statement={
                "Principal": {"AWS": list(("identifier", {}).values())},
                "Action": "events:PutEvents",
                "Resource": bus.event_bus_arn,
                "Effect": "Allow",
            },
        )

        events.Rule(
            self,
            "BusLoggingRule",
            event_bus=bus,
            event_pattern={"source": [{"prefix": ""}]},  # Match all
            targets=[CloudWatchLogGroup(bus_log_group)],
        )

        for id, application_account in ("identifier", {}).items():
            normalised_identifier = id.capitalize()
            local_bus_arn = (
                f"arn:aws:events:{Aws.REGION}:{application_account}"
                ":event-bus/local-bus-{identifier}"
            )
            rule = events.Rule(
                self,
                f"globalTo{normalised_identifier}",
                event_bus=bus,
                rule_name=f"globalTo{normalised_identifier}",
                event_pattern={"source": [{"anything-but": id}]},
            )
            rule.add_target(
                aws_events_targets.EventBus(
                    self, f"localBus{normalised_identifier}", local_bus_arn
                )
            )

        self.bus = bus
