import json
import os
from math import sqrt
from pathlib import Path

import matplotlib
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

PAPER_DIR = (
    Path(__file__).parent.parent.parent.parent.resolve() / "assets" / "paper_figs"
)

print(dict)
dicts = [
    {
        "name": "sand_pit.glb",
        "1_gen": 1.2337229879831297,
        "2_gen": 1.319106780657508,
        "3_gen": 1.3260518957378773,
        "4_gen": 1.34511429188045,
        "5_gen": 1.35435953655922,
    },
    {
        "name": "astronaut.glb",
        "1_gen": 0.2371519401647864,
        "2_gen": 0.2487028578449294,
        "3_gen": 0.2569943619510754,
        "4_gen": 0.2514103395491467,
        "5_gen": 0.25307362957917545,
    },
    {
        "name": "honda.glb",
        "1_gen": 3.947738152963809,
        "2_gen": 4.30759824645676,
        "3_gen": 4.370014749657662,
        "4_gen": 4.374419951923075,
        "5_gen": 4.301412711019624,
    },
    {
        "name": "dog.glb",
        "1_gen": 0.06510394089523554,
        "2_gen": 0.07881839893049458,
        "3_gen": 0.08374852775992818,
        "4_gen": 0.08441415254016874,
        "5_gen": 0.08501235395047467,
    },
    {
        "name": "Apple.off",
        "1_gen": 0.042649702781056405,
        "2_gen": 0.042541774848370996,
        "3_gen": 0.043008892614529386,
        "4_gen": 0.042660949762382924,
        "5_gen": 0.04221135746233675,
    },
    {
        "name": "maple_tree.glb",
        "1_gen": 2074.9360530929066,
        "2_gen": 2127.8979658725034,
        "3_gen": 1887.823290677102,
        "4_gen": 2236.2639703134632,
        "5_gen": 2022.1051525390683,
    },
    {
        "name": "space_station.off",
        "1_gen": 0.00029049711959186594,
        "2_gen": 0.00029638739697714675,
        "3_gen": 0.00029490172259327593,
        "4_gen": 0.0002965738261718677,
        "5_gen": 0.0002957370806632715,
    },
    {
        "name": "food_can_415g.gltf",
        "1_gen": 0.11944026620219132,
        "2_gen": 0.15181418932033916,
        "3_gen": 0.16101655616528596,
        "4_gen": 0.1619131127511107,
        "5_gen": 0.16259261552673074,
    },
    {
        "name": "rustic_chair.gltf",
        "1_gen": 0.12990608174748258,
        "2_gen": 0.1490475698207312,
        "3_gen": 0.1552578964654283,
        "4_gen": 0.15561102008045052,
        "5_gen": 0.15775972617092537,
    },
    {
        "name": "autumn_house.gltf",
        "1_gen": 145.91102194629372,
        "2_gen": 149.6115217655168,
        "3_gen": 157.25151325041094,
        "4_gen": 146.13831204351936,
        "5_gen": 162.50606412142773,
    },
]
import matplotlib.pyplot as plt

yvals = [np.array([x for x in dic.values() if isinstance(x, float)]) for dic in dicts]
yvals = [np.concatenate(([0], y / max(y))) for y in yvals]

xvals = [0, 1, 2, 3, 4, 5]

for idx, y in enumerate(yvals):
    plt.plot(xvals, y, label=dicts[idx]["name"])

import matplotlib

# plt.ion()
plt.ylabel("Normaliszed RMSE")
plt.xlabel("Generations")
plt.legend()
plt.show()
print()
