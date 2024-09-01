from tempfile import TemporaryDirectory

import numpy as np
from py_code import Asset
from py_code.encrypt.adaptive.types import (
    ImagesAdaptiveCipherParams,
    Key,
    MeshesAdaptiveCipherParams,
)
from py_code.local_tests.local_paths import (
    ASSET_EXPORT_DIR,
    glb_assets,
    gltf_assets,
    image_paths,
    off_assets,
)

"""Local testing"""
# from PIL import Image

# img = Image.open(image_paths[0])
# arr = np.asarray(img)
# flat = arr.flatten()
# for idx, elt in enumerate(flat):
#     if elt >= 128:
#         flat[idx] = np.random.randint(low=elt - 128, high=255)
#     else:
#         flat[idx]= np.random.randint(low=0, high=elt + 128)

# enc = Image.fromarray(flat.reshape(arr.shape))
# enc.show()

if __name__ == "__main__":

    filepath = glb_assets[3]
    asset = Asset.load(filepath)

    with TemporaryDirectory() as tmp_dir:
        plnm_plaintext = asset.file.plnm.__copy__()
        meshes_cipher_params = MeshesAdaptiveCipherParams(p=2, q=2, r=2)
        images_cipher_params = ImagesAdaptiveCipherParams(p=1, q=1, r=6)
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
