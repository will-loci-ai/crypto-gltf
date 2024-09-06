from tempfile import TemporaryDirectory

from crypto_gltf import Asset
from crypto_gltf.encrypt.adaptive.types import AdaptiveCipherParams, Key
from crypto_gltf.local_tests.local_paths import glb_assets, gltf_assets, off_assets

"""Local testing"""

if __name__ == "__main__":

    filepath = glb_assets[1]
    asset = Asset.load(filepath)

    with TemporaryDirectory() as tmp_dir:

        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = AdaptiveCipherParams(p=2, q=2, r=2)
        images_cipher_params = AdaptiveCipherParams(p=2, q=1, r=1)
        encryption_response = asset.encrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
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
                meshes_cipher_params=meshes_cipher_params,
                images_cipher_params=images_cipher_params,
                key=key,
            )

            encrypted_asset.file.render.show()

        encrypted_asset = Asset.load(export_path)
        encrypted_asset.decrypt(
            meshes_cipher_params=meshes_cipher_params,
            images_cipher_params=images_cipher_params,
            key=encryption_response.key,
        )
        assert plnm_plaintext == encrypted_asset.file.plnm

        print()
