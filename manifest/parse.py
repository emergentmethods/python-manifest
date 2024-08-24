import os
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Callable

from fsspec import AbstractFileSystem
from fsspec import open as fsspec_open
from fsspec.core import url_to_fs

from manifest.hooks import execute_hook, get_hooks
from manifest.serializers import (
    JSONSerializer,
    Serializer,
    TOMLSerializer,
    YAMLSerializer,
)
from manifest.utils import (
    coerce_to_basic_types,
    get_filename_suffix,
    merge_dicts,
    merge_dicts_flat,
    run_in_thread,
    set_by_dot_path,
)


Undefined = type("Undefined", (), {"__repr__": lambda self: "Undefined"})
current_file: ContextVar[str] = ContextVar("current_file", default="")


def parse_file_path(file_path: str) -> dict[str, Any]:
    """
    Parse a file path and return a dictionary containing the protocol, path, and whether
    the file is local.

    :param file_path: The path to the file.
    :type file_path: str
    :return: A dictionary containing the protocol, path, and whether the file is local.
    """
    fs: AbstractFileSystem
    fs, _ = url_to_fs(file_path)

    return {
        "protocol": fs.protocol,
        "path": fs._strip_protocol(file_path),
        "is_local": getattr(fs, "local_file", False),
    }


def determine_file_type(file_ext: str) -> str:
    """
    Given a file extension, return the corresponding file type.

    File types are used to determine which serializer to use when loading or dumping
    data from a file. For example, if the file extension is ".json", then the file type
    will be "JSON". If the file extension is not recognized, then the file type will be "*",
    which by default is used to indicate that no serializer was found.

    Only the following file types are supported:
        - JSON
        - YAML

    :param file_ext: The file extension to be checked.
    :type file_ext: str
    :return: The file type corresponding to the file extension.
    """
    _ext_map = {
        (".json",): "JSON",
        (".yaml", ".yml"): "YAML",
        (".toml",): "TOML",
    }
    for k, v in _ext_map.items():
        if file_ext in k:
            return v
    return "*"


def get_serializer_from_type(_type: str, _default: Any = Undefined) -> Serializer:
    """
    Given a file type, return the corresponding serializer.

    :param type: The file type to be checked.
    :type type: str
    :param _default: The default serializer to use if no serializer is
    found for the given file type.
    Defaults to NoOpSerializer.
    :type _default: Serializer
    :return: The serializer corresponding to the file type.
    """
    if _default is not Undefined and not isinstance(_default, Serializer):
        raise TypeError(f"Default serializer must be of type Serializer, not {type(_default)}")

    _serializers: dict[str, Serializer] = {
        "JSON": JSONSerializer,
        "YAML": YAMLSerializer,
        "TOML": TOMLSerializer,
    }

    if _default is not Undefined:
        _serializers["*"] = _default

    if _type not in _serializers:
        raise KeyError(f"No Serializer for: {_type}")

    return _serializers[_type]


async def read_from_file(file: str, **kwargs) -> bytes:
    """
    Read the contents of a file and return the data as a byte string.

    :param file: The path to the file to be read.
    :type file: Path
    :return: The contents of the file as a byte string.
    """

    def _():
        with fsspec_open(file, mode="rb", **kwargs) as f:
            return f.read()

    return await run_in_thread(_)


async def write_to_file(file: str, content: bytes, **kwargs) -> int:
    """
    Write the contents of a byte string to a file.

    :param file: The path to the file to be written to.
    :type file: Path
    :param content: The contents to be written to the file.
    :type content: bytes
    :return: The number of bytes written to the file.
    """

    def _():
        with fsspec_open(file, "wb", **kwargs) as f:
            return f.write(content)

    return await run_in_thread(_)


async def dump_to_file(
    file: str | Path,
    data: Any,
    pre_process_hooks: list[Callable] | None = None,
    post_process_hooks: list[Callable] | None = None,
    default_serializer: Any = Undefined,
    root_alias: str = "root",
    **kwargs,
) -> int:
    """
    Persist data to a file by serializing it, writing it to the file, and returning the number
    of bytes written.

    :param file: The path to the file to be written to.
    :type file: str
    :param data: The data to be persisted to the file.
    :type data: Any
    :param serializer: The serializer to be used to serialize the data.
    :type serializer: Serializer
    :param pre_process_hooks: A list of hooks to be called before serializing the data.
    :type pre_process_hooks: list[Callable]
    :param post_process_hooks: A list of hooks to be called after serializing the data.
    :type post_process_hooks: list[Callable]
    :return: The number of bytes written to the file.
    :rtype: int
    """
    string_path = str(file)
    pre_process_hooks = pre_process_hooks or []
    post_process_hooks = post_process_hooks or []

    if isinstance(data, dict) and root_alias in data:
        data = data[root_alias]

    # Get the serializer for the file type
    serializer = get_serializer_from_type(
        _type=determine_file_type(get_filename_suffix(string_path)), _default=default_serializer
    )

    pre_process_hooks = get_hooks("pre", operation="dump") + pre_process_hooks
    post_process_hooks = get_hooks("post", operation="dump") + post_process_hooks

    # Set the current file context variable to have a reference of the current file
    # being worked on in the hooks
    token = current_file.set(string_path)

    try:
        # Pre-process the data
        for pre_hook in pre_process_hooks:
            data = await execute_hook(pre_hook, data)

        # Serialize the data
        serialized_data = serializer.dumps(data)

        # Post-process the data
        for post_hook in post_process_hooks:
            serialized_data = await execute_hook(post_hook, serialized_data)
    finally:
        # Reset the current file context variable
        current_file.reset(token)

    # Write the serialized data to the file
    return await write_to_file(string_path, serialized_data, **kwargs)


