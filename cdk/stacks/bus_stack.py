from typing import Dict

from aws_cdk import Aws, CfnOutput, Stack, aws_events, aws_events_targets, aws_logs
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
        self,
        scope: Construct,
        id: str,
        application_account_by_identifier: Dict[str, str],
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.principal_values = list(application_account_by_identifier.values())

        self.bus_log_group = aws_logs.LogGroup(
            self, "GlobalBusLogs", retention=aws_logs.RetentionDays.ONE_WEEK
        )

        self.bus = aws_events.EventBus(self, "Bus", event_bus_name="global-bus")

        CfnOutput(self, "globalBusName", value=self.bus.event_bus_name)

        aws_events.CfnEventBusPolicy(
            self,
            "BusPolicy",
            event_bus_name=self.bus.event_bus_name,
            statement_id="global-bus-policy-stmt",
            statement={
                "Principal": {"AWS": self.principal_values},
                "Action": "events:PutEvents",
                "Resource": self.bus.event_bus_arn,
                "Effect": "Allow",
            },
        )

        aws_events.Rule(
            self,
            "BusLoggingRule",
            event_bus=self.bus,
            event_pattern=aws_events.EventPattern(source=[""]),  # Match all
            targets=[CloudWatchLogGroup(self.bus_log_group)],
        )

        for (
            id,
            app_account,
        ) in application_account_by_identifier.items():
            normalised_identifier = id.capitalize()
            local_bus_arn = (
                f"arn:aws:events:{Aws.REGION}:{app_account}:event-bus/local-bus-{id}"
            )

            rule = aws_events.Rule(
                self,
                f"globalTo{normalised_identifier}",
                event_bus=self.bus,
                rule_name=f"globalTo{normalised_identifier}",
                event_pattern=aws_events.EventPattern(source=[id]),
            )
            rule.add_target(
                aws_events_targets.EventBus(
                    aws_events.EventBus.from_event_bus_arn(
                        self, f"localBus{normalised_identifier}", local_bus_arn
                    )
                )
            )

        self.bus = self.bus
