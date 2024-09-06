# SPDX-FileCopyrightText: 2018-2021 The glTF-Blender-IO authors
#
# SPDX-License-Identifier: Apache-2.0

import array
import io
import typing

import numpy as np
from crypto_gltf.io.file.gltf2.com.gltf2_io_constants import ComponentType
from PIL import Image


class BinaryData:
    """Store for gltf binary data that can later be stored in a buffer."""

    def __init__(self, data: bytes, bufferViewTarget=None):
        if not isinstance(data, bytes):
            raise TypeError("Data is not a bytes array")
        self.data = data
        self.bufferViewTarget = bufferViewTarget

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    @classmethod
    def from_list(
        cls,
        lst: typing.List[typing.Any],
        gltf_component_type: ComponentType,
        bufferViewTarget=None,
    ):
        format_char = ComponentType.to_type_code(gltf_component_type)
        return BinaryData(array.array(format_char, lst).tobytes(), bufferViewTarget)

    @classmethod
    def from_numpy(
        cls,
        arr: np.ndarray,
        bufferViewTarget=None,
    ):
        return BinaryData(arr.tobytes(), bufferViewTarget)

    @classmethod
    def from_image(
        cls,
        image: Image.Image,
        bufferViewTarget=None,
    ):
        byteIO = io.BytesIO()
        image.save(byteIO, format="PNG")
        return BinaryData(byteIO.getvalue(), bufferViewTarget)

    @property
    def byte_length(self):
        return len(self.data)
