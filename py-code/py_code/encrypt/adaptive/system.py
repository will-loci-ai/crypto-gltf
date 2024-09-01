from __future__ import annotations

from time import time
from typing import Literal

import numpy as np
from loguru import logger
from py_code.data.types import AAD_DICT, EncryptionResponse
from py_code.encrypt.adaptive.cryptography.key_gen import generate_keys, get_subkey
from py_code.encrypt.adaptive.decrypt import AdaptiveDecryptionModel
from py_code.encrypt.adaptive.encrypt import AdaptiveEncryptionModel
from py_code.encrypt.adaptive.types import (
    BlockSelection,
    ImagesAdaptiveCipherParams,
    Key,
    MeshesAdaptiveCipherParams,
)
from py_code.io.plaintext.plnm import PlnM


class AdaptiveCryptoSystemV3(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: MeshesAdaptiveCipherParams,
        images_cipher_params: ImagesAdaptiveCipherParams | None = None,
        key: Key | None = None,
    ) -> EncryptionResponse[PlnM, AAD_DICT, Key]:

        tic = time()

        # Get non-integer type mesh arrays
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

        encrypt_meshes = len(float_arrs) > 0
        encrypt_images = len(plnm.images) > 0
        if not (encrypt_images or encrypt_meshes):
            raise Exception(f"No asset data to encrypt.")

        if not key:
            if encrypt_meshes:
                key = generate_keys(float_arrs, meshes_cipher_params)
            else:
                key = generate_keys(plnm.images, images_cipher_params)
        else:
            # a key has been provided
            assert key.k3 is not None
            if encrypt_meshes:
                generated_keys = generate_keys(float_arrs, meshes_cipher_params, key.k3)
            else:
                generated_keys = generate_keys(
                    plnm.images, meshes_cipher_params, key.k3
                )

            if not (
                key.k1 == generated_keys.k1
                and key.k2 == generated_keys.k2
                and key.k3 == generated_keys.k3
            ):
                logger.info("Invalid keys provided, regenerating keys")
                key = generated_keys

        aad = {}
        # data = [[float_arr, meshes_cipher_params] for float_arr in float_arrs]
        # if images_cipher_params is not None:
        #     data += [[img, images_cipher_params] for img in plnm.image]

        if encrypt_meshes:
            meshes_encryption_response = AdaptiveEncryptionModel._encrypt(
                data=float_arrs + plnm.images, key=key, params=meshes_cipher_params
            )
            for idx, i in enumerate(meshes_float_arrs_idxs):
                plnm.meshes[i] = meshes_encryption_response.ciphertext[idx]
            aad["meshes"] = meshes_encryption_response.aad
            logger.debug(f"Adaptive mesh encryption took {time()-tic} seconds.")
            logger.success(f"Mesh encrypted")

        if encrypt_images:
            tic = time()
            images_encryption_response = AdaptiveEncryptionModel._encrypt(
                data=plnm.images, key=key, params=images_cipher_params
            )  # create copy so we don't alter in place
            aad["images"] = images_encryption_response.aad
            logger.debug(f"Adaptive image encryption took {time()-tic} seconds.")
            logger.success(f"Images encrypted")

        return EncryptionResponse[PlnM, AAD_DICT, Key](
            ciphertext=plnm,
            aad=aad,
            key=key,
        )

    @staticmethod
    def decrypt(
        plnm: PlnM,
        meshes_cipher_params: MeshesAdaptiveCipherParams,
        key: Key,
        aad: AAD_DICT,
        images_cipher_params: ImagesAdaptiveCipherParams | None = None,
    ) -> PlnM:
        tic = time()

        mesh_aad = aad.get("meshes")
        images_aad = aad.get("images")
        meshes_encrypted = mesh_aad is not None
        images_encrypted = images_aad is not None

        if key.size == 0:
            raise Exception(f"Please provide a key")

        if meshes_encrypted:
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
                    aad=mesh_aad,
                    selection=BlockSelection(r=True),
                )

                key.k2 = get_subkey(
                    plnm_arrs=float_arrs,
                    params=meshes_cipher_params,
                    ki=key.k3,
                    selection=BlockSelection(r=True),
                )

            if key.k2:
                float_arrs = AdaptiveDecryptionModel._decrypt(
                    data=float_arrs,
                    key=key,
                    params=meshes_cipher_params,
                    aad=mesh_aad,
                    selection=BlockSelection(q=True),
                )

                key.k1 = get_subkey(
                    plnm_arrs=float_arrs,
                    params=meshes_cipher_params,
                    ki=key.k2,
                    selection=BlockSelection(q=True),
                )

            assert key.k1 is not None

            decrypted_data = AdaptiveDecryptionModel._decrypt(
                data=float_arrs,
                key=key,
                params=meshes_cipher_params,
                aad=mesh_aad,
                selection=BlockSelection(p=True),
            )

            for idx, i in enumerate(meshes_float_arrs_idxs):
                plnm.meshes[i] = decrypted_data[idx]

            assert key.filled
            logger.debug(f"Adaptive mesh decryption took {time()-tic} seconds.")
            logger.success(f"Mesh decrypted")

        images_arrs = plnm.images
        if images_encrypted:
            if key.k3:
                images_arrs = AdaptiveDecryptionModel._decrypt(
                    data=images_arrs,
                    key=key,
                    params=images_cipher_params,
                    aad=images_aad,
                    selection=BlockSelection(r=True),
                )

                if not meshes_encrypted:
                    # keys were generated using image data
                    key.k2 = get_subkey(
                        plnm_arrs=images_arrs,
                        params=images_cipher_params,
                        ki=key.k3,
                        selection=BlockSelection(r=True),
                    )

            if key.k2:
                images_arrs = AdaptiveDecryptionModel._decrypt(
                    data=images_arrs,
                    key=key,
                    params=images_cipher_params,
                    aad=images_aad,
                    selection=BlockSelection(q=True),
                )

                if not meshes_encrypted:
                    key.k1 = get_subkey(
                        plnm_arrs=images_arrs,
                        params=images_cipher_params,
                        ki=key.k2,
                        selection=BlockSelection(q=True),
                    )

            assert key.k1 is not None

            decrypted_data = AdaptiveDecryptionModel._decrypt(
                data=images_arrs,
                key=key,
                params=images_cipher_params,
                aad=images_aad,
                selection=BlockSelection(p=True),
            )

            assert key.filled
            logger.debug(f"Adaptive image decryption took {time()-tic} seconds.")
            logger.success(f"Images decrypted")

        return plnm
