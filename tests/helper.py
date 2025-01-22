#!/usr/bin/env python3
"""Helper functions for pytest


"""
import json
import pathlib
from typing import Any
import pytest
from config.helper import PROJECT_ROOT


def case_data_path(request: pytest.FixtureRequest) -> pathlib.Path:
    """return the path to test test case data directory"""
    module_dir = request.node.location[0].removesuffix(".py")

    # module_dir will look like "tests/path/to/pytest/module"
    # replace tests with test_data
    module_data = "test_data" + str(module_dir).removeprefix("tests")
    function_name = request.node.originalname
    try:
        case_name = request.node.callspec.id + "/"
    except AttributeError:
        case_name = ""
    return PROJECT_ROOT / f"{module_data}/{function_name}/{case_name}"


def update_data_file(
    base_path: pathlib.Path, relative_path: str, contents: str
) -> None:
    """
    Append a relative path to a base Path, ensure the full path exists,
    and write the contents to the file.

    :param base_path: The base directory as a Path object.
    :param relative_path: A string representing the subdirectory and filename.
    :param contents: The string to write to the file.
    """
    # Combine base path with the relative path
    full_path = base_path / relative_path

    # Ensure the parent directories exist
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the contents to the file
    full_path.write_text(contents, encoding="utf-8")


def read_data_file(base_path: pathlib.Path, relative_path: str) -> str:
    """
    Append a relative path to a base Path, assume it is a file,
    and return its contents.

    :param base_path: The base directory as a Path object.
    :param relative_path: A string representing the subdirectory and filename.
    :return: The contents of the file as a string.
    :raises FileNotFoundError: If the file does not exist.
    """
    # Combine base path with the relative path
    full_path = base_path / relative_path

    # Ensure the file exists and read its contents
    if not full_path.is_file():
        raise FileNotFoundError(f"The file at {full_path} does not exist.")

    return full_path.read_text(encoding="utf-8")


def read_json_data_file(base_path: pathlib.Path, relative_path: str) -> Any:
    """return object from json data file"""
    full_path = base_path / relative_path
    return json.loads(full_path.read_text(encoding="utf-8"))
