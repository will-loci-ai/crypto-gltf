from __future__ import annotations

from dataclasses import dataclass
from time import time

from loguru import logger
from py_code.data.asset_file_data_types import AssetFileDataType, Gltf2Data
from py_code.io.file.base_file import BaseFile
from py_code.io.file.gltf2.exp.gltf2_exporter import GlTF2Exporter
from py_code.io.file.gltf2.imp.gltf2_imp_binary_data import BinaryData as ImpBinaryData
from py_code.io.file.gltf2.imp.gltf2_importer import GlTF2Importer


@dataclass
class GLTFFile(BaseFile):
    data: AssetFileDataType.GLTF2

    @classmethod
    def load(cls, import_path: str) -> GLTFFile:
        """Load an glTF/glb file"""

        tic = time()
        gltf_importer = GlTF2Importer.from_filepath(
            filepath=import_path,
        )
        for i in range(len(gltf_importer.accessors)):
            ImpBinaryData.decode_accessor(gltf_importer, i, cache=True)

        for i in range(len(gltf_importer.images)):
            ImpBinaryData.decode_image(gltf_importer, i)

        if gltf_importer.glb_buffer:
            filename_ext = ".glb"
            is_glb = True
        else:
            filename_ext = ".gltf"
            is_glb = False

        data = Gltf2Data(
            gltf=gltf_importer.gltf,
            images=gltf_importer.image_cache,
            accessors=gltf_importer.accessor_cache,
            is_glb=is_glb,
        )

        logger.info(f"{filename_ext[1:]} import took {time()-tic} seconds")
        return cls(data=data, import_path=import_path, filename_ext=filename_ext)

    def save(self, export_dir: str) -> str:
        """Save to glTF/glb file"""

        tic = time()
        gltf_exporter = GlTF2Exporter(
            export_dir=export_dir,
            filename=self.filename,
            is_glb=self.data.is_glb,
            filename_ext=self.filename_ext,
        )
        export_filepath = gltf_exporter.export(self.data)

        logger.info(f"{self.filename_ext[1:]} export took {time()-tic} seconds")

        return export_filepath
