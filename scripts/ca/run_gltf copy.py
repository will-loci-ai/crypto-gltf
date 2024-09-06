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
    paper_figs_paths, PAPER_ASSETS_DIR, princeton_assets
)
from sklearn.metrics import mean_squared_error


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
if __name__ == "__main__":

    # glTF file encryption

    for idx, filepath in enumerate(paths[4 + 3 + 2 :]):
        asset = Asset.load(filepath)
        # asset.file.render.show()
        plnm = asset.file.plnm
        plnm_cpy = plnm.__copy__()
        plain_path = PAPER_DIR / f"plain_figs/{asset.file.filename}.png"
        gen1_ca = PAPER_DIR / f"gen1_ca/{asset.file.filename}.png"
        gen2_ca = PAPER_DIR / f"gen2_ca/{asset.file.filename}.png"
        gen5_ca = PAPER_DIR / f"gen5_ca/{asset.file.filename}.png"
        gens = [1, 2, 3, 4, 5]

        j = {"name": filepath}

        # asset.file.render.save(plain_path)

        for gen in gens:
            dir = PAPER_DIR / f"gen{gen}_ca"
            # Path.mkdir(dir, exist_ok=True)

            meshes_cipher_params = CACipherParams(gens=gen, ps=[])
            images_cipher_params = CACipherParams(gens=gen, ps=[])

            encryption = CACryptoSystem.from_pre_encryption(
                plnm=plnm,
                meshes_cipher_params=meshes_cipher_params,
                images_cipher_params=images_cipher_params,
                random_seed=42,
            )
            encryption.compute_generations()

            encryption.encrypt()

            j[f"{gen}_gen"] = rmse(plnm_cpy.meshes, encryption.plnm.meshes)

            # asset.file.insert_plnm(encryption.plnm)
            # # asset.file.render.save(dir / f"{asset.file.filename}.png")

            # encryption.decrypt()

            # asset.file.insert_plnm(encryption.plnm)
        dict.append(j)
        with open("data.json", "w") as f:
            json.dump(dict, f)


print(dict)
dicts = [
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/sand_pit.glb",
        "1_gen": 1.2337229879831297,
        "2_gen": 1.319106780657508,
        "3_gen": 1.3260518957378773,
        "4_gen": 1.34511429188045,
        "5_gen": 1.35435953655922,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/astronaut.glb",
        "1_gen": 0.2371519401647864,
        "2_gen": 0.2487028578449294,
        "3_gen": 0.2569943619510754,
        "4_gen": 0.2514103395491467,
        "5_gen": 0.25307362957917545,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/honda.glb",
        "1_gen": 3.947738152963809,
        "2_gen": 4.30759824645676,
        "3_gen": 4.370014749657662,
        "4_gen": 4.374419951923075,
        "5_gen": 4.301412711019624,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/dog.glb",
        "1_gen": 0.06510394089523554,
        "2_gen": 0.07881839893049458,
        "3_gen": 0.08374852775992818,
        "4_gen": 0.08441415254016874,
        "5_gen": 0.08501235395047467,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/Apple.off",
        "1_gen": 0.042649702781056405,
        "2_gen": 0.042541774848370996,
        "3_gen": 0.043008892614529386,
        "4_gen": 0.042660949762382924,
        "5_gen": 0.04221135746233675,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/maple_tree.glb",
        "1_gen": 2074.9360530929066,
        "2_gen": 2127.8979658725034,
        "3_gen": 1887.823290677102,
        "4_gen": 2236.2639703134632,
        "5_gen": 2022.1051525390683,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/space_station.off",
        "1_gen": 0.00029049711959186594,
        "2_gen": 0.00029638739697714675,
        "3_gen": 0.00029490172259327593,
        "4_gen": 0.0002965738261718677,
        "5_gen": 0.0002957370806632715,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/food_can_415g/food_can_415g.gltf",
        "1_gen": 0.11944026620219132,
        "2_gen": 0.15181418932033916,
        "3_gen": 0.16101655616528596,
        "4_gen": 0.1619131127511107,
        "5_gen": 0.16259261552673074,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/rustic_chair/rustic_chair.gltf",
        "1_gen": 0.12990608174748258,
        "2_gen": 0.1490475698207312,
        "3_gen": 0.1552578964654283,
        "4_gen": 0.15561102008045052,
        "5_gen": 0.15775972617092537,
    },
    {
        "name": "/home/will/stage2/assets/paper_figs/assets/autumn_house/autumn_house.gltf",
        "1_gen": 145.91102194629372,
        "2_gen": 149.6115217655168,
        "3_gen": 157.25151325041094,
        "4_gen": 146.13831204351936,
        "5_gen": 162.50606412142773,
    },
]
