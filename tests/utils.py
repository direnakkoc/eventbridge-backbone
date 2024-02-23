import os


def set_common_test_env_vars():
    os.environ["ENVIRONMENT"] = "pytest"
