#!/usr/bin/env python3
import os

from aws_cdk import App, Environment
from boto3 import client, session

from cdk.stacks.bus_stage import BusStage
from cdk.stacks.delivery_stage import DeliveryStage
from cdk.stacks.order_stage import OrderStage
from cdk.stacks.pipeline_stack import PipelineStack

ORDER_SERVICE_IDENTIFIER = "order-service"
DELIVERY_SERVICE_IDENTIFIER = "delivery-service"
account = client("sts").get_caller_identity()["Account"]
region = session.Session().region_name


app = App()

cicd_account = os.environ.get("cicd-account")
bus_account = os.environ.get("bus-account")
order_account = os.environ.get("order-service-account")
delivery_account = os.environ.get("delivery-service-account")

bus_stage = BusStage(
    app,
    "DirenBusStack",
    env=Environment(
        account=os.environ.get("bus-account", account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
    application_account_by_identifier={
        ORDER_SERVICE_IDENTIFIER: order_account,
        DELIVERY_SERVICE_IDENTIFIER: delivery_account,
    },
)

order_stage = OrderStage(
    app,
    "DirenOrderServiceStack",
    env=Environment(
        account=os.environ.get("order-service-account", account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
    identifier=ORDER_SERVICE_IDENTIFIER,
    bus_account=bus_account,
)

delivery_stage = DeliveryStage(
    app,
    "DirenDeliveryServiceStack",
    env=Environment(
        account=os.environ.get("delivery-service-account", account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
    identifier=DELIVERY_SERVICE_IDENTIFIER,
    bus_account=bus_account,
)

pipeline_stack = PipelineStack(
    app,
    "DirenPipelineStack",
    env=Environment(
        account=os.environ.get("cicd-account", account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
    stages=[bus_stage, order_stage, delivery_stage],
    accounts={
        "cicd-account": cicd_account,
        "bus-account": bus_account,
        "order-service-account": order_account,
        "delivery-service-account": delivery_account,
    },
)
app.synth()
