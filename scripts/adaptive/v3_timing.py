import json
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
from tqdm import tqdm

"""Test encryption without exporting encrypted file"""

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
successes = 0
assets = [asset for asset in loci_assets if not asset.endswith(".off")][:100]

# assets = paper_figs_paths
failures = {}


for filepath in tqdm(assets):
    try:
        tic = time()
        asset = Asset.load(filepath)
        timing["import"] += time() - tic
        # if True:
        # try:
        tic = time()
        asset = Asset.load(filepath)
        timing["import"] += time() - tic

        with TemporaryDirectory() as tmp_dir:
            plnm_plaintext = asset.file.plnm.__copy__()
            meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=1, r=1)
            images_cipher_params = ImagesAdaptiveCipherParams(p=2, q=1, r=1)
            # meshes_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
            # images_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
            encryption_response, timing = asset.encrypt(
                meshes_cipher_params=meshes_cipher_params,
                images_cipher_params=images_cipher_params,
                timing=timing,
            )
            tic = time()
            export = asset.save(tmp_dir)
            timing["export"] += time() - tic

            encrypted = Asset.load(export)
            bool_val, timing = encrypted.decrypt(
                timing=timing, key=encryption_response.key
            )
            # assert plnm_plaintext == encrypted.file.plnm
            assert [np.array_equal(arr1, arr2) for arr1, arr2 in zip(plnm_plaintext.images, encrypted.file.plnm.images)]
            timing["successes"] += 1

    except Exception as e:
        timing["failures"] += 1


print(timing['successes'])

for k, v in timing.items():
    v = v / (timing["successes"] - timing["failures"])
    print(k, f"{v:.6f}")

encrypt_other = (
    timing["encrypt"]
    - timing["encrypt_crypto"]
    - timing["encrypt_keygen"]
    - timing["encrypt_bit"]
)
decrypt_other = (
    timing["decrypt"]
    - timing["decrypt_crypto"]
    - timing["decrypt_keygen"]
    - timing["decrypt_bit"]
)
print(encrypt_other, decrypt_other)
print(
    timing["encrypt"],
    timing["encrypt_crypto"]
    + timing["encrypt_keygen"]
    + timing["encrypt_bit"]
    + encrypt_other,
)
print(
    timing["decrypt"],
    timing["decrypt_crypto"]
    + timing["decrypt_keygen"]
    + timing["decrypt_bit"]
    + encrypt_other,
)

print()
# 90
# import 0.056827
# export 3.722894
# encrypt 0.235385
# decrypt 0.230110
# encrypt_bit 0.229567
# decrypt_bit 0.226693
# encrypt_keygen 0.001740
# decrypt_keygen 0.001668
# encrypt_crypto 0.001506
# decrypt_crypto 0.000925
# successes 1.125000
# failures 0.125000
# 0.20563483238220215 0.06596112251281738