from typing import IO
from pathlib import Path


class ResourceManager:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def open(self, file: str | Path, mode: str = "rb") -> IO[bytes]:
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

    def get_shader_path(self, name: str, stage: str) -> Path:
        return self.root / "shaders" / name / f"{stage}.glsl"

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

    def get_shader(self, name: str, stage: str) -> str | None:
        path = self.get_shader_path(name, stage)

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_font(self, file: str) -> bytes | None:
        path = self.get_font_path(file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None
