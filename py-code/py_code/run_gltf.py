from py_code.data.base_data import PlnM
from py_code.encrypt.ca import EncryptionExpConwaysCA
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.local_tests.local_paths import ASSET_EXPORT_DIR, gltf_assets, glb_assets

if __name__ == "__main__":
    filepath = gltf_assets[0]

    gltf_file = GLTFFile.load(import_path=filepath)
    accessors = [accessor for accessor in gltf_file.data.accessors.values()]
    plnm = PlnM.from_list(accessors)
    gltf_file.render.show()

    encryption = EncryptionExpConwaysCA.from_pre_encryption(
        plnm=plnm,
        idl_points=[(0, 0) for i in range(plnm.dim)],
        gens=3,
        ps=[],
        random_seed=42,
    )

    encryption.encrypt()

    export_path = gltf_file.save(str(ASSET_EXPORT_DIR))

    gltf_file = GLTFFile.load(import_path=export_path)
