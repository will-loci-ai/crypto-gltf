from dataclasses import dataclass
from typing import Any

import numpy as np
from crypto_gltf.data.types import Composition, JSONDict
from PIL import Image
from pydantic import BaseModel, ConfigDict, model_validator


@dataclass
class OffData:
    model_config = ConfigDict(arbitrary_types_allowed=True)
    verts: type[np.ndarray]
    faces: list[Any]
    colors: type[np.ndarray]

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data):
        verts = data.get("verts")
        if not Composition.VERTS == verts:
            raise ValueError('Malformatted vertices. Bad .off file.')
        return data


@dataclass
class Gltf2Data:
    gltf: JSONDict
    images: dict[int, Image.Image]
    accessors: dict[int, np.ndarray]
    is_glb: bool


class AssetFileDataType:
    OFF = OffData
    GLTF2 = Gltf2Data
