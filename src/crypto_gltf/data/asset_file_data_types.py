from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image
from pydantic import BaseModel, ConfigDict, model_validator
from src.crypto_gltf.data.types import Composition, JSONDict


class OffData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    verts: type[np.ndarray]
    faces: list[Any]
    colors: type[np.ndarray]

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


class Gltf2Data(BaseModel):
    gltf: JSONDict
    images: dict[int, Image.Image]
    accessors: dict[int, np.ndarray]
    is_glb: bool


class AssetFileDataType:
    OFF = OffData
    GLTF2 = Gltf2Data
