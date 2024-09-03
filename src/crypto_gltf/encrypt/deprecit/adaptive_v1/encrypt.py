import os
from time import time
from typing import Literal

import numpy as np
from loguru import logger
from gltf_crypto_conan1014.data.types import EncryptionResponse
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.aes_gcm import aes_gcm_encrypt
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.base import AdaptiveBaseModel
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.types import Key
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.utils import get_bytes, insert_bytes


class AdaptiveEncryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _encrypt(
        data: list[np.ndarray], key: Key, position: Literal[0, 1, 2, 3]
    ) -> EncryptionResponse[list[np.ndarray], np.ndarray, Key]:

        tic = time()
        shapes = [arr.shape for arr in data]
        assert key.k1 is not None

        buffer = bytearray(b"")
        for arr in data:
            buffer.extend(get_bytes(arr, position))

        toc = time() - tic

        response = aes_gcm_encrypt(message=buffer, key=key.k1)

        tic = time()

        encrypted_data = []
        offset = 0
        for arr, shape in zip(data, shapes):
            encrypted_data.append(
                insert_bytes(
                    arr=arr,
                    position=position,
                    buffer=response.ciphertext[offset : offset + arr.size],
                ).reshape(shape)
            )
            offset += arr.size

        if not offset == sum([arr.size for arr in data]):
            raise Exception(f"Entire cipher text has not been used")

        single_aad_arr = np.frombuffer(response.aad, dtype=np.uint32)
        aad_arr = np.column_stack(
            (
                np.frombuffer(response.aad, dtype=np.uint32),
                np.zeros((len(single_aad_arr)), dtype=np.uint32),
                np.zeros((len(single_aad_arr)), dtype=np.uint32),
            )
        ) # convert to arr so we can embed in file

        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return EncryptionResponse[list[np.ndarray], np.ndarray, Key](
            ciphertext=encrypted_data, aad=aad_arr, key=key
        )
