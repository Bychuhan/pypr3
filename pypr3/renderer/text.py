from dataclasses import dataclass, field
from typing import Any, IO


import pygame
import moderngl as mgl
from loguru import logger


from pypr3.renderer.texture import TextureConverter


@dataclass
class TextTexture:
    texture: mgl.Texture
    font_size: int
    text: str
    y_offset: int = field(init=False)

    def __post_init__(self) -> None:
        self.y_offset = self.texture.height - self.font_size

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)

        return getattr(self.texture, name)


class TextRenderer:
    def __init__(self, ctx: mgl.Context) -> None:
        self._fonts: dict[str, pygame.font.Font] = {}
        self._ctx = ctx

    def load_font(self, name: str, path: str | IO[bytes], size: int) -> None:
        if name in self._fonts:
            logger.warning(f"Font '{name}' already registered, overwriting")

        self._fonts[name] = pygame.font.Font(path, size)

    def render_text(
        self,
        text: str,
        font_name: str,
        antialias: bool = True,
    ) -> TextTexture:
        if font_name not in self._fonts:
            raise KeyError(f"Font '{font_name}' not found")

        font = self._fonts[font_name]

        if not text:
            empty = pygame.Surface((1, 1), pygame.SRCALPHA)
            data = pygame.image.tobytes(empty, "RGBA", False)
            return TextTexture(
                texture=TextureConverter.from_bytes_with_wh(
                    self._ctx, "RGBA", (1, 1), data),
                font_size=font.get_height(),
                text=text,
            )

        lines = text.split("\n")

        line_surfaces: list[pygame.Surface] = []
        for line in lines:
            if not line:
                line_surface = pygame.Surface(
                    (1, font.get_height()), pygame.SRCALPHA)
            else:
                line_surface = self._render_line(font, line, antialias)
            line_surfaces.append(line_surface)

        total_width = max(s.get_width() for s in line_surfaces)
        total_height = (font.get_height() * (len(lines) - 1) +
            (line_surfaces[-1].get_height() if line_surfaces else 0))

        result = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        y = 0
        for s in line_surfaces:
            result.blit(s, (0, y))
            y += font.get_height()

        data = pygame.image.tobytes(result, "RGBA", False)

        return TextTexture(
            texture=TextureConverter.from_bytes_with_wh(
                self._ctx, "RGBA", result.get_size(), data),
            font_size=font.get_height(),
            text=text,
        )

    def _render_line(
        self,
        font: pygame.font.Font,
        line: str,
        antialias: bool,
    ) -> pygame.Surface:
        surfaces: list[pygame.Surface] = []
        for char in line:
            surface = font.render(char, antialias, (255, 255, 255, 255))
            surfaces.append(surface)

        if not surfaces:
            return pygame.Surface((1, font.get_height()), pygame.SRCALPHA)

        total_width = sum(s.get_width() for s in surfaces)
        max_height = max(s.get_height() for s in surfaces)

        result = pygame.Surface((total_width, max_height), pygame.SRCALPHA)

        x = 0
        for s in surfaces:
            result.blit(s, (x, 0))
            x += s.get_width()

        return result
