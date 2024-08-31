from ctypes import CDLL, c_size_t, c_uint32
from pathlib import Path

import numpy as np


def buffer_length(start: int, stop: int, rows: int, cols: int) -> int:
    """Returns length of uint32 buffer required"""
    slice_length = stop - start
    num_bits = slice_length * rows * cols
    return (num_bits - 1) // 32 + 1


CLIB_FILEPATH = str(Path(__file__).parent.parent.parent.resolve() / "clib/clib.so")

try:
    clib = CDLL(CLIB_FILEPATH)
except:
    raise Exception(f"Error: clib.so library has not been built.")

NP_FLOAT32_ARR_2D = np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags="C")
NP_UINT32_ARR_1D = np.ctypeslib.ndpointer(dtype=np.uint32, ndim=1, flags="C")

clib.get_bits.argtypes = [
    NP_FLOAT32_ARR_2D,
    NP_UINT32_ARR_1D,
    c_size_t,
    c_size_t,
    c_size_t,
    c_size_t,
    c_uint32,
]

clib.put_bits.argtypes = [
    NP_FLOAT32_ARR_2D,
    NP_UINT32_ARR_1D,
    c_size_t,
    c_size_t,
    c_size_t,
    c_size_t,
]


def get_bits(
    arr: np.ndarray,
    buffer: np.ndarray,
    shape: tuple[int, int],
    start: int,
    stop: int,
    fill: int = 0,  # buffer padding value
) -> None:
    """clib get_bits function wrapper"""
    rows, cols = shape[0], shape[1]
    assert len(arr.shape) == 2
    assert len(buffer.shape) == 1

    try:
        clib.get_bits(arr, buffer, rows, cols, start, stop, fill)  # call clib function
    except Exception as e:
        raise RuntimeError("Error running clib.get_bits.") from e


def put_bits(
    putarr: np.ndarray,
    buffer: np.ndarray,
    shape: tuple[int, int],
    start: int,
    stop: int,
) -> None:
    """clib put_bits function wrapper"""
    rows, cols = shape[0], shape[1]
    assert len(putarr.shape) == 2
    assert len(buffer.shape) == 1
    try:
        clib.put_bits(putarr, buffer, rows, cols, start, stop)  # call clib function
    except Exception as e:
        raise RuntimeError("Error running clib.put_bits.") from e
