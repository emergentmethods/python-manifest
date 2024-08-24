import asyncio
import os
import re
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable, Literal, Union

from fsspec.core import url_to_fs


class SentinelMeta(type):
    def __init__(cls, name, bases, dict):
        super(SentinelMeta, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SentinelMeta, cls).__call__(*args, **kwargs)
        return cls._instance

    def __repr__(cls) -> str:
        return f"<{cls.__name__}>"

    def __bool__(cls) -> Literal[False]:
        return False


class Sentinel(metaclass=SentinelMeta): ...


def is_async_callable(f: Callable) -> bool:
    """
    Test if the callable is an async callable

    :param f: The callable to test
    """
    from inspect import iscoroutinefunction

    if hasattr(f, "__wrapped__"):  # pragma: no cover
        f = f.__wrapped__

    return iscoroutinefunction(f)


async def run_in_thread(func: Callable, *args, **kwargs):
    """
    Run a sync function in the default ThreadPool.

    :param func: The callable to run
    :param *args: The args to pass to the callable
    :param **kwargs: The kwargs to pass to the callable
    :returns: The return value of the callable
    """
    return await asyncio.get_running_loop().run_in_executor(None, partial(func, *args, **kwargs))


def parse_dot_path(dot_path: str) -> list:
    """
    Parse a dot path into a list of keys and indices.
    Handles dot notation and bracket notation for lists.
    """
    path_parts = []
    # Split by dots
    parts = dot_path.split(".")
    for part in parts:
        # Find brackets in part
        match = re.match(r"(.*?)\[(\d*)\]", part)
        if match:
            key, index = match.groups()
            path_parts.append(key)
            if index:
                path_parts.append(int(index))
            else:
                path_parts.append(Sentinel)
        else:
            path_parts.append(part)
    return path_parts


def get_by_dot_path(data: dict, dot_path: str, default: Any = None) -> Any:
    """
    Get the value at the specified dot path.
    """
    assert isinstance(data, dict), "data must be a dictionary"
    keys = parse_dot_path(dot_path)

    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        elif isinstance(data, list) and isinstance(key, int):
            data = data[key] if key < len(data) else default
        elif key is Sentinel:
            return default
        else:
            return default
    return data


def set_by_dot_path(data: dict, dot_path: str, value: Any) -> dict:
    """
    Set the value at the specified dot path.
    """
    assert isinstance(data, dict), "data must be a dictionary"
    keys = parse_dot_path(dot_path)

    def set_value(ref: dict | list, key: str | int | Sentinel, value: Any) -> None:
        if isinstance(ref, dict):
            ref[key] = value
        elif isinstance(ref, list):
            if isinstance(key, int):
                while len(ref) <= key:
                    ref.append(Sentinel)
                ref[key] = value
            elif key is Sentinel:
                ref.append(value)

    ref = data
    for key in keys[:-1]:
        if isinstance(ref, dict):
            ref = ref.setdefault(key, {})
        elif isinstance(ref, list):
            if isinstance(key, int):
                while len(ref) <= key:
                    ref.append(Sentinel)
                ref[key] = value
                return data
            elif key is Sentinel:
                ref.append(value)
                return data
        else:
            raise ValueError(f"Unsupported type: {type(ref)}")

    set_value(ref, keys[-1], value)
    return data


def unset_by_dot_path(data: dict, dot_path: str) -> dict:
    """
    Delete the key-value pair at the specified dot path.
    """
    assert isinstance(data, dict), "data must be a dictionary"
    keys = parse_dot_path(dot_path)

    ref = data
    for key in keys[:-1]:
        if isinstance(ref, dict):
            ref = ref.get(key, {})
        elif isinstance(ref, list) and isinstance(key, int):
            ref = ref[key] if key < len(ref) else []
        else:
            return data

    if isinstance(ref, dict) and keys[-1] in ref:
        del ref[keys[-1]]
    elif isinstance(ref, list) and isinstance(keys[-1], int):
        if keys[-1] < len(ref):
            del ref[keys[-1]]
    return data


# def get_by_dot_path(data: dict, dot_path: str, default: Any = None) -> Any:
#     """
#     Get the value at the specified dot path.

#     :param data: The dictionary to get the value from.
#     :param dot_path: A string representing the dot path to the desired value.
#     :return: The value at the specified dot path.
#     """
#     assert isinstance(data, dict), "data must be a dictionary"
#     keys = dot_path.split('.')

#     try:
#         for k in keys:
#             data = data[k]
#         return data
#     except (KeyError, TypeError):
#         return default


# def set_by_dot_path(data: dict, dot_path: str, value: Any) -> dict:
#     """
#     Set the value at the specified dot path.

#     :param data: The dictionary to set the value in.
#     :param field_path: A string representing the dot path to the desired value.
#     :param value: The value to be set at the specified dot path.
#     """
#     assert isinstance(data, dict), "data must be a dictionary"
#     keys = dot_path.split('.')

#     ref = data
#     # Iterate through the keys and set the value at the final key.
#     for k in keys[:-1]:
#         ref = ref.setdefault(k, {})

#     ref[keys[-1]] = value
#     return data


# def unset_by_dot_path(data: dict, dot_path: str) -> dict:
#     """
#     Delete the key-value pair at the specified dot path.

#     :param data: The dictionary to delete the key-value pair from.
#     :param dot_path: A string representing the dot path to the desired key-value pair.
#     """
#     assert isinstance(data, dict), "data must be a dictionary"
#     keys = dot_path.split('.')

