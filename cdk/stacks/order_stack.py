from aws_cdk import (
    Aws,
    CfnOutput,
    Stack,
    aws_apigateway,
    aws_events,
    aws_events_targets,
    aws_iam,
    aws_lambda,
    aws_lambda_python_alpha,
    aws_logs,
)
from constructs import Construct

from cdk.constants import ENVIRONMENT, LAMBDA_BUILD_DIR, SERVICE_NAME


class OrderServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        bus_account,
        identifier,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.bus_account = bus_account
        self.identifier = identifier
        self.global_bus = aws_events.EventBus.from_event_bus_name(
            self, "GlobalBus", "global-bus"
        )
        self.local_bus = aws_events.EventBus(
            self, "LocalBus", event_bus_name=f"local-bus-{identifier}"
        )

        self.create_order_create_function()
        self.create_delivery_update_function()

    def create_order_create_function(self) -> aws_lambda_python_alpha.PythonFunction:
        create_order_function = aws_lambda_python_alpha.PythonFunction(
            self,
            "CreateOrderFunction",
            function_name=f"{SERVICE_NAME}-handle-order-create-{ENVIRONMENT}",
            index="order_handler/handler.py",
            entry=LAMBDA_BUILD_DIR,
            environment={
                "ENVIRONMENT": ENVIRONMENT,
                "SERVICE_NAME": SERVICE_NAME,
                "ACCOUNT": Aws.ACCOUNT_ID,
                "REGION": Aws.REGION,
                "BUS_ARN": self.global_bus.event_bus_arn,
                "SERVICE_IDENTIFIER": self.identifier,
                "POWERTOOLS_SERVICE_NAME": "OrderCreate",
            },
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        create_order_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[self.global_bus.event_bus_arn],
                actions=["events:PutEvents"],
            )
        )
        api = aws_apigateway.RestApi(self, "OrderApi", rest_api_name="order")
        api.root.add_method(
            "POST", aws_apigateway.LambdaIntegration(create_order_function)
        )

        CfnOutput(
            self,
            "apiEndpoint",
            value=f"https://{api.rest_api_id}.execute-api.{self.region}.{self.url_suffix}/{api.deployment_stage.stage_name}",
        )

    def create_delivery_update_function(self) -> aws_lambda_python_alpha.PythonFunction:
        delivery_update_function = aws_lambda_python_alpha.PythonFunction(
            self,
            "DeliveryUpdateFunction",
            function_name=f"{SERVICE_NAME}-handle-delivery-update-{ENVIRONMENT}",
            index="order_handler/handler.py",
            entry=LAMBDA_BUILD_DIR,
            environment={
                "ENVIRONMENT": ENVIRONMENT,
                "SERVICE_NAME": SERVICE_NAME,
                "ACCOUNT": Aws.ACCOUNT_ID,
                "REGION": Aws.REGION,
                "BUS_ARN": self.global_bus.event_bus_arn,
                "SERVICE_IDENTIFIER": self.identifier,
                "POWERTOOLS_SERVICE_NAME": "DeliveryUpdate",
            },
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        delivery_update_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[self.global_bus.event_bus_arn],
                actions=["events:PutEvents"],
            )
        )

        # React to delivery events
        delivery_events_rule = aws_events.Rule(
            self,
            "DeliveryHandlingRule",
            event_bus=self.local_bus,
            rule_name="order-service-rule",
            event_pattern=aws_events.EventPattern(detail_type=["Delivery.Updated"]),
        )
        delivery_events_rule.add_target(
            aws_events_targets.LambdaFunction(delivery_update_function)
        )

        CfnOutput(self, "deliveryEventsRule", value=delivery_events_rule.rule_name)
        CfnOutput(self, "deliveryEventsRuleTarget", value="Target0")
