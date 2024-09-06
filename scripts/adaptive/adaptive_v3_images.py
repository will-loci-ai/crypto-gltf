from tempfile import TemporaryDirectory

import numpy as np
from crypto_gltf import Asset
from crypto_gltf.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    Key,
    MeshesAdaptiveCipherParams,
)
from crypto_gltf.local_tests.local_paths import (
    ASSET_EXPORT_DIR,
    glb_assets,
    gltf_assets,
    image_paths,
    off_assets, princeton_assets
)

"""Local testing"""

if __name__ == "__main__":

    filepath = glb_assets[0]
    asset = Asset.load(filepath)

    with TemporaryDirectory() as tmp_dir:
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = MeshesAdaptiveCipherParams(p=3, q=1, r=2)
        images_cipher_params = ImagesAdaptiveCipherParams(p=1, q=1, r=6)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            # encrypt_images=True,
        )

        export_path = asset.save(tmp_dir)
        asset.file.render.show()

        keys = [
            Key(k1=encryption_response.key.k1),
            Key(k2=encryption_response.key.k2),
            Key(k3=encryption_response.key.k3),
        ]

        for key in keys:
            encrypted_asset = Asset.load(export_path)
            encrypted_asset.decrypt(
                key=key,
            )

            encrypted_asset.file.render.show()

        encrypted_asset = Asset.load(export_path)
        encrypted_asset.decrypt(
            key=encryption_response.key,
        )
        assert plnm_plaintext == encrypted_asset.file.plnm
    print()
