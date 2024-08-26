from typing import Literal

from pydantic import BaseModel


class AdaptiveCipherParams(BaseModel):

    position: Literal[0, 1, 2, 3]


class AdaptiveBaseModel:
    """Base model for adaptive encryption/decryption model"""

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f"{cls} should not be instantiated")
