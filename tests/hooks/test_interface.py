import pytest

from manifest.hooks.interface import (
    unregister_hook,
    register_hook,
    execute_hook,
    get_hooks
)


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

    # Register the hook
    register_hook(hook, hook_type="pre", operation="load")

    # Assert it's in there
    hooks = get_hooks(hook_type="pre", operation="load")
    assert hook in hooks

    # Assert invalid hook types or operations return an empty list
    assert get_hooks(hook_type="invalid", operation="load") == []

    # Assert invalid hook types or operations raise ValueError in register_hook
    with pytest.raises(ValueError):
        register_hook(hook, hook_type="invalid", operation="load")

    # Unregister the hook
    unregister_hook(hook, hook_type="pre", operation="load")

    # Assert it's no longer in there
    hooks = get_hooks(hook_type="pre", operation="load")
    assert hook not in hooks

    # Assert invalid hook types or operations raise ValueError in unregister_hook
    with pytest.raises(ValueError):
        unregister_hook(hook, hook_type="invalid", operation="load")
