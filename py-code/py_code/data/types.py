from typing import Any, Literal, NamedTuple

JSONDict = dict[str, Any]

# FILETYPES


class Extension:
    """Extensions for filetypes"""

    ASSET = Literal[".off", ".glb", ".gltf"]
    IMAGE = Literal[".png", ".jpeg", ".jpg"]

    ANY_SUPPORTED = Literal[".off", ".png", ".jpeg", ".jpg"]


FileTypeName = Literal["ASSET", "IMAGE"]


class FileTypeConfig(NamedTuple):
    name: FileTypeName
    extensions: tuple[Extension.ANY_SUPPORTED, ...]


class FileType:
    ASSET = FileTypeConfig("ASSET", tuple(Extension.ASSET.__args__))  # type: ignore[attr-defined]
    IMAGE = FileTypeConfig("IMAGE", tuple(Extension.IMAGE.__args__))  # type: ignore[attr-defined]


# DATATYPES


class Composition:
    """Number of matrices the datatype is composed of"""

    MESH = 2  # Faces & verts
    RGB = 3  # RGB
    GREYSCALE = 2  # Black & white
    RGBA = 4


DataTypeName = Literal["GREYSCALE", "RGB", "MESH", "RGBA"]


class PlnMDataType(NamedTuple):
    name: DataTypeName
    composition: int


class CombinedPlnMDataTypes:
    GREYSCALE = PlnMDataType("GREYSCALE", Composition.GREYSCALE)  # type: ignore[attr-defined]
    RGB = PlnMDataType("RGB", Composition.RGB)  # type: ignore[attr-defined]
    MESH = PlnMDataType("MESH", Composition.MESH)  # type: ignore[attr-defined]
    RGBA = PlnMDataType("RGBA", Composition.RGBA)  # type: ignore[attr-defined]
