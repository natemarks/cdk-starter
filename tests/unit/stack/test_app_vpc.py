#!/usr/bin/env python3
""" compare the app_vpc stack to the expected stacks

use test data for teh actual environments and any other contrived cases that
seem useful


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
    """test app_vpc stack"""
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
