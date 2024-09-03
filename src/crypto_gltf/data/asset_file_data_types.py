from dataclasses import dataclass

import numpy as np
from PIL import Image
from gltf_crypto_conan1014.data.types import Composition, JSONDict
from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any

class OffData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    verts: np.ndarray
    faces: list[Any]
    colors: np.ndarray

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data):
        verts, colors = data.get("verts"), data.get("colors")
        assert Composition.VERTS == verts
        # assert (
        #     (Composition.RGB == colors)
        #     or (Composition.RGBA == colors)
        #     or (Composition.GREYSCALE == colors)
        #     or (Composition.EMPTY == colors)
        # )
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
