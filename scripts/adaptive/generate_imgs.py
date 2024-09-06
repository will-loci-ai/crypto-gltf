from tempfile import TemporaryDirectory

import numpy as np
from crypto_gltf import Asset
from crypto_gltf.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    Key,
    MeshesAdaptiveCipherParams,
)

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
params_list = [
    (1,1,6),
    (1,2,5),
    (1,3,4),
    (1,4,3),
]
asset_path = "/home/will/stage2/assets/import/lightning_mcqueen.glb"
save_dir = "/home/will/stage2/assets/paper_figs/mqueen"

for param in params_list:
    meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=2, r=10)
    images_cipher_params = ImagesAdaptiveCipherParams(
        p=param[0], q=param[1], r=param[2]
    )
    asset = Asset.load(asset_path)

    with TemporaryDirectory() as tmp_dir:
        plnm_plaintext = asset.file.plnm.__copy__()

        encryption_response, timing = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encrypt_images=True,
            timing=timing,
        )
        asset.file.render.save(
            save_dir
            + f"/{images_cipher_params.p}{images_cipher_params.q}{images_cipher_params.r}{'high'}.png"
        )

        export_path = asset.save(tmp_dir)

        keys = {
            "mid": Key(k1=encryption_response.key.k1),
            "low": Key(k2=encryption_response.key.k2),
        }

        for k, v in keys.items():
            encrypted_asset = Asset.load(export_path)
            encrypted_asset.decrypt(key=v, timing=timing)

            encrypted_asset.file.render.save(
                save_dir
                + f"/{images_cipher_params.p}{images_cipher_params.q}{images_cipher_params.r}{k}.png"
            )
