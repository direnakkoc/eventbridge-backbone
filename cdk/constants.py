import os

from aws_cdk import Aws

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
PIP_INDEX_URL = "https://artifactory.renre.com/artifactory/api/pypi/pypi/simple/"
PRIMARY_REGION = "eu-west-1"
SERVICE_NAME = "eventbridge-backbone"
LAMBDA_BUILD_DIR = ".BUILD/HANDLERS/"
ORDER_SERVICE_IDENTIFIER = os.environ.get("order-service", Aws.ACCOUNT_ID)
DELIVERY_SERVICE_IDENTIFIER = os.environ.get("delivery-service", Aws.ACCOUNT_ID)
BUS_ACCOUNT = os.environ.get("BUS_ARN", Aws.ACCOUNT_ID)
