import secrets

import numpy as np
from py_code.encrypt.deprecit.adaptive_v1.base import AdaptiveCipherParams
from py_code.encrypt.deprecit.adaptive_v1.system import AdaptiveCipherSystem
from py_code.io.file.off.off import OffFile
from py_code.io.plaintext.plnm import PlnM
from py_code.local_tests.local_paths import off_assets

if __name__ == "__main__":

    # OFF file encryption

    asset = off_assets[0]
    key = secrets.token_bytes(32)

    off_file = OffFile.load(import_path=asset)
    plnm = PlnM.from_off(off_file)

    # off_file.render.show()

    meshes_cipher_params = AdaptiveCipherParams(position=2)
    images_cipher_params = AdaptiveCipherParams(position=2)

    encryption_response = AdaptiveCipherSystem.encrypt(
        plnm=plnm,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        key=key,
    )

    encryption_response.ciphertext.to_off(off_file=off_file)
    off_file.render.show()

    decrypted_plnm = AdaptiveCipherSystem.decrypt(
        plnm=encryption_response.ciphertext,
        aad_b64=encryption_response.aad,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        key=key,
    )

    decrypted_plnm.to_off(off_file=off_file)
    off_file.render.show()

    print()
