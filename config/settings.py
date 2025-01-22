""" dataclasses for settings files


"""

from dataclasses import dataclass
from pathlib import Path
from config.helper import get_logger, dict_from_json_file

module_logger = get_logger(str(__name__))


def get_actual_path(environment: str) -> Path:
    """return the data path for a given environment
    This is used to access the live data as opposed to test_data

    """
    return Path(__file__).parent.joinpath(environment)


@dataclass(frozen=True, kw_only=True)
class EnvironmentSetting:
    """environment config data used for all stacks"""

    admin_team: str  # ex. "Operations"
    aws_account_name: str  # ex. "Daisy Sandbox"
    aws_account_number: str  # ex. "709310380790"
    default_fqdn: str  # ex. "sandbox.daisy.com"
    default_region: str  # ex. "us-east-1"
    app_env: str  # ex. "sandbox"
    is_release: bool  # ex. False

    @staticmethod
    def from_data_path(data_path: Path) -> "EnvironmentSetting":
        """Load a EnvironmentSetting instance from a configuration directory."""

        return EnvironmentSetting(
            **dict_from_json_file(data_path / "environment.json")
        )

    def prefix(self) -> str:
        """return the environment part pf the resource prefix"""
        return self.app_env.capitalize()


@dataclass(frozen=False, kw_only=True)
class SimpleAsgSetting:
    """environment config data used for all stacks"""

    ami_id: str
    instance_type: str = "t3.micro"
    max_instances: int = 1
    min_instances: int = 1
    root_block_device_name: str = "/dev/xvda"
    root_block_device_size: int = 100  # in GB

    @staticmethod
    def setting_path(data_path: Path, stack_id: str) -> Path:
        """return the path to the setting file"""
        return data_path / "simple_asg" / stack_id / "simple_asg.json"

    @staticmethod
    def from_data_path(data_path: Path, stack_id: str) -> "SimpleAsgSetting":
        """Load a SimpleAsgSetting instance from a data_path"""

        return SimpleAsgSetting(
            **dict_from_json_file(
                SimpleAsgSetting.setting_path(data_path, stack_id)
            )
        )


@dataclass(frozen=True, kw_only=True)
class AppVpcSetting:
    """settings for app vpc"""

    cidr: str
    max_azs: int = 2

    @staticmethod
    def from_data_path(data_path: Path) -> "AppVpcSetting":
        """Load a AppVpcSetting instance from a data_path"""

        return AppVpcSetting(
            **dict_from_json_file(data_path / "app_vpc" / "app_vpc.json")
        )
