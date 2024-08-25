from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from loguru import logger
from PIL import Image
from py_code.data.types import ArrayComposition3D, PlnMDataType
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.file.off.off import OffFile
from py_code.io.plaintext.base_plaintext import BasePlainText


@dataclass
class PlnM(BasePlainText):
    """Data class for multi matrix 3D asset attributes (colors, meshes etc.)"""

    meshes: list[np.ndarray]
    images: list[np.ndarray]

    @property
    def renders(self) -> list[Image.Image]:
        """Render image data classes"""

        renders = []
        for image in self.images:
            datatype = PlnMDataType.from_data(image)
            assert datatype.renderable
            renders.append(Image.fromarray(image, datatype.typed_name))

        return renders

    @classmethod
    def from_gltf2(cls, gltf_file: GLTFFile) -> PlnM:
        """'Get plaintext from GLTFFile"""
        accessors = [accessor for accessor in gltf_file.data.accessors.values()]
        images = [np.asarray(image) for image in gltf_file.data.images.values()]
        return cls(
            meshes=accessors,
            images=images,
            meshes_dim=len(accessors),
            images_dim=len(images),
        )

    def to_gltf2(self, gltf_file: GLTFFile) -> GLTFFile:
        """Insert plaintext in GLTFFile
        assumes the plaintext data came from the same GLTFFile"""

        gltf_file.data.accessors = {i: self.meshes[i] for i in range(self.meshes_dim)}
        gltf_file.data.images = {
            i: Image.fromarray(self.images[i]) for i in range(self.images_dim)
        }
        return gltf_file

    @classmethod
    def from_off(cls, off_file: OffFile) -> PlnM:
        """'Get plaintext from OffFile"""

        verts, faces, colors = (
            off_file.data.verts,
            off_file.data.faces,
            off_file.data.colors,
        )
        return cls(meshes=[verts, faces, colors], images=[], meshes_dim=3, images_dim=0)

    def to_off(self, off_file: OffFile) -> OffFile:
        """Insert plaintext in OffFile
        assumes the plaintext data came from the same OffFile"""

        off_file.data.verts = self.meshes[0]
        off_file.data.faces = self.meshes[1]
        off_file.data.colors = self.meshes[2]

        return off_file

    @classmethod
    def from_images(cls, images: list[Image.Image]) -> PlnM:
        """'Get plaintext from list of images"""

        img_arrays = [np.asarray(image) for image in images]
        return cls(meshes=[], images=img_arrays, meshes_dim=0, images_dim=len(images))
    
    
