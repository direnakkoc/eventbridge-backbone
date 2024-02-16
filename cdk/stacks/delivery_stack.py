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
from constructs import Construct

from cdk.constants import ENVIRONMENT, LAMBDA_BUILD_DIR, SERVICE_NAME


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
        self.local_bus = aws_events.EventBus(
            self, "LocalBus", event_bus_name=f"local-bus-{identifier}-delivery"
        )
        self.create_order_delivery_function()

    def create_order_delivery_function(self) -> None:
        order_delivery_function = aws_lambda_python_alpha.PythonFunction(
            self,
            "OrderDeliveryFunction",
            function_name=f"{SERVICE_NAME}-handle-delivery-{ENVIRONMENT}",
            index="delivery_handler/handler.py",
            entry=LAMBDA_BUILD_DIR,
            environment={
                "ENVIRONMENT": ENVIRONMENT,
                "SERVICE_NAME": SERVICE_NAME,
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
