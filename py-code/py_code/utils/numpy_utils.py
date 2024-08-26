from typing import Literal

import numpy as np

stack_dict = {"HEIGHT": 0, "WIDTH": 1, "DEPTH": 2}


def split_array_stack(
    stacked_data: np.ndarray,
    stacktype: Literal["HEIGHT", "WIDTH", "DEPTH"],
) -> list[np.ndarray]:
    """split numpy array stack by height, width or depth"""

    dim = stacked_data.shape[stack_dict[stacktype]]

    splits = np.split(
        ary=stacked_data,
        indices_or_sections=dim,
        axis=stack_dict[stacktype],
    )
    return [arr.reshape(arr.shape[0], arr.shape[1]) for arr in splits]


