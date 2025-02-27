"""base configuration for settings module

SimpleAsg demonstrates a stack that:
 - can be deployed multpiple times in an application
 - depends upon another stack (AppVpc)


"""

from dataclasses import dataclass
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
)
from aws_cdk import Environment as cdk_environment
from constructs import Construct
from config.helper import APP_NAME
from config.settings import EnvironmentSetting, SimpleAsgSetting
from stack.app_vpc import AppVpcStack


@dataclass(frozen=True, kw_only=True)
class SimpleAsgInput:
    """Input class for SimpleAsg stack

    This object contains data required to deploy a SimpleAsg stack
    """

    stack_id: str
    env_setting: EnvironmentSetting
    sa_setting: SimpleAsgSetting

    def prefix(self) -> str:
        """return the resource prefix string"""
        return (
            f"{APP_NAME}{self.env_setting.prefix()}"
            f"SimpleAsg{self.stack_id.capitalize()}"
        )

    @classmethod
    def from_config_directory(
        cls, data_path: Path, stack_id: str
    ) -> "SimpleAsgInput":
        """Load a AppVpcInput instance from a configuration directory."""

        return cls(
            stack_id=stack_id,
            env_setting=EnvironmentSetting.from_data_path(data_path),
            sa_setting=SimpleAsgSetting.from_data_path(data_path, stack_id),
        )


class SimpleAsgStack(Stack):
    """deploy a simple asg"""

    def __init__(
        self,
        scope: Construct,
        cdk_env: cdk_environment,
        s_input: SimpleAsgInput,
        app_vpc_stack: AppVpcStack,
        **kwargs,
    ):
        self.s_input = s_input
        prefix = s_input.prefix()
        super().__init__(
            scope=scope, id=f"{prefix}Stack", env=cdk_env, **kwargs
        )
        self.vpc = app_vpc_stack.vpc
        instance_sg = ec2.SecurityGroup(
            self,
            f"{prefix}SecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
        )
        # role for ASG instances
        # this must exist in order to use ssm_session_permissions parameter
        asg_role = iam.Role(
            self,
            f"{prefix}ASGRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        default_region = self.s_input.env_setting.default_region
        ami_id = self.s_input.sa_setting.ami_id
        userdata_file = (Path(__file__).parent) / "simple_asg/userdata.sh"
        l_tpl = ec2.LaunchTemplate(
            self,
            f"{prefix}LaunchTpl",
            associate_public_ip_address=False,
            block_devices=[
                ec2.BlockDevice(
                    device_name=self.s_input.sa_setting.root_block_device_name,
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=self.s_input.sa_setting.root_block_device_size,
                    ),
                )
            ],
            instance_type=ec2.InstanceType(
                self.s_input.sa_setting.instance_type
            ),
            # this is an easy way to grab the latest ECS image
            # but I wanted to use the AMI ID as an example of discovery
            # machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            machine_image=ec2.GenericLinuxImage(
                {
                    default_region: ami_id,
                }
            ),
            http_put_response_hop_limit=1,  # default=1
            require_imdsv2=True,  # default=False
            security_group=instance_sg,
            user_data=ec2.UserData.custom(
                userdata_file.read_text(encoding="utf-8")
            ),
            role=asg_role,
        )
        autoscaling.AutoScalingGroup(
            self,
            f"{prefix}ASG",
            min_capacity=self.s_input.sa_setting.min_instances,
            max_capacity=self.s_input.sa_setting.max_instances,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            ssm_session_permissions=True,
            launch_template=l_tpl,
        )
