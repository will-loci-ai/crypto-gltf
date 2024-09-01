from __future__ import annotations

import secrets
from time import time

import numpy as np
from loguru import logger
from py_code.data.types import EncryptionResponse
from py_code.encrypt.deprecit.adaptive_v1.decrypt import AdaptiveDecryptionModel
from py_code.encrypt.deprecit.adaptive_v1.encrypt import AdaptiveEncryptionModel
from py_code.encrypt.deprecit.adaptive_v1.types import AdaptiveCipherParamsV1, Key
from py_code.io.plaintext.plnm import PlnM


class AdaptiveCryptoSystemV1(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParamsV1,
        images_cipher_params: AdaptiveCipherParamsV1,
        key: Key,
    ) -> EncryptionResponse[PlnM, np.ndarray, Key]:

        tic = time()
        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [idx for idx, mesh in enumerate(plnm.meshes) if mesh.dtype.kind == "f"]
        )
        float_arrs = [
            plnm.meshes[i].astype(np.float32) for i in meshes_float_arrs_idxs
        ]  # convert to float32

        if key is None or key.k1 is None:
            key = Key(k1=secrets.token_bytes(32))

        encryption_response = AdaptiveEncryptionModel._encrypt(
            data=float_arrs, key=key, position=meshes_cipher_params.position
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = encryption_response.ciphertext[idx]

        logger.debug(f"Adaptive encryption took {time()-tic} seconds.")

        return EncryptionResponse[PlnM, np.ndarray, Key](
            ciphertext=plnm, aad=encryption_response.aad, key=key
        )

    @staticmethod
    def decrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParamsV1,
        images_cipher_params: AdaptiveCipherParamsV1,
        key: Key,
        aad: bytes,
    ) -> PlnM:
        tic = time()
        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [idx for idx, mesh in enumerate(plnm.meshes) if mesh.dtype.kind == "f"]
        )

        float_arrs = [plnm.meshes[i] for i in meshes_float_arrs_idxs]
        decrypted_data = AdaptiveDecryptionModel._decrypt(
            data=float_arrs,
            key=key,
            position=meshes_cipher_params.position,
            aad=aad,
        )
        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        logger.debug(f"Adaptive decryption took {time()-tic} seconds.")

        return plnm
