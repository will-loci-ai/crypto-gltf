import json
import os
from math import sqrt
from pathlib import Path

import numpy as np
from crypto_gltf import Asset
from crypto_gltf.encrypt.deprecit.ca.base import CACipherParams
from crypto_gltf.encrypt.deprecit.ca.system import CACryptoSystem
from crypto_gltf.io.file.gltf2.gltf2 import GLTFFile
from crypto_gltf.io.plaintext.plnm import PlnM
from crypto_gltf.local_tests.local_paths import (
    asset_paths,
    loci_assets,
    paper_figs_paths,
)
from sklearn.metrics import mean_squared_error

PAPER_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "paper_figs"
)

chosen_assets = loci_assets[:10]

chosen_assets = [
    "/home/will/stage/assets/import/Apple.off"
    "/home/will/stage/assets/import/rustic_chair/rustic_chair.gltf",
    "/home/will/stage/assets/import/sand_pit.glb",
    "/home/will/stage/assets/import/honda.glb",
    "/home/will/stage/assets/import/maple_tree.glb",
    "/home/will/stage/assets/import/rustic_chair.glb",
    "/home/will/stage/assets/import/food_can_415.g/food_can_415.g.gltf",
    "/home/will/stage/assets/import/astronaut.glb",
    "/home/will/stage/assets/import/dog_puppy.glb",
    "/home/will/stage/assets/import/autumn_house.glb",
    "/home/will/stage/assets/import/phone.glb",
]
# assets =
paths = paper_figs_paths
print(paths)

# paths = [
#     # "/home/will/stage2/assets/paper_figs/assets/plane.off",
#     # "/home/will/stage2/assets/paper_figs/assets/astronaut.glb",
#     # "/home/will/stage2/assets/paper_figs/assets/dog.glb",
#     "/home/will/stage2/assets/paper_figs/assets/maple_tree.glb",
# ]


def rmse_vec(vec1, vec2):
    try:
        rms = sqrt(mean_squared_error(vec1, vec2))
        return rms
    except:
        return 0


rmse_vec(np.arange(9).reshape((3, 3)), np.zeros((3, 3)))


def rmse(l: list[np.ndarray], m: list[np.ndarray]) -> float:

    total = 0
    for arr1, arr2 in zip(l, m):
        try:
            total += rmse_vec(arr1, arr2) / arr1.size
        except:
            pass
    return total


dict = []
flt = 0
non_flt = 0
if __name__ == "__main__":

    # glTF file encryption

    for idx, filepath in enumerate(paths):
        asset = Asset.load(filepath)
        # asset.file.render.show()
        plnm = asset.file.plnm
        asset_flt = 0
        asset_non_flt = 0

        for mesh in plnm.meshes:
            if mesh.dtype.kind == "f":
                asset_flt += mesh.size
            else:
                asset_non_flt += mesh.size
        
        flt += asset_flt/(asset_flt + asset_non_flt)

print(paths)
print(100*flt/10)