import secrets

import numpy as np
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import (
    AdaptiveCipherParamsV2,
    BlockSelection,
    Key,
)
from crypto_gltf.encrypt.deprecit.adaptive_v2.utils import combine_sblocks, get_sblocks
from crypto_gltf.io.plaintext.plnm import PlnM
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


def get_source_arrays(float_arrs: list[np.ndarray]) -> list[np.ndarray]:
    """Return first n matrices in float_arrs such that the sum of matrix sizes is greater than 32.
    (32*4 = 256 = AES keylength)"""

    source_arrays: list[np.ndarray] = []

    for arr in float_arrs:
        source_arrays.append(arr)
        size = sum([arr.size for arr in source_arrays])
        if size > 32:
            break

    if sum([arr.size for arr in source_arrays]) < 32:
        raise Exception("Mesh too small to generate keys")

    return source_arrays


def generate_keys(
    plnm: PlnM, params: AdaptiveCipherParamsV2, k3: bytes | None = None
) -> Key:
    """Calculates k1, k2 and k3 for a given plaintext asset"""

    float_arrs = [mesh for mesh in plnm.meshes if mesh.dtype.kind == "f"]
    source_arrays = get_source_arrays(float_arrs=float_arrs)

    sblocks_list = []
    for arr in source_arrays:
        sblocks_list.append(
            get_sblocks(
                arr=arr,
                params=params,
                to_get=BlockSelection.all(),
            )
        )
    combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

    s3 = combined_sblocks.s3[:32]
    s2 = combined_sblocks.s2[:32]

    if k3:
        assert len(k3) == 32
        logger.info("User specified key detected, using key provided.")
    else:
        k3 = secrets.token_bytes(32)

    k2 = aes_sha(sblock=s3, ki=k3)
    k1 = aes_sha(sblock=s2, ki=k2)

    return Key(k1=k1, k2=k2, k3=k3)


def get_k2(
    float_arrs: list[np.ndarray], params: AdaptiveCipherParamsV2, k3: bytes
) -> bytes:
    """Calculate k2 from k3 for a given plaintext"""

    source_arrays = get_source_arrays(float_arrs=float_arrs)

    sblocks_list = []
    for arr in source_arrays:
        sblocks_list.append(
            get_sblocks(arr=arr, params=params, to_get=BlockSelection(r=True))
        )

    combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

    s3 = combined_sblocks.s3[:32]
    k2 = aes_sha(sblock=s3, ki=k3)

    return k2


def get_k1(
    float_arrs: list[np.ndarray], params: AdaptiveCipherParamsV2, k2: bytes
) -> bytes:
    """Calculate k1 from k2 for a given plaintext"""

    source_arrays = get_source_arrays(float_arrs)

    sblocks_list = []
    for arr in source_arrays:
        sblocks_list.append(
            get_sblocks(arr=arr, params=params, to_get=BlockSelection(q=True))
        )

    combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

    s2 = combined_sblocks.s2[:32]
    k1 = aes_sha(sblock=s2, ki=k2)

    return k1
