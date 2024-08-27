from __future__ import annotations

from base64 import urlsafe_b64encode as b64e
from dataclasses import dataclass

from pydantic import BaseModel, model_validator


@dataclass
class AdaptiveCipherParams:
    # p, q, r here represents the byte to be taken from the float32
    p: int
    q: int
    r: int

    @model_validator(mode="before")
    def validate_fields(self):
        assert len(set([self.p, self.q, self.r])) == 3  # check p, q, r are distinct
        assert (
            self.p > self.q > self.r
        )  # r must be least significant byte of the 3, p the most significant


class SBlocks(BaseModel):
    s1: bytes
    s2: bytes
    s3: bytes


@dataclass
class Key:
    k1: bytes | None = None
    k2: bytes | None = None
    k3: bytes | None = None

    @model_validator(mode="before")
    def validate_fields(self):
        assert self.k1 or self.k2 or self.k3

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
