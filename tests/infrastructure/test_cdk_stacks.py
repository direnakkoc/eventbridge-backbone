from aws_cdk import App
from aws_cdk.assertions import Template

from cdk.stacks.bus_stack import BusStack
from cdk.stacks.delivery_stack import DeliveryServiceStack
from cdk.stacks.order_stack import OrderServiceStack


def test_stacks_synthesizes_properly(snapshot):
    app = App()
    delivery_stack = DeliveryServiceStack(
        app,
        "delivery-stack-test",
        "test-bus-delivery-account",
        "test-delivery-service-identifier",
        env={"region": "eu-west-1", "account": "123456789012"},
    )

    order_stack = OrderServiceStack(
        app,
        "order-stack-test",
        "test-bus-order-account",
        "test-order-service-identifier",
        env={"region": "eu-west-1", "account": "123456789012"},
    )

    bus_stack = BusStack(
        app,
        "bus-stack-test",
        application_account_by_identifier={"test-bus-identifier": "123456789012"},
        env={"region": "eu-west-1", "account": "123456789012"},
    )

    template_delivery_stack = Template.from_stack(delivery_stack)
    template_order_stack = Template.from_stack(order_stack)
    template_bus_stack = Template.from_stack(bus_stack)

    template_delivery_stack.resource_count_is("AWS::Lambda::Function", 3)
    assert template_delivery_stack.to_json() == snapshot()
    assert template_bus_stack.to_json() == snapshot()
    assert template_order_stack.to_json() == snapshot()
