from time import time
from typing import Literal

import numpy as np
from py_code.encrypt.adaptive.base import AdaptiveBaseModel
from py_code.encrypt.adaptive.utils import get_bytes, insert_bytes
from py_code.encrypt.aes_gcm import aes_gcm_decrypt
from loguru import logger

class AdaptiveDecryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _decrypt(
        data: list[np.ndarray],
        key: bytes,
        position: Literal[0, 1, 2, 3],
        aad_b64: bytes,
    ) -> list[np.ndarray]:
        tic = time()

        shapes = [arr.shape for arr in data]

        buffer = bytearray(b"")
        vals = []
        for arr in data:
            buffer.extend(get_bytes(arr, position))
            vals.append(get_bytes(arr, position))

        toc = time() - tic

        decrypted_buffer = aes_gcm_decrypt(ciphertext=buffer, aad_b64=aad_b64, key=key)

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
