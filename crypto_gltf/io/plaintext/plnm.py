from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from crypto_gltf.data.types import PlnMDataType
from crypto_gltf.io.plaintext.base_plaintext import BasePlainText
from PIL import Image


@dataclass
class PlnM(BasePlainText):
    """Plaintext data class for multi matrix 3D asset attributes (colors, meshes etc.)"""

    meshes: list[np.ndarray]
    images: list[np.ndarray]

    def __eq__(self, plnm: PlnM) -> bool:
        if (self.meshes_dim != plnm.meshes_dim) or (self.images_dim != plnm.images_dim):
            return False
        meshes_eq = all(
            [np.allclose(arr1, arr2) for arr1, arr2 in zip(self.meshes, plnm.meshes)]
        )  # allclose to account for type conversions to np.float32
        images_eq = all(
            [np.allclose(arr1, arr2, 3) for arr1, arr2 in zip(self.images, plnm.images)]
        ) # allclose as jpeg compression sometimes alters the image
        return meshes_eq and images_eq

    def __copy__(self):
        return PlnM(
            meshes=[np.copy(arr) for arr in self.meshes],
            images=[np.copy(arr) for arr in self.images],
            meshes_dim=self.meshes_dim,
            images_dim=self.images_dim,
        )

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
    def from_images(cls, images: list[Image.Image]) -> PlnM:
        """'Get plaintext from list of images"""

        img_arrays = [np.asarray(image) for image in images]
        return cls(meshes=[], images=img_arrays, meshes_dim=0, images_dim=len(images))
