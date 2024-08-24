from manifest.hooks.builtin import substitute_env_vars
from manifest.hooks.expressions import resolve_expressions
from manifest.hooks.interface import execute_hook, get_hooks, register_hook


register_hook(substitute_env_vars, hook_type="pre", operation="load")
register_hook(resolve_expressions, hook_type="post", operation="load")


__all__ = (
    "get_hooks",
    "register_hook",
    "execute_hook",
    "substitute_env_vars",
    "resolve_expressions",
)
