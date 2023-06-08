from typing import Any, Callable

from manifest.utils import is_async_callable, run_in_thread


async def ref_op(args: list[str], data: dict) -> Any:
    """
    Resolve a $ref expression in a dictionary and return the referenced value.

    This function takes a dictionary and a $ref key in the format "file_path|key_path"
    or "key_path" and returns the value of that key. If `file_path` is included,
    then the `key_path` value is retrieved from that file.

    Example:
        ```py
        >>> ref_operation("compute.cpus", {"compute": {"cpus": 4}})
        4
        >>> ref_operation("config.yaml|compute.cpus", {})
        4
        ```
    Or in a manifest:
        ```yaml
        compute:
            cpus: 4

        # ...

        another_val: $ref{compute.cpus}
        ```

    :param args: The arguments called with the operation. Only the first argument is used as
    the path to the $ref key in the format "file_path|key_path" or "key_path".
    :type args: list[str]
    :returns: The resolved value of the $ref key.
    :rtype: Any
    :raises ValueError: If the $ref key is invalid or if the referenced file is not found.
    :raises KeyError: If the referenced key is not found in the referenced file.

    """
    from manifest.parse import load_from_file

    # Split the path into file_path and key_path
    path, *_ = args
    parts = path.split("|")

    if len(parts) == 2:
        # Both file_path and key_path are included
        file_path, key_path = parts
        ref_data = await load_from_file(file_path)
    elif len(parts) == 1:
        # Only a dict path, referencing part from same data
        key_path = parts[0]
        ref_data = data
    else:
        raise ValueError(f"Invalid $ref format: {path}")

    # Split the key_path into individual keys
    keys = key_path.split(".")

    # Traverse the dictionary using each key in key_path
    for key in keys:
        if not isinstance(ref_data, dict) or key not in ref_data:
            raise KeyError(f"No such key: {key_path}")
        ref_data = ref_data[key]
    return ref_data


def add_op(args: list[str], _) -> int:
    """
    Sums the values in the comma-separated string argument and returns the result.

    :param args: The arguments to sum
    :type args: list[str]
    :returns: The sum of the values
    :rtype: int
    """
    return sum(
        [
            int(v)
            for v in args
        ]
    )


def reverse_op(args: list[str], _) -> str:
    """
    Reverses a string.

    :param args: The string to reverse.
    :type args: list[str]
    :returns: The reversed string.
    :rtype: str
    """
    # Ensure each arg is a string
    args = [str(arg) for arg in args]

    # Reverse each string
    reversed_strings = [arg[::-1] for arg in args]

    # Join them
    return "".join(reversed_strings)


OPERATIONS: dict[str, Callable] = {
    "ref": ref_op,
    "add": add_op,
    "reverse": reverse_op,
}


def add_operation(operation_name: str, func: Callable[[list[str], dict], Any]) -> None:
    """
    Register an operation with the given name.

    :param operation_name: The name of the operation.
    :type operation_name: str
    :param func: The function to register.
    :type func: Callable
    """
    OPERATIONS[operation_name] = func


async def execute_operation(operation: str, args: list[str], data: dict) -> Any:
    """
    Execute an operation with the given arguments and data.

    :param operation: The operation to execute.
    :type operation: str
    :param args: The arguments to the operation.
    :type args: list[str]
    :param data: The data to execute the operation on.
    :type data: dict
    :returns: The result of the operation.
    :rtype: Any
    """
    op_func = OPERATIONS.get(operation, None)

    if not op_func:
        raise ValueError(f"Unknown operation: `{operation}`")

    if not is_async_callable(op_func):
        return await run_in_thread(op_func, args, data)

    return await op_func(args, data)
