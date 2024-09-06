from __future__ import annotations

import numpy as np
from crypto_gltf.encrypt.deprecit.ca.base import CABaseModel, CACipherParams
from crypto_gltf.encrypt.deprecit.ca.ca import ExpConwaysHCA


class CADecryptionModel(CABaseModel):
    """Conways game of life cellular automata encryption model"""

    @staticmethod
    def decrypt(
        cipher_text: list[np.ndarray],
        expHCA: ExpConwaysHCA,
        cipher_params: CACipherParams,
    ) -> list[np.ndarray]:
        """Decrypt cipher text"""
        for i in range(cipher_params.gens - 1, -1, -1):

            if i in cipher_params.ps:
                continue
            else:
                cipher_text = CADecryptionModel.resolve_all_ct_matrices(
                    cipher_text=cipher_text,
                    expCA=expHCA.expHCA[i],
                    idl_points=cipher_params.idl_points,
                )

        return cipher_text

    @staticmethod
    def resolve_all_ct_matrices(
        cipher_text: list[np.ndarray],
        expCA: np.ndarray,
        idl_points: np.ndarray,
    ) -> list[np.ndarray]:
        """Inverse of confuse_all_pt_matrices: resolve all cipher text matrices.
        Conducts one resolve step"""
        resolved_data = [
            CADecryptionModel.resolve_single_ct_matrix(
                expCA=expCA, encrypted_text=mat, idl=idl
            )
            for mat, idl in zip(cipher_text, idl_points)
        ]
        return resolved_data

    @staticmethod
    def resolve_single_ct_matrix(
        expCA: np.ndarray, encrypted_text: np.ndarray, idl: tuple[int, int]
    ) -> np.ndarray:
        """Resolve a single ciphertext matrix one step.
        Split into 2D matrices and send to resolve_2d_matrix"""

        shape = encrypted_text.shape
        dims = len(shape)
        match dims:
            case 0:
                return encrypted_text
            case 1:
                return encrypted_text
            case 2:
                return CADecryptionModel.resolve_2d_matrix(
                    expCA=expCA, encrypted_text=encrypted_text, idl=idl
                )
            case 3:
                resolved_mat = np.empty(shape, dtype=encrypted_text.dtype)
                for i in range(shape[2]):
                    resolved_mat[:, :, i] = CADecryptionModel.resolve_2d_matrix(
                        expCA=expCA, encrypted_text=encrypted_text[:, :, i], idl=idl
                    )
                return resolved_mat
            case _:
                raise Exception(
                    f"Matrix has too many dimensions: {dims}, for CA encryptioon"
                )

    @staticmethod
    def resolve_2d_matrix(
        expCA: np.ndarray,
        encrypted_text: np.ndarray,
        idl: tuple[int, int],
    ) -> np.ndarray:
        """Resolve a single 2D ciphertext matrix one step"""
        if encrypted_text.size == 0:
            return encrypted_text
        flat_encrypted_text = encrypted_text.flatten()

        nonzero_elts_flat_idxs = CADecryptionModel.get_nonzero_idxs(
            expCA=expCA, mat=encrypted_text, idl=idl
        )
        zero_elts_flat_idxs = CADecryptionModel.get_zero_idxs(
            nonzero_elts_flat_idxs=nonzero_elts_flat_idxs, mat=encrypted_text
        )

        return np.concatenate(
            (
                np.take(flat_encrypted_text, nonzero_elts_flat_idxs),
                np.take(flat_encrypted_text, zero_elts_flat_idxs),
            )
        ).reshape(encrypted_text.shape)
