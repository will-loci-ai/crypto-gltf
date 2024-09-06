from __future__ import annotations

from time import time

import numpy as np
from crypto_gltf.data.types import AAD_DATA, EncryptionResponse
from crypto_gltf.encrypt.adaptive.cryptography.key_gen import generate_keys, get_subkey
from crypto_gltf.encrypt.adaptive.decrypt import AdaptiveDecryptionModel
from crypto_gltf.encrypt.adaptive.encrypt import AdaptiveEncryptionModel
from crypto_gltf.encrypt.adaptive.types import (
    AdaptiveCipherParams,
    BlockSelection,
    ImagesAdaptiveCipherParams,
    Key,
    MeshesAdaptiveCipherParams,
)
from crypto_gltf.io.plaintext.plnm import PlnM
from loguru import logger


class AdaptiveCryptoSystemV3(AdaptiveEncryptionModel, AdaptiveDecryptionModel):
    """Adaptive cipher system"""

    AAD: bool = True

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: MeshesAdaptiveCipherParams,
        images_cipher_params: ImagesAdaptiveCipherParams,
        k3: bytes | None = None,
        encrypt_images: bool = False,
    ) -> EncryptionResponse[PlnM, AAD_DATA, Key]:

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

        if len(float_arrs) == 0:
            raise Exception(f"No asset data to encrypt.")
        if not k3:
            key = generate_keys(float_arrs, meshes_cipher_params)
        else:
            # a key has been provided
            if not len(k3) == 32:
                raise Exception(f"Key must be 32 bytes long, received {len(k3)} bytes")
            key = generate_keys(float_arrs[:50], meshes_cipher_params, k3)

        data: list[tuple[np.ndarray, AdaptiveCipherParams]] = [
            (float_arr, meshes_cipher_params) for float_arr in float_arrs
        ]
        if encrypt_images:
            data += [(img, images_cipher_params) for img in plnm.images]

        encryption_response = AdaptiveEncryptionModel._encrypt(data=data, key=key)
        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = encryption_response.ciphertext[idx]

        if encrypt_images:
            plnm.images = encryption_response.ciphertext[len(float_arrs) :]

        aad = AAD_DATA(
            aad=encryption_response.aad,
            encrypt_images=encrypt_images,
            meshes_params=meshes_cipher_params.__dict__,
            images_params=images_cipher_params.__dict__,
        )

        # logger.debug(f"Adaptive mesh encryption took {time()-tic} seconds.")
        logger.success(f"Asset encrypted")

        return EncryptionResponse[PlnM, AAD_DATA, Key](
            ciphertext=plnm,
            aad=aad,
            key=key,
        )

    @staticmethod
    def decrypt(
        plnm: PlnM,
        key: Key,
        aad: AAD_DATA,
    ) -> PlnM:
        tic = time()

        meshes_cipher_params = MeshesAdaptiveCipherParams(**aad.meshes_params)

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

        data: list[tuple[np.ndarray, AdaptiveCipherParams]] = [
            (float_arr, meshes_cipher_params) for float_arr in float_arrs
        ]
        if aad.encrypt_images:
            images_cipher_params = ImagesAdaptiveCipherParams(**aad.images_params)
            data += [(img, images_cipher_params) for img in plnm.images]

        if key.k3:
            visual_level = "clear"
        elif key.k2:
            visual_level = "low"
        elif key.k1:
            visual_level = "mid"
        else:
            visual_level = "high"

        if key.k3:
            data = AdaptiveDecryptionModel._decrypt(
                data=data, key=key, aad=aad.aad, selection=BlockSelection(r=True)
            )

            key.k2 = get_subkey(
                plnm_arrs=[item[0] for item in data[: len(float_arrs)]],
                params=meshes_cipher_params,
                ki=key.k3,
                selection=BlockSelection(r=True),
            )

        if key.k2:
            data = AdaptiveDecryptionModel._decrypt(
                data=data, key=key, aad=aad.aad, selection=BlockSelection(q=True)
            )

            key.k1 = get_subkey(
                plnm_arrs=[item[0] for item in data[: len(float_arrs)]],
                params=meshes_cipher_params,
                ki=key.k2,
                selection=BlockSelection(q=True),
            )

        assert key.k1 is not None

        decrypted_data = AdaptiveDecryptionModel._decrypt(
            data=data, key=key, aad=aad.aad, selection=BlockSelection(p=True)
        )

        for idx, i in enumerate(meshes_float_arrs_idxs):
            plnm.meshes[i] = decrypted_data[idx][0]

        assert key.filled

        # logger.debug(f"Adaptive mesh decryption took {time()-tic} seconds.")
        logger.success(f"Asset decrypted to visual level {visual_level}")

        return plnm
