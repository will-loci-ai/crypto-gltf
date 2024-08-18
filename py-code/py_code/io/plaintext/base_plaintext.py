from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from py_code.data.types import Extension
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.file.off.off import OffFile
from typing_extensions import TypedDict


class Extras(TypedDict):
    filename_ext: Extension.ASSET
    import_path: str


@dataclass
class BasePlainTex:
    """Base class for all plaintext types"""

    data: Any
    extras: Extras

    @classmethod
    def from_gltf2(cls, gltf_file: GLTFFile) -> BasePlainTex:
        raise NotImplementedError()

    @classmethod
    def from_off(cls, off_file: OffFile) -> BasePlainTex:
        raise NotImplementedError()

    @property
    def to_gltf2(self) -> GLTFFile:
        raise NotImplementedError()

    @property
    def to_off(self) -> OffFile:
        raise NotImplementedError()
