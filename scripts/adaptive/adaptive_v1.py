from tempfile import TemporaryDirectory

from crypto_gltf import Asset
from crypto_gltf.encrypt.deprecit.adaptive_v1.types import AdaptiveCipherParamsV1
from crypto_gltf.local_tests.local_paths import glb_assets, gltf_assets, off_assets

"""Local testing"""

if __name__ == "__main__":

    filepath = glb_assets[2]
    asset = Asset.load(filepath)

    with TemporaryDirectory() as tmp_dir:
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParamsV1(p=2)
        images_cipher_params = AdaptiveCipherParamsV1(p=2)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encryptor="AdaptiveV1",
        )

        export_path = asset.save(tmp_dir)

        encrypted_asset = Asset.load(export_path)
        encrypted_asset.decrypt(
            key=encryption_response.key,
            decryptor="AdaptiveV1",
        )

        assert plnm_plaintext == encrypted_asset.file.plnm
