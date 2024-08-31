from __future__ import annotations

from base64 import urlsafe_b64encode as b64e
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Literal

import numpy as np
from py_code.data.types import BaseKey, BaseParams
from py_code.encrypt.adaptive.utils import buffer_length
from pydantic import BaseModel, model_validator


@dataclass
class Key(BaseKey):
    k1: bytes | None = None
    k2: bytes | None = None
    k3: bytes | None = None

    @model_validator(mode="before")
    def validate_fields(self, data: Any):
        k1, k2, k3 = data.get("k1"), data.get("k2"), data.get("k3")
        assert k1 or k2 or k3  # at least one key must be provided
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

    @property
    def single_block(self) -> Literal["p", "q", "r"]:
        assert sum([self.p, self.q, self.r]) == 1
        if self.p:
            return "p"
        elif self.q:
            return "q"
        else:
            return "r"


@dataclass
class AdaptiveCipherParams(BaseParams):
    p: int
    q: int
    r: int

    @model_validator(mode="before")
    def validate_fields(self, data: Any):
        p, q, r = data.get("p"), data.get("q"), data("r")
        assert p and q and r  # all fields must be provided
        assert p >= 1
        assert q >= 1
        assert r >= 1
        assert p + q + r <= 23
        return data

    @cached_property
    def pstart(self) -> int:
        return 9

    @cached_property
    def pstop(self) -> int:
        return 9 + self.p

    @cached_property
    def qstart(self) -> int:
        return self.pstop

    @cached_property
    def qstop(self) -> int:
        return self.qstart + self.q

    @cached_property
    def rstart(self) -> int:
        return self.qstop

    @cached_property
    def rstop(self) -> int:
        return self.rstart + self.r

    def start(self, block: Literal["p", "q", "r"]) -> int:
        MAPPING = {"p": "pstart", "q": "qstart", "r": "rstart"}
        return self.__getattribute__(MAPPING[block])

    def stop(self, block: Literal["p", "q", "r"]) -> int:
        MAPPING = {"p": "pstop", "q": "qstop", "r": "rstop"}
        return self.__getattribute__(MAPPING[block])

    def selection(self, selection: BlockSelection) -> dict:
        """'Returns selected params"""
        return {k: self.__getattribute__(k) for k, v in selection.__dict__.items() if v}


class BufferView(BaseModel):
    rows: int
    cols: int
    params: AdaptiveCipherParams

    @classmethod
    def from_shape(
        cls, shape: tuple[int, int], params: AdaptiveCipherParams
    ) -> BufferView:
        return cls(rows=shape[0], cols=shape[1], params=params)

    @cached_property
    def pbufflen(self) -> int:
        """p uint32 buffer length required"""
        return buffer_length(
            self.params.pstart, self.params.pstop, self.rows, self.cols
        )

    @cached_property
    def qbufflen(self) -> int:
        """q uint32 buffer length required"""
        return buffer_length(
            self.params.qstart, self.params.qstop, self.rows, self.cols
        )

    @cached_property
    def rbufflen(self) -> int:
        """r uint32 buffer length required"""
        return buffer_length(
            self.params.rstart, self.params.rstop, self.rows, self.cols
        )

    @property
    def p_buffer(self) -> np.ndarray:
        return np.zeros((self.pbufflen), dtype=np.uint32, order="C")

    @property
    def q_buffer(self) -> np.ndarray:
        return np.zeros((self.qbufflen), dtype=np.uint32, order="C")

    @property
    def r_buffer(self) -> np.ndarray:
        return np.zeros((self.rbufflen), dtype=np.uint32, order="C")

    def buffer(self, block: Literal["p", "q", "r"]) -> np.ndarray:
        MAPPING = {"p": "p_buffer", "q": "q_buffer", "r": "r_buffer"}
        return self.__getattribute__(MAPPING[block])

    def bufflen(self, block: Literal["p", "q", "r"]) -> np.ndarray:
        MAPPING = {"p": "pbufflen", "q": "qbufflen", "r": "rbufflen"}
        return self.__getattribute__(MAPPING[block])
