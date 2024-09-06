import json
import os
import struct
from functools import cached_property

from crypto_gltf.data.asset_file_data_types import Gltf2Data
from crypto_gltf.io.file.gltf2.com.gltf2_io import Buffer, BufferView
from crypto_gltf.io.file.gltf2.exp.gltf2_io_binary_data import (
    BinaryData as ExpBinaryData,
)
from crypto_gltf.io.file.gltf2.exp.gltf2_io_buffer import Buffer as ExpBuffer
from crypto_gltf.io.file.gltf2.utils import uri_to_path


class GlTF2Exporter:
    """Class to handle glTF2 export"""

    def __init__(
        self,
        export_dir: str,
        filename: str,
        is_glb: bool,
        filename_ext: str,
        images_encrypted: bool = False,
    ):
        self.export_buffer: ExpBuffer = ExpBuffer()
        self.buffer_views: list[BufferView] = []
        self.export_dir: str = export_dir
        self.filename: str = filename
        self.is_glb: bool = is_glb
        self.filename_ext: str = filename_ext
        self.images_encrypted: bool = images_encrypted

    @cached_property
    def export_filepath(self) -> str:
        return f"{self.export_dir}/{self.filename}{self.filename_ext}"

    def export(self, gltf_data: Gltf2Data) -> str:
        """Export glTF2 file"""

        self.gltf = gltf_data.gltf.copy()

        # Export accessors
        for i in range(len(gltf_data.accessors)):
            self.export_accessor(gltf_data, i)

        # Export images
        for i in range(len(gltf_data.images)):
            self.export_image(gltf_data, i)

        if self.is_glb:
            uri = None
        else:
            uri = "scene.bin"

        buffer = Buffer(
            byte_length=self.export_buffer.byte_length,
            extensions=None,
            extras=None,
            name=None,
            uri=uri,
        )

        # Set buffer and buffer views
        self.gltf["bufferViews"] = [
            buffer_view.to_dict() for buffer_view in self.buffer_views
        ]
        self.gltf["buffers"] = [buffer.to_dict()]

        gltf_bytes = json.dumps(self.gltf).encode("utf-8")
        buffer_bytes = self.export_buffer.to_bytes()

        match self.is_glb:
            case True:
                with open(self.export_filepath, "wb") as f:

                    length_gltf = len(gltf_bytes)
                    spaces_gltf = (4 - (length_gltf & 3)) & 3
                    length_gltf += spaces_gltf

                    length_bin = len(buffer_bytes)
                    zeros_bin = (4 - (length_bin & 3)) & 3
                    length_bin += zeros_bin

                    length = 12 + 8 + length_gltf
                    if length_bin > 0:
                        length += 8 + length_bin

                    # Header (Version 2)
                    f.write("glTF".encode())
                    f.write(struct.pack("I", 2))
                    f.write(struct.pack("I", length))

                    # Chunk 0 (JSON)
                    f.write(struct.pack("I", length_gltf))
                    f.write("JSON".encode())
                    f.write(gltf_bytes)
                    f.write(b" " * spaces_gltf)

                    # Chunk 1 (BIN)
                    if length_bin > 0:
                        f.write(struct.pack("I", length_bin))
                        f.write("BIN\0".encode())
                        f.write(buffer_bytes)
                        f.write(b"\0" * zeros_bin)

            case False:
                self.export_data(
                    buffer_bytes,
                    filepath=f"{self.export_dir}/{uri_to_path(buffer.uri)}",
                )
                self.export_data(
                    gltf_bytes,
                    filepath=self.export_filepath,
                )

        return self.export_filepath

    def export_data(self, data: bytes, filepath: str) -> str:
        """Safely writes data to destination in export_dir"""
        path = os.path.join(os.path.dirname(self.export_dir), filepath)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            return path
        except Exception as e:
            raise Exception(f"Couldn't export file: {path}") from e

    def export_accessor(self, gltf_data: Gltf2Data, accessor_idx: int) -> bool:
        """Export accessor to buffer"""
        binary_data = ExpBinaryData.from_numpy(arr=gltf_data.accessors[accessor_idx])
        buffer_view = self.export_buffer.add_and_get_view(
            binary_data
        )  # add to buffer and get buffer view
        self.buffer_views.append(buffer_view)

        # Update accessor references in json
        self.gltf["accessors"][accessor_idx]["byteOffset"] = 0
        self.gltf["accessors"][accessor_idx]["bufferView"] = accessor_idx
        return True

    def export_image(self, gltf_data: Gltf2Data, image_idx: int) -> bool:
        """Export image, either by adding to buffer or writing to file"""
        pyimage = gltf_data.gltf["images"][image_idx]
        uri, buffer_view = pyimage.get("uri", None), pyimage.get("bufferView", None)

        assert not (uri is None and buffer_view is None)

        if uri is not None:
            # write to file
            if self.images_encrypted:
                # .jpeg alters some RGB values on export
                # therefore have to use lossless png filetype
                if not uri.endswith(".png"):
                    uri = os.path.splitext(uri)[0] + ".png"
                    gltf_data.gltf["images"][image_idx]["uri"] = uri

            path = os.path.join(self.export_dir, uri_to_path(uri))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            gltf_data.images[image_idx].save(path, compression_level=0)

        elif buffer_view is not None:
            # add to buffer
            binary_data = ExpBinaryData.from_image(image=gltf_data.images[image_idx])
            buffer_view = self.export_buffer.add_and_get_view(binary_data)
            self.buffer_views.append(buffer_view)

            # update image buffer view references in json
            self.gltf["images"][image_idx]["bufferView"] = (
                len(self.buffer_views) - 1
            )  # TODO: make static
        else:
            raise Exception(
                f"Missing image data: {gltf_data.gltf['images'][image_idx]}"
            )
        return True
