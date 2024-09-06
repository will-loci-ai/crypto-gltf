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
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

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
# with open('data.json', 'w') as f:
#     json.dump(timing, f)

with open("data.json", "r") as f:
    timing_master = json.load(f)

assets = assets[timing_master['successes'] + timing_master['failures'] :]
timed_out = 0
for filepath in tqdm(assets):
    timing = timing_master.copy()
    try:
        with time_limit(20):
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
                # meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=1, r=1)
                # images_cipher_params = ImagesAdaptiveCipherParams(p=2, q=1, r=1)
                meshes_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
                images_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
                encryption_response, timing = asset.encrypt(
                    meshes_cipher_params=meshes_cipher_params,
                    images_cipher_params=images_cipher_params,
                    encryptor="AdaptiveV2",
                    timing=timing,
                )
                tic = time()
                export = asset.save(tmp_dir)
                timing["export"] += time() - tic

                encrypted = Asset.load(export)
                bool_val, timing = encrypted.decrypt(
                    timing=timing, key=encryption_response.key, decryptor="AdaptiveV2"
                )
                assert plnm_plaintext == encrypted.file.plnm
                timing["successes"] += 1

                with open("data.json", "w") as f:
                    json.dump(timing, f)
                timing_master = timing
                print()
            # except Exception as e:
            #     timing["failures"] += 1

            #     with open("data.json", "w") as f:
            #         json.dump(timing, f)
            #     timing_master = timing

    except TimeoutException as e:
        print("Timed out!")    
        timed_out +=1 
    except Exception as e:
        pass

    #     with open("data.json", "w") as f:
    #         json.dump(timing, f)
    #     timing_master = timing
    

print(successes)
print(len(failures))
print(successes - len(failures))
print(timed_out)
for k, v in timing.items():
    v = v / (timing['successes'] - timing['failures'])
    print(k, v)

encrypt_other = (
    timing["encrypt"]
    - timing["encrypt_crypto"]
    - timing["encrypt_keygen"]
    - timing["encrypt_bit"]
)/ (timing['successes'] - timing['failures'])
decrypt_other = (
    timing["decrypt"]
    - timing["decrypt_crypto"]
    - timing["decrypt_keygen"]
    - timing["decrypt_bit"]
)/ (timing['successes'] - timing['failures'])
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
