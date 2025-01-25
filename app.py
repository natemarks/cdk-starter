#!/usr/bin/env python3
""" AWS CDK Application
"""
import aws_cdk as cdk
from config.inventory import get_inventory

# call the data sync checker to ensure the data is in sync

app = cdk.App()

# set hybrid env name from user input
app_env = app.node.try_get_context("app_env")

# set project-wide tag
cdk.Tags.of(app).add("iac", "github.com/natemarks/cdk-starter")

inv = get_inventory(app_env)
inv.set_environment_tags(app)

# set the cdk_environment
cdk_env = cdk.Environment(
    account=inv.environment_setting.aws_account_number,
    region=inv.environment_setting.default_region,
)

inv.deploy_stacks(app, cdk_env)


app.synth()
