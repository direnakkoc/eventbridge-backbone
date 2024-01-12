from aws_cdk import (
    Aws,
    CfnOutput,
    Stack,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk.aws_events_targets import CloudWatchLogGroup
from constructs import Construct

"""
 Base stack class used for any application requiring a local bus
 with logs and permissions to receive events from the global bus.
"""


class BaseStack(Stack):
    local_bus: events.IEventBus
    global_bus: events.IEventBus
    global_bus_put_events_statement: iam.PolicyStatement

    def __init__(
        self, scope: Construct, id: str, bus_account: str, identifier: str
    ) -> None:
        super().__init__(scope, id, bus_account, identifier)

        global_bus_arn = (
            f"arn:aws:events:{Aws.REGION}:{bus_account}:event-bus/global-bus"
        )
        self.global_bus = events.EventBus.from_event_bus_arn(
            self, "GlobalBus", global_bus_arn
        )
        # This is a reusable policy statement that allows Lambda
        # functions to publish events to the global bus
        self.global_bus_put_events_statement = iam.PolicyStatement(
            actions=["events:PutEvents"],
            resources=[global_bus_arn],
        )

        bus_log_group = logs.LogGroup(
            self, "LocalBusLogs", retention=logs.RetentionDays.ONE_WEEK
        )

        local_bus = events.EventBus(
            self, "LocalBus", event_bus_name=f"local-bus-{identifier}"
        )

        CfnOutput(self, "localBusName", value=local_bus.event_bus_name)

        events.CfnEventBusPolicy(
            self,
            "LocalBusPolicy",
            event_bus_name=local_bus.event_bus_name,
            statement_id=f"local-bus-policy-stmt-{identifier}",
            statement={
                "Principal": {"AWS": self.global_bus.env.account},
                "Action": "events:PutEvents",
                "Resource": local_bus.event_bus_arn,
                "Effect": "Allow",
            },
        )

        local_logging_rule = events.Rule(
            self,
            "LocalLoggingRule",
            event_bus=local_bus,
            rule_name="local-logging",
            event_pattern={"source": [{"prefix": ""}]},  # Match all
        )
        local_logging_rule.add_target(CloudWatchLogGroup(bus_log_group))

        self.local_bus = local_bus
