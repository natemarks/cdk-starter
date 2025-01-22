""" Test the functions that manage config settings

"""

import pytest
from config.settings import get_actual_path, EnvironmentSetting
from config.helper import PROJECT_ROOT
from tests.helper import case_data_path, update_data_file, read_data_file


@pytest.mark.unit
@pytest.mark.parametrize(
    "environment",
    [
        pytest.param("dev", id="dev"),
    ],
)
def test_get_actual_environment(environment):
    """test"""

    expected = PROJECT_ROOT.joinpath(f"config/{environment}")
    assert expected == get_actual_path(environment)


@pytest.mark.unit
@pytest.mark.parametrize(
    "data_path",
    [
        pytest.param(get_actual_path("dev"), id="dev"),
    ],
)
def test_environment_factory(data_path):
    """test"""
    result = EnvironmentSetting.from_data_path(data_path)
    assert isinstance(result, EnvironmentSetting)


@pytest.mark.unit
def test_case_data_path_no_params(request, update_golden):
    """sdf"""
    contents = "myoasdjkfasf,xt_contents"
    data_path = case_data_path(request)
    if update_golden:
        update_data_file(data_path, "expected.txt", contents)
    result = read_data_file(data_path, "expected.txt")
    assert result == contents


@pytest.mark.unit
@pytest.mark.parametrize(
    "contents",
    [
        pytest.param("1111", id="case1"),
    ],
)
def test_case_data_with_params(request, update_golden, contents):
    """test"""
    data_path = case_data_path(request)
    if update_golden:
        update_data_file(data_path, "expected.txt", contents)
    result = read_data_file(data_path, "expected.txt")
    assert result == contents
