#!/usr/bin/env python3
import os

from aws_cdk import App, Aws, Environment

from cdk.stacks.bus_stage import BusStage
from cdk.stacks.delivery_stage import DeliveryStage
from cdk.stacks.order_stage import OrderStage

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

app.synth()
