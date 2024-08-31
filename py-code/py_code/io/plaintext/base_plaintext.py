from dataclasses import dataclass
from typing import Any


@dataclass
class BasePlainText:
    """Base class for all plaintext types"""

    meshes: Any
    images: Any

    meshes_dim: int
    images_dim: int
