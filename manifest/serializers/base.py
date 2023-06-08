from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Serializer(Protocol):
    @staticmethod
    def loads(data: bytes) -> Any:
        ...  # pragma: no cover

    @staticmethod
    def dumps(data: Any) -> bytes:
        ...  # pragma: no cover
