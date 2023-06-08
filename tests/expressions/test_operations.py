import pytest

from manifest.expressions.operations import execute_operation
from manifest.parse import dump_to_file


async def test_add_operation():
    result = await execute_operation("add", ["1", "2", "3"], {})
    assert result == 6


async def test_reverse_operation():
    result = await execute_operation("reverse", ["HelloWorld"], {})
    assert result == "dlroWolleH"


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
