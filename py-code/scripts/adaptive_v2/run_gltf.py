import secrets

import numpy as np
from py_code.encrypt.adaptive.key_gen import generate_keys, get_k1, get_k2
from py_code.encrypt.adaptive.system import AdaptiveCipherSystem
from py_code.encrypt.adaptive.types import AdaptiveCipherParams, Key
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.plaintext.plnm import PlnM
from py_code.local_tests.local_paths import glb_assets, gltf_assets


def float32_meshes_copy(plnm: PlnM) -> list[np.ndarray]:
    """create copy of plnm.meshes with float arrays converted to float32"""

    meshes_copy = plnm.meshes.copy()
    meshes_float_arrs_idxs = np.array(
        [idx for idx, mesh in enumerate(meshes_copy) if mesh.dtype.kind == "f"]
    )
    float_arrs = [
        meshes_copy[i].astype(np.float32) for i in meshes_float_arrs_idxs
    ]  # convert to float32
    for idx, i in enumerate(meshes_float_arrs_idxs):
        meshes_copy[i] = float_arrs[idx]

    assert all(
        [np.array_equal(arr, arr_cpy) for arr, arr_cpy in zip(plnm.meshes, meshes_copy)]
    )

    return meshes_copy


if __name__ == "__main__":
    # glTF file encryption

    filepath = glb_assets[0]

    gltf_file = GLTFFile.load(import_path=filepath)
    plnm = PlnM.from_gltf2(gltf_file)

    meshes_copy = float32_meshes_copy(plnm=plnm)

    meshes_cipher_params = AdaptiveCipherParams(p=2, q=1, r=0)
    images_cipher_params = AdaptiveCipherParams(p=2, q=1, r=0)

    og = generate_keys(plnm=plnm, params=meshes_cipher_params)

    encryption_response = AdaptiveCipherSystem.encrypt(
        plnm=plnm,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        key=og,
    )
    enc_copy = encryption_response

    assert not all(
        [np.array_equal(arr, arr_cpy) for arr, arr_cpy in zip(plnm.meshes, meshes_copy)]
    )

    encryption_response.ciphertext.to_gltf2(gltf_file=gltf_file)
    # gltf_file.render.show()

    key = Key(k3=og.k3)

    decrypted_plnm = AdaptiveCipherSystem.decrypt(
        plnm=enc_copy.ciphertext,
        aad_b64=enc_copy.aad,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        key=key,
    )

    assert all(
        [np.array_equal(arr, arr_cpy) for arr, arr_cpy in zip(plnm.meshes, meshes_copy)]
    )

    decrypted_plnm.to_gltf2(gltf_file=gltf_file)
    # gltf_file.render.show()

    print()
