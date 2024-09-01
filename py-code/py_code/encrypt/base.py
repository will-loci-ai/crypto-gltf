from typing import ClassVar, Literal

import numpy as np
from py_code.data.types import AAD_DICT, BaseKey, BaseParams, EncryptionResponse
from py_code.io.plaintext.plnm import PlnM

CRYPTO_SYSTEMS = Literal["AdaptiveV1", "AdaptiveV2", "AdaptiveV3", "CA"]


class BaseCryptoSystem:
    """Base model for encryption/decryption system"""

    AAD: ClassVar[bool]  # true if the system uses aad data

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f"{cls} should not be instantiated")

    @staticmethod
    def encrypt(
        plnm: PlnM,
        meshes_cipher_params: BaseParams,
        images_cipher_params: BaseParams | None = None,
        key: BaseKey | None = None,
    ) -> EncryptionResponse[PlnM, AAD_DICT, BaseKey]:
        raise NotImplementedError()

    @staticmethod
    def decrypt(
        plnm: PlnM,
        meshes_cipher_params: BaseParams,
        key: BaseKey,
        aad: AAD_DICT,
        images_cipher_params: BaseParams | None = None,
    ) -> PlnM:
        raise NotImplementedError()
