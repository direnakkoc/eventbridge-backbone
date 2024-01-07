import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.stacks.regional_stack import EventbridgeBackboneStack


# example tests. To run these tests, uncomment this file along with the example
# resource in eventbridge_backbone/eventbridge_backbone_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EventbridgeBackboneStack(app, "eventbridge-backbone")
    assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
