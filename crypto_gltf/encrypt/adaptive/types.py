from __future__ import annotations

from base64 import urlsafe_b64encode as b64e
from functools import cached_property
from typing import Any, Literal

import numpy as np
from crypto_gltf.data.types import BaseKey, BaseParams
from crypto_gltf.encrypt.adaptive.utils import buffer_length
from pydantic import BaseModel, model_validator


class Key(BaseKey):

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any):
        k1, k2, k3 = data.get("k1"), data.get("k2"), data.get("k3")
        if not (k1 or k2 or k3):
            raise ValueError(f'At least one key value must be initialised.')
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


class AdaptiveCipherParams(BaseParams):
    p: int
    q: int
    r: int

    @cached_property
    def pstart(self) -> int:
        raise NotImplementedError()

    @cached_property
    def pstop(self) -> int:
        raise NotImplementedError()

    @cached_property
    def qstart(self) -> int:
        raise NotImplementedError()

    @cached_property
    def qstop(self) -> int:
        raise NotImplementedError()

    @cached_property
    def rstart(self) -> int:
        raise NotImplementedError()

    @cached_property
    def rstop(self) -> int:
        raise NotImplementedError()

    def start(self, block: Literal["p", "q", "r"]) -> int:
        MAPPING = {"p": "pstart", "q": "qstart", "r": "rstart"}
        return self.__getattribute__(MAPPING[block])

    def stop(self, block: Literal["p", "q", "r"]) -> int:
        MAPPING = {"p": "pstop", "q": "qstop", "r": "rstop"}
        return self.__getattribute__(MAPPING[block])

    def selection(self, selection: BlockSelection) -> dict:
        """'Returns selected params"""
        return {k: self.__getattribute__(k) for k, v in selection.__dict__.items() if v}


class ImagesAdaptiveCipherParams(AdaptiveCipherParams):

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any):
        p, q, r = data.get("p"), data.get("q"), data.get("r")
        if not (p and q and r ):  # all fields must be provided
            raise ValueError(f'All three cipher parameters must be specified.')
        if not (p >= 1 and q >= 1 and r >= 1):
            raise ValueError(f'All three cipher parameters must be >= 1.')
        if not (p+q+r==8):
            raise ValueError(f'For full scale image encryption, cipher parameters sum must equal 8.')
        return data

    @cached_property
    def pstart(self) -> int:
        return self.qstart - self.p

    @cached_property
    def pstop(self) -> int:
        return self.qstart

    @cached_property
    def qstart(self) -> int:
        return self.qstop - self.q

    @cached_property
    def qstop(self) -> int:
        return self.rstart

    @cached_property
    def rstart(self) -> int:
        return 8 - self.r

    @cached_property
    def rstop(self) -> int:
        return 8


class MeshesAdaptiveCipherParams(AdaptiveCipherParams):

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any):
        p, q, r = data.get("p"), data.get("q"), data.get("r")
        if not (p is not None and q is not None and r is not None ):  # all fields must be provided
            raise ValueError(f'All three cipher parameters must be specified.')
        if not (p >= 1 and q >= 1 and r >= 1):
            raise ValueError(f'All three cipher parameters must be >= 1.')
        if not (p+q+r<=23):
            raise ValueError(f'Sum of cipher parameters must be <=23.')
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


class BufferView(BaseModel):

    params: AdaptiveCipherParams
    rows: int
    cols: int
    slices: int = 1

    @classmethod
    def from_shape(
        cls, shape: tuple[int, int] | tuple[int, int, int], params: AdaptiveCipherParams
    ) -> BufferView:
        if len(shape) == 2:
            return cls(rows=shape[0], cols=shape[1], params=params)
        elif len(shape) == 3:
            return cls(rows=shape[0], cols=shape[1], slices=shape[2], params=params)

    @cached_property
    def pbufflen(self) -> int:
        """p uint32 buffer length required"""
        return buffer_length(
            self.params.pstart, self.params.pstop, self.rows, self.cols, self.slices
        )

    @cached_property
    def qbufflen(self) -> int:
        """q uint32 buffer length required"""
        return buffer_length(
            self.params.qstart, self.params.qstop, self.rows, self.cols, self.slices
        )

    @cached_property
    def rbufflen(self) -> int:
        """r uint32 buffer length required"""
        return buffer_length(
            self.params.rstart, self.params.rstop, self.rows, self.cols, self.slices
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
