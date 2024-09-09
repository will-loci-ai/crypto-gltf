from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Type

import numpy as np
from crypto_gltf.data.types import AAD_DATA, BaseKey, BaseParams, EncryptionResponse
from crypto_gltf.encrypt.adaptive.system import AdaptiveCryptoSystemV3
from crypto_gltf.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    Key,
    MeshesAdaptiveCipherParams,
)
from crypto_gltf.io.file.base_file import BaseFile
from crypto_gltf.io.file.file import File
from crypto_gltf.io.plaintext.plnm import PlnM


@dataclass
class Asset:
    file: BaseFile
    images_encrypted: bool = False

    @classmethod
    def load(
        cls,
        import_filepath: str,
    ) -> Asset:
        """Load file from import_filepath"""
        return cls(file=File(import_filepath=import_filepath))

    def save(self, export_dir: str) -> str:
        """Save file to export_dir"""
        return self.file.save(
            export_dir=export_dir, images_encrypted=self.images_encrypted
        )

    def encrypt(
        self,
        meshes_cipher_params: tuple[int, int, int] = (2, 2, 10),
        images_cipher_params: tuple[int, int, int] = (1, 1, 6),
        key: bytes | None = None,
        encrypt_images: bool = False,
    ) -> EncryptionResponse[PlnM, AAD_DATA, Key]:
        """Encrypt a file"""
        self.images_encrypted = encrypt_images

        if len(meshes_cipher_params)!=3 or len(images_cipher_params)!=3:
            raise ValueError(f'All three cipher parameters must be specified.')
        
        mesh_params = MeshesAdaptiveCipherParams(
            p=meshes_cipher_params[0],
            q=meshes_cipher_params[1],
            r=meshes_cipher_params[2],
        )
        img_params = ImagesAdaptiveCipherParams(
            p=images_cipher_params[0],
            q=images_cipher_params[1],
            r=images_cipher_params[2],
        )
        response = AdaptiveCryptoSystemV3.encrypt(
            plnm=self.file.plnm,
            meshes_cipher_params=mesh_params,
            images_cipher_params=img_params,
            k3=key,
            encrypt_images=encrypt_images,
        )
        self.file.insert_plnm(response.ciphertext)

        assert response.aad is not None
        self.file.embed_aad(response.aad)

        return response

    def decrypt(
        self,
        k1: bytes | None = None,
        k2: bytes | None = None,
        k3: bytes | None = None,
    ) -> bool:
        """Decrypt a file"""
        key = Key(k1=k1, k2=k2, k3=k3)
        aad = (
            self.file.aad
        )  # important we do this before extracting plnm, else aad extracted as well

        plnm = AdaptiveCryptoSystemV3.decrypt(plnm=self.file.plnm, key=key, aad=aad)
        self.file.insert_plnm(plnm)
        return True
