from __future__ import annotations

from time import sleep
from typing import Sequence

import numpy as np
from cellular_automaton import CellularAutomaton, EdgeRule, MooreNeighborhood
from loguru import logger
from py_code.data.base_data import PlnM
from py_code.data.params import RANDOM_VARIANCE

ALIVE = [1]
DEAD = [0]


from pydantic import BaseModel, ConfigDict


class ConwaysCA(CellularAutomaton):
    """Cellular automaton with the evolution rules of conways game of life"""

    def __init__(self, dimension: tuple[int, int] = (100, 100)) -> None:
        super().__init__(
            dimension=dimension,
            neighborhood=MooreNeighborhood(
                EdgeRule.FIRST_AND_LAST_CELL_OF_DIMENSION_ARE_NEIGHBORS
            ),
        )

    def init_cell_state(self, __) -> Sequence:
        return [np.random.choice([0, 1])]

    def evolve_rule(self, last_cell_state, neighbors_last_states) -> Sequence:
        """Cellular automaton generation evolution rule"""
        new_cell_state = last_cell_state
        alive_neighbours = self.__count_alive_neighbours(neighbors_last_states)
        if last_cell_state == DEAD and alive_neighbours == 3:
            new_cell_state = ALIVE
        if last_cell_state == ALIVE and alive_neighbours < 2:
            new_cell_state = DEAD
        if last_cell_state == ALIVE and 1 < alive_neighbours < 4:
            new_cell_state = ALIVE
        if last_cell_state == ALIVE and alive_neighbours > 3:
            new_cell_state = DEAD
        return new_cell_state

    @staticmethod
    def __count_alive_neighbours(neighbours) -> int:
        """Count cell alive neighbours"""
        alive_neighbors = []
        for n in neighbours:
            if n == ALIVE:
                alive_neighbors.append(1)
        return len(alive_neighbors)


class ExpConwaysHCA(ConwaysCA):
    """Expanded hybrid cellular automata with the evolution rules of conways game of life"""

    expHCA: np.ndarray

    def __init__(
        self,
        dimension: tuple[int, int] = (100, 100),
    ) -> None:
        super().__init__(dimension=dimension)
        self.expHCA = np.reshape(
            self.ca_as_np_array, (1, self.dimension[0], self.dimension[1])
        )

    def insert_ps(self) -> None:
        """Insert a bogus bits generation"""
        np.append(
            self.expHCA,
            np.random.choice([0, 1], size=(self.dimension[0], self.dimension[1], 1)),
        )

    def diffuse(self) -> None:
        """Run a diffusion generation"""
        self.evolve()
        self.expHCA = np.vstack((self.expHCA, np.array([self.ca_as_np_array])))

    @property
    def ca_as_np_array(self) -> np.ndarray:
        """Get ca in np array format"""
        return np.array([cell.state for cell in self.get_cells().values()]).reshape(
            self.dimension
        )


