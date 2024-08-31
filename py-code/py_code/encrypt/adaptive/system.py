from __future__ import annotations

from time import time

import numpy as np
from loguru import logger
from py_code.data.types import EncryptionResponse
from py_code.encrypt.adaptive.cryptography.key_gen import generate_keys, get_subkey
from py_code.encrypt.adaptive.decrypt import AdaptiveDecryptionModel
from py_code.encrypt.adaptive.encrypt import AdaptiveEncryptionModel
from py_code.encrypt.adaptive.types import AdaptiveCipherParams, BlockSelection, Key
from py_code.io.plaintext.plnm import PlnM


class AdaptiveCryptoSystemV3(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParams,
        images_cipher_params: AdaptiveCipherParams,
        key: Key | None = None,
    ) -> EncryptionResponse[PlnM, np.ndarray, Key]:

        tic = time()

        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [
                idx
                for idx, mesh in enumerate(plnm.meshes)
                if mesh.dtype.kind == "f" and mesh.size > 0
            ]
        )
        float_arrs = [
            plnm.meshes[i].astype(np.float32) for i in meshes_float_arrs_idxs
        ]  # convert to float32

        if not key:
            key = generate_keys(float_arrs, meshes_cipher_params)

        encryption_response = AdaptiveEncryptionModel._encrypt(
            data=float_arrs, key=key, params=meshes_cipher_params
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = encryption_response.ciphertext[idx]

        logger.debug(f"Adaptive encryption took {time()-tic} seconds.")
        logger.success(f"Mesh encrypted")

        return EncryptionResponse[PlnM, np.ndarray, Key](
            ciphertext=plnm,
            aad=encryption_response.aad,
            key=key,
        )

    @staticmethod
    def decrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParams,
        images_cipher_params: AdaptiveCipherParams,
        key: Key,
        aad: np.ndarray,
    ) -> PlnM:
        tic = time()

        if key.size == 0:
            raise Exception(f"Please provide a key")

        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [
                idx
                for idx, mesh in enumerate(plnm.meshes)
                if mesh.dtype.kind == "f" and mesh.size > 0
            ]
        )

        float_arrs = [plnm.meshes[i] for i in meshes_float_arrs_idxs]

        if key.k3:
            float_arrs = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad=aad,
                selection=BlockSelection(r=True),
            )

            key.k2 = get_subkey(
                float_arrs=float_arrs,
                params=meshes_cipher_params,
                ki=key.k3,
                selection=BlockSelection(r=True),
            )

        if key.k2:
            float_arrs = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad=aad,
                selection=BlockSelection(q=True),
            )

            key.k1 = get_subkey(
                float_arrs=float_arrs,
                params=meshes_cipher_params,
                ki=key.k2,
                selection=BlockSelection(q=True),
            )

        assert key.k1 is not None

        decrypted_data = AdaptiveDecryptionModel._decrypt(
            data=float_arrs,
            key=key,
            params=meshes_cipher_params,
            aad=aad,
            selection=BlockSelection(p=True),
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        assert key.filled
        logger.debug(f"Adaptive decryption took {time()-tic} seconds.")
        logger.success(f"Mesh decrypted")

        return plnm
