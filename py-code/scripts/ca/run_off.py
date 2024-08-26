from py_code.encrypt.deprecit.ca.base import CACipherParams
from py_code.encrypt.deprecit.ca.system import CACipherSystem
from py_code.io.file.off.off import OffFile
from py_code.io.plaintext.plnm import PlnM
from py_code.local_tests.local_paths import off_assets

if __name__ == "__main__":

    # OFF file encryption

    asset = off_assets[0]

    off_file = OffFile.load(import_path=asset)
    plnm = PlnM.from_off(off_file)

    off_file.render.show()

    meshes_cipher_params = CACipherParams(gens=10, ps=[])
    images_cipher_params = CACipherParams(gens=1, ps=[])

    encryption = CACipherSystem.from_pre_encryption(
        plnm=plnm,
        meshes_cipher_params=meshes_cipher_params,
        images_cipher_params=images_cipher_params,
        random_seed=42,
    )

    encryption.compute_generations()
    encryption.encrypt()

    off_file = plnm.to_off(off_file=off_file)
    off_file.render.show()

    encryption.decrypt()

    off_file = plnm.to_off(off_file=off_file)
    off_file.render.show()
