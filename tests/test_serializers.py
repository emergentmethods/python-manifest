import pytest

from manifest.serializers import (
    JSONSerializer,
    YAMLSerializer,
    TOMLSerializer,
)


@pytest.fixture
def dummy_data():
    return {"key": "value", "array": [1, 2, 3], "nested": {"key": "value"}}


@pytest.mark.parametrize(
    "serializer", [
        JSONSerializer,
        YAMLSerializer,
        TOMLSerializer,
    ]
)
def test_json_serializers(serializer, dummy_data):
    data = serializer.dumps(dummy_data)
    assert isinstance(data, bytes)
    assert serializer.loads(data) == dummy_data