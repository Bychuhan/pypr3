from typing import IO, Literal, overload, cast
from enum import StrEnum
from pathlib import Path


from loguru import logger


class AssetCategory(StrEnum):
    TEXTURE = "textures"
    SOUND = "sounds"
    FONT = "fonts"
    SHADER = "shaders"


class ResourceManager:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @overload
    def open(self, file: str | Path, mode: Literal["rb"]) -> IO[bytes]:
        pass

    @overload
    def open(self, file: str | Path, mode: Literal["r"]) -> IO[str]:
        pass

    @overload
    def open(self, file: str | Path) -> IO[bytes]:
        pass

    def open(self, file: str | Path, mode: str = "rb") -> IO[bytes] | IO[str]:
        return cast(IO[bytes] | IO[str], open(self.root / file, mode))

    def get_file(self, file: str) -> bytes | None:
        path = self.root / file

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_path(self, category: AssetCategory, file: str | Path) -> Path:
        return self.root / category.value / file

    def get_texture(self, file: str) -> bytes | None:
        path = self.get_path(AssetCategory.TEXTURE, file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            logger.opt(colors=True).warning(
                "Texture not found: <yellow>{}</yellow>", path
            )

            return None

    def get_sound(self, file: str) -> bytes | None:
        path = self.get_path(AssetCategory.SOUND, file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            logger.opt(colors=True).warning(
                "Sound not found: <yellow>{}</yellow>", path
            )

            return None

    def get_shader(self, name: str, stage: str) -> str | None:
        path = self.get_path(AssetCategory.SHADER, f"{name}/{stage}.glsl")

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.opt(colors=True).warning(
                "Shader not found: <yellow>{}</yellow> (name='{}', stage='{}')",
                path, name, stage
            )

            return None

    def get_font(self, file: str) -> bytes | None:
        path = self.get_path(AssetCategory.FONT, file)

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            logger.opt(colors=True).warning(
                "Font not found: <yellow>{}</yellow>", path
            )

            return None