async def load_from_file(
    file: str | Path,
    pre_process_hooks: list[Callable] | None = None,
    post_process_hooks: list[Callable] | None = None,
    default_serializer: Any = Undefined,
    root_alias: str = "root",
    **kwargs,
) -> Any:
    """
    Parse a file by loading it, deserializing it, and returning the resulting dictionary.

    :param file: The path to the file to be parsed.
    :type file: str
    :param pre_process_hooks: A list of hooks to be called before deserializing the file.
    :type pre_process_hooks: list[Callable]
    :param post_process_hooks: A list of hooks to be called after deserializing the file.
    :type post_process_hooks: list[Callable]
    :return: The parsed data from the file.
    :rtype: Any
    """
    string_path = str(file)
    pre_process_hooks = pre_process_hooks or []
    post_process_hooks = post_process_hooks or []

    # Get the serializer for the file type
    serializer = get_serializer_from_type(
        _type=determine_file_type(get_filename_suffix(string_path)), _default=default_serializer
    )

    pre_process_hooks = get_hooks("pre", operation="load") + pre_process_hooks
    post_process_hooks = get_hooks("post", operation="load") + post_process_hooks

    parsed_info = parse_file_path(string_path)

    if parsed_info["is_local"]:
        if not os.path.isabs(file):
            # parse_file_path gives an expanded filepath if local, so replace it
            # with that to ensure the referenced file path is always absolute
            file = parsed_info["path"]

    # Read the file
    raw_data = await read_from_file(string_path, **kwargs)
    # Set the current file context variable to have a reference of the current file
    # being worked on in the hooks
    token = current_file.set(string_path)

    try:
        # Pre-process the file contents
        for pre_hook in pre_process_hooks:
            raw_data = await execute_hook(pre_hook, raw_data)

        # Deserialize the file contents
        data = serializer.loads(raw_data)

        # Handle empty files
        if not data:
            data = {}

        # Handle files with different root types
        if not isinstance(data, dict):
            data = {root_alias: data}

        # Post-process the file contents
        for post_hook in post_process_hooks:
            data = await execute_hook(post_hook, data)
    finally:
        # Reset the current file context variable
        current_file.reset(token)

    return data


async def parse_files(
    files: list[str | Path],
    pre_process_hooks: list[Callable] | None = None,
    post_process_hooks: list[Callable] | None = None,
    **kwargs,
) -> dict:
    """
    Parse multiple files by calling `parse_file()` on each one and returning the merged
    dictionary.

    :param files: A list of file paths to be parsed.
    :type files: list[str]
    :return: A dictionary containing the parsed data from all of the files.
    :rtype: dict[str, Any]
    """
    return merge_dicts_flat(
        *[
            await load_from_file(
                file=file,
                pre_process_hooks=pre_process_hooks,
                post_process_hooks=post_process_hooks,
                **kwargs,
            )
            for file in files
        ]
    )


def parse_env_vars(env_vars: dict[str, Any], prefix: str, delimiter: str = "__") -> dict:
    """
    Parse environment variables by converting them into a list of strings in the format "key=value",
    filtering out any keys that do not start with the specified prefix, and then calling
    `parse_key_values()` on the resulting list.

    :param env_vars: A dictionary containing environment variables to be parsed.
    :type env_vars: dict[str, Any]
    :param prefix: A prefix that identifies which environment variables to parse.
    :type prefix: str
    :param delimiter: A delimiter used in the keys of the environment variables. Defaults to "__".
    :type delimiter: str
    :return: The parsed environment variables as a dictionary.
    :rtype: dict[str, Any]
    """
    return parse_key_values(
        [
            "{k}={v}".format(
                # Remove the beginning prefix and delimiter, and convert to lowercase
                k=key.replace(prefix + delimiter, "").lower(),
                v=val,
            ).replace(delimiter, ".")
            # Replace any delimiters with dots to be parsed by `parse_key_values()`
            for key, val in env_vars.items()
            # Only parse environment variables that start with the prefix
            if key.startswith(prefix)
        ],
        coerce=True,
    )


def parse_key_value(key_value: str, coerce: bool = False) -> dict:
    """
    Parse a key-value pair in the format "a.b.c=value" and return a dictionary.

    :param key_value: A key-value pair in the format "key=value".
    :type key_value: str
    :param coerce: Whether to coerce the value to a basic type. Defaults to False.
    :type coerce: bool
    :return: A dictionary containing the parsed key-value pair.
    :rtype: dict[str, Any]
    """
    k, v = key_value.split("=", 1)
    return set_by_dot_path({}, k, v if not coerce else coerce_to_basic_types(v))


def parse_key_values(key_values: list[str], coerce: bool = False) -> dict:
    """
    Parse a list of dot-delimited key value strings and return a nested dictionary.

    This function takes a list of dot-delimited strings in the format "a.b.c=value"
    and returns a nested dictionary where each key in the dictionary represents
    a level of nesting in the original dot-delimited string.

    :param key_values: A list of dot-delimited strings.
    :type key_values: List[str]
    :param coerce: Whether to coerce the values to basic types. Defaults to False.
    :type coerce: bool
    :returns: A nested dictionary containing the parsed key-value pairs.
    :rtype: dict

    :Example:
        >>> kvs = ["a.b.c=1", "a.b.d=2", "a.e=3"]
        >>> parse_key_values(kvs)
        {'a': {'b': {'c': '1', 'd': '2'}, 'e': '3'}}
    """
    return merge_dicts(*[parse_key_value(key_value, coerce=coerce) for key_value in key_values])
