import re
from typing import Any

from manifest.hooks.expressions.operations import execute_operation


EXPRESSION_REGEX = re.compile(r"\$(?P<operation>\w+)\{(?P<args>.*)\}")
EXPRESSION_LOC_REGEX = re.compile(r"\$(\w+)\{([^{}]*)\}")


def parse_expression(expression: str) -> dict | None:
    """
    Parses an expression string and returns the matched objects,
    or None if the string is not an expression.

    An expression is a string that starts with `$`, contains at least one `{` and one `}`,
    and is assumed to be in the format `$operation_name{arg,arg}`.

    :param expression: The expression string to parse.
    :type expression: str
    :returns: The matched objects, or None if the string is not an expression.
    :rtype: dict or None
    """
    match = re.match(pattern=EXPRESSION_REGEX, string=expression)
    return match.groupdict() if match else None


async def resolve_expression(expression: str, context: Any) -> Any:
    """
    Resolve expressions within a string and return the resolved value.

    This function takes a string that may contain expressions in the format "$operation_name{arg}"
    and a context, and returns the string with all expressions resolved.

    Example:

        >>> await resolve_expression("some text with $reverse{hello}", {})
        "some text with olleh"

    :param expression: The string that may contain expressions to be resolved.
    :type expression: str
    :param context: The context to resolve the expressions in.
    :type context: dict
    :returns: The string with all expressions resolved.
    :rtype: Any
    :raises ValueError: If an expression string is invalid or unknown.
    """
    if not isinstance(expression, str):
        return expression

    async def _resolve(expr: str) -> str:
        # Parse the expression string
        parsed = parse_expression(expr)

        if not parsed:
            return expr

        # Get the expression information
        op = parsed["operation"]
        args = parsed["args"].split(",")

        # Ensure nested directives in args are resolved
        return await execute_operation(
            op, [await resolve_expression(arg, context) for arg in args], context
        )

    while True:
        matches = list(re.finditer(EXPRESSION_LOC_REGEX, expression))
        if not matches:
            break

        for match in reversed(matches):
            start, end = match.span()
            resolved_value = await _resolve(match.group(0))

            if expression == match.group(0):
                # If the entire expression is the match, return the resolved value directly
                return resolved_value
            else:
                # Otherwise, concatenate the resolved value as a string
                expression = expression[:start] + str(resolved_value) + expression[end:]

    return expression


async def resolve_expressions(data: dict | list | Any, parent: Any | None = None):
    """
    Recursively resolves expressions in a dictionary and returns a new dictionary
    with the resolved values.

    :param data: The dictionary to resolve expressions in.
    :type data: dict
    :param parent: The parent dictionary. Defaults to None.
    :type parent: dict, optional
    :returns: A new dictionary with the resolved values.
    :rtype: dict
    """
    if not parent:
        parent = data

    if isinstance(data, dict):
        return {key: await resolve_expressions(value, parent) for key, value in data.items()}
    elif isinstance(data, list):
        return [await resolve_expressions(item, parent) for item in data]
    else:
        return await resolve_expression(data, parent)

    return data
