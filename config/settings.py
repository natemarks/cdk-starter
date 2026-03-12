""" dataclasses for settings files


"""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Type, TypeVar

from config.helper import get_logger, dict_from_json_file

module_logger = get_logger(str(__name__))

t_json_setting = TypeVar(  # pylint: disable=invalid-name
    "t_json_setting", bound="JsonSettingBase"
)


class JsonSettingBase:
    """Base class for config dataclasses loaded from JSON files."""

    RELATIVE_PATH_TEMPLATE: ClassVar[str] = ""

    @classmethod
    def setting_path(cls, data_path: Path, *path_args: str) -> Path:
        """Return the setting file path for this setting class."""
        if not cls.RELATIVE_PATH_TEMPLATE:
            raise RuntimeError(
                f"{cls.__name__} must define RELATIVE_PATH_TEMPLATE"
            )
        try:
            rel_path = cls.RELATIVE_PATH_TEMPLATE.format(*path_args)
        except IndexError as exc:
            raise ValueError(
                f"Missing path parameter for {cls.__name__}: {exc}"
            ) from exc
        return data_path / rel_path

    @classmethod
    def from_data_path(
        cls: Type[t_json_setting], data_path: Path, *path_args: str
    ) -> t_json_setting:
        """Load a setting instance from a configuration directory."""
        return cls(
            **dict_from_json_file(cls.setting_path(data_path, *path_args))
        )


def get_actual_path(environment: str) -> Path:
    """return the data path for a given environment
    This is used to access the live data as opposed to test_data

    """
    return Path(__file__).parent.joinpath(environment)


@dataclass(frozen=True, kw_only=True)
class EnvironmentSetting(JsonSettingBase):
    """environment config data used for all stacks"""

    RELATIVE_PATH_TEMPLATE: ClassVar[str] = "environment.json"

    admin_team: str  # ex. "Operations"
    aws_account_name: str  # ex. "Daisy Sandbox"
    aws_account_number: str  # ex. "709310380790"
    default_fqdn: str  # ex. "sandbox.daisy.com"
    default_region: str  # ex. "us-east-1"
    app_env: str  # ex. "sandbox"
    is_release: bool  # ex. False

    def prefix(self) -> str:
        """return the environment part pf the resource prefix"""
        return self.app_env.capitalize()


@dataclass(frozen=False, kw_only=True)
class SimpleAsgSetting(JsonSettingBase):
    """environment config data used for all stacks"""

    RELATIVE_PATH_TEMPLATE: ClassVar[str] = "simple_asg/{0}/simple_asg.json"

    ami_id: str
    instance_type: str = "t3.micro"
    max_instances: int = 1
    min_instances: int = 1
    root_block_device_name: str = "/dev/xvda"
    root_block_device_size: int = 100  # in GB


@dataclass(frozen=True, kw_only=True)
class AppVpcSetting(JsonSettingBase):
    """settings for app vpc"""

    RELATIVE_PATH_TEMPLATE: ClassVar[str] = "app_vpc/app_vpc.json"

    cidr: str
    max_azs: int = 2
