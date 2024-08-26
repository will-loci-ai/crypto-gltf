from time import time

import numpy as np
from loguru import logger
from py_code.encrypt.adaptive.aes_gcm import aes_gcm_decrypt
from py_code.encrypt.adaptive.base import AdaptiveBaseModel
from py_code.encrypt.adaptive.types import AdaptiveCipherParams, SBlocks
from py_code.encrypt.adaptive.utils import (
    combine_sblocks,
    get_s_blocks,
    insert_s_blocks,
)


class AdaptiveDecryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _decrypt(
        data: list[np.ndarray],
        key: bytes,
        params: AdaptiveCipherParams,
        aad_b64: bytes,
    ) -> list[np.ndarray]:

        tic = time()

        sblocks_list = []
        for arr in data:
            sblocks_list.append(get_s_blocks(arr=arr, params=params))

        toc = time() - tic

        combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

        s1 = aes_gcm_decrypt(
            ciphertext=combined_sblocks.s1, aad_b64=aad_b64[:56], key=key
        )
        s2 = aes_gcm_decrypt(
            ciphertext=combined_sblocks.s2, aad_b64=aad_b64[56:112], key=key
        )
        s3 = aes_gcm_decrypt(
            ciphertext=combined_sblocks.s3, aad_b64=aad_b64[112:], key=key
        )

        s_blocks = SBlocks(s1=s1, s2=s2, s3=s3)

        tic = time()

        decrypted_data = []
        offset = 0
        for arr in data:
            decrypted_data.append(
                insert_s_blocks(
                    arr=arr, params=params, s_blocks=s_blocks, offset=offset
                )
            )
            offset += arr.size

        if not offset == sum([arr.size for arr in data]):
            raise Exception(f"Entire plain text has not been used")

        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return decrypted_data
