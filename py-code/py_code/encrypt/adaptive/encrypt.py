from time import time

import numpy as np
from loguru import logger
from py_code.data.types import EncryptionResponse
from py_code.encrypt.adaptive.aes_gcm import aes_gcm_encrypt
from py_code.encrypt.adaptive.base import AdaptiveBaseModel
from py_code.encrypt.adaptive.types import (
    AdaptiveCipherParams,
    BlockSelection,
    Key,
    SBlocks,
)
from py_code.encrypt.adaptive.utils import combine_sblocks, get_sblocks, put_sblocks

class AdaptiveEncryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _encrypt(
        data: list[np.ndarray], key: Key, params: AdaptiveCipherParams
    ) -> EncryptionResponse[list[np.ndarray]]:

        tic = time()

        sblocks_list = []
        for arr in data:
            sblocks_list.append(
                get_sblocks(arr=arr, params=params, to_get=BlockSelection.all())
            )

            np.ctypeslib.as_ctypes(arr)

        toc = time() - tic

        combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

        assert key.k1 and key.k2 and key.k3

        r1 = aes_gcm_encrypt(message=combined_sblocks.s1, key=key.k1)
        r2 = aes_gcm_encrypt(message=combined_sblocks.s2, key=key.k2)
        r3 = aes_gcm_encrypt(message=combined_sblocks.s3, key=key.k3)

        r_blocks = SBlocks(s1=r1.ciphertext, s2=r2.ciphertext, s3=r3.ciphertext)

        # combine aads
        aad = bytearray(b"")
        aad.extend(r1.aad)
        aad.extend(r2.aad)
        aad.extend(r3.aad)

        tic = time()

        encrypted_data = []
        offset = 0
        for arr in data:
            encrypted_data.append(
                put_sblocks(
                    arr=arr,
                    params=params,
                    sblocks=r_blocks,
                    offset=offset,
                    to_put=BlockSelection.all(),
                )
            )
            offset += arr.size

        if not offset == sum([arr.size for arr in data]):
            raise Exception(f"Entire cipher text has not been used")

        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return EncryptionResponse[list[np.ndarray]](ciphertext=encrypted_data, aad=aad)
