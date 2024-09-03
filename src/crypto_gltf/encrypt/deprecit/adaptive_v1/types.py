from typing import Literal

from gltf_crypto_conan1014.data.types import BaseKey, BaseParams


class AdaptiveCipherParamsV1(BaseParams):
    position: Literal[0, 1, 2, 3]


class Key(BaseKey): ...
