from time import time

import numpy as np
from loguru import logger
from py_code.encrypt.adaptive.base import AdaptiveBaseModel
from py_code.encrypt.adaptive.cryptography.aes_gcm import aes_gcm_decrypt
from py_code.encrypt.adaptive.types import (
    AdaptiveCipherParams,
    BlockSelection,
    BufferView,
    Key,
)
from py_code.encrypt.adaptive.utils import get_bits, put_bits


class AdaptiveDecryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _decrypt(
        data: list[np.ndarray],
        key: Key,
        params: AdaptiveCipherParams,
        selection: BlockSelection,
        aad: np.ndarray,
    ) -> list[np.ndarray]:
        tic = time()

        block = selection.single_block

        assert len(aad) == len(data) + 14  # +14 for 14 rows of aad data

        start = params.start(block)
        stop = params.stop(block)

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
        for idx, arr in enumerate(data):
            buffer_view = BufferView.from_shape(shape=arr.shape, params=params)
            buffer = buffer_view.buffer(block=block)
            get_bits(arr, buffer, start, stop)
            buffer[-1] = padding_arr[idx]
            combined_sblocks.extend(buffer.tobytes())

        toc = time() - tic

        decrypted_data = aes_gcm_decrypt(
            ciphertext=combined_sblocks, aad_b64=aad_b64, key=subkey
        )

        tic = time()

        decrypted_data_arr = np.frombuffer(decrypted_data, dtype=np.uint32)

        offset = 0
        for arr in data:
            buffer_view = BufferView.from_shape(shape=arr.shape, params=params)

            put_bits(
                arr,
                decrypted_data_arr[offset : offset + buffer_view.bufflen(block=block)],
                start,
                stop,
            )

            offset += buffer_view.bufflen(block=block)

        if not offset == len(decrypted_data_arr):
            raise Exception(f"Entire plain text has not been used")

        logger.debug(
            f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        )
        return data
