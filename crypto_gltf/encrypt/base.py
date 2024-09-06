from typing import ClassVar, Literal

import numpy as np
from crypto_gltf.data.types import AAD_DATA, BaseKey, BaseParams, EncryptionResponse
from crypto_gltf.io.plaintext.plnm import PlnM

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
        encrypt_images: bool = False,
    ) -> EncryptionResponse[PlnM, AAD_DATA, BaseKey]:
        raise NotImplementedError()

    @staticmethod
    def decrypt(
        plnm: PlnM,
        key: BaseKey,
        aad: AAD_DATA,
    ) -> PlnM:
        raise NotImplementedError()