class EncryptionExpConwaysCA(BaseModel):
    """Conways game of life cellular automata encryption model"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    expHCA: ExpConwaysHCA
    plnm: PlnM  # Data
    idl_points: np.ndarray
    gens: int
    ps: list[int]
    img_dtype: np.dtype | None = None

    @classmethod
    def from_pre_encryption(
        cls,
        plnm: PlnM,
        idl_points: list[tuple[int, int]],
        gens: int,
        ps: list[int],
        random_seed: int = 0,
    ) -> EncryptionExpConwaysCA:
        """Initialise class using pre-encryption steps"""
        if random_seed:
            logger.info(f"Setting random seed = {random_seed}")
            np.random.seed(random_seed)

        if len(idl_points) != len(plnm.data):
            raise Exception(f"Number of plaintext matrices != number of idl points")

        mat_shapes = np.array([mat.shape for mat in plnm.data])
        r, c = max(mat_shapes[..., 0]), max(mat_shapes[..., 1])
        n1, n2 = np.random.randint(0, RANDOM_VARIANCE, 2)  # ExpCA expansion values
        dimension = (r + n1, c + n2)
        logger.info(f"Using CA dimension {dimension}")
        expHCA = ExpConwaysHCA(dimension=dimension)
        idl_points_arr = np.array(idl_points)
        return cls(
            expHCA=expHCA,
            plnm=plnm,
            idl_points=idl_points_arr,
            gens=gens,
            ps=ps,
        )

    def encrypt(self, demonstrate: bool = False) -> PlnM:
        """Encrypt data"""
        for i in range(self.gens):
            if demonstrate:
                self.plnm.image.show()
            logger.info(f"Calculating generation {i+1}")
            if i in self.ps:
                self.expHCA.insert_ps()
            self.expHCA.diffuse()
            self.confuse_all_pt_matrices()
        return self.plnm

    def decrypt(self, demonstrate: bool = False) -> PlnM:
        """ "Decrypt data"""
        for i in range(self.gens, 0, -1):
            if i in self.ps:
                continue
            else:
                self.resolve_all_ct_matrices(expCA=self.expHCA.expHCA[i])
                if demonstrate:
                    self.plnm.image.show()
                    sleep(1)

        return self.plnm

    def resolve_all_ct_matrices(self, expCA: np.ndarray) -> None:
        """Inverse of confuse_all_pt_matrices: resolve all cipher text matrices.
        Conducts one resolve step"""
        self.plnm.data = [
            EncryptionExpConwaysCA.resolve_single_ct_matrix(
                expCA=expCA, encrypted_text=mat, idl=idl
            )
            for mat, idl in zip(self.plnm.data, self.idl_points)
        ]

    def confuse_all_pt_matrices(self) -> None:
        """Confuse all plaintext matrices, conducts a single confuse step"""
        expCA = self.expHCA.ca_as_np_array
        self.plnm.data = [
            EncryptionExpConwaysCA.confuse_single_pt_matrix(
                expCA=expCA, plain_text=mat, idl=idl
            )
            for mat, idl in zip(self.plnm.data, self.idl_points)
        ]

    @staticmethod
    def resolve_single_ct_matrix(
        expCA: np.ndarray,
        encrypted_text: np.ndarray,
        idl: tuple[int, int] = (0, 0),
    ) -> np.ndarray:
        """Resolve a single ciphertext matrix one step"""
        flat_encrypted_text = encrypted_text.flatten()

        nonzero_elts_flat_idxs = EncryptionExpConwaysCA.get_nonzero_idxs(
            expCA=expCA, mat=encrypted_text, idl=idl
        )
        zero_elts_flat_idxs = EncryptionExpConwaysCA.get_zero_idxs(
            nonzero_elts_flat_idxs=nonzero_elts_flat_idxs, mat=encrypted_text
        )

        return np.concatenate(
            (
                np.take(flat_encrypted_text, nonzero_elts_flat_idxs),
                np.take(flat_encrypted_text, zero_elts_flat_idxs),
            )
        ).reshape(encrypted_text.shape)

    @staticmethod
    def confuse_single_pt_matrix(
        expCA: np.ndarray, plain_text: np.ndarray, idl: tuple[int, int] = (0, 0)
    ) -> np.ndarray:
        """Confuse a single plaintext matrix. One confusion step"""
        confused_mat = np.zeros(plain_text.shape, int)
        flat_plaintext = plain_text.flatten()

        nonzero_elts_flat_idxs = EncryptionExpConwaysCA.get_nonzero_idxs(
            expCA=expCA, mat=plain_text, idl=idl
        )
        zero_elts_flat_idxs = EncryptionExpConwaysCA.get_zero_idxs(
            nonzero_elts_flat_idxs=nonzero_elts_flat_idxs, mat=plain_text
        )

        confused_mat.put(
            nonzero_elts_flat_idxs,
            flat_plaintext[: len(nonzero_elts_flat_idxs)],
        )
        confused_mat.put(
            zero_elts_flat_idxs,
            flat_plaintext[len(nonzero_elts_flat_idxs) :],
        )

        return confused_mat

    @staticmethod
    def get_nonzero_idxs(
        expCA: np.ndarray, mat: np.ndarray, idl: tuple[int, int] = (0, 0)
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
