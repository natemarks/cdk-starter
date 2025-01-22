#!/usr/bin/env python3
""" Discover external data required to deploy the stacks in an environment

Given an app environment id: dev | staging | production

Run the discovery for the configuration data based on the stacks in the
environment stack inventory



"""
import argparse
from dataclasses import asdict
import json
from typing import Dict, Type
from config.helper import check_aws_account, check_app_env, latest_ecs_ami_id
from config.settings import (
    SimpleAsgSetting,
    get_logger,
    get_actual_path,
    EnvironmentSetting,
)

mlog = get_logger(str(__name__))


def get_environment_id():
    """
    Parse the command line arguments to get the environment ID.
    The environment ID must be one of ['dev', 'staging', 'production'].
    """
    parser = argparse.ArgumentParser(description="Get the environment ID.")
    parser.add_argument(
        "environment",
        type=str,
        choices=["dev", "staging", "production"],
        help="Environment ID (must be one of: dev, staging, production)",
    )
    args = parser.parse_args()
    return args.environment


class Disco:  # pylint: disable=too-few-public-methods
    """Discover external configuration data
    gather external data for a given app_env (dev | staging | production)

    update the appropriate settings files in config/
    """

    def __init__(self, app_env: str):
        check_app_env(app_env)
        check_aws_account(app_env)
        self.data_path = get_actual_path(app_env)
        self.es = EnvironmentSetting.from_data_path(self.data_path)

    def update_simple_asg(self, stack_id: str):
        """discover the external data for SimpleAsgSetting
        ami_id: update the setting with the latest available AMI ID


        """
        mlog.info("updating simple_asg: %s - %s", self.es.app_env, stack_id)
        data = SimpleAsgSetting.from_data_path(self.data_path, stack_id)
        data.ami_id = latest_ecs_ami_id(self.es.default_region)
        contents = json.dumps(asdict(data), indent=2)
        file_path = data.setting_path(self.data_path, stack_id)
        file_path.write_text(contents, encoding="utf-8")

    def update_config(self):
        """abstract"""
        raise NotImplementedError


class DevDisco(Disco):
    """docstring for DevDisco."""

    def update_config(self):
        """sdfg"""
        self.update_simple_asg("aaa")


class StagingDisco(Disco):
    """docstring for DevDisco."""

    def update_config(self):
        """sdfg"""
        self.update_simple_asg("bbb")


class ProductionDisco(Disco):
    """docstring for DevDisco."""

    def update_config(self):
        """sdfg"""
        self.update_simple_asg("ccc")


# Dictionary to map setting types to dataclass constructors
DISCO_MAP: Dict[str, Type] = {
    "dev": DevDisco,
    "staging": StagingDisco,
    "production": ProductionDisco,
}


def get_disco(app_env: str) -> Disco:
    """Create an instance of the appropriate Disco type"""
    if app_env in DISCO_MAP:
        return DISCO_MAP[app_env](app_env=app_env)
    raise ValueError(f"invalid environment for locations: {app_env}")


if __name__ == "__main__":
    disc = get_disco(get_environment_id())
    disc.update_config()
