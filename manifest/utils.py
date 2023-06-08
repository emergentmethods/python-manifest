import asyncio
import os
from typing import Any, Callable, Union
from pathlib import Path
from functools import partial
from collections import UserDict
from fsspec.core import url_to_fs
from contextlib import contextmanager


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
    return await asyncio.get_running_loop().run_in_executor(
        None, partial(func, *args, **kwargs)
    )


class DotDict(UserDict):
    """
    A dictionary-like object that supports dot paths as keys.

    Inherits from UserDict to provide a dictionary-like interface.
    """

    def __init__(self, data: dict | None = None) -> None:
        super().__init__(data or {})

    def __getitem__(self, key):
        """
        Get the value at the specified dot path.

        :param key: A string representing the dot path to the desired value.
        :return: The value at the specified dot path.
        :raises KeyError: If the dot path does not exist in the DotDict.
        """
        value = self.get_by_dot_path(key)

        if value is None:
            raise KeyError(key)

        return value

    def __setitem__(self, key, value):
        """
        Set the value at the specified dot path.

        :param key: A string representing the dot path to the desired value.
        :param value: The value to be set at the specified dot path.
        :raises KeyError: If the dot path does not exist in the DotDict and
                          its parent keys cannot be created.
        """
        self.set_by_dot_path(key, value)

    def __delitem__(self, key):
        """
        Delete the key-value pair at the specified dot path.

        :param key: A string representing the dot path to the desired key-value pair.
        :raises KeyError: If the dot path does not exist in the DotDict.
        """
        self.unset_by_dot_path(key)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the value at the specified dot path.

        :param key: A string representing the dot path to the desired value.
        :param default: Optional default value to return if the dot path does not exist.
        :return: The value at the specified dot path, or the default value.
        """
        return self.get_by_dot_path(key, default)

    def get_by_dot_path(self, dot_path: str, default: Any = None) -> Any:
        """
        Get the value at the specified dot path.

        :param dot_path: A string representing the dot path to the desired value.
        :param default: Optional default value to return if the dot path does not exist.
        :return: The value at the specified dot path, or the default value.
        """
        keys = dot_path.split('.')
        current_data = self.data
        for key in keys:
            if key in current_data:
                current_data = current_data[key]
            else:
                return default
        return current_data

    def set_by_dot_path(self, dot_path: str, value: Any) -> None:
        """
        Set the value at the specified dot path.

        :param dot_path: A string representing the dot path to the desired value.
        :param value: The value to be set at the specified dot path.
        :raises KeyError: If the dot path does not exist in the DotDict and
                          its parent keys cannot be created.
        """
        keys = dot_path.split('.')
        current_data = self.data
        for key in keys[:-1]:
            current_data = current_data.setdefault(key, {})
        current_data[keys[-1]] = value

    def unset_by_dot_path(self, dot_path: str) -> None:
        """
        Delete the key-value pair at the specified dot path.

        :param dot_path: A string representing the dot path to the desired key-value pair.
        :raises KeyError: If the dot path does not exist in the DotDict.
        """
        keys = dot_path.split('.')
        current_data = self.data
        for key in keys[:-1]:
            if key in current_data:
                current_data = current_data[key]
            else:
                raise KeyError(dot_path)
        try:
            del current_data[keys[-1]]
        except KeyError:
            raise KeyError(dot_path)


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
        module_path, class_name = path.strip(' ').rsplit('.', 1)
    except ValueError:
        raise ImportError(f"{path} isn\'t a valid module path.")

    initial = import_module(module_path)
    module = reload(initial)

    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError(f"Module {path} does not have a `{class_name}` attribute")  # noqa:E501


def merge_dicts_flat(*dicts) -> dict:
    """
    Merge any number of dictionaries into a single flat dictionary.

    This function takes any number of dictionaries and merges them into a single flat
    dictionary where keys with identical names are merged into a single value.

    :param dicts: The dictionaries to merge.
    :type dicts: Any number of dicts
    :returns: A dictionary containing the merged key-value pairs.
    :rtype: dict

    :Example:
        >>> dict1 = {'a': 1, 'b': 2}
        >>> dict2 = {'b': 3, 'c': 4}
        >>> dict3 = {'d': 5}
        >>> merge_dicts_flat(dict1, dict2, dict3)
        {'a': 1, 'b': 3, 'c': 4, 'd': 5}
    """
    return {k: v for d in dicts for k, v in d.copy().items()}


def merge_dicts(*dicts) -> dict:
    """
    Merge any number of dictionaries into a single nested dictionary.

    This function takes any number of dictionaries and merges them into a single nested
    dictionary where keys with identical paths are merged into a single value.

    :param dicts: The dictionaries to merge.
    :type dicts: Any number of dicts
    :returns: A nested dictionary containing the merged key-value pairs.
    :rtype: dict

    :Example:
        >>> dict1 = {'a': {'b': {'c': '1'}}}
        >>> dict2 = {'a': {'b': {'d': '2'}}}
        >>> dict3 = {'a': {'e': {'f': '3'}}}
        >>> merge_dicts(dict1, dict2, dict3)
        {'a': {'b': {'c': '1', 'd': '2'}, 'e': {'f': '3'}}}
    """
    result: dict = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
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


def coerce_to_basic_types(value: Any) -> Union[int, float, bool, str, list, dict, None]:
    """
    Coerces a given value to basic types, including int, float, bool, and str.

    :param value: The value to be coerced.
    :type value: Any

    :return: The coerced value.
    :rtype: Union[int, float, bool, str, List, Dict, None]
    """

    if isinstance(value, (list, tuple)):
        return [coerce_to_basic_types(item) for item in value]
    elif isinstance(value, dict):
        return {k: coerce_to_basic_types(v) for k, v in value.items()}
    elif hasattr(value, '__dict__'):
        try:
            return {k: coerce_to_basic_types(v) for k, v in value.__dict__.items()}
        except:
            pass
    elif isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ['true', 'false']:
            return normalized == 'true'
        elif normalized in ['none', 'null']:
            return None
    elif isinstance(value, bool):
        return value

    try:
        if float(value).is_integer():
            return int(value)
        else:
            return float(value)
    except:
        try:
            return str(value)
        except:
            pass
    return None