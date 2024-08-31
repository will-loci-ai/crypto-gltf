from pathlib import Path
from typing import Type

from py_code.io.file.base_file import BaseFile
from py_code.io.file.gltf2.gltf2 import GLTFFile
from py_code.io.file.off.off import OffFile


def File(import_filepath: str) -> BaseFile:
    """Factory method for initializing any filetype"""

    localizers: dict[str, Type[BaseFile]] = {
        ".gltf": GLTFFile,
        ".glb": GLTFFile,
        ".off": OffFile,
    }
    path = Path(import_filepath)

    filetype = localizers.get(path.suffix.lower())
    if not filetype:
        raise Exception(f"Filetype {filetype} not supported.")

    return filetype.load(import_filepath)
