import os
from time import time
from typing import Literal

import numpy as np
from loguru import logger
from py_code.data.types import EncryptionResponse
from py_code.encrypt.deprecit.adaptive_v1.aes_gcm import aes_gcm_encrypt
from py_code.encrypt.deprecit.adaptive_v1.base import AdaptiveBaseModel
from py_code.encrypt.deprecit.adaptive_v1.utils import get_bytes, insert_bytes


class AdaptiveEncryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _encrypt(
        data: list[np.ndarray], key: bytes, position: Literal[0, 1, 2, 3]
    ) -> EncryptionResponse[list[np.ndarray]]:

        tic = time()
        shapes = [arr.shape for arr in data]

        buffer = bytearray(b"")
        for arr in data:
            buffer.extend(get_bytes(arr, position))

        toc = time() - tic

        response = aes_gcm_encrypt(message=buffer, key=key)

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

        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return EncryptionResponse[list[np.ndarray]](
            ciphertext=encrypted_data, aad=response.aad
        )