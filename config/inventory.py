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
from typing import Dict, Type

from aws_cdk import App, Environment, Stack, Tags

from config.settings import EnvironmentSetting, get_actual_path
from config.helper import check_aws_account, check_app_env
from stack.app_vpc import AppVpcInput, AppVpcStack
from stack.simple_asg import SimpleAsgInput, SimpleAsgStack


class Inventory:
    """stack inventory for an environment"""

    def __init__(self, app_env: str):
        check_app_env(app_env)
        check_aws_account(app_env)
        self.data_path = get_actual_path(app_env)
        self.app_env = app_env
        self.unique_stacks = {}  # type: Dict[str, Stack]
        self.multi_stacks = {}  # type: Dict[str, Dict[str, Stack]]
        self.environment_setting = EnvironmentSetting.from_data_path(
            self.data_path
        )

    def deploy_stacks(self, app: App, cdk_env: Environment):
        """deploy the stacks"""
        raise NotImplementedError

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
        if "simple_asg" not in self.multi_stacks:
            self.multi_stacks["simple_asg"] = {}

        s_input = SimpleAsgInput.from_config_directory(
            self.data_path, stack_id
        )
        self.multi_stacks["simple_asg"][stack_id] = SimpleAsgStack(
            scope=app,
            cdk_env=cdk_env,
            s_input=s_input,
            app_vpc_stack=self.unique_stacks["app_vpc"],
            termination_protection=termination_protection,
        )
        return self.multi_stacks["simple_asg"][stack_id]


class DevInventory(Inventory):
    """stack inventory for dev environment

    DevAppVpcStack
    DevBiometricAwareStack
    DevXRayAccessDev2Stack
    """

    def deploy_stacks(self, app: App, cdk_env: Environment):
        """deploy the stacks"""
        self.app_vpc_stack(app, cdk_env, termination_protection=False)
        self.simple_asg_stack(
            app, cdk_env, "aaa", termination_protection=False
        )


class StagingInventory(Inventory):
    """stack inventory for staging environment

    StagingAppVpcStack
    StagingBiometricAwareStack
    StagingXRayAccessStaging1Stack
    StagingXRayAccessStaging2Stack
    """

    def deploy_stacks(self, app: App, cdk_env: Environment):
        """deploy the stacks"""
        self.app_vpc_stack(app, cdk_env, termination_protection=False)
        self.simple_asg_stack(
            app, cdk_env, "bbb", termination_protection=False
        )


class ProductionInventory(Inventory):
    """stack inventory for production environment

    ProductionAppVpcStack
    ProductionBiometricAwareStack
    ProductionXRayAccessProd1Stack
    ProductionXRayAccessProd2Stack
    """

    def deploy_stacks(self, app: App, cdk_env: Environment):
        """deploy the stacks"""
        self.app_vpc_stack(app, cdk_env, termination_protection=False)
        self.simple_asg_stack(
            app, cdk_env, "ccc", termination_protection=False
        )


# Dictionary to map setting types to dataclass constructors
INVENTORY_MAP: Dict[str, Type] = {
    "dev": DevInventory,
    "staging": StagingInventory,
    "production": ProductionInventory,
}


def get_inventory(app_env: str) -> Inventory:
    """Create an instance of the appropriate Inventory type"""
    if app_env in INVENTORY_MAP:
        return INVENTORY_MAP[app_env](app_env=app_env)
    raise ValueError(f"invalid environment for locations: {app_env}")
