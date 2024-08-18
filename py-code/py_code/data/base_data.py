from __future__ import annotations

from typing import Literal, Optional

import numpy as np
from loguru import logger
from PIL import Image
from py_code.data.types import CombinedPlnMDataTypes, PlnMDataType
from pydantic import BaseModel, ConfigDict

stack_dict = {"HEIGHT": 0, "WIDTH": 1, "DEPTH": 2}


class PlnM(BaseModel):
    """Data class for multi matrix 3D asset attributes (colors, meshes etc.)"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    dim: int
    data: list[np.ndarray]  # array of data matrices of length datatype.composition
    dtype: np.dtype
    stacktype: Literal["HEIGHT", "WIDTH", "DEPTH"]
    empty: bool = False
    datatype: Optional[PlnMDataType]

    @classmethod
    def from_np_stack(
        cls,
        stacked_data: np.ndarray,
        stacktype: Literal["HEIGHT", "WIDTH", "DEPTH"],
        datatype: PlnMDataType | None = None,
    ) -> PlnM:
        """Load data class from stacked np.ndarray"""

        if stacktype not in stack_dict.keys():
            raise Exception("Invalid stack type")

        dim = stacked_data.shape[stack_dict[stacktype]]
        if datatype and datatype.composition != dim:
            logger.error("Incorrect datatype chosen, setting to none.")
            datatype = None

        splits = np.split(
            ary=stacked_data,
            indices_or_sections=dim,
            axis=stack_dict[stacktype],
        )
        data = [arr.reshape(arr.shape[0], arr.shape[1]) for arr in splits]
        return cls(
            dim=dim,
            data=data,
            dtype=stacked_data.dtype,
            stacktype=stacktype,
            datatype=datatype,
        )

    @classmethod
    def from_list(
        cls, data_list: list[np.ndarray], datatype: PlnMDataType | None = None
    ) -> PlnM:
        """Load data class from list[np.ndarray] format"""
        if datatype and len(data_list) != datatype.composition:
            logger.error("Incorrect datatype chosen, setting to none.")
            datatype = None

        return cls(
            dim=len(data_list),
            data=data_list,
            dtype=data_list[0].dtype,
            stacktype="HEIGHT",
            datatype=datatype,
        )

    @classmethod
    def from_empty(cls, datatype: PlnMDataType) -> PlnM:
        """Load empty data class"""
        return cls(
            dim=datatype.composition,
            data=[],
            dtype=np.dtype(np.int32),
            stacktype="HEIGHT",
            empty=True,
            datatype=datatype,
        )
    
    @property
    def data_list(self):
        """Return data class as list of numpy arrays"""
        return self.data
    

    @property
    def np_reconstruction(self):
        """Return data class as reconstructed numpy array.
        Returns orignal stack formatting load array"""
        return np.array(
            np.stack(
                arrays=[arr for arr in self.data], axis=stack_dict[self.stacktype]
            ),
            dtype=self.dtype,
        )
    


    @property
    def image(self):
        """Render image data classes"""
        match self.datatype:
            case CombinedPlnMDataTypes.MESH:
                raise Exception("Mesh type has no image property")
            case CombinedPlnMDataTypes.RGB:
                return Image.fromarray(self.np_reconstruction, "RGB")
            case CombinedPlnMDataTypes.RGBA:
                return Image.fromarray(self.np_reconstruction, "RGBA")
            case CombinedPlnMDataTypes.GREYSCALE:
                return Image.fromarray(self.np_reconstruction, "L")
            case _:
                raise Exception("Invalid PlnM type")
