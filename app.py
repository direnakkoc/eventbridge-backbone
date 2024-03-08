#!/usr/bin/env python3
import os

from aws_cdk import App, Aws, Environment

from cdk.constants import (
    BUS_ACCOUNT,
    CICD_ACCOUNT,
    DELIVERY_SERVICE_IDENTIFIER,
    ORDER_SERVICE_IDENTIFIER,
)
from cdk.stacks.bus_stage import BusStage
from cdk.stacks.delivery_stage import DeliveryStage
from cdk.stacks.order_stage import OrderStage
from cdk.stacks.pipeline_stack import PipelineStack

app = App()


bus_stage = BusStage(
    app,
    "DirenBusStage",
    env=Environment(
        account=os.environ.get("AWS_DEFAULT_ACCOUNT", Aws.ACCOUNT_ID),
        region=os.environ.get("AWS_DEFAULT_REGION", Aws.REGION),
    ),
)

order_stage = OrderStage(
    app,
    "DirenOrderServiceStage",
    env=Environment(
        account=os.environ.get("AWS_DEFAULT_ACCOUNT", Aws.ACCOUNT_ID),
        region=os.environ.get("AWS_DEFAULT_REGION", Aws.REGION),
    ),
)

delivery_stage = DeliveryStage(
    app,
    "DirenDeliveryServiceStage",
    env=Environment(
        account=os.environ.get("AWS_DEFAULT_ACCOUNT", Aws.ACCOUNT_ID),
        region=os.environ.get("AWS_DEFAULT_REGION", Aws.REGION),
    ),
)

pipeline_stack = PipelineStack(
    app,
    "DirenPipelineStack",
    stages=[bus_stage, order_stage, delivery_stage],
    accounts={
        "cicd-account": CICD_ACCOUNT,
        "bus-account": BUS_ACCOUNT,
        "order-service-account": ORDER_SERVICE_IDENTIFIER,
        "delivery-service-account": DELIVERY_SERVICE_IDENTIFIER,
    },
    env=Environment(
        account=os.environ.get("AWS_DEFAULT_ACCOUNT", Aws.ACCOUNT_ID),
        region=os.environ.get("AWS_DEFAULT_REGION", Aws.REGION),
    ),
)
app.synth()
