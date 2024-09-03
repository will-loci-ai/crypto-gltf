from __future__ import annotations

from time import time

import numpy as np
from loguru import logger
from gltf_crypto_conan1014.data.types import EncryptionResponse
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v2.decrypt import AdaptiveDecryptionModel
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v2.encrypt import AdaptiveEncryptionModel
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v2.key_gen import generate_keys, get_k1, get_k2
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v2.types import (
    AdaptiveCipherParamsV2,
    BlockSelection,
    Key,
)
from gltf_crypto_conan1014.io.plaintext.plnm import PlnM


class AdaptiveCryptoSystemV2(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParamsV2,
        images_cipher_params: AdaptiveCipherParamsV2,
        key: Key | None = None,
    ) -> EncryptionResponse[PlnM, np.ndarray, Key]:

        tic = time()
        if not key:
            key = generate_keys(plnm, meshes_cipher_params)
        else:
            assert key.size == 1 and key.k3 is not None
            key = generate_keys(plnm, meshes_cipher_params, k3=key.k3)

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

        encryption_response = AdaptiveEncryptionModel._encrypt(
            data=float_arrs, key=key, params=meshes_cipher_params
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
        meshes_cipher_params: AdaptiveCipherParamsV2,
        images_cipher_params: AdaptiveCipherParamsV2,
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

            key.k2 = get_k2(
                float_arrs=float_arrs, params=meshes_cipher_params, k3=key.k3
            )

        if key.k2:
            float_arrs = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad=aad,
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
            aad=aad,
            selection=BlockSelection(p=True),
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        assert key.filled
        logger.debug(f"Adaptive decryption took {time()-tic} seconds.")

        return plnm