#     ref = data
#     # Iterate through the keys and get the dictionary at the penultimate key.
#     for k in keys[:-1]:
#         try:
#             ref = ref[k]
#         except KeyError:
#             # If a key in the path doesn't exist, there's nothing to unset
#             return data

#     # Delete the value at the final key.
#     if keys[-1] in ref:
#         del ref[keys[-1]]

#     return data


@contextmanager
def current_directory(directory: Path):
    """
    Context manager that changes the current working directory to the specified `directory`.
    Upon completion, the current working directory is restored to its original value.

    :param directory: A `Path` object representing the directory to change to.
    :type directory: Path

    :raises ValueError: If the specified path does not exist or is not a directory.

    :yields: None
    """
    import os

    # Check if the specified path exists and is a directory.
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"`{directory}` must be a directory")

    # Save the current working directory before changing it.
    old = os.getcwd()

    try:
        # Change the current working directory to the specified directory.
        os.chdir(directory.resolve())
        # Yield control back
        yield
    finally:
        # Restore the original working directory.
        os.chdir(old)


def import_from_string(path: str) -> Any:
    from importlib import import_module, reload

    try:
        module_path, class_name = path.strip(" ").rsplit(".", 1)
    except ValueError:
        raise ImportError(f"{path} isn't a valid module path.") from None

    initial = import_module(module_path)
    module = reload(initial)

    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError(f"Module {path} does not have a `{class_name}` attribute") from None  # noqa:E501


def merge_dicts_flat(*dicts) -> dict:
    """
    Merge any number of dictionaries into a single flat dictionary.

    This function takes any number of dictionaries and merges them into a single flat
    dictionary where keys with identical names are merged into a single value.

    If a key contains a list, the latest list replaces the old one unless `Sentinel`
    is used in which case only the `Sentinel` values are overridden.

    :param dicts: The dictionaries to merge.
    :type dicts: Any number of dicts
    :returns: A dictionary containing the merged key-value pairs.
    :rtype: dict

    :Example:
        >>> dict1 = {'a': 1, 'b': [1, 2, 3]}
        >>> dict2 = {'b': [Sentinel, 5, Sentinel]}
        >>> dict3 = {'c': 3}
        >>> merge_dicts_flat(dict1, dict2, dict3)
        {'a': 1, 'b': [1, 5, 3], 'c': 3}
    """
    result: dict = {}

    for d in dicts:
        for key, value in d.items():
            if key in result:
                if isinstance(result[key], list) and isinstance(value, list):
                    merged_list = result[key]
                    for i in range(len(value)):
                        if i < len(merged_list):
                            if value[i] is not Sentinel:
                                merged_list[i] = value[i]
                        else:
                            merged_list.append(value[i])
                    result[key] = merged_list
                else:
                    result[key] = value
            else:
                result[key] = value

    return result


def merge_dicts(*dicts) -> dict:
    """
    Merge any number of dictionaries into a single nested dictionary.

    This function takes any number of dictionaries and merges them into a single nested
    dictionary where keys with identical paths are merged into a single value.

    If a key contains a list, the lists are concatenated with later values taking precedence,
    and `Sentinel` placeholders in lists are overridden by subsequent values.

    :param dicts: The dictionaries to merge.
    :type dicts: Any number of dicts
    :returns: A nested dictionary containing the merged key-value pairs.
    :rtype: dict
    """
    result: dict = {}

    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                merged_list = result[key]
                for i in range(len(value)):
                    if i < len(merged_list):
                        if value[i] is not Sentinel:
                            merged_list[i] = value[i]
                    else:
                        merged_list.append(value[i])
                result[key] = merged_list
            else:
                result[key] = value

    return result


def get_filename_suffix(file_path: str):
    """
    Get the suffix of a file path.

    :param file_path: The path to the file.
    :type file_path: str
    :returns: The suffix of the file path.
    :rtype: str
    """
    # parse the URL and get the path
    _, path = url_to_fs(file_path)
    file_name, file_extension = os.path.splitext(path)

    return file_extension


def coerce_sequence(value: list | tuple) -> list:
    return [coerce_to_basic_types(item) for item in value]


def coerce_dict(value: dict) -> dict:
    return {k: coerce_to_basic_types(v) for k, v in value.items()}


def coerce_object(value: object) -> dict:
    if hasattr(value, "__dict__"):
        try:
            return coerce_dict(value.__dict__)
        except AttributeError:
            pass
    return {}


def coerce_str(value: str) -> Union[int, float, str, bool, None]:
    normalized = value.strip().lower()
    if normalized in ["true", "false"]:
        return normalized == "true"
    elif normalized in ["none", "null"]:
        return None
    return coerce_num(value)


def coerce_num(value: Union[int, float, str]) -> Union[int, float, str]:
    try:
        if "." not in str(value):
            return int(value)
        else:
            return float(value)
    except (ValueError, TypeError):
        return str(value)


def coerce_to_basic_types(value: Any) -> Union[int, float, bool, str, list, dict, None]:
    """
    Coerces a given value to basic types, including int, float, bool, and str, list, dict, and None.

    :param value: The value to be coerced.
    :type value: Any

    :return: The coerced value.
    :rtype: Union[int, float, bool, str, List, Dict, None]
    """
    if isinstance(value, (list, tuple)):
        return coerce_sequence(value)
    elif isinstance(value, dict):
        return coerce_dict(value)
    elif hasattr(value, "__dict__"):
        return coerce_object(value)
    elif isinstance(value, str):
        return coerce_str(value)
    elif isinstance(value, bool) or value is None:
        return value
    else:
        return coerce_num(value)
