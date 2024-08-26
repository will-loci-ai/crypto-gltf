from typing import Literal

import numpy as np


def get_bytes(arr: np.ndarray, position: Literal[0, 1, 2, 3]) -> bytes:
    """Get byte at position for every element in float32 arr"""

    if arr.dtype != np.float32:
        raise Exception(f"Invalid array dtype {arr.dtype}, must be float32")

    bytes_arr = np.ndarray.tobytes(arr)
    buffer = bytearray(b"")
    for i in range(arr.size):
        buffer.extend(bytes_arr[4 * i + position : 4 * i + position + 1])

    return buffer


def insert_bytes(
    arr: np.ndarray, position: Literal[0, 1, 2, 3], buffer: bytes
) -> np.ndarray:
    """Insert bytes at position in every element in float32 arr"""

    bytes_arr = np.ndarray.tobytes(arr)
    for i in range(arr.size):
        bytes_arr = (
            bytes_arr[: 4 * i + position]
            + buffer[i : i + 1]
            + bytes_arr[4 * i + position + 1 :]
        )
    return np.frombuffer(bytes_arr, dtype=np.float32)
