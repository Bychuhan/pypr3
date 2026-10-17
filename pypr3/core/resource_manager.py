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

    def get_file_path(self, file: str) -> Path:
        return self.root / file

    def get_texture_path(self, file: str) -> Path:
        return self.root / "textures" / file

    def get_sound_path(self, file: str) -> Path:
        return self.root / "sounds" / file

    def get_shader_path(self, name: str) -> tuple[Path, Path, Path]:
        vs_path = self.root / "shaders" / name / "vert.glsl"
        fs_path = self.root / "shaders" / name / "frag.glsl"
        gs_path = self.root / "shaders" / name / "geom.glsl"

        return vs_path, fs_path, gs_path

    def get_font_path(self, file: str) -> Path:
        return self.root / "fonts" / file

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
        if vs_path.exists():
            with open(vs_path, "r", encoding="utf-8") as f:
                vs = f.read()

        fs = None
        if fs_path.exists():
            with open(fs_path, "r", encoding="utf-8") as f:
                fs = f.read()

        gs = None
        if gs_path.exists():
            with open(gs_path, "r", encoding="utf-8") as f:
                gs = f.read()

        return vs, fs, gs

    def get_font(self, file: str) -> bytes | None:
        path = self.get_font_path(file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None
