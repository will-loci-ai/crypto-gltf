from dataclasses import dataclass

import numpy as np
from PIL import Image
from py_code.data.base_data import PlnM
from py_code.data.types import JSONDict


@dataclass
class OffData:
    mesh: PlnM
    colors: PlnM


@dataclass
class Gltf2Data:
    gltf: JSONDict
    images: dict[int, Image.Image]
    accessors: dict[int, np.ndarray]
    is_glb: bool


class AssetFileDataType:
    OFF = OffData
    GLTF2 = Gltf2Data
