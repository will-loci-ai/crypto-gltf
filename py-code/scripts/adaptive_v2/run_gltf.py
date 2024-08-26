import secrets

from py_code.encrypt.adaptive.system import AdaptiveCipherSystem
from py_code.encrypt.adaptive.types import AdaptiveCipherParams
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.plaintext.plnm import PlnM
from py_code.local_tests.local_paths import glb_assets, gltf_assets

if __name__ == "__main__":
    # glTF file encryption

    filepath = glb_assets[0]
    key = secrets.token_bytes(32)

    gltf_file = GLTFFile.load(import_path=filepath)
    plnm = PlnM.from_gltf2(gltf_file)
    # gltf_file.render.show()

    meshes_cipher_params = AdaptiveCipherParams(p=3, q=2, r=1)
    images_cipher_params = AdaptiveCipherParams(p=2, q=1, r=0)

    encryption_response = AdaptiveCipherSystem.encrypt(
        plnm=plnm,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        key=key,
    )

    encryption_response.ciphertext.to_gltf2(gltf_file=gltf_file)
    gltf_file.render.show()

    decrypted_plnm = AdaptiveCipherSystem.decrypt(
        plnm=encryption_response.ciphertext,
        aad_b64=encryption_response.aad,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        key=key,
    )

    decrypted_plnm.to_gltf2(gltf_file=gltf_file)
    gltf_file.render.show()

    print()
