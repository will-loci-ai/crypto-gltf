from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Type

import numpy as np
from py_code.data.types import AAD_DICT, BaseKey, BaseParams, EncryptionResponse
from py_code.encrypt.adaptive.system import AdaptiveCryptoSystemV3
from py_code.encrypt.base import CRYPTO_SYSTEMS, BaseCryptoSystem
from py_code.encrypt.deprecit.adaptive_v1.system import AdaptiveCryptoSystemV1
from py_code.encrypt.deprecit.adaptive_v2.system import AdaptiveCryptoSystemV2
from py_code.io.file.base_file import BaseFile
from py_code.io.file.file import File
from py_code.io.plaintext.plnm import PlnM


@dataclass
class Asset:
    file: BaseFile

    @classmethod
    def load(
        cls,
        import_filepath: str,
    ) -> Asset:
        """Load file from import_filepath"""
        return cls(file=File(import_filepath=import_filepath))

    def save(self, export_dir: str) -> str:
        """Save file to export_dir"""
        return self.file.save(export_dir=export_dir)

    def encrypt(
        self,
        meshes_cipher_params: BaseParams,
        images_cipher_params: BaseParams,
        key: BaseKey | None = None,
        encryptor: CRYPTO_SYSTEMS = "AdaptiveV3",
    ) -> EncryptionResponse[PlnM, AAD_DICT, BaseKey]:
        """Encrypt a file"""
        encrypt_localizer: dict[CRYPTO_SYSTEMS, Type[BaseCryptoSystem]] = {
            "AdaptiveV1": AdaptiveCryptoSystemV1,
            "AdaptiveV2": AdaptiveCryptoSystemV2,
            "AdaptiveV3": AdaptiveCryptoSystemV3,
        }
        SYSTEM = encrypt_localizer[encryptor]
        response = SYSTEM.encrypt(
            self.file.plnm, meshes_cipher_params, images_cipher_params, key
        )
        self.file.insert_plnm(response.ciphertext)

        if SYSTEM.AAD:
            assert response.aad is not None
            self.file.embed_aad(response.aad)

        return response

    def decrypt(
        self,
        meshes_cipher_params: BaseParams,
        images_cipher_params: BaseParams,
        key: BaseKey,
        decryptor: CRYPTO_SYSTEMS = "AdaptiveV3",
    ) -> bool:
        """Decrypt a file"""
        decrypt_localizer: dict[CRYPTO_SYSTEMS, Type[BaseCryptoSystem]] = {
            "AdaptiveV1": AdaptiveCryptoSystemV1,
            "AdaptiveV2": AdaptiveCryptoSystemV2,
            "AdaptiveV3": AdaptiveCryptoSystemV3,
        }
        SYSTEM = decrypt_localizer[decryptor]

        if SYSTEM.AAD:
            aad = self.file.aad
        else:
            aad = {}

        plnm = SYSTEM.decrypt(
            self.file.plnm,
            meshes_cipher_params,
            images_cipher_params,
            key,
            aad,
        )
        self.file.insert_plnm(plnm)
        return True
