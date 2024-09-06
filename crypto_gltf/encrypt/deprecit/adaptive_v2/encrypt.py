from time import time

import numpy as np
from crypto_gltf.data.types import EncryptionResponse
from crypto_gltf.encrypt.deprecit.adaptive_v2.aes_gcm import aes_gcm_encrypt
from crypto_gltf.encrypt.deprecit.adaptive_v2.base import AdaptiveBaseModel
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import (
    AdaptiveCipherParamsV2,
    BlockSelection,
    Key,
    SBlocks,
)
from crypto_gltf.encrypt.deprecit.adaptive_v2.utils import (
    combine_sblocks,
    get_sblocks,
    put_sblocks,
)
from loguru import logger


class AdaptiveEncryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _encrypt(
        data: list[np.ndarray], key: Key, params: AdaptiveCipherParamsV2
    ) -> EncryptionResponse[list[np.ndarray], np.ndarray, Key]:

        tic = time()

        sblocks_list = []
        for arr in data:
            sblocks_list.append(
                get_sblocks(arr=arr, params=params, to_get=BlockSelection.all())
            )

        toc = time() - tic
        combined_sblocks = combine_sblocks(sblocks_list=sblocks_list)

        assert key.k1 and key.k2 and key.k3

        r1 = aes_gcm_encrypt(message=combined_sblocks.s1, key=key.k1)
        r2 = aes_gcm_encrypt(message=combined_sblocks.s2, key=key.k2)
        r3 = aes_gcm_encrypt(message=combined_sblocks.s3, key=key.k3)

        r_blocks = SBlocks(s1=r1.ciphertext, s2=r2.ciphertext, s3=r3.ciphertext)

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

        aad_arr = np.column_stack(
            (
                np.frombuffer(r1.aad, dtype=np.uint32),
                np.frombuffer(r2.aad, dtype=np.uint32),
                np.frombuffer(r3.aad, dtype=np.uint32),
            )
        )  # convert to arr so we can embed in file
        logger.info(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )

        return EncryptionResponse[list[np.ndarray], np.ndarray, Key](
            ciphertext=encrypted_data, aad=aad_arr, key=key
        )
