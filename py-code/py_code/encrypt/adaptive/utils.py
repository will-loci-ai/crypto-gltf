import numpy as np
from py_code.encrypt.adaptive.types import AdaptiveCipherParams, SBlocks


def combine_sblocks(sblocks_list: list[SBlocks]) -> SBlocks:
    """Combine sblock list into single sblock buffers"""
    s1, s2, s3 = bytearray(b""), bytearray(b""), bytearray(b"")
    for sblocks in sblocks_list:
        s1.extend(sblocks.s1)
        s2.extend(sblocks.s2)
        s3.extend(sblocks.s3)

    return SBlocks(s1=s1, s2=s2, s3=s3)


def get_s_blocks(arr: np.ndarray, params: AdaptiveCipherParams) -> SBlocks:
    """Get byte at position for every element in float32 arr"""

    if arr.dtype != np.float32:
        raise Exception(f"Invalid array dtype {arr.dtype}, must be float32")

    bytes_arr = np.ndarray.tobytes(arr)  # flat bytes array
    p_buffer, q_buffer, r_buffer = bytearray(b""), bytearray(b""), bytearray(b"")
    for i in range(arr.size):  # iterate through all array elements
        p_buffer.extend(bytes_arr[4 * i + params.p : 4 * i + params.p + 1])
        q_buffer.extend(bytes_arr[4 * i + params.q : 4 * i + params.q + 1])
        r_buffer.extend(bytes_arr[4 * i + params.r : 4 * i + params.r + 1])

    return SBlocks(s1=p_buffer, s2=q_buffer, s3=r_buffer)


def insert_s_blocks(
    arr: np.ndarray, params: AdaptiveCipherParams, s_blocks: SBlocks, offset: int
) -> np.ndarray:
    """Insert bytes at position in every element in float32 arr"""

    bytes_arr = np.ndarray.tobytes(arr)  # flat bytes array
    for i in range(arr.size):  # iterate through all array elements

        bytes_arr = (
            bytes_arr[: 4 * i + params.r]
            + s_blocks.s3[offset + i : offset + i + 1]
            + bytes_arr[4 * i + params.r + 1 : 4 * i + params.q]
            + s_blocks.s2[offset + i : offset + i + 1]
            + bytes_arr[4 * i + params.q + 1 : 4 * i + params.p]
            + s_blocks.s1[offset + i : offset + i + 1]
            + bytes_arr[4 * i + params.p + 1 :]
        )

    return np.frombuffer(bytes_arr, dtype=np.float32).reshape(
        arr.shape
    )  # frombuffer returns a flat array, need to reshape
