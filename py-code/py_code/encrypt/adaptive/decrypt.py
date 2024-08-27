from time import time

import numpy as np
from loguru import logger
from py_code.encrypt.adaptive.aes_gcm import aes_gcm_decrypt
from py_code.encrypt.adaptive.base import AdaptiveBaseModel
from py_code.encrypt.adaptive.types import (
    AdaptiveCipherParams,
    BlockSelection,
    Key,
    SBlocks,
)
from py_code.encrypt.adaptive.utils import combine_sblocks, get_sblocks, put_sblocks


class AdaptiveDecryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _decrypt(
        data: list[np.ndarray],
        key: Key,
        params: AdaptiveCipherParams,
        aad_b64: bytes,
        selection: BlockSelection,
    ) -> list[np.ndarray]:

        tic = time()

        sblocks_list = []
        for arr in data:
            sblocks_list.append(get_sblocks(arr=arr, params=params, to_get=selection))

        toc = time() - tic

        combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

        s1, s2, s3 = bytearray(b""), bytearray(b""), bytearray(b"")

        if selection.p:
            assert key.k1  # check key exists
            s1 = aes_gcm_decrypt(
                ciphertext=combined_sblocks.s1, aad_b64=aad_b64[:56], key=key.k1
            )
        if selection.q:
            assert key.k2  # check key exists
            s2 = aes_gcm_decrypt(
                ciphertext=combined_sblocks.s2, aad_b64=aad_b64[56:112], key=key.k2
            )
        if selection.r:
            assert key.k3  # check key exists
            s3 = aes_gcm_decrypt(
                ciphertext=combined_sblocks.s3, aad_b64=aad_b64[112:], key=key.k3
            )

        s_blocks = SBlocks(s1=s1, s2=s2, s3=s3)

        tic = time()

        decrypted_data = []
        offset = 0
        for arr in data:
            decrypted_data.append(
                put_sblocks(
                    arr=arr,
                    params=params,
                    sblocks=s_blocks,
                    offset=offset,
                    to_put=selection,
                )
            )
            offset += arr.size

        if not offset == sum([arr.size for arr in data]):
            raise Exception(f"Entire plain text has not been used")

        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return decrypted_data
