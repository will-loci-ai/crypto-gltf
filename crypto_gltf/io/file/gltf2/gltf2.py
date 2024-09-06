from __future__ import annotations

from time import time

import numpy as np
from crypto_gltf.data.asset_file_data_types import Gltf2Data
from crypto_gltf.data.types import AAD_DATA, Composition
from crypto_gltf.io.file.base_file import BaseFile
from crypto_gltf.io.file.gltf2.exp.gltf2_exporter import GlTF2Exporter
from crypto_gltf.io.file.gltf2.imp.gltf2_imp_binary_data import (
    BinaryData as ImpBinaryData,
)
from crypto_gltf.io.file.gltf2.imp.gltf2_importer import GlTF2Importer
from crypto_gltf.io.plaintext.plnm import PlnM
from loguru import logger
from PIL import Image


class GLTFFile(BaseFile):
    data: Gltf2Data

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

        # logger.debug(f"{filename_ext[1:]} import took {time()-tic} seconds")
        return cls(data=data, import_path=import_path, filename_ext=filename_ext)

    def save(self, export_dir: str, images_encrypted: bool = False) -> str:
        """Save to glTF/glb file"""

        tic = time()
        gltf_exporter = GlTF2Exporter(
            export_dir=export_dir,
            filename=self.filename,
            is_glb=self.data.is_glb,
            filename_ext=self.filename_ext,
            images_encrypted=images_encrypted,
        )
        export_filepath = gltf_exporter.export(self.data)

        # logger.debug(f"{self.filename_ext[1:]} export took {time()-tic} seconds")

        return export_filepath

    @property
    def plnm(self) -> PlnM:
        """'Get plaintext data from GLTFFile"""
        accessors = [accessor for accessor in self.data.accessors.values()]
        images = [
            np.asarray(image, dtype=np.uint8) for image in self.data.images.values()
        ]
        for image in images:
            assert image.dtype == np.uint8
            assert len(image.shape) < 4

        return PlnM(
            meshes=accessors,
            images=images,
            meshes_dim=len(accessors),
            images_dim=len(images),
        )

    def insert_plnm(self, plnm: PlnM) -> None:
        """Insert plaintext in GLTFFile
        assumes the plaintext data came from the same GLTFFile"""

        self.data.accessors = {idx: mesh for idx, mesh in enumerate(plnm.meshes)}
        self.data.images = {
            idx: Image.fromarray(image) for idx, image in enumerate(plnm.images)
        }

    def embed_aad(self, aad: AAD_DATA) -> None:
        """Embed aad data in file for retrieval during decryption"""

        num_accessors = len(self.data.accessors)
        assert Composition.AAD == aad.aad
        self.data.accessors[num_accessors] = aad.aad
        self.data.gltf["accessors"].append(
            {
                "bufferView": num_accessors,
                "byteOffset": 0,
                "componentType": 5125,
                "count": len(aad.aad),
                "type": "VEC3",
            }
        )
        encryption_info = {
            "encrypted": True,
            "accessor": num_accessors,
            "images_encrypted": aad.encrypt_images,
            "meshes_params": aad.meshes_params,
            "images_params": aad.images_params,
        }

        extras = self.data.gltf["asset"].get("extras")
        if extras is not None:
            self.data.gltf["asset"]["extras"]["encryption_info"] = encryption_info
        else:
            self.data.gltf["asset"]["extras"] = {"encryption_info": encryption_info}

    @property
    def aad(self) -> AAD_DATA:
        """Retrieve embedded aad data"""

        encryption_info = self.data.gltf["asset"].get("extras").get("encryption_info")
        if not encryption_info:
            raise Exception(f"No embedded aad data exists, unable to decrypt asset")
        if not encryption_info["encrypted"]:
            raise Exception("Asset not encrypted")

        aad_accessor_idx = encryption_info["accessor"]
        aad = self.data.accessors[aad_accessor_idx]

        # remove embedded aad
        self.data.gltf["accessors"].pop(aad_accessor_idx)
        self.data.accessors.pop(aad_accessor_idx)

        return AAD_DATA(
            aad=aad,
            encrypt_images=encryption_info["images_encrypted"],
            meshes_params=encryption_info["meshes_params"],
            images_params=encryption_info["images_params"],
        )
