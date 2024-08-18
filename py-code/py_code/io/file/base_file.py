from __future__ import annotations

import os
from dataclasses import dataclass
from functools import cached_property
from tempfile import TemporaryDirectory
from typing import Any

from loci_asset.asset import LociAsset
from py_code.data.asset_file_data_types import AssetFileDataType
from py_code.data.types import Extension


@dataclass
class BaseFile:
    """Base class for 3D asset file types"""

    import_path: str
    filename_ext: Extension.ASSET
    data: AssetFileDataType

    @classmethod
    def load(cls, import_path: str) -> BaseFile:
        raise NotImplementedError()

    def save(self, export_dir: str) -> str:
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
    def render(self):
        """Render file"""
        with TemporaryDirectory() as tmp_dir:
            ret = self.save(tmp_dir)
            asset = LociAsset.from_url(ret)
            img = asset.medium_res_image
            return img