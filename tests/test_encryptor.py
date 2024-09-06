from crypto_gltf import Asset
from crypto_gltf.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    MeshesAdaptiveCipherParams,
)


class TestEncryptor:

    def test_encryptor(
        self,
        asset: Asset,
    ):
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=2, r=10)
        images_cipher_params = ImagesAdaptiveCipherParams(p=1, q=3, r=4)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encryptor='AdaptiveV3'
        )
        asset.decrypt(
            key=encryption_response.key,
        )
        assert plnm_plaintext == asset.file.plnm
