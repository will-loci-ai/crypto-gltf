import numpy as np
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import (
    AdaptiveCipherParamsV2,
    BlockSelection,
    SBlocks,
)


def combine_sblocks(sblocks_list: list[SBlocks]) -> SBlocks:
    """Combine sblock list into single sblock buffers"""
    s1, s2, s3 = bytearray(b""), bytearray(b""), bytearray(b"")
    for sblocks in sblocks_list:
        s1.extend(sblocks.s1)
        s2.extend(sblocks.s2)
        s3.extend(sblocks.s3)

    return SBlocks(s1=s1, s2=s2, s3=s3)


def get_sblocks(
    arr: np.ndarray,
    params: AdaptiveCipherParamsV2,
    to_get: BlockSelection,
) -> SBlocks:
    """Get byte at position for every element in float32 arr"""

    if arr.dtype != np.float32:
        raise Exception(f"Invalid array dtype {arr.dtype}, must be float32")

    bytes_arr = np.ndarray.tobytes(arr)  # flat bytes array
    p_buffer, q_buffer, r_buffer = bytearray(b""), bytearray(b""), bytearray(b"")
    for i in range(arr.size):  # iterate through all array elements
        if to_get.p:
            p_buffer.extend(bytes_arr[4 * i + params.p : 4 * i + params.p + 1])

        if to_get.q:
            q_buffer.extend(bytes_arr[4 * i + params.q : 4 * i + params.q + 1])

        if to_get.r:
            r_buffer.extend(bytes_arr[4 * i + params.r : 4 * i + params.r + 1])

    return SBlocks(s1=p_buffer, s2=q_buffer, s3=r_buffer)


def put_sblocks(
    arr: np.ndarray,
    params: AdaptiveCipherParamsV2,
    sblocks: SBlocks,
    offset: int,
    to_put: BlockSelection,
) -> np.ndarray:
    """Insert bytes at position in every element in float32 arr"""

    if arr.dtype != np.float32:
        raise Exception(f"Invalid array dtype {arr.dtype}, must be float32")

    bytes_arr = np.ndarray.tobytes(arr)  # flat bytes array
    for i in range(arr.size):  # iterate through all array elements
        if to_put.p:
            bytes_arr = (
                bytes_arr[: 4 * i + params.p]
                + sblocks.s1[offset + i : offset + i + 1]
                + bytes_arr[4 * i + params.p + 1 :]
            )
        if to_put.q:
            bytes_arr = (
                bytes_arr[: 4 * i + params.q]
                + sblocks.s2[offset + i : offset + i + 1]
                + bytes_arr[4 * i + params.q + 1 :]
            )
        if to_put.r:
            bytes_arr = (
                bytes_arr[: 4 * i + params.r]
                + sblocks.s3[offset + i : offset + i + 1]
                + bytes_arr[4 * i + params.r + 1 :]
            )

    return np.frombuffer(bytes_arr, dtype=np.float32).reshape(
        arr.shape
    )  # frombuffer returns a flat array, need to reshape
