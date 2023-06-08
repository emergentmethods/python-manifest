from typing import Any

from manifest.serializers.base import Serializer


class NoOpSerializer(Serializer):
    """
    NoOp serializer that returns data as-is.
    """
    @staticmethod
    def loads(data: Any) -> Any:
        return data  # pragma: no cover

    @staticmethod
    def dumps(data: Any) -> Any:
        return data  # pragma: no cover
