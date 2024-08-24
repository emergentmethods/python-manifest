import os
from pathlib import Path
from typing import Any, Callable, Type, TypeVar

from dotenv import dotenv_values

from manifest.parse import (
    dump_to_file,
    parse_env_vars,
    parse_files,
    parse_key_values,
)
from manifest.pydantic import (
    BaseModel,
    get_model_extras,
    model_copy,
    model_dump,
)
from manifest.utils import (
    get_by_dot_path,
    merge_dicts,
    merge_dicts_flat,
    set_by_dot_path,
    unset_by_dot_path,
)


T = TypeVar("T", bound="Manifest")


class Manifest(BaseModel):
    def normalize(
        self,
        *,
        include: set[str] | set[int] | dict[int, Any] | dict[str, Any] | None = None,
        exclude: set[str] | set[int] | dict[int, Any] | dict[str, Any] | None = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, Any]:
        """
        Return a dictionary representation of the Manifest
        with the values coerced to basic types.

        :param include: A set of fields to include
        :type include: set[str] | set[int] | dict[int, Any] | dict[str, Any] | None
        :param exclude: A set of fields to exclude
        :type exclude: set[str] | set[int] | dict[int, Any] | dict[str, Any] | None
        :param by_alias: Whether to use the alias names or not
        :type by_alias: bool
        :param exclude_unset: Whether to exclude unset values or not
        :type exclude_unset: bool
        :param exclude_defaults: Whether to exclude default values or not
        :type exclude_defaults: bool
        :param exclude_none: Whether to exclude None values or not
        :type exclude_none: bool
        """
        return model_dump(
            self,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @property
    def extra_fields(self) -> dict[str, Any]:
        # Get any extra fields that were set but not defined in the model
        return get_model_extras(self)

    @classmethod
    async def build(
        cls: Type[T],
        files: list[str | Path] | None = None,
        dotenv_files: list[str] | None = None,
        key_values: list[str] | None = None,
        env_prefix: str = "CONFIG",
        env_delimiter: str = "__",
        pre_process_hooks: list[Callable] | None = None,
        post_process_hooks: list[Callable] | None = None,
        filesystem_options: dict[str, Any] | None = None,
        **kwargs,
    ) -> T:
        """
        Build the Manifest from a variety of sources.

        :param files: A list of files to parse
        :type files: list[Path]
        :param dotenv_files: A list of dotenv files to parse
        :type dotenv_files: list[Path]
        :param key_values: A list of key_values in the form `a.b.c=value`
        :type key_values: list[str]
        :param env_prefix: A prefix to identify environment variables to parse
        :type env_prefix: str
        :param env_delimiter: The delimiter used in the environment variables
        :type env_delimiter: str
        :param pre_process_hooks: A list of pre-process hooks to run before deserialization
        :type pre_process_hooks: list[Callable]
        :param post_process_hooks: A list of post-process hooks to run after deserialization
        :type post_process_hooks: list[Callable]
        :param kwargs: Additional keyword arguments to pass to the model
        :type kwargs: dict[str, Any]
        :return: The built Manifest
        """
        # Get the environment variables from any dotenv files if
        # provided and os.environ and merge to a flat dict
        env_vars = merge_dicts_flat(
            *[dotenv_values(dotenv_file) for dotenv_file in dotenv_files or []] + [dict(os.environ)]
        )

        # Parse the files if they are provided
        parsed_files = (
            await parse_files(
                files=files or [],
                pre_process_hooks=pre_process_hooks,
                post_process_hooks=post_process_hooks,
                **(filesystem_options or {}),
            )
            if files
            else {}
        )

        # Parse the env vars for the final dictionary representation
        parsed_env_vars = parse_env_vars(
            env_vars=env_vars, prefix=env_prefix, delimiter=env_delimiter
        )

        # Parse any key_values provided
        parsed_overrides = parse_key_values(key_values or [], coerce=True)
        # Merge everything together into a single material dictionary
        material = merge_dicts(parsed_files, parsed_env_vars, parsed_overrides, kwargs)
        return cls(**material)

    @classmethod
    async def from_files(
        cls: Type[T],
        files: list[str | Path],
        pre_process_hooks: list[Callable] | None = None,
        post_process_hooks: list[Callable] | None = None,
        root_alias: str = "root",
        filesystem_options: dict | None = None,
        **kwargs,
    ) -> T:
        """
        Build the Manifest from a list of files.

        :param files: A list of files to parse
        :type files: list[Path]
        :param pre_process_hooks: A list of pre-process hooks to run before deserialization
        :type pre_process_hooks: list[Callable]
        :param post_process_hooks: A list of post-process hooks to run after deserialization
        :type post_process_hooks: list[Callable]
        :param kwargs: Additional keyword arguments to pass to the model
        :type kwargs: dict[str, Any]
        :return: The built Manifest
        """
        parsed_files = await parse_files(
            files=files,
            pre_process_hooks=pre_process_hooks,
            post_process_hooks=post_process_hooks,
            root_alias=root_alias,
            **(filesystem_options or {}),
        )

        return cls(**{**parsed_files, **kwargs})

    @classmethod
    async def from_file(
        cls: Type[T],
        file_path: str | Path,
        pre_process_hooks: list[Callable] | None = None,
        post_process_hooks: list[Callable] | None = None,
        root_alias: str = "root",
        filesystem_options: dict | None = None,
        **kwargs,
    ) -> T:
        """
        Build the Manifest from a file.

        :param file_path: The path to the file to parse
        :type file_path: str
        :param pre_process_hooks: A list of pre-process hooks to run before deserialization
        :type pre_process_hooks: list[Callable]
        :param post_process_hooks: A list of post-process hooks to run after deserialization
        :type post_process_hooks: list[Callable]
        :param kwargs: Additional keyword arguments to pass to the model
        :type kwargs: dict[str, Any]
        :return: The built Manifest
        """
        return await cls.from_files(
            files=[file_path],
            pre_process_hooks=pre_process_hooks,
            post_process_hooks=post_process_hooks,
            filesystem_options=filesystem_options,
            root_alias=root_alias,
            **kwargs,
        )

    @classmethod
    async def from_env(
        cls: Type[T],
        dotenv_files: list[str] | None = None,
        env_prefix: str = "CONFIG",
        env_delimiter: str = "__",
        **kwargs,
    ) -> T:
        """
        Get the Manifest from environment variables.

        :param dotenv_files: A list of dotenv files to parse, optional
        :type dotenv_files: list[str]
        :param env_prefix: A prefix to identify environment variables to parse
        :type env_prefix: str
        :param env_delimiter: The delimiter used in the environment variables
        :type env_delimiter: str
        :param kwargs: Additional keyword arguments to pass to the model
        :type kwargs: dict[str, Any]
        :return: The built Manifest
        """
        # Get the environment variables from any dotenv files if
        # provided and os.environ and merge to a flat dict
        env_vars = merge_dicts_flat(
            *[dotenv_values(dotenv_file) for dotenv_file in dotenv_files or []] + [dict(os.environ)]
        )

        # Parse the env vars for the final dictionary representation
        parsed_env_vars = parse_env_vars(
            env_vars=env_vars, prefix=env_prefix, delimiter=env_delimiter
        )

        return cls(**{**parsed_env_vars, **kwargs})

    @classmethod
    async def from_key_values(cls: Type[T], key_values: list[str], **kwargs) -> T:
        """
        Build the Manifest from a list of key-value pairs.

        :param key_values: A list of key-value pairs in the form `a.b.c=value`
        :type key_values: list[str]
        :param kwargs: Additional keyword arguments to pass to the model
        :type kwargs: dict[str, Any]
        :return: The built Manifest
        """
        parsed_key_values = parse_key_values(key_values, coerce=True)
        return cls(**{**parsed_key_values, **kwargs})

    def set_by_key(self, key: str, value: Any):
        """
        Get a copy of the Manifest with the given key set to the given value.

        :param key: The key to set which looks like `a.b.c` for nested parameters
        :type key: str
        :param value: The value to set
        :type value: Any
        :return: A copy of the Manifest with the given key set to the given value
        """
        return model_copy(self, update=set_by_dot_path(self.normalize(), key, value))

    def unset_by_key(self, key: str):
        """
        Get a copy of the Manifest with the given key unset.

        :param key: The key to unset which looks like `a.b.c` for nested parameters
        :type key: str
        :return: A copy of the Manifest with the given key unset
        """
        return type(self)(**unset_by_dot_path(self.normalize(), key))

    def get_by_key(self, key: str):
        """
        Get the value of a key in the Manifest.

        :param key: The key to get which looks like `a.b.c` for nested parameters
        :type key: str
        :return: The value of the key
        """
        return get_by_dot_path(self.normalize(), key)

    async def to_file(
        self,
        file_path: str | Path,
        pre_process_hooks: list[Callable] | None = None,
        post_process_hooks: list[Callable] | None = None,
        root_alias: str = "root",
        filesystem_options: dict | None = None,
        **kwargs,
    ) -> int:
        """
        Save the Manifest to a file.

        :param file_path: The path to the file to save to
        :type file_path: str
        :param pre_process_hooks: A list of pre-process hooks to run before serialization
        :type pre_process_hooks: list[Callable]
        :param post_process_hooks: A list of post-process hooks to run after serialization
        :type post_process_hooks: list[Callable]
        :param root_alias: The alias to use for the root model, defaults to "root"
        :type root_alias: str
        :param filesystem_options: Additional keyword arguments to pass to the filesystem
        :return: The number of bytes written to the file
        """
        return await dump_to_file(
            file=file_path,
            data=self.normalize(),
            pre_process_hooks=pre_process_hooks,
            post_process_hooks=post_process_hooks,
            root_alias=root_alias,
            **(filesystem_options or {}),
            **kwargs,
        )
