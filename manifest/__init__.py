from importlib import metadata
__version__ = metadata.version(__name__)
del metadata


from manifest.base import Manifest
from manifest.instantiable import Instantiable


__all__ = (
    "Manifest",
    "Instantiable",
)
