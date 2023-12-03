import yaml
from typing import Any

from manifest.serializers.base import Serializer


class YAMLSerializer(Serializer):
    """
    Serializer for YAML data.
    """
    @staticmethod
    def loads(data: bytes) -> Any:
        return yaml.safe_load(data)

    @staticmethod
    def dumps(data: Any) -> bytes:
        return yaml.dump(data, sort_keys=False).encode()
