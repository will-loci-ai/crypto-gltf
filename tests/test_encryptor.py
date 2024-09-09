from crypto_gltf import Asset



class TestEncryptor:

    def test_encryptor(
        self,
        asset: Asset,
    ):
        plnm_plaintext = asset.file.plnm.__copy__()
        encryption_response = asset.encrypt()
        asset.decrypt(k3=encryption_response.key.k3)
        assert plnm_plaintext == asset.file.plnm

    def test_image_encryptor(
        self,
        asset: Asset,
    ):
        plnm_plaintext = asset.file.plnm.__copy__()
        encryption_response = asset.encrypt(encrypt_images=True)
        asset.decrypt(k3=encryption_response.key.k3)
        assert plnm_plaintext == asset.file.plnm
