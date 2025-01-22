""" AppVpc Stack Module
Stack and Stack Input classes to deploy the Application VPC template

"""

from dataclasses import dataclass
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_route53 as r53,
)
from aws_cdk import Environment as cdk_environment
from constructs import Construct
from config.helper import APP_NAME
from config.settings import EnvironmentSetting, AppVpcSetting


@dataclass(frozen=True, kw_only=True)
class AppVpcInput:
    """Input class for AppVpc stack

    This object contains data required to deploy a AppVpc stack
    """

    env_setting: EnvironmentSetting
    app_vpc_setting: AppVpcSetting

    def prefix(self) -> str:
        """return the resource prefix string"""
        return f"{APP_NAME}{self.env_setting.prefix()}AppVpc"

    @classmethod
    def from_config_directory(cls, data_path: Path) -> "AppVpcInput":
        """Load a AppVpcInput instance from a configuration directory."""

        return cls(
            env_setting=EnvironmentSetting.from_data_path(data_path),
            app_vpc_setting=AppVpcSetting.from_data_path(data_path),
        )


class AppVpcStack(Stack):
    """sdf"""

    def __init__(
        self,
        scope: Construct,
        cdk_env: cdk_environment,
        s_input: AppVpcInput,
        **kwargs,
    ):
        self.s_input = s_input
        self._prefix = s_input.prefix()
        super().__init__(
            scope=scope, id=f"{self._prefix}Stack", env=cdk_env, **kwargs
        )
        self.vpc_name = (
            f"{APP_NAME.lower()}-{self.s_input.env_setting.app_env}-app-vpc"
        )
        self.vpc = ec2.Vpc(
            self,
            f"{self._prefix}AppVpc",
            max_azs=self.s_input.app_vpc_setting.max_azs,
            ip_addresses=ec2.IpAddresses.cidr(
                self.s_input.app_vpc_setting.cidr
            ),
            vpc_name=self.vpc_name,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{self.vpc_name}_public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name=f"{self.vpc_name}_private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
                ec2.SubnetConfiguration(
                    name=f"{self.vpc_name}_isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
        )
        # add VPC interface endpoints
        self.vpc.add_interface_endpoint(
            "EC2", service=ec2.InterfaceVpcEndpointAwsService.EC2
        )
        self.vpc.add_interface_endpoint(
            "EC2_MESSAGES",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
        )
        self.vpc.add_interface_endpoint(
            "SSM", service=ec2.InterfaceVpcEndpointAwsService.SSM
        )
        self.vpc.add_interface_endpoint(
            "SSM_MESSAGES",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
        )
        self.vpc.add_interface_endpoint(
            "SECRETS_MANAGER",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )
        self.vpc.add_interface_endpoint(
            "ECS_AGENT",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_AGENT,
        )
        self.vpc.add_interface_endpoint(
            "ECS",
            service=ec2.InterfaceVpcEndpointAwsService.ECS,
        )
        self.vpc.add_interface_endpoint(
            "ECS_TELEMETRY",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_TELEMETRY,
        )
        self.internal_r53_zone = r53.PrivateHostedZone(
            self,
            f"{self._prefix}PrivateR53Zone",
            zone_name=f"{self.s_input.env_setting.app_env}.internal."
            f"{self.s_input.env_setting.default_fqdn}",
            vpc=self.vpc,
        )
