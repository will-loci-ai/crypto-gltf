from py_code.data.base_data import PlnM
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.file.off.off import OffFile
from py_code.io.plaintext.base_plaintext import BasePlainTex


class PlainTextPlnM(BasePlainTex):
    data: PlnM

    @classmethod
    def from_gltf2(cls, gltf_file: GLTFFile) -> BasePlainTex:
        raise NotImplementedError()

    @classmethod
    def from_off(cls, off_file: OffFile) -> BasePlainTex:
        raise NotImplementedError()

    @property
    def to_gltf2(self) -> GLTFFile:
        raise NotImplementedError()

    @property
    def to_off(self) -> OffFile:
        raise NotImplementedError()
