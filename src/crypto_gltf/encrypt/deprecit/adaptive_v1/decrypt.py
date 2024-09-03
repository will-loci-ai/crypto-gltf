from time import time
from typing import Literal

import numpy as np
from loguru import logger
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.aes_gcm import aes_gcm_decrypt
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.base import AdaptiveBaseModel
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.types import Key
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.utils import get_bytes, insert_bytes


class AdaptiveDecryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _decrypt(
        data: list[np.ndarray],
        key: Key,
        position: Literal[0, 1, 2, 3],
        aad: bytes,
    ) -> list[np.ndarray]:
        tic = time()

        shapes = [arr.shape for arr in data]

        buffer = bytearray(b"")
        for arr in data:
            buffer.extend(get_bytes(arr, position))

        toc = time() - tic

        assert key.k1
        decrypted_buffer = aes_gcm_decrypt(ciphertext=buffer, aad_b64=aad, key=key.k1)

        tic = time()

        decrypted_data = []
        offset = 0
        for arr, shape in zip(data, shapes):
            decrypted_data.append(
                insert_bytes(
                    arr=arr,
                    position=position,
                    buffer=decrypted_buffer[offset : offset + arr.size],
                ).reshape(shape)
            )
            offset += arr.size

        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return decrypted_data