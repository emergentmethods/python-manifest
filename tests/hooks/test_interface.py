import pytest

from manifest.hooks.interface import register_hook, execute_hook, get_hooks


async def test_execute_hook():
    def hook():
        return "value"

    async def async_hook():
        return "async value"

    result = await execute_hook(hook)
    result_async = await execute_hook(async_hook)

    # Assert the result is as expected
    assert result == "value"
    assert result_async == "async value"


def test_register_get_hooks():
    def hook(value: bytes):
        return value

    register_hook(hook, hook_type="pre", operation="load")

    hooks = get_hooks(hook_type="pre", operation="load")

    # Assert the result is as expected
    assert hook in hooks

    assert get_hooks(hook_type="invalid", operation="load") == []

    with pytest.raises(ValueError):
        register_hook(hook, hook_type="invalid", operation="load")

