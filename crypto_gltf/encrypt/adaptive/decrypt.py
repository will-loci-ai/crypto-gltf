from time import time

import numpy as np
from crypto_gltf.encrypt.adaptive.base import AdaptiveBaseModel
from crypto_gltf.encrypt.adaptive.cryptography.aes_gcm import aes_gcm_decrypt
from crypto_gltf.encrypt.adaptive.types import (
    AdaptiveCipherParams,
    BlockSelection,
    BufferView,
    Key,
)
from crypto_gltf.encrypt.adaptive.utils import get_bits, put_bits
from loguru import logger


class AdaptiveDecryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _decrypt(
        data: list[tuple[np.ndarray, AdaptiveCipherParams]],
        key: Key,
        selection: BlockSelection,
        aad: np.ndarray,
    ) -> list[tuple[np.ndarray, AdaptiveCipherParams]]:
        tic = time()

        block = selection.single_block

        assert len(aad) == len(data) + 14  # +14 for 14 rows of aad data

        match selection.single_block:
            case "p":
                assert key.k1  # check key exists
                subkey = key.k1
                padding_arr = aad[:, 0]
            case "q":
                assert key.k2  # check key exists
                subkey = key.k2
                padding_arr = aad[:, 1]
            case "r":
                assert key.k3  # check key exists
                subkey = key.k3
                padding_arr = aad[:, 2]
            case _:
                raise Exception("No blocks selected.")

        aad_b64 = padding_arr[-14:].tobytes()

        combined_sblocks = bytearray(b"")
        for idx, (arr, params) in enumerate(data):

            start = params.start(block)
            stop = params.stop(block)
            buffer_view = BufferView.from_shape(shape=arr.shape, params=params)
            buffer = buffer_view.buffer(block=block)
            get_bits(arr, buffer, start, stop)
            buffer[-1] = padding_arr[idx]
            combined_sblocks.extend(buffer.tobytes())

        toc = time() - tic

        try:
            decrypted_data = aes_gcm_decrypt(
                ciphertext=combined_sblocks, aad_b64=aad_b64, key=subkey
            )
        except:
            raise Exception("Invalid key.")

        tic = time()

        decrypted_data_arr = np.frombuffer(decrypted_data, dtype=np.uint32)

        offset = 0
        for arr, params in data:
            buffer_view = BufferView.from_shape(shape=arr.shape, params=params)
            start = params.start(block)
            stop = params.stop(block)

            put_bits(
                arr,
                decrypted_data_arr[offset : offset + buffer_view.bufflen(block=block)],
                start,
                stop,
            )
            offset += buffer_view.bufflen(block=block)

        if not offset == len(decrypted_data_arr):
            raise Exception(f"Entire plain text has not been used")

        # logger.debug(
        #     f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        # )
        return data
