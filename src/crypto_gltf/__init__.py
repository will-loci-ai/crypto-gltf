from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Type

import numpy as np
from gltf_crypto_conan1014.data.types import AAD_DATA, BaseKey, BaseParams, EncryptionResponse
from gltf_crypto_conan1014.encrypt.adaptive.system import AdaptiveCryptoSystemV3
from gltf_crypto_conan1014.encrypt.base import CRYPTO_SYSTEMS, BaseCryptoSystem
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v1.system import AdaptiveCryptoSystemV1
from gltf_crypto_conan1014.encrypt.deprecit.adaptive_v2.system import AdaptiveCryptoSystemV2
from gltf_crypto_conan1014.io.file.base_file import BaseFile
from gltf_crypto_conan1014.io.file.file import File
from gltf_crypto_conan1014.io.plaintext.plnm import PlnM


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
        encrypt_images: bool = False,
        encryptor: CRYPTO_SYSTEMS = "AdaptiveV3",
    ) -> EncryptionResponse[PlnM, AAD_DATA, BaseKey]:
        """Encrypt a file"""
        encrypt_localizer: dict[CRYPTO_SYSTEMS, Type[BaseCryptoSystem]] = {
            "AdaptiveV1": AdaptiveCryptoSystemV1,
            "AdaptiveV2": AdaptiveCryptoSystemV2,
            "AdaptiveV3": AdaptiveCryptoSystemV3,
        }
        SYSTEM = encrypt_localizer[encryptor]
        response = SYSTEM.encrypt(
            plnm=self.file.plnm,
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            key=key,
            encrypt_images=encrypt_images,
        )
        self.file.insert_plnm(response.ciphertext)

        if SYSTEM.AAD:
            assert response.aad is not None
            self.file.embed_aad(response.aad)

        return response

    def decrypt(
        self,
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
        aad = (
            self.file.aad
        )  # important we do this before extracting plnm, else aad extracted as well

        plnm = SYSTEM.decrypt(
            plnm=self.file.plnm,
            key=key,
            aad=aad,
        )
        self.file.insert_plnm(plnm)
        return True
