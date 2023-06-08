import os
from typing import Callable, Any

from manifest.utils import is_async_callable, run_in_thread


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


def substitute_env_vars(text: bytes, env_vars: dict[str, str] = {}) -> bytes:
    """
    Replace environment variables in a string with their values.

    The string variables are formatted as $VAR or ${VAR}.

    :param text: The string to substitute environment variables in.
    :return: The string with environment variables substituted.
    """
    from string import Template

    if not env_vars:
        env_vars = dict(os.environ)

    template = Template(text.decode("utf-8"))
    substituted = template.safe_substitute(env_vars)

    return substituted.encode("utf-8")
