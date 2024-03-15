from aws_cdk import (
    Aws,
    CfnOutput,
    Stack,
    aws_events,
    aws_iam,
    aws_logs,
)
from aws_cdk.aws_events_targets import CloudWatchLogGroup
from constructs import Construct

"""
 Base stack class used for any application requiring a local bus
 with logs and permissions to receive events from the global bus.
"""


class BaseStack(Stack):
    def __init__(
        self, scope: Construct, id: str, bus_account: str, identifier: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.bus_account = bus_account
        self.identifier = identifier

        self.global_bus_arn = (
            f"arn:aws:events:{Aws.REGION}:{bus_account}:event-bus/global-bus"
        )
        self.global_bus = aws_events.EventBus.from_event_bus_arn(
            self, "GlobalBus", self.global_bus_arn
        )
        # This is a reusable policy statement that allows Lambda
        # functions to publish events to the global bus
        self.global_bus_put_events_statement = aws_iam.PolicyStatement(
            actions=["events:PutEvents"],
            resources=[self.global_bus_arn],
        )

        self.bus_log_group = aws_logs.LogGroup(
            self, "LocalBusLogs", retention=aws_logs.RetentionDays.ONE_WEEK
        )

        self.local_bus = aws_events.EventBus(
            self, "LocalBus", event_bus_name=f"local-bus-{identifier}"
        )

        CfnOutput(self, "localBusName", value=self.local_bus.event_bus_name)

        aws_events.CfnEventBusPolicy(
            self,
            "LocalBusPolicy",
            event_bus_name=self.local_bus.event_bus_name,
            statement_id=f"local-bus-policy-stmt-{identifier}",
            statement={
                "Principal": {"AWS": self.global_bus.env.account},
                "Action": "events:PutEvents",
                "Resource": self.local_bus.event_bus_arn,
                "Effect": "Allow",
            },
        )

        aws_events.Rule(
            self,
            "LocalLoggingRule",
            event_bus=self.local_bus,
            rule_name="local-logging",
            event_pattern=aws_events.EventPattern(
                source=aws_events.Match.prefix("")
            ),  # Match all
            targets=[CloudWatchLogGroup(self.bus_log_group)],
        )

        self.local_bus = self.local_bus
