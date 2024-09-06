import pytest
from crypto_gltf import Asset
from crypto_gltf.encrypt.deprecit.adaptive_v1.types import AdaptiveCipherParamsV1
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import AdaptiveCipherParamsV2


class TestDeprecit:

    @pytest.mark.skip(reason="Model depreciated")
    def test_encryptor_v1(self, asset: Asset):
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParamsV1(p=2)
        images_cipher_params = AdaptiveCipherParamsV1(p=2)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encryptor="AdaptiveV1",
        )
        asset.decrypt(key=encryption_response.key, decryptor="AdaptiveV1")
        assert plnm_plaintext == asset.file.plnm

    @pytest.mark.skip(reason="Model depreciated")
    def test_encryptor_v2(self, asset: Asset):
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
        images_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encryptor="AdaptiveV2",
        )
        asset.decrypt(key=encryption_response.key, decryptor="AdaptiveV2")
        assert plnm_plaintext == asset.file.plnm
