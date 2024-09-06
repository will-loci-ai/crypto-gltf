from __future__ import annotations

import numpy as np
from crypto_gltf.encrypt.deprecit.ca.base import CABaseModel, CACipherParams
from crypto_gltf.encrypt.deprecit.ca.ca import ExpConwaysHCA
from loguru import logger


class CAEncryptionModel(CABaseModel):
    """Conways game of life cellular automata encryption model"""

    @staticmethod
    def compute_gens(
        expHCA: ExpConwaysHCA, cipher_params: CACipherParams
    ) -> ExpConwaysHCA:
        """Encrypt data"""

        for i in range(cipher_params.gens - 1):
            logger.info(f"Calculating generation {i+1}")
            if i in cipher_params.ps:
                expHCA.insert_ps()
            else:
                expHCA.diffuse()

        return expHCA

    @staticmethod
    def encrypt(
        plain_text: list[np.ndarray],
        expHCA: ExpConwaysHCA,
        cipher_params: CACipherParams,
    ) -> list[np.ndarray]:
        """Encrypt data"""
        for i in range(cipher_params.gens):
            if i in cipher_params.ps:
                continue
            else:
                plain_text = CAEncryptionModel.confuse_all_pt_matrices(
                    plain_text=plain_text,
                    expCA=expHCA.expHCA[i],
                    idl_points=cipher_params.idl_points,
                )
        return plain_text

    @staticmethod
    def confuse_all_pt_matrices(
        plain_text: list[np.ndarray],
        expCA: np.ndarray,
        idl_points: np.ndarray,
    ) -> list[np.ndarray]:
        """Confuse all plaintext matrices, conducts a single confuse step"""
        confused_data = [
            CAEncryptionModel.confuse_single_pt_matrix(
                expCA=expCA, plain_text=mat, idl=idl
            )
            for mat, idl in zip(plain_text, idl_points)
        ]
        return confused_data

    @staticmethod
    def confuse_single_pt_matrix(
        expCA: np.ndarray, plain_text: np.ndarray, idl: tuple[int, int]
    ) -> np.ndarray:
        """Confuse a single plain_text matrix. One confusion step.
        Split into 2D matrices and send to confuse_2d_matrix"""

        shape = plain_text.shape
        dims = len(shape)
        match dims:
            case 0:
                return plain_text
            case 1:
                return plain_text
            case 2:
                return CAEncryptionModel.confuse_2d_matrix(
                    expCA=expCA, plain_text=plain_text, idl=idl
                )
            case 3:
                confused_mat = np.empty(shape, dtype=plain_text.dtype)
                for i in range(shape[-1]):
                    confused_mat[:, :, i] = CAEncryptionModel.confuse_2d_matrix(
                        expCA=expCA, plain_text=plain_text[:, :, i], idl=idl
                    )
                return confused_mat
            case _:
                raise Exception(
                    f"Matrix has too many dimensions: {dims}, for CA encryptioon"
                )

    @staticmethod
    def confuse_2d_matrix(
        expCA: np.ndarray, plain_text: np.ndarray, idl: tuple[int, int]
    ) -> np.ndarray:
        """Confuse a single 2D plain_text matrix. One confusion step"""
        if plain_text.size == 0:
            return plain_text
        confused_mat = np.zeros(plain_text.shape, dtype=plain_text.dtype)
        flat_plain_text = plain_text.flatten()

        nonzero_elts_flat_idxs = CAEncryptionModel.get_nonzero_idxs(
            expCA=expCA, mat=plain_text, idl=idl
        )
        zero_elts_flat_idxs = CAEncryptionModel.get_zero_idxs(
            nonzero_elts_flat_idxs=nonzero_elts_flat_idxs, mat=plain_text
        )

        confused_mat.put(
            nonzero_elts_flat_idxs,
            flat_plain_text[: len(nonzero_elts_flat_idxs)],
        )
        confused_mat.put(
            zero_elts_flat_idxs,
            flat_plain_text[len(nonzero_elts_flat_idxs) :],
        )

        return confused_mat
