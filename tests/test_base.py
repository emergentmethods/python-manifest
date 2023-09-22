import pytest
import os
from typing import Optional, Union
from pydantic import RootModel

from manifest.base import Manifest, BaseModel
from manifest.parse import dump_to_file


class NestedModel(BaseModel):
    foo: bool = True
    bar: dict[str, Optional[Union[int, float]]] = {}


class MyManifest(Manifest, extra='allow'):
    x: int = 5
    database: str = "sqlite:///database.db"
    nested: NestedModel = NestedModel()


@pytest.fixture
async def test_config_files():
    await dump_to_file(
        "memory://base.json",
        {
            "x": 10,
            "database": "someotherplace"
        }
    )

    await dump_to_file(
        "memory://nested.yml",
        {
            "nested": {
                "foo": False,
                "bar": {
                    "j": 0.5,
                    "k": 10,
                    "l": None
                }
            }
        }
    )

    await dump_to_file(
        "memory://alternate.json",
        [1, 2, 3]
    )


async def test_manifest_build(test_config_files):
    files = ["memory://base.json", "memory://nested.yml"]

    # Test file parsing
    config = await MyManifest.build(files)
    expected_model = {
        "x": 10,
        "database": "someotherplace",
        "nested": {
            "foo": False,
            "bar": {
                "j": 0.5,
                "k": 10,
                "l": None
            }
        }
    }
    assert config.model_dump() == expected_model

    # Test passing kwargs
    expected_model["x"] = 1
    config = await MyManifest.build(files, x=1)
    assert config.model_dump() == expected_model

    # Test key_values
    expected_model["nested"]["foo"] = True
    config = await MyManifest.build(files, key_values=["nested.foo=True"], x=1)
    assert config.model_dump() == expected_model

    # Test environment variable overrides
    expected_model["nested"]["bar"]["j"] = 0.1
    expected_model["nested"]["bar"]["k"] = 10
    expected_model["nested"]["bar"]["l"] = None
    os.environ["CONFIG__NESTED__BAR__J"] = "0.1"
    os.environ["CONFIG__NESTED__BAR__K"] = "10"
    os.environ["CONFIG__NESTED__BAR__L"] = "None"
    config = await MyManifest.build(files, key_values=["nested.foo=True"], x=1)
    assert config.model_dump() == expected_model
    del os.environ["CONFIG__NESTED__BAR__J"]
    del os.environ["CONFIG__NESTED__BAR__K"]
    del os.environ["CONFIG__NESTED__BAR__L"]
    expected_model["nested"]["bar"]["j"] = 0.5

    # Test post process hooks and extra fields
    config = await MyManifest.build(
        files,
        post_process_hooks=[lambda d: {**d, "y": 1}],
        key_values=["nested.foo=True"],
        x=1,
    )
    expected_model["y"] = 1
    assert config.model_dump() == expected_model
    assert config.extra_fields == {"y": 1}


async def test_manifest_from_files(test_config_files):
    files = ["memory://base.json", "memory://nested.yml"]
    config = await MyManifest.from_files(files)

    expected_model = {
        "x": 10,
        "database": "someotherplace",
        "nested": {
            "foo": False,
            "bar": {
                "j": 0.5,
                "k": 10,
                "l": None
            }
        }
    }

    assert config.model_dump() == expected_model


async def test_manifest_from_key_values(test_config_files):
    config = await MyManifest.from_key_values(
        key_values=["x=10", "database=someotherplace"]
    )

    expected_model = {
        "x": 10,
        "database": "someotherplace",
        "nested": {
            "foo": True,
            "bar": {}
        }
    }

    assert config.model_dump() == expected_model


async def test_manifest_from_env(test_config_files):
    os.environ["CONFIG__X"] = "10"
    os.environ["CONFIG__DATABASE"] = "someotherplace"

    config = await MyManifest.from_env()

    del os.environ["CONFIG__X"]
    del os.environ["CONFIG__DATABASE"]

    expected_model = {
        "x": 10,
        "database": "someotherplace",
        "nested": {
            "foo": True,
            "bar": {}
        },
    }

    assert config.model_dump() == expected_model


async def test_manifest_to_file(test_config_files):
    from manifest.parse import read_from_file

    config = await MyManifest.from_key_values(
        key_values=["x=10", "database=someotherplace", "nested.bar.l=None"]
    )

    # Test JSON
    assert (await config.to_file("memory://test.json")) > 0
    actual_result_json = b"""{
    "x": 10,
    "database": "someotherplace",
    "nested": {
        "foo": true,
        "bar": {
            "l": null
        }
    }
}"""
    assert (await read_from_file("memory://test.json")) == actual_result_json
    # Test YAML
    assert (await config.to_file("memory://test.yml")) > 0
    actual_result_yaml = b"""database: someotherplace
nested:
  bar:
    l: null
  foo: true
x: 10
"""
    assert (await read_from_file("memory://test.yml")) == actual_result_yaml


async def test_manifest_set_by_key(test_config_files):
    config = await MyManifest.from_key_values(
        key_values=["x=10", "database=someotherplace"]
    )

    assert config.x == 10
    assert config.database == "someotherplace"

    config = config.set_by_key("x", 1)
    config = config.set_by_key("database", "sqlite:///database.db")

    assert config.x == 1
    assert config.database == "sqlite:///database.db"


async def test_manifest_unset_by_key(test_config_files):
    config = await MyManifest.from_key_values(
        key_values=["x=10", "database=someotherplace"]
    )

    assert config.x == 10
    assert config.database == "someotherplace"

    config = config.unset_by_key("x")
    config = config.unset_by_key("database")

    assert config.x == 5
    assert config.database == "sqlite:///database.db"


async def test_manifest_get_by_key(test_config_files):
    config = await MyManifest.from_key_values(
        key_values=["x=10", "database=someotherplace"]
    )

    assert config.get_by_key("x") == 10
    assert config.get_by_key("database") == "someotherplace"
    assert config.get_by_key("nested.foo") == True


async def test_alternate_root_manifest(test_config_files) -> None:
    file = "memory://alternate.json"

    class MyManifest(Manifest, RootModel):
        root: list[int] = []

    config = await MyManifest.from_files([file])
    assert config.root == [1, 2, 3]

    config.root.append(4)
    await config.to_file(file)

    config = await MyManifest.from_files([file])
    assert config.root == [1, 2, 3, 4]