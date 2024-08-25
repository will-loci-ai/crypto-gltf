from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.file.off.off import OffFile


@dataclass
class BasePlainText:
    """Base class for all plaintext types"""

    meshes: Any
    images: Any

    meshes_dim: int
    images_dim: int

    @classmethod
    def from_gltf2(cls, gltf_file: GLTFFile) -> BasePlainText:
        raise NotImplementedError()

    @classmethod
    def from_off(cls, off_file: OffFile) -> BasePlainText:
        raise NotImplementedError()

    @property
    def to_gltf2(self) -> GLTFFile:
        raise NotImplementedError()

    @property
    def to_off(self) -> OffFile:
        raise NotImplementedError()
