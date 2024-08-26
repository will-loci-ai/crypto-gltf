from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict


class CACipherParams(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    gens: int
    ps: list[int]
    idl_points: np.ndarray = np.empty(0, dtype=int)

    def validate_idl_points(self, dim: int) -> None:
        # use default idl points if undefined
        if len(self.idl_points) == 0:
            self.idl_points = np.zeros((dim, 2), dtype=int)
        if len(self.idl_points) != dim:
            raise Exception(f"Number of plaintext matrices != number of idl points")


class CABaseModel:
    """Base model for Conways game of life cellular automata encryption/decryption model"""

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f"{cls} should not be instantiated")

    @staticmethod
    def get_nonzero_idxs(
        expCA: np.ndarray, mat: np.ndarray, idl: tuple[int, int]
    ) -> np.ndarray:
        """Get flattened indices of non-zero expCA cells"""

        row_idxs = np.arange(idl[0], idl[0] + mat.shape[0]) % expCA.shape[0]
        col_idxs = np.arange(idl[1], idl[1] + mat.shape[1]) % expCA.shape[1]

        covered_expCA = expCA[np.ix_(row_idxs, col_idxs)]
        flat_covered_expCA = covered_expCA.flatten()
        nonzero_elts_flat_idxs = np.nonzero(flat_covered_expCA)[0]

        return nonzero_elts_flat_idxs

    @staticmethod
    def get_zero_idxs(
        nonzero_elts_flat_idxs: np.ndarray, mat: np.ndarray
    ) -> np.ndarray:
        """Get flattened indices of zero expCA cells"""

        zero_elts_flat_idxs = np.setdiff1d(np.arange(mat.size), nonzero_elts_flat_idxs)
        if len(zero_elts_flat_idxs) + len(nonzero_elts_flat_idxs) != mat.size:
            raise Exception(
                f"Mismatched confused/resolved matrix and covered expCA ndarray sizes: \
                        {len(zero_elts_flat_idxs) + len(nonzero_elts_flat_idxs)} != {mat.size}"
            )
        return zero_elts_flat_idxs
