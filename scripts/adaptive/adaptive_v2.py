from tempfile import TemporaryDirectory

from crypto_gltf import Asset
from crypto_gltf.encrypt.deprecit.adaptive_v2.types import AdaptiveCipherParamsV2, Key
from crypto_gltf.local_tests.local_paths import glb_assets, gltf_assets, off_assets

"""Local testing"""

if __name__ == "__main__":

    filepath = off_assets[1]
    asset = Asset.load(filepath)

    with TemporaryDirectory() as tmp_dir:

        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
        images_cipher_params = AdaptiveCipherParamsV2(p=2, q=1, r=0)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            encryptor="AdaptiveV2",
        )

        export_path = asset.save(tmp_dir)

        encrypted_asset = Asset.load(export_path)
        encrypted_asset.decrypt(
            key=encryption_response.key,
            decryptor="AdaptiveV2",
        )
        assert plnm_plaintext == encrypted_asset.file.plnm

        print()
