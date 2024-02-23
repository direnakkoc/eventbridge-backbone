from aws_cdk import App
from aws_cdk.assertions import Template

from cdk.stacks.bus_stage import BusStage
from cdk.stacks.delivery_stage import DeliveryStage
from cdk.stacks.order_stage import OrderStage


def test_stacks_synthesizes_properly(snapshot):
    app = App()
    delivery_stack = DeliveryStage(
        app,
        "delivery-stack-test",
        env={"region": "eu-west-1", "account": "123456789012"},
    )

    order_stack = OrderStage(
        app, "order-stack-test", env={"region": "eu-west-1", "account": "123456789012"}
    )

    bus_stack = BusStage(
        app, "bus-stack-test", env={"region": "eu-west-1", "account": "123456789012"}
    )

    template_delivery_stack = Template.from_stack(delivery_stack)
    Template.from_stack(order_stack)
    Template.from_stack(bus_stack)

    template_delivery_stack.resource_count_is("AWS::Lambda::Function", 1)
    # assert template.to_json() == snapshot(exclude=props("S3Key"))
