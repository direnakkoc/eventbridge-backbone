from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    aws_events,
    aws_lambda,
    aws_lambda_python_alpha,
    aws_logs,
)
from aws_cdk import (
    aws_events_targets as targets,
)
from constructs import Construct

from cdk.constants import ENVIRONMENT, LAMBDA_BUILD_DIR, SERVICE_NAME

from .base_stack import BaseStack, BaseStackProps


class DeliveryServiceStack(BaseStack):
    local_bus: aws_events.EventBus
    identifier: str

    def __init__(self, scope: Construct, id: str, props: BaseStackProps) -> None:
        super().__init__(scope, id, props)
        self.identifier = props.identifier
        self.create_order_delivery_function()

    def create_order_delivery_function(self) -> None:
        order_delivery_function = aws_lambda_python_alpha.PythonFunction(
            self,
            "OrderDeliveryFunction",
            function_name=f"{SERVICE_NAME}-handle-order-create-{ENVIRONMENT}",
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
        order_delivery_function.add_to_role_policy(self.global_bus_put_events_statement)

        # The delivery function reacts to orders being created
        order_delivery_rule = aws_events.Rule(
            self,
            "OrderDeliveryRule",
            event_bus=self.local_bus,
            rule_name="order-delivery-rule",
            event_pattern={
                "detailType": ["Order.Created"],
            },
        )
        order_delivery_rule.add_target(targets.LambdaFunction(order_delivery_function))

        CfnOutput(self, "orderDeliveryRule", value=order_delivery_rule.rule_name)
        CfnOutput(self, "orderDeliveryRuleTarget", value="Target0")
