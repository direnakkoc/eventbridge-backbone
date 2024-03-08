from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    Stack,
    aws_events,
    aws_events_targets,
    aws_iam,
    aws_lambda,
    aws_lambda_python_alpha,
    aws_logs,
)
from aws_cdk.aws_events_targets import CloudWatchLogGroup
from constructs import Construct

from cdk.constants import (
    ENVIRONMENT,
    SERVICE_NAME,
)


class DeliveryServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        bus_account: str,
        identifier: str,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            id,
            **kwargs,
        )
        self.bus_account = bus_account
        self.identifier = identifier
        self.global_bus = aws_events.EventBus.from_event_bus_name(
            self, "GlobalBus", "global-bus"
        )
        self.global_bus_arn = (
            f"arn:aws:events:{Aws.REGION}:{bus_account}:event-bus/global-bus"
        )

        self.global_bus_put_events_statement = aws_iam.PolicyStatement(
            actions=["events:PutEvents"],
            resources=[self.global_bus_arn],
        )
        self.bus_log_group = aws_logs.LogGroup(
            self, "LocalBusLogs", retention=aws_logs.RetentionDays.ONE_WEEK
        )

        self.local_bus = aws_events.EventBus(
            self, "LocalBus", event_bus_name=f"local-bus-{identifier}-delivery"
        )

        aws_events.CfnEventBusPolicy(
            self,
            "LocalBusPolicy",
            event_bus_name=self.local_bus.event_bus_name,
            statement_id=f"local-bus-policy-stmt-{identifier}-delivery",
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

        CfnOutput(self, "localBusName", value=self.local_bus.event_bus_name)

        self.create_order_delivery_function()

    def create_order_delivery_function(self) -> None:
        order_delivery_function = aws_lambda_python_alpha.PythonFunction(
            self,
            "OrderDeliveryFunction",
            function_name=f"{SERVICE_NAME}-handle-delivery-{ENVIRONMENT}",
            handler="handle_order_created",
            index="delivery_handler/handler.py",
            entry="handlers",
            environment={
                "POWERTOOLS_NAMESPACE_NAME": f"{SERVICE_NAME}-messaging",
                "ENVIRONMENT": ENVIRONMENT,
                "SERVICE_NAME": SERVICE_NAME,
                "SERVICE": f"{SERVICE_NAME}-messaging",
                "ACCOUNT": Aws.ACCOUNT_ID,
                "REGION": Aws.REGION,
                "BUS_ARN": self.global_bus.event_bus_arn,
                "SERVICE_IDENTIFIER": self.identifier,
                "POWERTOOLS_SERVICE_NAME": "OrderDelivery",
            },
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            timeout=Duration.seconds(10),
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        order_delivery_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[self.global_bus.event_bus_arn],
                actions=["events:PutEvents"],
            )
        )

        # The delivery function reacts to orders being created
        order_delivery_rule = aws_events.Rule(
            self,
            "OrderDeliveryRule",
            event_bus=self.local_bus,
            rule_name="order-delivery-rule",
            event_pattern=aws_events.EventPattern(
                detail_type=["Order.Created"],
            ),
        )
        order_delivery_rule.add_target(
            aws_events_targets.LambdaFunction(order_delivery_function)
        )
        CfnOutput(self, "orderDeliveryRule", value=order_delivery_rule.rule_name)
        CfnOutput(self, "orderDeliveryRuleTarget", value="Target0")
