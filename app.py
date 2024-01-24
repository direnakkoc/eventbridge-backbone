#!/usr/bin/env python3
import os

from aws_cdk import App, Aws, Environment
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

CICD_ACCOUNT = os.environ.get(Aws.ACCOUNT_ID, "")
BUS_ACCOUNT = os.environ.get(Aws.ACCOUNT_ID, "")
ORDER_ACCOUNT = os.environ.get(Aws.ACCOUNT_ID, "")
DELIVERY_ACCOUNT = os.environ.get(Aws.ACCOUNT_ID, "")

bus_stage = BusStage(
    app,
    "DirenBusStack",
    env=Environment(
        account=os.environ.get(BUS_ACCOUNT, account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
)

order_stage = OrderStage(
    app,
    "DirenOrderServiceStack",
    env=Environment(
        account=os.environ.get(DELIVERY_ACCOUNT, account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
)

delivery_stage = DeliveryStage(
    app,
    "DirenDeliveryServiceStack",
    env=Environment(
        account=os.environ.get(DELIVERY_ACCOUNT, account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
)

pipeline_stack = PipelineStack(
    app,
    "DirenPipelineStack",
    stages=[bus_stage, order_stage, delivery_stage],
    accounts={
        "cicd-account": CICD_ACCOUNT,
        "bus-account": BUS_ACCOUNT,
        "order-service-account": ORDER_ACCOUNT,
        "delivery-service-account": DELIVERY_ACCOUNT,
    },
    env=Environment(
        account=os.environ.get(CICD_ACCOUNT, account),
        region=os.environ.get("AWS_DEFAULT_ACCOUNT", region),
    ),
)
app.synth()
