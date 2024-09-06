from typing import Literal

import numpy as np
from crypto_gltf.utils.bit_utils import bit_slice

stack_dict = {"HEIGHT": 0, "WIDTH": 1, "DEPTH": 2}


def split_array_stack(
    stacked_data: np.ndarray,
    stacktype: Literal["HEIGHT", "WIDTH", "DEPTH"],
) -> list[np.ndarray]:
    """split numpy array stack by height, width or depth"""

    dim = stacked_data.shape[stack_dict[stacktype]]

    splits = np.split(
        ary=stacked_data,
        indices_or_sections=dim,
        axis=stack_dict[stacktype],
    )
    return [arr.reshape(arr.shape[0], arr.shape[1]) for arr in splits]


def array_bit_slice(arr: np.ndarray, start: int, stop: int) -> np.ndarray:
    """Returns array of bit slices for each element of arr"""
    assert len(arr.shape) == 1  # make sure array is 1D
    return np.array([bit_slice(int(val), start, stop) for val in arr])


def array_bit_slice_eq(
    arr1: np.ndarray, arr2: np.ndarray, start: int, stop: int
) -> bool:
    """Returns equality of bit slices of every element in arr1 nad arr2"""
    arr1_slice = array_bit_slice(arr1.flatten(), start, stop)
    arr2_slice = array_bit_slice(arr2.flatten(), start, stop)
    return np.array_equal(arr1_slice, arr2_slice)
