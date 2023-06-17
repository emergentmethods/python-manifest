import pytest

from manifest.serializers import (
    JSONSerializer,
    YAMLSerializer,
    TOMLSerializer,
)


@pytest.fixture
def dummy_data_complete():
    return {"key": "value", "array": [1, 2, 3], "nested": {"key": "value"}, "t": None}


@pytest.fixture
def dummy_data_toml():
    # TOML doesn't support anything like a None or Null value
    # It's better to follow the specification when using TOML rather than
    # attempting to hack around it
    # If none values are needed, use another format
    return {"key": "value", "array": [1, 2, 3], "nested": {"key": "value"}}


@pytest.mark.parametrize(
    "serializer", [
        JSONSerializer,
        YAMLSerializer,
    ]
)
def test_complete_serializers(serializer, dummy_data_complete):
    data = serializer.dumps(dummy_data_complete)
    assert isinstance(data, bytes)
    assert serializer.loads(data) == dummy_data_complete


def test_toml_serializer(dummy_data_toml):
    data = TOMLSerializer.dumps(dummy_data_toml)
    assert isinstance(data, bytes)
    assert TOMLSerializer.loads(data) == dummy_data_toml
