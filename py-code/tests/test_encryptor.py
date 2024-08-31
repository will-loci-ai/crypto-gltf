from py_code import Asset
from py_code.encrypt.adaptive.types import AdaptiveCipherParams


class TestEncryptor:

    def test_encryptor(
        self,
        asset: Asset,
    ):
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
