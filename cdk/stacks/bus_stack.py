from typing import Dict

from aws_cdk import (
    Aws,
    CfnOutput,
    Stack,
    StackProps,
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


# check the type??
class BusStackProps(StackProps):
    application_account_by_identifier: Dict[str, str]


"""
 Stack to create a global EventBus. All applications post
 cross-domain events to this bus.
 This bus also has rules to forward global events to local
 buses in each application account
 where rules can be created to handle events in each application.
"""


class BusStack(Stack):
    bus: events.EventBus

    def __init__(self, scope: Construct, id: str, props: BusStackProps) -> None:
        super().__init__(scope, id, props)

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
                "Principal": {
                    "AWS": list(
                        props.get("application_account_by_identifier", {}).values()
                    )
                },
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

        for identifier, application_account in props.get(
            "application_account_by_identifier", {}
        ).items():
            normalised_identifier = identifier.capitalize()
            local_bus_arn = (
                f"arn:aws:events:{Aws.REGION}:{application_account}"
                ":event-bus/local-bus-{identifier}"
            )
            rule = events.Rule(
                self,
                f"globalTo{normalised_identifier}",
                event_bus=bus,
                rule_name=f"globalTo{normalised_identifier}",
                event_pattern={"source": [{"anything-but": identifier}]},
            )
            rule.add_target(
                aws_events_targets.EventBus(
                    self, f"localBus{normalised_identifier}", local_bus_arn
                )
            )

        self.bus = bus
