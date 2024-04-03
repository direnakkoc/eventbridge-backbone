import json
import time

import aws_iatk
import pytest
import requests

from cdk.constants import (
    BUS_PROFILE,
    DELIVERY_SERVICE_PROFILE,
    ORDER_SERVICE_PROFILE,
    REGION,
)

created_by_tag_value = "event-bridge-backbone-int-tests"
delivery_service_stack_name = "DirenDeliveryServiceStage-DirenDeliveryServiceStack"
order_service_stack_name = "DirenOrderServiceStage-DirenOrderServiceStack"
bus_stack_name = "DirenBusStage-DirenBusStack"

region = "eu-west-1"
iatk_bus = aws_iatk.AwsIatk(profile=BUS_PROFILE, region=REGION)
iatk_delivery_service = aws_iatk.AwsIatk(
    profile=DELIVERY_SERVICE_PROFILE, region=REGION
)
atk_order_service = aws_iatk.AwsIatk(profile=ORDER_SERVICE_PROFILE, region=REGION)


@pytest.fixture(scope="module")
def iatk():
    # Create AwsIatk instances with the correct profiles for each AWS account

    # Clean up from abandoned previous runs in each account
    remove_listeners(iatk_bus)
    remove_listeners(iatk_delivery_service)
    remove_listeners(atk_order_service)

    # Yield the AwsIatk instances for use in tests
    yield iatk_bus, iatk_delivery_service, atk_order_service

    # Clean up resources from each account after tests complete
    remove_listeners(iatk_bus)
    remove_listeners(iatk_delivery_service)
    remove_listeners(atk_order_service)


def test_order_delivery(iatk: aws_iatk.AwsIatk):
    """Check whether delivery events are received when an order is created"""
    iatk_bus, iatk_delivery_service, atk_order_service = iatk

    # Get EventBridge resource identifiers from the Delivery Service stack
    delivery_outputs = iatk_delivery_service.get_stack_outputs(
        delivery_service_stack_name,
        output_names=["localBusName", "orderDeliveryRule", "orderDeliveryRuleTarget"],
    ).outputs

    delivery_local_bus_name = delivery_outputs["localBusName"]
    order_delivery_rule = delivery_outputs["orderDeliveryRule"].split("|")[-1]
    order_delivery_rule_target = delivery_outputs["orderDeliveryRuleTarget"]

    # Get resource identifiers from the Order Service stack
    order_outputs = atk_order_service.get_stack_outputs(
        order_service_stack_name,
        output_names=[
            "apiEndpoint",
            "localBusName",
            "deliveryEventsRule",
            "deliveryEventsRuleTarget",
        ],
    ).outputs

    api_endpoint = order_outputs["apiEndpoint"]

    # Set up an IATK listener for EventBridge rules on the Delivery Service
    delivery_listener_id = iatk_delivery_service.add_listener(
        event_bus_name=delivery_local_bus_name,
        rule_name=order_delivery_rule,
        target_id=order_delivery_rule_target,
        tags={"CreatedBy": created_by_tag_value},
    ).id

    # Create an order with the Order Service
    response = requests.post(api_endpoint)
    order_id = response.json()["order_id"]
    assert order_id is not None
    trace_id = response.headers["x-amzn-trace-id"]

    # Check whether the delivery service received the Order.Created event
    def event_assertion(event: str):
        payload = json.loads(event)
        assert payload["detail-type"] == "Order.Created"
        assert payload["detail"]["data"]["order_id"] == order_id

    assert iatk_delivery_service.wait_until_event_matched(
        delivery_listener_id, event_assertion
    )

    def trace_assertion(trace: aws_iatk.GetTraceTreeOutput):
        trace_tree = trace.trace_tree
        assert [[seg.origin for seg in path] for path in trace_tree.paths] == [
            [
                "AWS::Lambda",
                "AWS::Lambda::Function",
                "AWS::Events",
                "AWS::Lambda",
                "AWS::Lambda::Function",
                "AWS::Events",
                "AWS::Lambda",
                "AWS::Lambda::Function",
                "AWS::Events",
            ]
        ]
        assert trace_tree.source_trace.duration < 20

    # This sleep should not be required for retry_get_trace_tree_until
    # but it seems to mitigate
    # https://github.com/awslabs/aws-iatk/issues/106
    time.sleep(15)

    assert atk_order_service.retry_get_trace_tree_until(
        tracing_header=trace_id,
        assertion_fn=trace_assertion,
        timeout_seconds=60,
    )


def remove_listeners(iatk):
    """Remove all listeners created by integration tests"""
    iatk.remove_listeners(
        tag_filters=[
            aws_iatk.RemoveListeners_TagFilter(
                key="CreatedBy",
                values=[created_by_tag_value],
            )
        ]
    )


remove_listeners(iatk_bus)
remove_listeners(iatk_delivery_service)
remove_listeners(atk_order_service)
