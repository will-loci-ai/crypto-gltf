from __future__ import annotations

from time import time

import numpy as np
from loguru import logger
from PIL import Image
from py_code.data.asset_file_data_types import AssetFileDataType, Gltf2Data
from py_code.data.types import AAD_DICT, Composition, PlnMDataType
from py_code.io.file.base_file import BaseFile
from py_code.io.file.gltf2.exp.gltf2_exporter import GlTF2Exporter
from py_code.io.file.gltf2.imp.gltf2_imp_binary_data import BinaryData as ImpBinaryData
from py_code.io.file.gltf2.imp.gltf2_importer import GlTF2Importer
from py_code.io.plaintext.plnm import PlnM


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

        logger.debug(f"{filename_ext[1:]} import took {time()-tic} seconds")
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

        logger.debug(f"{self.filename_ext[1:]} export took {time()-tic} seconds")

        return export_filepath

    @property
    def plnm(self) -> PlnM:
        """'Get plaintext data from GLTFFile"""
        accessors = [accessor for accessor in self.data.accessors.values()]
        images = [np.asarray(image) for image in self.data.images.values()]
        for image in images:
            assert (
                (Composition.RGB == image)
                or (Composition.RGBA == image)
                or (Composition.GREYSCALE == image)
                or (Composition.EMPTY == image)
                or (Composition.P == image)
            )
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
        for img in self.data.images.values():
            img.show()


    def embed_aad(self, aad: AAD_DICT) -> None:
        """Embed aad data in file for retrieval during decryption"""

        num_accessors = len(self.data.accessors)
        encryption_info = {}
        aad_meshes, aad_images = aad.get("meshes"), aad.get("images")
        meshes_encrypted = aad_meshes is not None
        images_encrypted = aad_images is not None

        if meshes_encrypted:
            assert Composition.AAD == aad_meshes
            self.data.accessors[num_accessors] = aad_meshes
            self.data.gltf["accessors"].append(
                {
                    "bufferView": num_accessors,
                    "byteOffset": 0,
                    "componentType": 5125,
                    "count": len(aad_meshes),
                    "type": "VEC3",
                }
            )
            encryption_info["meshes"] = {
                "encrypted": True,
                "accessor": num_accessors,
            }
            num_accessors += 1
        else:
            encryption_info["meshes"] = {
                "encrypted": False,
            }

        if images_encrypted:
            assert Composition.AAD == aad_images
            self.data.accessors[num_accessors] = aad_images
            self.data.gltf["accessors"].append(
                {
                    "bufferView": num_accessors,
                    "byteOffset": 0,
                    "componentType": 5125,
                    "count": len(aad_images),
                    "type": "VEC3",
                }
            )
            encryption_info["images"] = {
                "encrypted": True,
                "accessor": num_accessors,
            }
        else:
            encryption_info["images"] = {
                "encrypted": False,
            }

        extras = self.data.gltf["asset"].get("extras")
        if extras is not None:
            self.data.gltf["asset"]["extras"]["encryption_info"] = encryption_info
        else:
            self.data.gltf["asset"]["extras"] = {"encryption_info": encryption_info}

    @property
    def aad(self) -> AAD_DICT:
        """Retrieve embedded aad data"""
        aad = {}

        encryption_info = self.data.gltf["asset"].get("extras").get("encryption_info")
        if not encryption_info:
            raise Exception(f"No embedded aad data exists, unable to decrypt asset")

        if encryption_info["images"]["encrypted"]:
            images_aad_accessor_idx = encryption_info["images"]["accessor"]
            aad["images"] = self.data.accessors[images_aad_accessor_idx]

            # remove embedded aad
            self.data.gltf["accessors"].pop(images_aad_accessor_idx)
            self.data.accessors.pop(images_aad_accessor_idx)

        if encryption_info["meshes"]["encrypted"]:
            meshes_aad_accessor_idx = encryption_info["meshes"]["accessor"]
            aad["meshes"] = self.data.accessors[meshes_aad_accessor_idx]

            # remove embedded aad
            self.data.gltf["accessors"].pop(meshes_aad_accessor_idx)
            self.data.accessors.pop(meshes_aad_accessor_idx)

        self.data.gltf["asset"]["extras"].pop("encryption_info")
        return aad
