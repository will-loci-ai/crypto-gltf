from dataclasses import dataclass

import numpy as np
from PIL import Image
from py_code.data.types import Composition, JSONDict
from pydantic import model_validator


@dataclass
class OffData:
    verts: np.ndarray
    faces: np.ndarray
    colors: np.ndarray

    @model_validator(mode="before")
    def validate_fields(self):
        assert Composition.VERTS == self.verts
        assert Composition.FACES == self.faces
        assert (
            (Composition.RGB == self.colors)
            or (Composition.RGBA == self.colors)
            or (Composition.GREYSCALE == self.colors)
        )


@dataclass
class Gltf2Data:
    gltf: JSONDict
    images: dict[int, Image.Image]
    accessors: dict[int, np.ndarray]
    is_glb: bool


class AssetFileDataType:
    OFF = OffData
    GLTF2 = Gltf2Data
