from __future__ import annotations

from base64 import urlsafe_b64encode as b64e
from dataclasses import dataclass
from typing import Any

from crypto_gltf.data.types import BaseKey, BaseParams
from pydantic import BaseModel, model_validator


class AdaptiveCipherParamsV2(BaseParams):
    # p, q, r here represents the byte to be taken from the float32
    p: int
    q: int
    r: int

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any):
        p, q, r = data.get("p"), data.get("q"), data.get("r")
        assert (
            (p is not None) and (q is not None) and (r is not None)
        )  # all fields must be provided
        assert (
            3 >= p > q > r >= 0
        )  # r must be least significant byte of the 3, p the most significant

        return data


class SBlocks(BaseModel):
    s1: bytes
    s2: bytes
    s3: bytes


class Key(BaseKey):
    k1: bytes | None = None
    k2: bytes | None = None
    k3: bytes | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any):
        k1, k2, k3 = data.get("k1"), data.get("k2"), data.get("k3")
        assert k1 or k2 or k3
        return data

    def __str__(self) -> str:
        return str({k: b64e(v) for k, v in self.__dict__.items() if v is not None})

    @property
    def filled(self) -> bool:
        """Returns true if all subkeys below highest non-null subkey exist"""
        if self.k3 is not None:
            return (self.k2 is not None) and (self.k1 is not None)
        elif self.k2 is not None:
            return self.k1 is not None
        else:
            return self.k1 is not None  # could remove but kept for clarity

    @property
    def size(self) -> int:
        """Returns the number of non null subkeys"""
        return len([ki for ki in self.__dict__.values() if ki is not None])


class BlockSelection(BaseModel):
    p: bool = False
    q: bool = False
    r: bool = False

    @classmethod
    def all(cls) -> BlockSelection:
        """Select all blocks"""
        return cls(p=True, q=True, r=True)
