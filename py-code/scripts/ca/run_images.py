import numpy as np
from PIL import Image
from py_code.data.types import CombinedPlnMDataTypes, Composition
from py_code.encrypt.ca_encryption.base import CACipherParams
from py_code.encrypt.ca_encryption.hazmat import CACipherSystem
from py_code.io.file.off.off import OffFile
from py_code.io.plaintext.plnm import PlnM
from py_code.local_tests.local_paths import image_paths, off_assets

if __name__ == "__main__":

    # Image encryption

    img_filepath = image_paths[0]
    image = Image.open(img_filepath)
    plnm = PlnM.from_images([image])

    meshes_cipher_params = CACipherParams(gens=3, ps=[])
    images_cipher_params = CACipherParams(gens=3, ps=[])

    encryption = CACipherSystem.from_pre_encryption(
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
