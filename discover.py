#!/usr/bin/env python3
""" Discover external data required to deploy the stacks in an environment
 this module contains a base Disco class and a subclass for each environment:
DevDisco, StagingDisco, ProductionDisco

Every subclass has n 'update_config()' method that is specific to the stacks in
an environment.

The example is ONLY able to update the ami_id in the setting for SimpleAsg, so
the subclasses are a bit overkill. It could bbe handled with simple functions.
As the project grows to include many stacks, the functions become unwieldly.
The Disco classes help me keep things organized.


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

        discover the latest AWS ECS AMI ID  for use in SimpleASg as an example


        """
        mlog.info("updating simple_asg: %s - %s", self.es.app_env, stack_id)
        # find the correct setting data to update
        data = SimpleAsgSetting.from_data_path(self.data_path, stack_id)
        # lookup the latest ami_id and update the setting data
        data.ami_id = latest_ecs_ami_id(self.es.default_region)
        # write the setting data to the original location
        contents = json.dumps(asdict(data), indent=2)
        file_path = data.setting_path(self.data_path, stack_id)
        file_path.write_text(contents, encoding="utf-8")

    def update_config(self):
        """abstract"""
        raise NotImplementedError


class DevDisco(Disco):
    """Disco subclass for dev

    The dev environment has one Simple Asg to update ('aaa'). The data is in
    config/dev/simple_asg/aaa/
    """

    def update_config(self):
        """sdfg"""
        self.update_simple_asg("aaa")


class StagingDisco(Disco):
    """Disco subclass for staging

    The staging environment has one Simple Asg to update ('bbb'). The data is in
    config/staging/simple_asg/bbb/
    """

    def update_config(self):
        """sdfg"""
        self.update_simple_asg("bbb")


class ProductionDisco(Disco):
    """Disco subclass for production

    The production environment has one Simple Asg to update ('ccc'). The data is in
    config/production/simple_asg/ccc/
    """

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
