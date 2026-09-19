import os
from typing import IO
from pathlib import Path


class ResourceManager:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def open(self, file: str, mode: str = "rb") -> IO[bytes]:
        path = self.root / file

        return open(path, mode)

    def get_file(self, file: str) -> bytes | None:
        path = self.root / file

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_file_path(self, file: str) -> str:
        return str(self.root / file)

    def get_texture_path(self, file: str) -> str:
        return str(self.root / "textures" / file)

    def get_sound_path(self, file: str) -> str:
        return str(self.root / "sounds" / file)

    def get_shader_path(self, name: str) -> tuple[str, str, str]:
        vs_path = str(self.root / "shaders" / name / "vert.glsl")
        fs_path = str(self.root / "shaders" / name / "frag.glsl")
        gs_path = str(self.root / "shaders" / name / "geom.glsl")

        return vs_path, fs_path, gs_path

    def get_texture(self, file: str) -> bytes | None:
        path = self.get_texture_path(file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_sound(self, file: str) -> bytes | None:
        path = self.get_sound_path(file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_shader(self, name: str) -> tuple[str | None, str | None, str | None]:
        vs_path, fs_path, gs_path = self.get_shader_path(name)

        vs = None
        if os.path.exists(vs_path):
            with open(vs_path, "r", encoding="utf-8") as f:
                vs = f.read()

        fs = None
        if os.path.exists(fs_path):
            with open(fs_path, "r", encoding="utf-8") as f:
                fs = f.read()

        gs = None
        if os.path.exists(gs_path):
            with open(gs_path, "r", encoding="utf-8") as f:
                gs = f.read()

        return vs, fs, gs
