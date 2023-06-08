import toml
from typing import Any

from manifest.serializers.base import Serializer


class TOMLSerializer(Serializer):
    """
    Serializer for TOML data.
    """
    @staticmethod
    def loads(data: bytes) -> Any:
        return toml.loads(data.decode())

    @staticmethod
    def dumps(data: Any) -> bytes:
        return toml.dumps(data).encode()
