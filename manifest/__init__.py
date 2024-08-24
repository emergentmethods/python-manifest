from importlib import metadata  # noqa: I001

__version__ = metadata.version("python-manifest")
del metadata


from manifest.base import Manifest  # noqa: E402
from manifest.instantiable import Instantiable  # noqa: E402


__all__ = (
    "Manifest",
    "Instantiable",
)
