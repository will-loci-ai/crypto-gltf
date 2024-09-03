from typing import Literal

from src.crypto_gltf.data.types import BaseKey, BaseParams


class AdaptiveCipherParamsV1(BaseParams):
    position: Literal[0, 1, 2, 3]


class Key(BaseKey): ...
