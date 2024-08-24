import pytest
import os

from manifest.hooks.expressions.operations import (
    execute_operation,
    register_operation,
    get_operation,
    unregister_operation
)
from manifest.parse import dump_to_file


def test_register_unregister_get_operation():
    def test_func():
        pass

    register_operation("test", test_func)
    assert get_operation("test") == test_func

    unregister_operation("test")
    with pytest.raises(KeyError):
        get_operation("test")


async def test_ref_operation():
    data = {"compute": {"cpus": 4}}
    file_path = "memory://test.json"
    await dump_to_file(file_path, data)

    # test path in same data
    result = await execute_operation("ref", ["compute.cpus"], data)
    assert result == 4

    # test path in different file
    result = await execute_operation("ref", [f"{file_path}|compute.cpus"], {})
    assert result == 4

    with pytest.raises(KeyError):
        await execute_operation("ref", ["invalid.path"], {})

    with pytest.raises(ValueError):
        await execute_operation("ref", ["invalid|path|4|5"], {})


async def test_env_operation():
    os.environ["TEST_ENV"] = "test"

    result = await execute_operation("env", ["TEST_ENV"], {})
    assert result == "test"

    result = await execute_operation("env", ["INVALID_ENV"], {})
    assert result == ""

    del os.environ["TEST_ENV"]
