from __future__ import annotations

import secrets
from time import time

import numpy as np
from crypto_gltf.data.types import AAD_DATA, EncryptionResponse
from crypto_gltf.encrypt.deprecit.adaptive_v1.decrypt import AdaptiveDecryptionModel
from crypto_gltf.encrypt.deprecit.adaptive_v1.encrypt import AdaptiveEncryptionModel
from crypto_gltf.encrypt.deprecit.adaptive_v1.types import AdaptiveCipherParamsV1, Key
from crypto_gltf.io.plaintext.plnm import PlnM
from loguru import logger


class AdaptiveCryptoSystemV1(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: AdaptiveCipherParamsV1,
        images_cipher_params: AdaptiveCipherParamsV1,
        key: Key | None = None,
        encrypt_images: bool = False,
    ) -> EncryptionResponse[PlnM, AAD_DATA, Key]:

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
            data=float_arrs, key=key, position=meshes_cipher_params.p
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = encryption_response.ciphertext[idx]

        logger.debug(f"Adaptive encryption took {time()-tic} seconds.")
        aad = AAD_DATA(
            aad=encryption_response.aad,
            encrypt_images=encrypt_images,
            meshes_params=meshes_cipher_params.__dict__,
            images_params=images_cipher_params.__dict__,
        )

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
        # Get non-integer type arrays
        # i.e. vertices and colors
        meshes_float_arrs_idxs = np.array(
            [idx for idx, mesh in enumerate(plnm.meshes) if mesh.dtype.kind == "f"]
        )

        float_arrs = [plnm.meshes[i] for i in meshes_float_arrs_idxs]
        decrypted_data = AdaptiveDecryptionModel._decrypt(
            data=float_arrs,
            key=key,
            position=AdaptiveCipherParamsV1(**aad.meshes_params).p,
            aad=aad.aad,
        )
        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx]

        logger.debug(f"Adaptive decryption took {time()-tic} seconds.")

        return plnm
