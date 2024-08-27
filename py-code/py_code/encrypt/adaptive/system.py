from __future__ import annotations

from time import time

import numpy as np
from loguru import logger
from py_code.data.types import EncryptionResponse
from py_code.encrypt.adaptive.decrypt import AdaptiveDecryptionModel
from py_code.encrypt.adaptive.encrypt import AdaptiveEncryptionModel
from py_code.encrypt.adaptive.key_gen import get_k1, get_k2
from py_code.encrypt.adaptive.types import AdaptiveCipherParams, BlockSelection, Key
from py_code.io.plaintext.plnm import PlnM


class AdaptiveCipherSystem(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParams,
        images_cipher_params: AdaptiveCipherParams,
        key: Key,
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
            data=float_arrs, key=key, params=meshes_cipher_params
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
        key: Key,
    ) -> PlnM:
        tic = time()

        if key.size == 0:
            raise Exception(f"Please provide a key")
        if key.size > 1:
            raise Exception(f"Multiple keys provided")

        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [idx for idx, mesh in enumerate(plnm.meshes) if mesh.dtype.kind == "f"]
        )

        float_arrs = [plnm.meshes[i] for i in meshes_float_arrs_idxs]

        if key.k3:
            float_arrs = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad_b64=aad_b64,
                selection=BlockSelection(r=True),
            )
            # for idx, i in enumerate(meshes_float_arrs_idxs):
            #     plnm.meshes[i] = decrypted_data[idx]

            key.k2 = get_k2(
                float_arrs=float_arrs, params=meshes_cipher_params, k3=key.k3
            )

        if key.k2:
            float_arrs = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad_b64=aad_b64,
                selection=BlockSelection(q=True),
            )

            key.k1 = get_k1(
                float_arrs=float_arrs, params=meshes_cipher_params, k2=key.k2
            )

        assert key.k1 is not None

        decrypted_data = AdaptiveDecryptionModel._decrypt(
            data=float_arrs,
            key=key,
            params=meshes_cipher_params,
            aad_b64=aad_b64,
            selection=BlockSelection(p=True),
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        assert key.filled
        logger.info(f"Adaptive decryption took {time()-tic} seconds.")

        return plnm
