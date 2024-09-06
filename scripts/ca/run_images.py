from crypto_gltf.encrypt.deprecit.ca.base import CACipherParams
from crypto_gltf.encrypt.deprecit.ca.system import CACryptoSystem
from crypto_gltf.io.plaintext.plnm import PlnM
from crypto_gltf.local_tests.local_paths import image_paths
from PIL import Image

if __name__ == "__main__":

    # Image encryption

    img_filepath = image_paths[0]
    image = Image.open(img_filepath)
    plnm = PlnM.from_images([image])

    meshes_cipher_params = CACipherParams(gens=3, ps=[])
    images_cipher_params = CACipherParams(gens=3, ps=[])

    encryption = CACryptoSystem.from_pre_encryption(
        plnm=plnm,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        random_seed=42,
    )

    for render in encryption.plnm.renders:
        render.show()

    encryption.compute_generations()
    encryption.encrypt()

    for render in encryption.plnm.renders:
        render.show()

    encryption.decrypt()

    for render in encryption.plnm.renders:
        render.show()
