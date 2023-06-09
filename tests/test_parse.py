import pytest
import fsspec

from manifest.parse import (
    get_serializer_from_type,
    determine_file_type,
    parse_dot_list,
    parse_env_vars,
    load_from_file,
    dump_to_file,
    write_to_file,
    read_from_file,
)
from manifest.serializers import (
    JSONSerializer,
    YAMLSerializer,
    NoOpSerializer
)


def test_determine_file_type():
    assert determine_file_type(".json") == "JSON"
    assert determine_file_type(".yaml") == "YAML"
    assert determine_file_type(".txt") == "*"
    assert determine_file_type(".yml") == "YAML"


def test_get_serializer_from_type():
    assert issubclass(get_serializer_from_type("JSON"), JSONSerializer)
    assert issubclass(get_serializer_from_type("YAML"), YAMLSerializer)
    assert issubclass(get_serializer_from_type("*", _default=NoOpSerializer), NoOpSerializer)

    with pytest.raises(KeyError):
        get_serializer_from_type("*")
    
    with pytest.raises(KeyError):
        get_serializer_from_type("Unsupported")


def test_parse_dot_list():
    assert parse_dot_list(["a.b.c=5"]) == {"a": {"b": {"c": 5}}}
    assert parse_dot_list(["a.b.c=5", "a.b.d=6"]) == {"a": {"b": {"c": 5, "d": 6}}}


@pytest.mark.parametrize(
    "env_vars, prefix, delimiter, expected_result",
    [
        (
            {
                "APP__NAME": "MyApp",
                "APP__VERSION": "1.0",
                "DB__HOST": "localhost",
                "DB__PORT": "5432",
                "API__ENABLED": "true",
            },
            "APP",
            "__",
            {
                "name": "MyApp",
                "version": "1.0",
            }
        ),
        (
            {
                "APP-NAME": "MyApp",
                "APP-VERSION": "1.0",
                "DB-HOST": "localhost",
                "DB-PORT": "5432",
                "API-ENABLED": "true",
            },
            "APP",
            "-",
            {
                "name": "MyApp",
                "version": "1.0",
            }
        ),
        (
            {
                "DB__HOST": "localhost",
                "DB__PORT": "5432",
                "API__ENABLED": "true",
            },
            "APP",
            "__",
            {}
        ),
    ]
)
def test_parse_env_vars(env_vars, prefix, delimiter, expected_result):
    result = parse_env_vars(env_vars, prefix, delimiter)
    assert result == expected_result


@pytest.mark.parametrize(
        "file_path, content", [
            (
                "memory://test_file1.txt", b"Hello, World!"
            ),  # Good case
            (
                "memory://test_file2.txt", b"Python is great!"
            ),  # Good case
            (
                "", b"Hello, World!"
            ),  # Bad case - empty file path
            (
                None, b"Hello, World!"
            ),  # Bad case - None file path
            (
                "memory://test_file3.txt", ""
            ),  # Bad case - empty content
            (
                "memory://test_file4.txt", None
            ),  # Bad case - None content
        ]
)
async def test_read_write_to_file(file_path, content):
    if file_path and content:
        await write_to_file(file_path, content)
        assert await read_from_file(file_path) == content
    else:
        with pytest.raises(Exception):
            await write_to_file(file_path, content)


@pytest.mark.parametrize(
    "file_path, data",
    [
        (
            "memory://test_file.json",
            {"name": "John Doe", "age": 30},
        ),
        (
            "memory://test_file.yaml",
            {"name": "John Doe", "age": 30},
        ),
        (
            "memory://test_file.toml",
            {"name": "John Doe", "age": 30},
        ),
        (
            "memory://empty.json",
            {}
        )
    ]
)
async def test_load_dumps(file_path, data):
    await dump_to_file(file_path, data)
    result = await load_from_file(file_path)