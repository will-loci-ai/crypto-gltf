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
)
from sklearn.metrics import mean_squared_error
from tqdm import tqdm

# timings = [
#     "import",
#     "export",
#     "encrypt",
#     "decrypt",
#     "encrypt_bit",
#     "decrypt_bit",
#     "encrypt_keygen",
#     "decrypt_keygen",
#     "encrypt_crypto",
#     "decrypt_crypto",
#     "successes",
#     "failures",
# ]
# timing = {val: 0 for val in timings}


# def rmse_vec(vec1, vec2):
#     shape = vec1.shape
#     # try:
#     rms = 0
#     if len(shape) == 1:
#         rms = dist(vec1, vec2)**2
#         return rms, 1
#     elif len(shape) == 2:
#         rms = sum(
#             [dist(vec1, vec2)**2 for vec1, vec2 in zip(vec1, vec2)]

#         )

#         return rms, shape[0]
#     elif len(shape) == 3:

#         rms = sum(
#             [
#                 dist(vec1[i][j], vec2[i][j])**2
#                 for i, j in zip(range(shape[0]), shape[1])
#             ]
#         )
#         return rms,  shape[0] * shape[1]
#     else:
#         return 0, 0
#     # except:
#     #     return 0


# def rmse(l: list[np.ndarray], m: list[np.ndarray]) -> float:

#     total = 0
#     count=0
#     for arr1, arr2 in zip(l, m):
#         # try:
#         if arr1.size:
#             tot, cou = rmse_vec(arr1, arr2)
#             total+=tot
#             count+=cou
#         # except:
#         #     pass
#     return sqrt(total/count)

# params_list = [
#     (1, 5, 8),
#     (2, 5, 8),
#     (3, 5, 8),
#     (4, 5, 8),
#     (5, 5, 8),
#     (2, 2, 10),
#     (2, 4, 10),
#     (2, 6, 10),
#     (2, 8, 10),
#     (2, 10, 10),
#     (3, 1, 1),
#     (3, 1, 5),
#     (3, 1, 10),
#     (3, 1, 15),
#     (3, 1, 19),
# ]

# np.random.seed(42)
# idxs = np.random.randint(0, 1814, 100)
# dict = {param: {"count": 0, "high": 0, "mid": 0, "low": 0} for param in params_list}

# for param in params_list:
#     for idx in tqdm(idxs):
#         try:
#             filepath = princeton_assets[idx]
#             asset = Asset.load(filepath)
#             with TemporaryDirectory() as tmp_dir:
#                 plnm_plaintext = asset.file.plnm.__copy__()
#                 meshes_cipher_params = MeshesAdaptiveCipherParams(
#                     p=param[0], q=param[1], r=param[2]
#                 )
#                 images_cipher_params = ImagesAdaptiveCipherParams(p=2, q=1, r=5)
#                 encryption_response, timing = asset.encrypt(
#                     meshes_cipher_params=meshes_cipher_params,
#                     images_cipher_params=images_cipher_params,
#                     timing=timing,
#                 )
#                 high = rmse(
#                     plnm_plaintext.meshes, encryption_response.ciphertext.meshes
#                 )
#                 export = asset.save(tmp_dir)

#                 encrypted = Asset.load(export)
#                 bool_val, timing = encrypted.decrypt(
#                     timing=timing, key=Key(k1=encryption_response.key.k1)
#                 )
#                 mid = rmse(plnm_plaintext.meshes, encrypted.file.plnm.meshes)

#                 encrypted = Asset.load(export)
#                 bool_val, timing = encrypted.decrypt(
#                     timing=timing, key=Key(k2=encryption_response.key.k2)
#                 )
#                 low = rmse(plnm_plaintext.meshes, encrypted.file.plnm.meshes)

#                 if high<1000:
#                     dict[param]["count"] += 1
#                     dict[param]["high"] += high
#                     dict[param]["mid"] += mid
#                     dict[param]["low"] += low
#                 else:
#                     print()

#         except Exception as e:
#             pass
#     with open("data.json", "w") as f:
#         json.dump(str(dict), f)

dict = {
    (1, 5, 8): {
        "count": 99,
        "high": 21.208890093826888,
        "mid": 10.51604906305211,
        "low": 0.3307726562757458,
    },
    (2, 5, 8): {
        "count": 99,
        "high": 21.212983621761662,
        "mid": 5.346840312450034,
        "low": 0.1662824491261831,
    },
    (3, 5, 8): {
        "count": 99,
        "high": 21.091110232773495,
        "mid": 2.6665668482941154,
        "low": 0.08296228960818473,
    },
    (4, 5, 8): {
        "count": 99,
        "high": 21.23152718879147,
        "mid": 1.3367663015892424,
        "low": 0.04129298021558184,
    },
    (5, 5, 8): {
        "count": 99,
        "high": 21.14944034082953,
        "mid": 0.6604944877420508,
        "low": 0.02080275766405891,
    },
    (2, 2, 10): {
        "count": 97,
        "high": 20.7091704248651,
        "mid": 5.211955924490866,
        "low": 1.3027789733787576,
    },
    (2, 4, 10): {
        "count": 99,
        "high": 21.18102720364433,
        "mid": 5.312298052073284,
        "low": 0.330157677122962,
    },
    (2, 6, 10): {
        "count": 99,
        "high": 21.19385087676301,
        "mid": 5.325823655475327,
        "low": 0.08312949586656122,
    },
    (2, 8, 10): {
        "count": 99,
        "high": 21.24469836641541,
        "mid": 5.33140823568762,
        "low": 0.020645158042408202,
    },
    (2, 10, 10): {
        "count": 99,
        "high": 21.148059526918157,
        "mid": 5.339205250248173,
        "low": 0.005198308126326687,
    },
    (3, 1, 1): {
        "count": 95,
        "high": 20.269160130050246,
        "mid": 2.458895838330455,
        "low": 1.1030712240477847,
    },
    (3, 1, 5): {
        "count": 95,
        "high": 20.276270884054497,
        "mid": 2.54141438758392,
        "low": 1.275812264426198,
    },
    (3, 1, 10): {
        "count": 95,
        "high": 20.282420889762985,
        "mid": 2.5451839722043204,
        "low": 1.2788262797044738,
    },
    (3, 1, 15): {
        "count": 95,
        "high": 20.266713323432494,
        "mid": 2.5457129290151466,
        "low": 1.2820671833730803,
    },
    (3, 1, 19): {
        "count": 95,
        "high": 20.306587561162775,
        "mid": 2.5426327449234574,
        "low": 1.2795148124517224,
    },
}

for K, V in dict.items():
    # print(f'${K}$')
    for k, v in V.items():
        if k != "count":
            dict[K][k] = v / (V["count"])
            # print(f"& ${dict[K][k]:.6f}$")

    # print("\\\ \hline")

l = [(K, V) for K, V in dict.items()]

for tup in l[:5]:
    print('mich')
# print(dict)
