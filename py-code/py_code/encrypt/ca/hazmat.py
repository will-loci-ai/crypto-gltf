from __future__ import annotations

import numpy as np
from loguru import logger
from py_code.encrypt.ca.base import CACipherParams
from py_code.encrypt.ca.ca import ExpConwaysHCA
from py_code.encrypt.ca.decrypt import CADecryptionModel
from py_code.encrypt.ca.encrypt import CAEncryptionModel
from py_code.encrypt.params import RANDOM_VARIANCE
from py_code.io.plaintext.plnm import PlnM
from pydantic import BaseModel, ConfigDict


class CACipherSystem(BaseModel):
    """Conways game of life cellular automata cipher system"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    plnm: PlnM  # Data

    meshes_expHCA: ExpConwaysHCA
    images_expHCA: ExpConwaysHCA

    meshes_cipher_params: CACipherParams
    images_cipher_params: CACipherParams

    generations_computed: bool = False

    @classmethod
    def from_pre_encryption(
        cls,
        plnm: PlnM,
        meshes_cipher_params: CACipherParams,
        images_cipher_params: CACipherParams,
        random_seed: int = 0,
    ) -> CACipherSystem:
        """Initialise class using pre-encryption steps"""
        if random_seed:
            logger.info(f"Setting random seed = {random_seed}")
            np.random.seed(random_seed)

        meshes_cipher_params.validate_idl_points(plnm.meshes_dim)
        images_cipher_params.validate_idl_points(plnm.images_dim)

        meshes_expHCA = ExpConwaysHCA(
            dimension=CACipherSystem.get_expHCA_dimension(plnm.meshes)
        )
        images_expHCA = ExpConwaysHCA(
            dimension=CACipherSystem.get_expHCA_dimension(plnm.images)
        )

        return cls(
            plnm=plnm,
            meshes_expHCA=meshes_expHCA,
            images_expHCA=images_expHCA,
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
        )

    @staticmethod
    def get_expHCA_dimension(data: list[np.ndarray]) -> tuple[int, int]:
        """Get expHCA dimensions from data and random variance"""
        if len(data) == 0:
            return (0, 0)
        mat_shapes = np.zeros((len(data), 3), dtype=int)
        for idx, mat in enumerate(data):
            shape = mat.shape
            mat_shapes[idx][: len(shape)] = shape

        r, c = max(mat_shapes[..., 0]), max(
            mat_shapes[..., 1]
        )  # max row and column numbers in list
        n1, n2 = np.random.randint(0, RANDOM_VARIANCE, 2)  # ExpCA expansion values
        dimension = (r + n1, c + n2)
        logger.info(f"Using CA dimension {dimension}")
        return dimension

    def compute_generations(self):
        """Compute expHCA generations for mesh and image automatas"""
        self.meshes_expHCA = CAEncryptionModel.compute_gens(
            expHCA=self.meshes_expHCA, cipher_params=self.meshes_cipher_params
        )
        self.images_expHCA = CAEncryptionModel.compute_gens(
            expHCA=self.images_expHCA, cipher_params=self.images_cipher_params
        )
        self.generations_computed = True

    def encrypt(self):
        """Encrypt all meshes and images"""
        if not self.generations_computed:
            raise Exception("Generations not yet computed")
        self.plnm.meshes = CAEncryptionModel.encrypt(
            plain_text=self.plnm.meshes,
            expHCA=self.meshes_expHCA,
            cipher_params=self.meshes_cipher_params,
        )
        self.plnm.images = CAEncryptionModel.encrypt(
            plain_text=self.plnm.images,
            expHCA=self.images_expHCA,
            cipher_params=self.images_cipher_params,
        )

    def decrypt(self):
        """Decrypt all meshes and images"""
        if not self.generations_computed:
            raise Exception("Generations not yet computed")
        self.plnm.meshes = CADecryptionModel.decrypt(
            cipher_text=self.plnm.meshes,
            expHCA=self.meshes_expHCA,
            cipher_params=self.meshes_cipher_params,
        )
        self.plnm.images = CADecryptionModel.decrypt(
            cipher_text=self.plnm.images,
            expHCA=self.images_expHCA,
            cipher_params=self.images_cipher_params,
        )
