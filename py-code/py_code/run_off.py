import numpy as np
from PIL import Image
from py_code.data.base_data import PlnM
from py_code.data.types import CombinedPlnMDataTypes
from py_code.encrypt.ca import EncryptionExpConwaysCA
from py_code.io.off import OffFile
from py_code.local_tests.local_paths import image_paths, off_assets

if __name__ == "__main__":

    # MESH ENCRYPTION

    asset = off_assets[0]

    off_file = OffFile.load(import_path=asset)

    encryption = EncryptionExpConwaysCA.from_pre_encryption(
        plnm=off_file.data.mesh,
        idl_points=[(0, 0), (0, 0)],
        gens=20,
        ps=[],
        random_seed=42,
    )
    off_file.render.show()

    encryption.encrypt()

    off_file.data.mesh = encryption.plnm
    off_file.render.show()

    encryption.decrypt()

    off_file.data.mesh = encryption.plnm
    off_file.render.show()

    # IMAGE ENCRYPTION

    img_filepath = image_paths[0]
    img = Image.open(img_filepath)
    numpy_img = np.asarray(img)

    image_plnm = PlnM.from_np_stack(
        stacked_data=numpy_img,
        stacktype="DEPTH",
        datatype=CombinedPlnMDataTypes.RGB,
    )

    encryption = EncryptionExpConwaysCA.from_pre_encryption(
        plnm=image_plnm,
        idl_points=[(0, 0), (0, 0), (0, 0)],
        gens=3,
        ps=[],
        random_seed=42,
    )
    encryption.plnm.image.show()

    encryption.encrypt(demonstrate=True)

    encryption.plnm.image.show()

    encryption.decrypt(demonstrate=True)

    encryption.plnm.image.show()
