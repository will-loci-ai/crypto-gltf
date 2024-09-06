from typing import Literal

from crypto_gltf.data.types import BaseKey, BaseParams


class AdaptiveCipherParamsV1(BaseParams):
    p: Literal[0, 1, 2, 3]
    q: int = 0
    r: int = 0


class Key(BaseKey): ...
