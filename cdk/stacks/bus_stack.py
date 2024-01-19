from aws_cdk import (
    CfnOutput,
    Stack,
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
        self, scope: Construct, id: str, application_account_by_identifier, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.principal_values = list(application_account_by_identifier.values())

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
                "Principal": {"AWS": self.principal_values},
                "Action": "events:PutEvents",
                "Resource": bus.event_bus_arn,
                "Effect": "Allow",
            },
        )

        events.Rule(
            self,
            "BusLoggingRule",
            event_bus=bus,
            event_pattern=events.EventPattern(source=[""]),  # Match all
            targets=[CloudWatchLogGroup(bus_log_group)],
        )

        for (
            identifier,
            application_account,
        ) in application_account_by_identifier.items():
            normalised_identifier = identifier.capitalize()
            events.Rule(
                self,
                f"globalTo{normalised_identifier}",
                event_bus=bus,
                rule_name=f"globalTo{normalised_identifier}",
                # event_pattern=events.EventPattern(source= [ self.principal_values]),
            )
            # rule.add_target(
            #     aws_events_targets.EventBus(
            #         f"localBus{normalised_identifier}",
            #         local_bus_arn
            #     )
            # )

        self.bus = bus
