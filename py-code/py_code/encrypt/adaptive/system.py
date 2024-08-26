from __future__ import annotations

from time import time

import numpy as np
from loguru import logger
from py_code.data.types import EncryptionResponse
from py_code.encrypt.adaptive.base import AdaptiveCipherParams
from py_code.encrypt.adaptive.decrypt import AdaptiveDecryptionModel
from py_code.encrypt.adaptive.encrypt import AdaptiveEncryptionModel
from py_code.io.plaintext.plnm import PlnM


class AdaptiveCipherSystem(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParams,
        images_cipher_params: AdaptiveCipherParams,
        key: bytes,
    ) -> EncryptionResponse[PlnM]:

        tic = time()
        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [idx for idx, mesh in enumerate(plnm.meshes) if mesh.dtype.kind == "f"]
        )
        float_arrs = [
            plnm.meshes[i].astype(np.float32) for i in meshes_float_arrs_idxs
        ]  # convert to float32
        encryption_response = AdaptiveEncryptionModel._encrypt(
            data=float_arrs, key=key, position=meshes_cipher_params.position
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = encryption_response.ciphertext[idx]

        logger.info(f"Adaptive encryption took {time()-tic} seconds.")

        return EncryptionResponse[PlnM](ciphertext=plnm, aad=encryption_response.aad)

    @staticmethod
    def decrypt(
        plnm: PlnM,
        aad_b64: bytes,
        meshes_cipher_params: AdaptiveCipherParams,
        images_cipher_params: AdaptiveCipherParams,
        key: bytes,
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
            aad_b64=aad_b64,
        )
        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        logger.info(f"Adaptive decryption took {time()-tic} seconds.")

        return plnm
