#!/usr/bin/env python3
""" compare the simple_asg stack to the expected stacks

use test data for teh actual environments and any other contrived cases that
seem useful


"""
# pylint: disable=duplicate-code
import json
import pytest
from aws_cdk import App, assertions, Environment
from config.settings import get_actual_path
from stack.app_vpc import AppVpcInput, AppVpcStack
from stack.simple_asg import SimpleAsgInput, SimpleAsgStack
from tests.helper import case_data_path, update_data_file, read_json_data_file


@pytest.mark.unit
@pytest.mark.parametrize(
    "environment,stack_id",
    [
        pytest.param("dev", "aaa", id="dev"),
        pytest.param("staging", "bbb", id="staging"),
        pytest.param("production", "ccc", id="production"),
    ],
)
def test_simple_asg_stack_actual(
    request, environment, stack_id, update_golden
):
    """test simple_asg stack with actual environment data

    use the live data in config/dev, config/staging and config/production
    """
    # use stack input data from actual environments
    input_path = get_actual_path(environment)
    # test_data path for case
    data_path = case_data_path(request)
    s_input = SimpleAsgInput.from_config_directory(input_path, stack_id)

    app = App()
    av_input = AppVpcInput.from_config_directory(input_path)
    av_stk = AppVpcStack(
        scope=app,
        cdk_env=Environment(),
        s_input=av_input,
    )
    stk = SimpleAsgStack(
        scope=app,
        cdk_env=Environment(),
        s_input=s_input,
        app_vpc_stack=av_stk,
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
    "stack_id",
    [
        pytest.param("aaa", id="custom_aaa"),
    ],
)
def test_simple_asg_stack_custom(request, stack_id, update_golden):
    """test app_vpc stack with custom configuration

    test using environment data stored in the case data path. This is convenient
    for test unusual cases without putting them into an actual environment.
    """
    # test_data path for case
    data_path = case_data_path(request)
    input_path = data_path
    s_input = SimpleAsgInput.from_config_directory(input_path, stack_id)

    app = App()
    av_input = AppVpcInput.from_config_directory(input_path)
    av_stk = AppVpcStack(
        scope=app,
        cdk_env=Environment(),
        s_input=av_input,
    )
    stk = SimpleAsgStack(
        scope=app,
        cdk_env=Environment(),
        s_input=s_input,
        app_vpc_stack=av_stk,
    )
    template = assertions.Template.from_stack(stk)
    if update_golden:
        update_data_file(
            data_path,
            "expected.json",
            json.dumps(template.to_json(), indent=2),
        )

    template.template_matches(read_json_data_file(data_path, "expected.json"))
