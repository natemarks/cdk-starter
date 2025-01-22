"""helper functions for settings module


"""

import logging
from pathlib import Path
import sys
from dataclasses import dataclass
import json
from typing import Any, Dict

import boto3

# APP_NAME is used to distinguis stacks with similar names in different projects
# like "AppVpc". this allows the project to be used multiple times in a single AWS account
APP_NAME = "Starter"
PROJECT_ROOT = Path(__file__).parent.parent


def get_logger(module_name: str) -> logging.Logger:
    """return standard logger
    usage:
    MODULE_LOGGER = get_logger(str(__name__))
    """
    my_logger = logging.getLogger(module_name)
    my_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s - {%(name)s} - {%(filename)s:%(funcName)s:%(lineno)d} - "
        "%(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    my_logger.addHandler(console_handler)
    return my_logger


module_logger = get_logger(str(__name__))

APP_ENV_TO_AWS_ACCOUNT = {
    "dev": "709310380790",
    "staging": "709310380790",
    "production": "709310380790",
}


def check_app_env(ae: str):
    """raise if the app_env isn't valid"""
    if ae not in APP_ENV_TO_AWS_ACCOUNT:
        raise ValueError(f"invalid app_env: {ae}")


def ensure_path_exists(path: Path):
    """Ensure that the directory of the given path exists.
    If the path is a file create all parent directories.
    If the path is a directory create the directory and all parent directories.
    """
    if not isinstance(path, Path):
        raise TypeError("path must be a pathlib.Path object")

    if path.is_dir() or not path.suffix:
        # Create the directory and all parent directories
        path.mkdir(parents=True, exist_ok=True)
        module_logger.info(
            "Ensured that the directory %s and all parent directories exist.",
            path,
        )
    else:
        # Create all parent directories of the file
        parent_directory = path.parent
        parent_directory.mkdir(parents=True, exist_ok=True)
        module_logger.info(
            "Ensured that all parent directories for the file %s exist.", path
        )


def dict_from_json_string(json_string: str) -> Dict[str, Any]:
    """return a ict  or a dataclass from a json string"""

    # Parse the JSON string into a dictionary
    def is_dict_with_string_keys(variable: Any) -> bool:
        if not isinstance(variable, dict):
            return False
        return all(isinstance(key, str) for key in variable.keys())

    data = json.loads(json_string)
    if not is_dict_with_string_keys(data):
        raise ValueError(
            "JSON string does not represent a dictionary: " + json_string
        )
    return data


def dict_from_json_file(json_file: Path) -> Any:
    """return a dictionary from a json file"""
    with json_file.open() as file:
        return dict_from_json_string(file.read())


@dataclass(frozen=False, kw_only=True)
class AwsCallerIdentity:
    """identity data class. handy for autocompletion"""

    account: str
    arn: str
    user_id: str


def get_caller_identity() -> AwsCallerIdentity:
    """return the current caller identity"""
    client = boto3.client("sts")
    response = client.get_caller_identity()

    return AwsCallerIdentity(
        **{
            "account": response["Account"],
            "arn": response["Arn"],
            "user_id": response["UserId"],
        }
    )


def check_aws_account(app_env: str):
    """raise an exception if current account is incorrect for hybrid_env"""
    caller_identity = get_caller_identity()
    if caller_identity.account != APP_ENV_TO_AWS_ACCOUNT[app_env]:
        raise RuntimeError(
            f"Local AWS Account {caller_identity.account} does not match "
            f"{app_env} AWS Account {APP_ENV_TO_AWS_ACCOUNT[app_env]}"
        )
    return caller_identity.account


def latest_ecs_ami_id(aws_region: str) -> str:
    """returtn the latest ECS ami

    name: 'amzn2-ami-ecs-hvm-*'
    virtualization-type: 'hvm'
    architecture: x86_64
    """
    ec2 = boto3.client("ec2", region_name=aws_region)
    paginator = ec2.get_paginator("describe_images")

    filters = [
        {"Name": "name", "Values": ["amzn2-ami-ecs-hvm-*"]},
        {"Name": "virtualization-type", "Values": ["hvm"]},
        {"Name": "architecture", "Values": ["x86_64"]},
    ]

    all_images = []

    for page in paginator.paginate(Owners=["amazon"], Filters=filters):
        all_images.extend(page["Images"])

    # Sort all images by CreationDate in descending order
    sorted_images = sorted(
        all_images, key=lambda x: x["CreationDate"], reverse=True
    )

    if not sorted_images:
        raise RuntimeError("No images found")

    # Return the most recent AMI ID, or None if no AMIs match
    return sorted_images[0]["ImageId"]
