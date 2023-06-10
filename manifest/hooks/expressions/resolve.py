import re
from typing import Any

from manifest.hooks.expressions.operations import execute_operation


def parse_expression(expression: str) -> dict | None:
    """
    Parses an expression string and returns the matched objects,
    or None if the string is not an expression.

    An expression is a string that starts with "$", contains at least one "{" and one "}",
    and is assumed to be in the format "$operation_name{arg,arg}".

    :param expression: The expression string to parse.
    :type expression: str
    :returns: The matched objects, or None if the string is not an expression.
    :rtype: dict or None
    """
    if not isinstance(expression, (str, bytes)):
        return None

    match = re.match(
        pattern=r"\$(?P<operation>\w+)\{(?P<args>.*)\}",
        string=expression
    )

    if not match:
        return None

    return match.groupdict()


async def resolve_expression(expression: str, context: dict) -> Any:
    """
    Resolve a single expression and return the resolved value.

    This function takes an expression string in the format "$operation_name{arg}" and
    a context, and returns the resolved value.

    :param expression: The expression string to be resolved.
    :type expression: str
    :param context: The context to resolve the expression in.
    :type context: dict
    :returns: The resolved value.
    :rtype: Any
    :raises ValueError: If the expression string is invalid or unknown.

    :Example:
        >>> resolve_expression("$reverse{hello}", {})
        "olleh"
    """
    # Parse the expression string
    parsed = parse_expression(expression)

    if not parsed:
        return expression

    # Get the expression information
    op = parsed["operation"]
    args = parsed["args"].split(",")

    # Ensure nested directives in args are resolved
    args = [await resolve_expression(arg, context) for arg in args]

    return await execute_operation(op, args, context)


async def resolve_expressions(data: dict, parent: dict | None = None):
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

    for key, value in data.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recursively call resolve_expressions
            # on the value and assign the result to the corresponding key in
            # the result dictionary
            data[key] = await resolve_expressions(value, parent)
        elif isinstance(value, list):
            # If the value is a list, iterate over each item and resolve the
            # expression
            data[key] = [await resolve_expression(k, parent) for k in value]
        else:
            # Otherwise, call resolve_expression on the value and assign the
            # resolved value to the corresponding key in the result dictionary
            data[key] = await resolve_expression(value, parent)
    return data
