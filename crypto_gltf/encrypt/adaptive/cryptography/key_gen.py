import secrets

import numpy as np
from crypto_gltf.encrypt.adaptive.types import (
    AdaptiveCipherParams,
    BlockSelection,
    BufferView,
    Key,
)
from crypto_gltf.encrypt.adaptive.utils import get_bits
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from loguru import logger


def aes_sha(sblock: bytes, ki: bytes) -> bytes:
    """Generate subsequent subkey k_(i-1) using AES followed by sha"""

    assert len(sblock) == 32

    cipher = Cipher(algorithms.AES(ki), modes.ECB(), default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(sblock) + encryptor.finalize()

    digest = hashes.Hash(hashes.SHA256())
    digest.update(sblock)
    digest.update(ciphertext)

    return digest.finalize()


def get_source_arrays(plnm_arrs: list[np.ndarray], min_size: int) -> list[np.ndarray]:
    """Return first n matrices in plnm_arrs such that the sum of matrix sizes is greater than min_size.
    256 = AES keylength"""

    source_arrays: list[np.ndarray] = []

    for arr in plnm_arrs:
        source_arrays.append(arr)
        size = sum([arr.size for arr in source_arrays])
        if size > min_size:
            break

    if sum([arr.size for arr in source_arrays]) < min_size:
        raise Exception("Mesh too small to generate keys")

    return source_arrays


def get_min_size_plaintext(
    params: AdaptiveCipherParams, selection: BlockSelection
) -> int:
    """Returns minimum number of plaintext float32 values required to generate 256 bit subkeys"""
    smallest_selected_param = min(params.selection(selection).values())
    return 256 // smallest_selected_param + 1


def generate_keys(
    plnm_arrs: list[np.ndarray], params: AdaptiveCipherParams, k3: bytes | None = None
) -> Key:
    """Calculates k1, k2 and k3 for a given plaintext asset"""

    min_size = get_min_size_plaintext(
        params=params, selection=BlockSelection(q=True, r=True)
    )
    source_arrays = get_source_arrays(
        plnm_arrs=plnm_arrs,
        min_size=min_size,
    )

    s2, s3 = bytearray(b""), bytearray(b"")

    for arr in source_arrays:

        buffer_view = BufferView.from_shape(shape=arr.shape, params=params)

        q_buffer, r_buffer = (
            buffer_view.q_buffer,
            buffer_view.r_buffer,
        )
        get_bits(arr, q_buffer, params.qstart, params.qstop)
        get_bits(arr, r_buffer, params.rstart, params.rstop)

        s2.extend(q_buffer.tobytes())
        s3.extend(r_buffer.tobytes())

    s3 = s3[:32]
    s2 = s2[:32]

    if k3:
        assert len(k3) == 32
        logger.info("User specified key detected, using key provided.")
    else:
        k3 = secrets.token_bytes(32)

    k2 = aes_sha(sblock=s3, ki=k3)
    k1 = aes_sha(sblock=s2, ki=k2)

    return Key(k1=k1, k2=k2, k3=k3)


def get_subkey(
    plnm_arrs: list[np.ndarray],
    params: AdaptiveCipherParams,
    ki: bytes,
    selection: BlockSelection,
) -> bytes:
    """Calculate ki-1 from ki for a given plaintext"""

    min_size = get_min_size_plaintext(params, selection)
    source_arrays = get_source_arrays(plnm_arrs=plnm_arrs, min_size=min_size)

    block = selection.single_block
    start = params.start(block)
    stop = params.stop(block)

    si = bytearray(b"")
    for arr in source_arrays:
        buffer_view = BufferView.from_shape(arr.shape, params=params)
        buffer = buffer_view.buffer(block)
        get_bits(arr, buffer, start, stop)
        si.extend(buffer.tobytes())

    ki_minus_1 = aes_sha(sblock=si[:32], ki=ki)

    return ki_minus_1
