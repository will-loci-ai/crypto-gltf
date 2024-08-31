from dataclasses import dataclass
from typing import Literal

from py_code.data.types import BaseKey, BaseParams


@dataclass
class AdaptiveCipherParamsV1(BaseParams):

    position: Literal[0, 1, 2, 3]

@dataclass
class Key(BaseKey):
    key: bytes
