import secrets
from time import time

import numpy as np
from crypto_gltf.data.types import EncryptionResponse
from crypto_gltf.encrypt.adaptive.base import AdaptiveBaseModel
from crypto_gltf.encrypt.adaptive.cryptography.aes_gcm import aes_gcm_encrypt
from crypto_gltf.encrypt.adaptive.types import AdaptiveCipherParams, BufferView, Key
from crypto_gltf.encrypt.adaptive.utils import get_bits, put_bits
from loguru import logger


class AdaptiveEncryptionModel(AdaptiveBaseModel):

    @staticmethod
    def _encrypt(
        data: list[tuple[np.ndarray, AdaptiveCipherParams]], key: Key
    ) -> EncryptionResponse[list[np.ndarray], np.ndarray, Key]:

        tic = time()

        s1, s2, s3 = bytearray(b""), bytearray(b""), bytearray(b"")

        for arr, params in data:

            buffer_view = BufferView.from_shape(shape=arr.shape, params=params)

            p_buffer, q_buffer, r_buffer = (
                buffer_view.p_buffer,
                buffer_view.q_buffer,
                buffer_view.r_buffer,
            )

            get_bits(
                arr,
                p_buffer,
                params.pstart,
                params.pstop,
                secrets.randbits(32),
            )
            get_bits(
                arr,
                q_buffer,
                params.qstart,
                params.qstop,
                secrets.randbits(32),
            )
            get_bits(
                arr,
                r_buffer,
                params.rstart,
                params.rstop,
                secrets.randbits(32),
            )

            s1.extend(p_buffer.tobytes())
            s2.extend(q_buffer.tobytes())
            s3.extend(r_buffer.tobytes())

        toc = time() - tic
        assert key.k1 and key.k2 and key.k3

        r1 = aes_gcm_encrypt(message=s1, key=key.k1)
        r2 = aes_gcm_encrypt(message=s2, key=key.k2)
        r3 = aes_gcm_encrypt(message=s3, key=key.k3)

        # combine aads
        aad = bytearray(b"")
        aad.extend(r1.aad)
        aad.extend(r2.aad)
        aad.extend(r3.aad)

        tic = time()

        r1_arr = np.frombuffer(r1.ciphertext, dtype=np.uint32)
        r2_arr = np.frombuffer(r2.ciphertext, dtype=np.uint32)
        r3_arr = np.frombuffer(r3.ciphertext, dtype=np.uint32)

        padding = []
        poffset, qoffset, roffset = 0, 0, 0
        for arr, params in data:

            buffer_view = BufferView.from_shape(shape=arr.shape, params=params)
            put_bits(
                arr,
                r1_arr[poffset : poffset + buffer_view.pbufflen],
                params.pstart,
                params.pstop,
            )
            put_bits(
                arr,
                r2_arr[qoffset : qoffset + buffer_view.qbufflen],
                params.qstart,
                params.qstop,
            )
            put_bits(
                arr,
                r3_arr[roffset : roffset + buffer_view.rbufflen],
                params.rstart,
                params.rstop,
            )

            padding.append(
                [
                    r1_arr[poffset + buffer_view.pbufflen - 1],
                    r2_arr[qoffset + buffer_view.qbufflen - 1],
                    r3_arr[roffset + buffer_view.rbufflen - 1],
                ]
            )
            poffset += buffer_view.pbufflen
            qoffset += buffer_view.qbufflen
            roffset += buffer_view.rbufflen

        if not poffset == len(r1_arr):
            raise Exception(f"Entire p buffer has not been inserted")
        if not qoffset == len(r2_arr):
            raise Exception(f"Entire q buffer has not been inserted")
        if not roffset == len(r3_arr):
            raise Exception(f"Entire r buffer has not been inserted")

        aad_arr = np.column_stack(
            (
                np.frombuffer(r1.aad, dtype=np.uint32),
                np.frombuffer(r2.aad, dtype=np.uint32),
                np.frombuffer(r3.aad, dtype=np.uint32),
            )
        )  # convert to arr so we can embed in file
        aad = np.concatenate(
            (np.array(padding, dtype=np.uint32), aad_arr)
        )  # add padding to authentification information

        # logger.debug(
        #     f"Byte retrieval/insertion and reshaping took {time()-tic + toc} seconds"
        # )

        return EncryptionResponse[list[np.ndarray], np.ndarray, Key](
            ciphertext=[item[0] for item in data],
            aad=aad,
            key=key,
        )
