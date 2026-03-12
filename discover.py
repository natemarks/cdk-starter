#!/usr/bin/env python3
"""Discovery workflow for external configuration data.

Purpose:
- Query external AWS data required by stacks in each environment.
- Update config files in `config/<env>/...` with discovered values.

Flow:
- Parse target environment from CLI args.
- Build an environment-specific discovery class.
- Run `update_config` to refresh stack-specific settings.

Customize:
- Add new discovery methods for additional stacks.
- Extend environment subclasses to choose which stack IDs to refresh.
- Replace file writes with another storage backend if needed.
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
    """Return environment id from CLI args (`dev|staging|production`)."""
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
    """Base class for environment-specific discovery updates."""

    def __init__(self, app_env: str):
        check_app_env(app_env)
        check_aws_account(app_env)
        self.data_path = get_actual_path(app_env)
        self.es = EnvironmentSetting.from_data_path(self.data_path)

    def update_simple_asg(self, stack_id: str):
        """Refresh SimpleAsg settings with discovered external values.

        This currently updates `ami_id` to the latest ECS-optimized AMI in the
        environment's default region.
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
        """Run discovery updates for the target environment."""
        raise NotImplementedError


class DevDisco(Disco):
    """Discovery behavior for the dev environment."""

    def update_config(self):
        """Refresh discovery-backed settings for dev."""
        self.update_simple_asg("aaa")


class StagingDisco(Disco):
    """Discovery behavior for the staging environment."""

    def update_config(self):
        """Refresh discovery-backed settings for staging."""
        self.update_simple_asg("bbb")


class ProductionDisco(Disco):
    """Discovery behavior for the production environment."""

    def update_config(self):
        """Refresh discovery-backed settings for production."""
        self.update_simple_asg("ccc")


# Dictionary to map setting types to dataclass constructors
DISCO_MAP: Dict[str, Type] = {
    "dev": DevDisco,
    "staging": StagingDisco,
    "production": ProductionDisco,
}


def get_disco(app_env: str) -> Disco:
    """Return discovery implementation for the requested environment."""
    if app_env in DISCO_MAP:
        return DISCO_MAP[app_env](app_env=app_env)
    raise ValueError(f"invalid environment for locations: {app_env}")


if __name__ == "__main__":
    disc = get_disco(get_environment_id())
    disc.update_config()
