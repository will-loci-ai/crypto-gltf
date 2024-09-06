import json
from math import dist, sqrt
from tempfile import TemporaryDirectory
from time import time

import numpy as np
from crypto_gltf import Asset
from crypto_gltf.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    MeshesAdaptiveCipherParams,
)
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import AdaptiveCipherParamsV2, Key
from crypto_gltf.local_tests.local_paths import (
    glb_assets,
    gltf_assets,
    loci_assets,
    off_assets,
    paper_figs_paths,
    princeton_assets,
    xl_paths,
)
from sklearn.metrics import mean_squared_error
from tqdm import tqdm

timings = [
    "import",
    "export",
    "encrypt",
    "decrypt",
    "encrypt_bit",
    "decrypt_bit",
    "encrypt_keygen",
    "decrypt_keygen",
    "encrypt_crypto",
    "decrypt_crypto",
    "successes",
    "failures",
]
timing = {val: 0 for val in timings}
timing["failures"] = []


def rmse_vec(vec1, vec2):
    shape = vec1.shape
    # try:
    rms = 0
    if len(shape) == 1:
        rms = dist(vec1, vec2) ** 2
        return rms, 1
    elif len(shape) == 2:
        rms = sum([dist(vec1, vec2) ** 2 for vec1, vec2 in zip(vec1, vec2)])

        return rms, shape[0]
    elif len(shape) == 3:

        rms = sum(
            [
                dist(vec1[i][j], vec2[i][j]) ** 2
                for i, j in zip(range(shape[0]), shape[1])
            ]
        )
        return rms, shape[0] * shape[1]
    else:
        return 0, 0
    # except:
    #     return 0


def rmse(l: list[np.ndarray], m: list[np.ndarray]) -> float:

    total = 0
    count = 0
    for arr1, arr2 in zip(l, m):
        # try:
        if arr1.size:
            tot, cou = rmse_vec(arr1, arr2)
            total += tot
            count += cou
        # except:
        #     pass
    return sqrt(total / count)

np.random.seed(42)
idxs = np.random.randint(0, len(xl_paths), 100)
dict = {"high": 0, "mid": 0, "low": 0, "used": 0}


with open("timing.json", "r") as f:
    timing = json.load(f)

with open("data.json", "r") as f:
    dict = json.load(f)

for idx in tqdm(idxs):
    # try:
        filepath = xl_paths[idx]
        tic = time()
        asset = Asset.load(filepath)
        timing["import"] += time() - tic

        with TemporaryDirectory() as tmp_dir:
            plnm_plaintext = asset.file.plnm.__copy__()
            meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=2, r=10)
            images_cipher_params = ImagesAdaptiveCipherParams(p=2, q=1, r=5)
            encryption_response, timing = asset.encrypt(
                meshes_cipher_params=meshes_cipher_params,
                images_cipher_params=images_cipher_params,
                timing=timing,
            )
            high = rmse(plnm_plaintext.meshes, encryption_response.ciphertext.meshes)
            tic = time()
            export = asset.save(tmp_dir)
            timing["export"] += time() - tic

            tic = time()
            encrypted = Asset.load(export)
            timing["import"] += time() - tic

            bool_val, timing = encrypted.decrypt(
                timing=timing, key=Key(k1=encryption_response.key.k1)
            )
            mid = rmse(plnm_plaintext.meshes, encrypted.file.plnm.meshes)

            tic = time()
            encrypted = Asset.load(export)
            timing["import"] += time() - tic
            bool_val, timing = encrypted.decrypt(
                timing=timing, key=Key(k2=encryption_response.key.k2)
            )
            low = rmse(plnm_plaintext.meshes, encrypted.file.plnm.meshes)

            tic = time()
            encrypted = Asset.load(export)
            timing["import"] += time() - tic
            bool_val, timing = encrypted.decrypt(
                timing=timing, key=Key(k3=encryption_response.key.k3)
            )
            assert [
                np.array_equal(arr1, arr2)
                for arr1, arr2 in zip(plnm_plaintext.meshes, encrypted.file.plnm.meshes)
            ]

            if high < 100:
                dict["high"] += high
                dict["mid"] += mid
                dict["low"] += low
                dict["used"] += 1
            else:
                print()
            timing["successes"] += 1

    # except Exception as e:
    #     timing["failures"].append(str(e))
    #     pass

    # with open("data.json", "w") as f:
    #     json.dump(dict, f)

    # with open("timing.json", "w") as f:
    #     cpy = timing.copy()
    #     cpy["decrypt"] = timing["decrypt"] / (timing["successes"] * 3)
    #     cpy["import"] = timing["import"] / (timing["successes"] * 4)
    #     cpy["decrypt_bit"] = timing["decrypt_bit"] / (timing["successes"] * 3)
    #     cpy["decrypt_keygen"] = timing["decrypt_keygen"] / (timing["successes"] * 3)
    #     cpy["decrypt_crypto"] = timing["decrypt_crypto"] / (timing["successes"] * 3)
    #     cpy["encrypt"] = timing["encrypt"] / (timing["successes"] )
    #     cpy["export"] = timing["export"] / (timing["successes"] )
    #     cpy["encrypt_bit"] = timing["encrypt_bit"] / (timing["successes"] )
    #     cpy["encrypt_keygen"] = timing["encrypt_keygen"] / (timing["successes"] )
    #     cpy["encrypt_crypto"] = timing["encrypt_crypto"] / (timing["successes"] )

    #     json.dump(cpy, f)
