from typing import Callable, Any

from manifest.utils import is_async_callable, run_in_thread

_HOOKS: dict[tuple[str, str], list[Callable]] = {
    ("pre", "load"): [],
    ("post", "load"): [],
    ("pre", "dump"): [],
    ("post", "dump"): [],
}


def get_hooks(hook_type: str, operation: str) -> list[Callable]:
    """
    Get the pre hooks.

    The available hook_types are `pre` and `post`. The available operations are `load` and `dump`.

    :return: The pre hooks.
    :rtype: list[Callable]
    """
    return _HOOKS.get((hook_type, operation), [])


def register_hook(hook: Callable, hook_type: str, operation: str) -> None:
    """
    Register a hook to be executed on the data.

    The available hook_types are `pre` and `post`. The available operations are `load` and `dump`.

    :param hook: The hook to be registered.
    :type hook: Callable
    """
    key = (hook_type, operation)

    if key not in _HOOKS:
        raise ValueError(f"Invalid hook type: {hook_type}")

    _HOOKS[key].append(hook)


async def execute_hook(hook: Callable, *args, **kwargs) -> Any:
    """
    Execute a hook on the given data and return the result.

    :param hook: The hook to be executed.
    :type hook: Callable
    :param data: The data to be passed to the hook.
    :type data: Any
    :return: The result of the hook.
    :rtype: Any
    """
    if not is_async_callable(hook):
        return await run_in_thread(hook, *args, **kwargs)
    else:
        return await hook(*args, **kwargs)
