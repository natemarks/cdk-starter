#!/usr/bin/env python3
""" compare the app_vpc stack to the expected stacks

These tests provide examples for creating the stacks. 


"""
# pylint: disable=duplicate-code
import json
import pytest
from aws_cdk import App, assertions, Environment
from config.settings import get_actual_path
from stack.app_vpc import AppVpcStack, AppVpcInput
from tests.helper import case_data_path, update_data_file, read_json_data_file


@pytest.mark.unit
@pytest.mark.parametrize(
    "environment",
    [
        pytest.param("dev", id="dev"),
        pytest.param("staging", id="staging"),
        pytest.param("production", id="production"),
    ],
)
def test_app_vpc_stack_actual(request, environment, update_golden):
    """test app_vpc stack wiht actual environment data

    use the live data in config/dev, config/staging and config/production

    """
    # use stack input data from actual environments
    input_path = get_actual_path(environment)
    # test_data path for case
    data_path = case_data_path(request)
    s_input = AppVpcInput.from_config_directory(input_path)

    app = App()

    stk = AppVpcStack(
        scope=app,
        cdk_env=Environment(),
        s_input=s_input,
    )
    template = assertions.Template.from_stack(stk)
    if update_golden:
        update_data_file(
            data_path,
            "expected.json",
            json.dumps(template.to_json(), indent=2),
        )

    template.template_matches(read_json_data_file(data_path, "expected.json"))


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [
        pytest.param(id="explore_new_setting"),
    ],
)
def test_app_vpc_stack_custom(request, update_golden):
    """test app_vpc stack with custom configuration

    test using environment data stored in the case data path. This is convenient
    for test unusual cases without putting them into an actual environment.
    """
    # test_data path for case
    data_path = case_data_path(request)
    # the custom input files are in the case data
    input_path = data_path
    s_input = AppVpcInput.from_config_directory(input_path)

    app = App()

    stk = AppVpcStack(
        scope=app,
        cdk_env=Environment(),
        s_input=s_input,
    )
    template = assertions.Template.from_stack(stk)
    if update_golden:
        update_data_file(
            data_path,
            "expected.json",
            json.dumps(template.to_json(), indent=2),
        )

    template.template_matches(read_json_data_file(data_path, "expected.json"))
