import base64
import os
from typing import Any, Callable

from manifest.utils import is_async_callable, run_in_thread


async def ref_op(args: list[str], data: Any) -> Any:
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
    from manifest.parse import current_file, load_from_file, parse_file_path

    # Split the path into file_path and key_path
    path, *_ = args
    parts = path.split("|")

    if len(parts) == 2:
        # Both file_path and key_path are included
        file_path, key_path = parts
        parsed_path = parse_file_path(file_path)

        # If the file path is local, and it's relative
        # join it with the parent directory of the current file
        # so that it's relative to the current file and not the
        # current working directory
        if parsed_path["is_local"]:  # pragma: no cover
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.path.dirname(current_file.get()), file_path)

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


OPERATIONS: dict[str, Callable] = {
    "ref": ref_op,
    "env": lambda args, _: os.environ.get(args[0], ""),
    "sum": lambda args, _: sum([float(v) for v in args]),
    "reverse": lambda args, _: "".join([str(arg)[::-1] for arg in args]),
    "upper": lambda args, _: args[0].upper(),
    "lower": lambda args, _: args[0].lower(),
    "base64": lambda args, _: base64.b64encode(args[0].encode()).decode(),
    "unbase64": lambda args, _: base64.b64decode(args[0]).decode(),
}


def register_operation(operation_name: str, func: Callable[[list[str], dict], Any]) -> None:
    """
    Register an operation with the given name.

    :param operation_name: The name of the operation.
    :type operation_name: str
    :param func: The function to register.
    :type func: Callable
    """
    OPERATIONS[operation_name] = func


def unregister_operation(operation_name: str) -> None:
    """
    Unregister an operation with the given name.

    :param operation_name: The name of the operation.
    :type operation_name: str
    """
    del OPERATIONS[operation_name]


def get_operation(operation_name: str) -> Callable[[list[str], dict], Any]:
    """
    Get the operation with the given name.

    :param operation_name: The name of the operation.
    :type operation_name: str
    :returns: The operation.
    :rtype: Callable
    """
    return OPERATIONS[operation_name]


async def execute_operation(operation: str, args: list[str], data: Any) -> Any:
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
