from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Literal, NamedTuple, Type, TypeVar

import numpy as np
from pydantic import BaseModel, ConfigDict

JSONDict = dict[str, Any]

# FILETYPES


class Extension:
    """Extensions for filetypes"""

    ASSET = Literal[".off", ".glb", ".gltf"]
    IMAGE = Literal[".png", ".jpeg", ".jpg"]

    ANY_SUPPORTED = Literal[".off", ".png", ".jpeg", ".jpg"]


FileTypeName = Literal["ASSET", "IMAGE"]


class FileTypeConfig(NamedTuple):
    name: FileTypeName
    extensions: tuple[Extension.ANY_SUPPORTED, ...]


class FileType:
    ASSET = FileTypeConfig("ASSET", tuple(Extension.ASSET.__args__))
    IMAGE = FileTypeConfig("IMAGE", tuple(Extension.IMAGE.__args__))


# DATATYPES


@dataclass
class ArrayComposition3D:
    dim: int
    axis_restrictions: dict[Literal[0, 1, 2], int]
    dtype: type | None = None

    def __eq__(self, arr: np.ndarray) -> bool:
        """Check array is of composition composition"""
        shape, dtype = arr.shape, arr.dtype
        res = len(shape) == self.dim
        for k in self.axis_restrictions.keys():
            res = res and shape[k] == self.axis_restrictions[k]
        if self.dtype is not None:
            res = res and dtype == self.dtype
        return res

    @classmethod
    def from_data(cls, data: np.ndarray) -> ArrayComposition3D:
        """Initialise generalised composition from array"""
        return ArrayComposition3D(
            dim=len(data.shape), axis_restrictions={}, dtype=data.dtype
        )


class Composition:
    """Data type matrix composition"""

    FACES = ArrayComposition3D(dim=1, axis_restrictions={}, dtype=int)  # (n, 3)

    VERTS = ArrayComposition3D(
        dim=2, axis_restrictions={1: 3}, dtype=np.float32
    )  # (n, 3)

    RGB = ArrayComposition3D(
        dim=3, axis_restrictions={2: 3}, dtype=np.uint8
    )  # RGB (n, m, 3)

    GREYSCALE = ArrayComposition3D(
        dim=2, axis_restrictions={1: 2}
    )  # Black & white (n, 2)

    RGBA = ArrayComposition3D(dim=3, axis_restrictions={2: 4}, dtype=np.uint8)

    P = ArrayComposition3D(dim=2, axis_restrictions={}, dtype=np.uint8)

    AAD = ArrayComposition3D(dim=2, axis_restrictions={1: 3}, dtype=np.uint32)

    EMPTY = ArrayComposition3D(dim=1, axis_restrictions={0: 0})


DataTypeName = Literal[None, "GREYSCALE", "RGB", "MESH", "RGBA", "P"]


class PlnMDataType(NamedTuple):
    name: DataTypeName
    composition: ArrayComposition3D
    renderable: bool
    typed_name: str | None = None

    @classmethod
    def from_data(cls, data: np.ndarray) -> PlnMDataType:
        if Composition.FACES == data:
            return CombinedPlnMDataTypes.FACES
        elif Composition.VERTS == data:
            return CombinedPlnMDataTypes.VERTS
        elif Composition.GREYSCALE == data:
            return CombinedPlnMDataTypes.GREYSCALE
        elif Composition.RGB == data:
            return CombinedPlnMDataTypes.RGB
        elif Composition.RGBA == data:
            return CombinedPlnMDataTypes.RGBA
        elif Composition.P == data:
            return CombinedPlnMDataTypes.P
        else:
            composition = ArrayComposition3D.from_data(data)
            return cls(
                name=None,
                composition=composition,
                renderable=False,
                typed_name=None,
            )


class CombinedPlnMDataTypes:
    VERTS = PlnMDataType("MESH", Composition.VERTS, False)
    FACES = PlnMDataType("MESH", Composition.FACES, False)

    GREYSCALE = PlnMDataType("GREYSCALE", Composition.GREYSCALE, True, "L")
    RGB = PlnMDataType("RGB", Composition.RGB, True, "RGB")
    RGBA = PlnMDataType("RGBA", Composition.RGBA, True, "RGBA")
    P = PlnMDataType("P", Composition.P, True, "P")


# RESPONSE TYPES

T = TypeVar("T")
A = TypeVar("A")
K = TypeVar("K")


class EncryptionResponse(BaseModel, Generic[T, A, K]):
    """Generic response model for encryption model or system"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    ciphertext: T
    aad: A
    key: K


class AAD_DATA(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    aad: np.ndarray
    encrypt_images: bool
    meshes_params: JSONDict
    images_params: JSONDict


# ENCRYPTION BASE TYPES


class BaseParams(BaseModel):
    """Base class for encryption model parameters"""

    p: int
    q: int
    r: int


class BaseKey(BaseModel):
    """Base class for encryption model keys"""

    k1: bytes | None = None
    k2: bytes | None = None
    k3: bytes | None = None
