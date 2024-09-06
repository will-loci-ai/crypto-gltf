from ctypes import CDLL, c_size_t, c_uint32
from pathlib import Path

import numpy as np


def buffer_length(start: int, stop: int, rows: int, cols: int, slices: int = 1) -> int:
    """Returns length of uint32 buffer required for 2d or 3d mat"""
    slice_length = stop - start
    num_bits = slice_length * rows * cols * slices
    return (num_bits - 1) // 32 + 1


CLIB_FILEPATH = str(Path(__file__).parent.parent.parent.resolve() / "clib/clib.so")

try:
    clib = CDLL(CLIB_FILEPATH)
except:
    raise Exception(f"Error: clib.so library has not been built.")

NP_FLOAT32_ARR_2D = np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags="C")
NP_UINT32_ARR_1D = np.ctypeslib.ndpointer(dtype=np.uint32, ndim=1, flags="C")
NP_INT8_ARR_3D = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=3, flags="C")
NP_INT8_ARR_2D = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=2, flags="C")


clib.get_bits32.argtypes = [
    NP_FLOAT32_ARR_2D,
    NP_UINT32_ARR_1D,
    c_size_t,
    c_size_t,
    c_size_t,
    c_size_t,
    c_uint32,
]

clib.put_bits32.argtypes = [
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
    start: int,
    stop: int,
    fill: int = 0,  # buffer padding value
) -> None:
    """get_bits clib wrapper"""
    assert len(buffer.shape) == 1

    match arr.dtype.itemsize:
        case 4:
            """clib get_bits32 function wrapper"""
            if len(arr.shape) != 2:
                raise Exception(f"get_bits32 not supported for shape {arr.shape}")
            rows, cols = arr.shape[0], arr.shape[1]
            if arr.dtype.itemsize != 4:
                raise Exception(
                    f"dtype {arr.dtype} not supported for 2D get_bits, type must be 32 bits long"
                )
            try:
                clib.get_bits32(
                    arr, buffer, rows, cols, start, stop, fill
                )  # call clib function
            except Exception as e:
                raise RuntimeError("Error running clib.get_bits.") from e
        case 1:
            """clib get_bits8 function wrapper"""
            match len(arr.shape):
                case 3:
                    rows, cols, slices = arr.shape[0], arr.shape[1], arr.shape[2]
                    clib.get_bits8.argtypes = [
                        NP_INT8_ARR_3D,
                        NP_UINT32_ARR_1D,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_uint32,
                    ]
                case 2:
                    rows, cols, slices = arr.shape[0], arr.shape[1], 1
                    clib.get_bits8.argtypes = [
                        NP_INT8_ARR_2D,
                        NP_UINT32_ARR_1D,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_uint32,
                    ]
                case _:
                    raise Exception(f"get_bits8 not supported for shape {arr.shape}")
            try:
                clib.get_bits8(
                    arr, buffer, rows, cols, slices, start, stop, fill
                )  # call clib function
            except Exception as e:
                raise RuntimeError("Error running clib.get_bits.") from e
        case _:
            raise Exception(
                f"get_bits not supported for dtype {arr.dtype.itemsize}, bit length must be 8 or 32."
            )


def put_bits(
    putarr: np.ndarray,
    buffer: np.ndarray,
    start: int,
    stop: int,
) -> None:
    """put_bits clib wrapper"""
    assert len(buffer.shape) == 1

    match putarr.dtype.itemsize:
        case 4:
            """clib put_bits32 function wrapper"""
            if len(putarr.shape) != 2:
                raise Exception(f"put_bits32 not supported for shape {putarr.shape}")
            rows, cols = putarr.shape[0], putarr.shape[1]
            if putarr.dtype.itemsize != 4:
                raise Exception(
                    f"dtype {putarr.dtype} not supported for 2D put_bits, type must be 32 bits long"
                )
            try:
                clib.put_bits32(
                    putarr, buffer, rows, cols, start, stop
                )  # call clib function
            except Exception as e:
                raise RuntimeError("Error running clib.put_bits.") from e
        case 1:
            """clib put_bits8 function wrapper"""
            match len(putarr.shape):
                case 3:
                    rows, cols, slices = (
                        putarr.shape[0],
                        putarr.shape[1],
                        putarr.shape[2],
                    )
                    clib.put_bits8.argtypes = [
                        NP_INT8_ARR_3D,
                        NP_UINT32_ARR_1D,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                    ]
                case 2:
                    rows, cols, slices = putarr.shape[0], putarr.shape[1], 1
                    clib.put_bits8.argtypes = [
                        NP_INT8_ARR_2D,
                        NP_UINT32_ARR_1D,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                        c_size_t,
                    ]
                case _:
                    raise Exception(f"put_bits8 not supported for shape {putarr.shape}")
            try:
                clib.put_bits8(
                    putarr, buffer, rows, cols, slices, start, stop
                )  # call clib function
            except Exception as e:
                raise RuntimeError("Error running clib.put_bits.") from e
        case _:
            raise Exception(
                f"put_bits not supported for dtype {putarr.dtype.itemsize}, bit length must be 8 or 32."
            )
