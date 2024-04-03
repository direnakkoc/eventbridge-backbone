import os

from aws_cdk import Aws

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
PIP_INDEX_URL = "https://artifactory.renre.com/artifactory/api/pypi/pypi/simple/"
REGION = os.environ.get("AWS_REGION", "eu-west-1")
SERVICE_NAME = "eventbridge-backbone"
ORDER_SERVICE_ACCOUNT = os.environ.get("ORDER_SERVICE_ACCOUNT", Aws.ACCOUNT_ID)
DELIVERY_SERVICE_ACCOUNT = os.environ.get("DELIVERY_SERVICE_ACCOUNT", Aws.ACCOUNT_ID)
BUS_ACCOUNT = os.environ.get("BUS_ACCOUNT", Aws.ACCOUNT_ID)
BUS_PROFILE = os.environ.get("BUS_PROFILE", "dev1")
ORDER_SERVICE_PROFILE = os.environ.get("ORDER_SERVICE_PROFILE", "dev8")
DELIVERY_SERVICE_PROFILE = os.environ.get("DELIVERY_SERVICE_PROFILE", "dev2")
