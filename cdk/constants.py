import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
PIP_INDEX_URL = "https://artifactory.renre.com/artifactory/api/pypi/pypi/simple/"
PRIMARY_REGION = "eu-west-1"
SERVICE_NAME = "eventbridge-backbone"
LAMBDA_BUILD_DIR = ".build/handlers/"
