from tempfile import TemporaryDirectory

import numpy as np
from py_code import Asset
from py_code.encrypt.adaptive.types import AdaptiveCipherParams
from py_code.local_tests.local_paths import glb_assets, gltf_assets, off_assets

"""Test encryption without exporting encrypted file"""

if __name__ == "__main__":

    filepath = off_assets[0]
    asset = Asset.load(filepath)

    with TemporaryDirectory() as tmp_dir:
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParams(p=2, q=1, r=1)
        images_cipher_params = AdaptiveCipherParams(p=2, q=1, r=1)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
        )

        asset.decrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            key=encryption_response.key,
        )
        assert plnm_plaintext == asset.file.plnm

        print()
