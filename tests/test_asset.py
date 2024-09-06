from tempfile import TemporaryDirectory

import pytest
from crypto_gltf import Asset
from crypto_gltf.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    MeshesAdaptiveCipherParams,
)


@pytest.mark.dependency(depends=["test_encryptor", "test_import_export"])
def test_asset(asset: Asset):
    """test full import, export, encryption, decryption pipeline"""

    with TemporaryDirectory() as tmp_dir:
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=2, r=10)
        images_cipher_params = ImagesAdaptiveCipherParams(p=1, q=1, r=6)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
        )
        export_path = asset.save(tmp_dir)

        encrypted_asset = Asset.load(export_path)
        encrypted_asset.decrypt(
            key=encryption_response.key,
        )
        assert plnm_plaintext == encrypted_asset.file.plnm
