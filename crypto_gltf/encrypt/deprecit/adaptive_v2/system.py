from __future__ import annotations

from time import time

import numpy as np
from crypto_gltf.data.types import AAD_DATA, EncryptionResponse
from crypto_gltf.encrypt.deprecit.adaptive_v2.decrypt import AdaptiveDecryptionModel
from crypto_gltf.encrypt.deprecit.adaptive_v2.encrypt import AdaptiveEncryptionModel
from crypto_gltf.encrypt.deprecit.adaptive_v2.key_gen import (
    generate_keys,
    get_k1,
    get_k2,
)
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import (
    AdaptiveCipherParamsV2,
    BlockSelection,
    Key,
)
from crypto_gltf.io.plaintext.plnm import PlnM
from loguru import logger


class AdaptiveCryptoSystemV2(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParamsV2,
        images_cipher_params: AdaptiveCipherParamsV2,
        encrypt_images: bool = False,
        key: Key | None = None,
    ) -> EncryptionResponse[PlnM, AAD_DATA, Key]:

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

        aad = AAD_DATA(
            aad=encryption_response.aad,
            encrypt_images=encrypt_images,
            meshes_params=meshes_cipher_params.__dict__,
            images_params=images_cipher_params.__dict__,
        )

        logger.debug(f"Adaptive encryption took {time()-tic} seconds.")
        return EncryptionResponse[PlnM, AAD_DATA, Key](
            ciphertext=plnm, aad=aad, key=key
        )

    @staticmethod
    def decrypt(
        plnm: PlnM,
        key: Key,
        aad: AAD_DATA,
    ) -> PlnM:
        tic = time()
        meshes_cipher_params = AdaptiveCipherParamsV2(**aad.meshes_params)

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
                aad=aad.aad,
                selection=BlockSelection(r=True),
            )

            toc = time()
            key.k2 = get_k2(
                float_arrs=float_arrs, params=meshes_cipher_params, k3=key.k3
            )

        if key.k2:
            float_arrs = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad=aad.aad,
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
            aad=aad.aad,
            selection=BlockSelection(p=True),
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        assert key.filled

        logger.debug(f"Adaptive decryption took {time()-tic} seconds.")

        return plnm
