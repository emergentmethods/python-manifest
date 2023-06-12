from importlib import metadata
__version__ = metadata.version("python-manifest")
del metadata


from manifest.base import Manifest
from manifest.instantiable import Instantiable


__all__ = (
    "Manifest",
    "Instantiable",
)
