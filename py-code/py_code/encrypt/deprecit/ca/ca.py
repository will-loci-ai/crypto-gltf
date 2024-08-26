from __future__ import annotations

from time import sleep
from typing import Sequence

import numpy as np
from cellular_automaton import CellularAutomaton, EdgeRule, MooreNeighborhood

ALIVE = [1]
DEAD = [0]


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
