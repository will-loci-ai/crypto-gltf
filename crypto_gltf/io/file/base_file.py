from __future__ import annotations

import os
from functools import cached_property
from tempfile import TemporaryDirectory

from crypto_gltf.data.asset_file_data_types import AssetFileDataType
from crypto_gltf.data.types import AAD_DATA, Extension
from crypto_gltf.io.plaintext.plnm import PlnM
from pydantic import BaseModel, ConfigDict


class BaseFile(BaseModel):
    """Base class for 3D asset file types"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    import_path: str
    filename_ext: Extension.ASSET
    data: AssetFileDataType

    @classmethod
    def load(cls, import_path: str) -> BaseFile:
        raise NotImplementedError()

    def save(self, export_dir: str, images_encrypted: bool = False) -> str:
        """Returns export filepath"""
        raise NotImplementedError()

    @cached_property
    def basename(self) -> str:
        return os.path.basename(self.import_path)

    @cached_property
    def filename(self) -> str:
        return os.path.splitext(self.basename)[0]

    @cached_property
    def import_dirpath(self) -> str:
        return os.path.dirname(self.import_path)

    @cached_property
    def import_dirname(self) -> str:
        return os.path.basename(self.import_dirpath)

    @cached_property
    def export_filename(self) -> str:
        return f"exported_{self.filename}{self.filename_ext}"

    @property
    def plnm(self) -> PlnM:
        """Return plaintext data from file"""
        raise NotImplementedError()

    def insert_plnm(self, plnm: PlnM) -> None:
        """Insert plaintext data in file
        assumes the plaintext data came from the same file"""
        raise NotImplementedError()

    def embed_aad(self, aad: AAD_DATA) -> None:
        """Embed aad data in file for retrieval during decryption"""
        raise NotImplementedError()

    @property
    def aad(self) -> AAD_DATA:
        """Retrieve embedded aad data"""
        raise NotImplementedError()
