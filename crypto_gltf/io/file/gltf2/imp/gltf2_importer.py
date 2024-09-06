from __future__ import annotations

import base64
import json
import os
import struct
from dataclasses import dataclass

import numpy as np
from crypto_gltf.data.types import JSONDict
from crypto_gltf.io.file.gltf2.com.gltf2_io import Accessor, Buffer, BufferView, Image
from crypto_gltf.io.file.gltf2.utils import uri_to_path
from PIL import Image as PILImage
from pydantic import BaseModel, ConfigDict


class GlbModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    gltf: JSONDict
    glb_buffer: memoryview | None


class DataChunkModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data_type: bytes
    data_length: int
    data: memoryview
    offset: int


@dataclass
class GlTF2Importer:
    filepath: str
    gltf: JSONDict

    accessors: list[Accessor]
    buffers: dict[int, Buffer]
    buffer_views: dict[int, BufferView]
    images: dict[int, Image]

    glb_buffer: memoryview | None
    loaded_buffers: dict[int, memoryview]

    accessor_cache: dict[int, np.ndarray]
    image_cache: dict[int, PILImage.Image]

    @classmethod
    def from_filepath(cls, filepath: str) -> GlTF2Importer:
        """Load glTF from filepath"""
        if not os.path.isfile(filepath):
            raise ImportError("Please select a file")

        with open(filepath, "rb") as f:
            content = memoryview(f.read())

        if content[:4] == b"glTF":
            glb_model = cls.load_glb(content)
            gltf, glb_buffer = glb_model.gltf, glb_model.glb_buffer
        else:
            gltf = cls.load_json(content)
            glb_buffer = None

        cls.check_version(gltf)

        if gltf.get("accessors"):
            accessors = [Accessor.from_dict(accessor) for accessor in gltf["accessors"]]
        else:
            accessors = []
        if gltf.get("buffers"):
            buffers = [Buffer.from_dict(buffer) for buffer in gltf["buffers"]]
        else:
            buffers = []
        if gltf.get("bufferViews"):
            buffer_views = [
                BufferView.from_dict(bufferview) for bufferview in gltf["bufferViews"]
            ]
        else:
            buffer_views = []
        if "images" in gltf.keys():
            images = [Image.from_dict(image) for image in gltf["images"]]
        else:
            images = []

        return cls(
            filepath=filepath,
            gltf=gltf,
            accessors=accessors,
            buffers={idx: buffer for idx, buffer in enumerate(buffers)},
            buffer_views={
                idx: buffer_view for idx, buffer_view in enumerate(buffer_views)
            },
            images={idx: image for idx, image in enumerate(images)},
            glb_buffer=glb_buffer,
            accessor_cache={},
            loaded_buffers={},
            image_cache={},
        )

    def load_buffer(self, buffer_idx: int) -> None:
        """Load buffer."""
        buffer = self.buffers[buffer_idx]

        if buffer.uri:
            data = self.load_uri(buffer.uri)
            if data is None:
                raise ImportError("Missing resource, '" + buffer.uri + "'.")
            self.loaded_buffers[buffer_idx] = data

        else:
            # GLB-stored buffer
            if buffer_idx == 0 and self.glb_buffer is not None:
                self.loaded_buffers[buffer_idx] = self.glb_buffer

    def load_uri(self, uri: str) -> memoryview:
        """Loads a URI."""
        sep = ";base64,"
        if uri.startswith("data:"):
            idx = uri.find(sep)
            if idx != -1:
                data = uri[idx + len(sep) :]
                return memoryview(base64.b64decode(data))

        path = os.path.join(os.path.dirname(self.filepath), uri_to_path(uri))
        try:
            with open(path, "rb") as f_:
                return memoryview(f_.read())
        except Exception as e:
            raise Exception(f"Couldn't read file: {path}") from e

    @staticmethod
    def load_glb(content: memoryview) -> GlbModel:
        """Load binary glb."""

        magic = content[:4]
        if magic != b"glTF":
            raise ImportError("This file is not a glTF/glb file")

        version, file_size = struct.unpack_from("<II", content, offset=4)
        if version != 2:
            raise ImportError("GLB version must be 2; got %d" % version)
        if file_size != len(content):
            raise ImportError("Bad GLB: file size doesn't match")

        glb_buffer = None
        offset = 12  # header size = 12

        # JSON chunk is first
        data_chunk = GlTF2Importer.load_chunk(content, offset)
        json_bytes = data_chunk.data

        if data_chunk.data_type != b"JSON":
            raise ImportError("Bad GLB: first chunk not JSON")
        if data_chunk.data_length != len(json_bytes):
            raise ImportError("Bad GLB: length of json chunk doesn't match")
        gltf = GlTF2Importer.load_json(json_bytes)

        # BIN chunk is second (if it exists)
        if data_chunk.offset < len(content):
            data_chunk = GlTF2Importer.load_chunk(content, data_chunk.offset)

            if data_chunk.data_type == b"BIN\0":
                if data_chunk.data_length != len(data_chunk.data):
                    raise ImportError("Bad GLB: length of BIN chunk doesn't match")
                glb_buffer = data_chunk.data

        return GlbModel(gltf=gltf, glb_buffer=glb_buffer)

    @staticmethod
    def load_chunk(content: memoryview, offset: int) -> DataChunkModel:
        """Load chunk."""
        chunk_header = struct.unpack_from("<I4s", content, offset)
        data_length = chunk_header[0]
        data_type = chunk_header[1]
        data = content[offset + 8 : offset + 8 + data_length]

        return DataChunkModel(
            data_type=data_type,
            data_length=data_length,
            data=data,
            offset=offset + 8 + data_length,
        )

    @staticmethod
    def load_json(content: memoryview) -> JSONDict:
        def bad_constant(val):
            raise ImportError("Bad glTF: json contained %s" % val)

        try:
            text = str(content, encoding="utf-8")
            return json.loads(text, parse_constant=bad_constant)
        except ValueError as e:
            raise ImportError("Bad glTF: json error: %s" % e.args[0])

    @staticmethod
    def check_version(gltf: JSONDict) -> None:
        """Check version.."""
        if not isinstance(gltf, dict) or "asset" not in gltf:
            raise ImportError("Bad glTF: no asset in json")
        if "version" not in gltf["asset"]:
            raise ImportError("Bad glTF: no version")
        if gltf["asset"]["version"] != "2.0":
            raise ImportError(
                "glTF version must be 2.0; got %s" % gltf["asset"]["version"]
            )
