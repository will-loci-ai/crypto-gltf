from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from loguru import logger
from py_code.data.asset_file_data_types import AssetFileDataType, OffData
from py_code.data.types import Composition
from py_code.io.file.base_file import BaseFile
from py_code.io.plaintext.plnm import PlnM


@dataclass
class OffFile(BaseFile):
    data: AssetFileDataType.OFF

    @classmethod
    def load(cls, import_path: str) -> OffFile:
        """Load an OFF Mesh file"""

        # Parse mesh from OFF file
        import_path_bin = os.fsencode(import_path)
        file = open(import_path_bin, "r")
        first_line = file.readline().rstrip()
        use_colors = first_line == "COFF"
        colors = []

        # handle blank and comment lines after the first line
        line = file.readline()
        while line.isspace() or line[0] == "#":
            line = file.readline()

        vcount, fcount, ecount = [int(x) for x in line.split()]
        verts = []
        faces = []
        edges = []
        i = 0
        while i < vcount:
            line = file.readline()
            if line.isspace():
                continue  # skip empty lines
            try:
                bits = [float(x) for x in line.split()]
                px = bits[0]
                py = bits[1]
                pz = bits[2]
                if use_colors:
                    colors.append(
                        [
                            float(bits[3]) / 255,
                            float(bits[4]) / 255,
                            float(bits[5]) / 255,
                            1.0,
                        ]
                    )

            except ValueError:
                i = i + 1
                continue
            verts.append((px, py, pz))
            i = i + 1

        i = 0
        while i < fcount:
            line = file.readline()
            if line.isspace():
                continue  # skip empty lines
            try:
                splitted = line.split()
                ids = list(map(int, splitted))
                if len(ids) > 3:
                    faces.append(tuple(ids[1:]))
                elif len(ids) == 3:
                    edges.append(tuple(ids[1:]))
            except ValueError:
                i = i + 1
                continue
            i = i + 1

        logger.info(f".off file loaded from {import_path}")

        return cls(
            import_path=import_path,
            data=OffData(
                verts=np.array(verts, dtype=np.float32),
                faces=faces,
                colors=np.array(colors, dtype=np.float32),
            ),
            filename_ext=".off",
        )

    def save(self, export_dir: str) -> str:
        """Save to OFF Mesh file"""

        off_data = self.data

        verts = off_data.verts
        faces = off_data.faces
        colors = off_data.colors

        # Write geometry to file
        export_filepath = f"{export_dir}/{self.export_filename}"
        export_dir_bin = os.fsencode(export_filepath)
        fp = open(export_dir_bin, "w")

        if colors.size > 0:
            fp.write("COFF\n")
        else:
            fp.write("OFF\n")

        fp.write("%d %d 0\n" % (len(verts), len(faces)))

        for i, vert in enumerate(verts):
            fp.write(f"{vert[0]:.32} {vert[1]:.32} {vert[2]:.32}")
            if colors.size > 0:
                fp.write(f" {colors[i][0]:d} {colors[i][1]:d} {colors[i][2]:d} 255")
            fp.write("\n")

        # for face in faces:
        for i, face in enumerate(faces):
            fp.write("%d" % len(face))
            for vid in face:
                fp.write(" %d" % vid)
            fp.write("\n")

        fp.close()

        logger.info(f".off file saved to {export_filepath}")

        return export_filepath

    @property
    def plnm(self) -> PlnM:
        """'Get plaintext from OffFile"""

        verts, colors = (
            self.data.verts,
            self.data.colors,
        )  # skip faces as they're of inhomogeneous shape
        return PlnM(meshes=[verts, colors], images=[], meshes_dim=2, images_dim=0)

    def insert_plnm(self, plnm: PlnM) -> None:
        """Insert plaintext in OffFile
        assumes the plaintext data came from the same OffFile"""

        self.data.verts = plnm.meshes[0]
        self.data.colors = plnm.meshes[1]

    def embed_aad(self, aad: np.ndarray) -> None:
        """Embed aad data in file for retrieval during decryption"""

        assert Composition.AAD == aad
        num_used_vertices = max(max(x) for x in self.data.faces) + 1
        aad_float32 = np.frombuffer(aad.tobytes(), dtype=np.float32).reshape((-1, 3))
        self.data.verts = np.concatenate(
            (self.data.verts[:num_used_vertices], aad_float32)
        )

    @property
    def aad(self) -> np.ndarray:
        """Retrieve embedded aad data"""
        num_used_vertices = max(max(x) for x in self.data.faces) + 1
        aad = self.data.verts[num_used_vertices:]
        self.data.verts = self.data.verts[
            :num_used_vertices
        ]  # remove embedded aad data
        return np.frombuffer(aad.tobytes(), dtype=np.uint32).reshape((-1, 3))
