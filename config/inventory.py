#!/usr/bin/env python3
""" the inventory of stacks in an environment

The inventory is used to determine which stacks should be deployyed based on
the environment. It handles two types of stacks:

 - unique stack: can only be deployed once per environment. doesn't need a stack_id
 - multi stack: can be deployed multiple times in an environment. needs a stack_id

This module is used by app.py like this:

inv = get_inventory(app_env) # get the class for the environment
inv.set_environment_tags(app) # set env specific tags

# set the cdk_environment
cdk_env = cdk.Environment(
account=inv.environment_setting().aws_account_number,
region=inv.environment_setting().default_region,)

inv.deploy_stacks(app, cdk_env) # deploy the correct stacks for the env


"""
from typing import ClassVar

from aws_cdk import App, Environment, Tags

from config.settings import EnvironmentSetting, get_actual_path
from config.helper import check_aws_account, check_app_env
from stack.app_vpc import AppVpcInput, AppVpcStack
from stack.simple_asg import SimpleAsgInput, SimpleAsgStack


class Inventory:
    """stack inventory for an environment"""

    SIMPLE_ASG_IDS: ClassVar[tuple[str, ...]] = ()
    TERMINATION_PROTECTION: ClassVar[bool] = False

    def __init__(self, app_env: str):
        check_app_env(app_env)
        check_aws_account(app_env)
        self.data_path = get_actual_path(app_env)
        self.app_env = app_env
        self.unique_stacks: dict[str, AppVpcStack] = {}
        self.multi_stacks: dict[str, dict[str, SimpleAsgStack]] = {}
        self.environment_setting = EnvironmentSetting.from_data_path(
            self.data_path
        )

    def deploy_stacks(self, app: App, cdk_env: Environment):
        """deploy the stacks"""
        self.app_vpc_stack(
            app,
            cdk_env,
            termination_protection=self.TERMINATION_PROTECTION,
        )
        for stack_id in self.SIMPLE_ASG_IDS:
            self.simple_asg_stack(
                app,
                cdk_env,
                stack_id,
                termination_protection=self.TERMINATION_PROTECTION,
            )

    def set_environment_tags(self, app: App):
        """set the tags for the stack"""
        Tags.of(app).add("env_id", self.app_env)
        Tags.of(app).add("app_env", self.app_env)
        Tags.of(app).add("Environment", self.app_env)

    def app_vpc_stack(
        self, app: App, cdk_env: Environment, termination_protection: bool
    ) -> AppVpcStack:
        """create the app vpc stack"""
        s_input = AppVpcInput.from_config_directory(self.data_path)
        self.unique_stacks["app_vpc"] = AppVpcStack(
            scope=app,
            cdk_env=cdk_env,
            s_input=s_input,
            termination_protection=termination_protection,
        )
        return self.unique_stacks["app_vpc"]

    def simple_asg_stack(
        self,
        app: App,
        cdk_env: Environment,
        stack_id: str,
        termination_protection: bool,
    ) -> SimpleAsgStack:
        """create the simple_asg stack"""
        app_vpc_stack = self.unique_stacks.get("app_vpc")
        if app_vpc_stack is None:
            raise RuntimeError(
                "app_vpc stack must be created before simple_asg stacks"
            )

        simple_asg_stacks = self.multi_stacks.setdefault("simple_asg", {})

        s_input = SimpleAsgInput.from_config_directory(
            self.data_path, stack_id
        )
        simple_asg_stacks[stack_id] = SimpleAsgStack(
            scope=app,
            cdk_env=cdk_env,
            s_input=s_input,
            app_vpc_stack=app_vpc_stack,
            termination_protection=termination_protection,
        )
        return simple_asg_stacks[stack_id]


class DevInventory(Inventory):
    """stack inventory for dev environment

    DevAppVpcStack
    DevBiometricAwareStack
    DevXRayAccessDev2Stack
    """

    SIMPLE_ASG_IDS = ("aaa",)


class StagingInventory(Inventory):
    """stack inventory for staging environment

    StagingAppVpcStack
    StagingBiometricAwareStack
    StagingXRayAccessStaging1Stack
    StagingXRayAccessStaging2Stack
    """

    SIMPLE_ASG_IDS = ("bbb",)


class ProductionInventory(Inventory):
    """stack inventory for production environment

    ProductionAppVpcStack
    ProductionBiometricAwareStack
    ProductionXRayAccessProd1Stack
    ProductionXRayAccessProd2Stack
    """

    SIMPLE_ASG_IDS = ("ccc",)


# Dictionary to map setting types to dataclass constructors
INVENTORY_MAP: dict[str, type[Inventory]] = {
    "dev": DevInventory,
    "staging": StagingInventory,
    "production": ProductionInventory,
}


def get_inventory(app_env: str) -> Inventory:
    """Create an instance of the appropriate Inventory type"""
    if app_env in INVENTORY_MAP:
        return INVENTORY_MAP[app_env](app_env=app_env)
    raise ValueError(f"invalid environment for locations: {app_env}")
