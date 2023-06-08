import rapidjson
from typing import Any

from manifest.serializers.base import Serializer


class JSONSerializer(Serializer):
    """
    Serializer for JSON data.
    """
    @staticmethod
    def loads(data: bytes) -> Any:
        return rapidjson.loads(
            data,
            parse_mode=rapidjson.PM_COMMENTS | rapidjson.PM_TRAILING_COMMAS
        )

    @staticmethod
    def dumps(data: Any) -> bytes:
        return rapidjson.dumps(data, write_mode=rapidjson.WM_PRETTY, indent=4).encode()
