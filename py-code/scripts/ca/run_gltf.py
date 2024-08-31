from py_code.encrypt.deprecit.ca.base import CACipherParams
from py_code.encrypt.deprecit.ca.system import CACryptoSystem
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.plaintext.plnm import PlnM
from py_code.local_tests.local_paths import glb_assets

if __name__ == "__main__":

    # glTF file encryption

    filepath = glb_assets[0]

    gltf_file = GLTFFile.load(import_path=filepath)
    plnm = gltf_file.plnm
    gltf_file.render.show()

    meshes_cipher_params = CACipherParams(gens=1, ps=[])
    images_cipher_params = CACipherParams(gens=1, ps=[])

    encryption = CACryptoSystem.from_pre_encryption(
        plnm=plnm,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        random_seed=42,
    )
    encryption.compute_generations()

    encryption.encrypt()

    gltf_file.insert_plnm(encryption.plnm)
    gltf_file.render.show()

    encryption.decrypt()

    gltf_file.insert_plnm(encryption.plnm)
    gltf_file.render.show()
