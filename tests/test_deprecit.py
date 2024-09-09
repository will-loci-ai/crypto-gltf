import pytest
from crypto_gltf import Asset
from crypto_gltf.encrypt.deprecit.adaptive_v1.system import AdaptiveCryptoSystemV1
from crypto_gltf.encrypt.deprecit.adaptive_v1.types import AdaptiveCipherParamsV1
from crypto_gltf.encrypt.deprecit.adaptive_v1.types import Key as v1key
from crypto_gltf.encrypt.deprecit.adaptive_v2.system import AdaptiveCryptoSystemV2
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import AdaptiveCipherParamsV2
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import Key as v2key


class TestDeprecit:

    @pytest.mark.skip(reason="Model depreciated")
    def test_encryptor_v1(self, asset: Asset):
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParamsV1(p=2)
        images_cipher_params = AdaptiveCipherParamsV1(p=2)
        response = AdaptiveCryptoSystemV1.encrypt(
            plnm=asset.file.plnm,
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encrypt_images=False,
        )
        asset.file.insert_plnm(response.ciphertext)

        assert response.aad is not None
        asset.file.embed_aad(response.aad)

        key = v1key(k1=response.key.k1, k2=response.key.k2, k3=response.key.k3)
        aad = (
            asset.file.aad
        )  # important we do this before extracting plnm, else aad extracted as well

        plnm = AdaptiveCryptoSystemV1.decrypt(plnm=asset.file.plnm, key=key, aad=aad)

        assert plnm_plaintext == plnm

    @pytest.mark.skip(reason="Model depreciated")
    def test_encryptor_v2(self, asset: Asset):
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
        images_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
        response = AdaptiveCryptoSystemV2.encrypt(
            plnm=asset.file.plnm,
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encrypt_images=False,
        )
        asset.file.insert_plnm(response.ciphertext)

        assert response.aad is not None
        asset.file.embed_aad(response.aad)

        key = v2key(k1=response.key.k1, k2=response.key.k2, k3=response.key.k3)
        aad = (
            asset.file.aad
        )  # important we do this before extracting plnm, else aad extracted as well

        plnm = AdaptiveCryptoSystemV2.decrypt(plnm=asset.file.plnm, key=key, aad=aad)

        assert plnm_plaintext == plnm
