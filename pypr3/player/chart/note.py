from typing import Any
from abc import ABC, abstractmethod


import moderngl as mgl


from pypr3.audio.registry import SoundRegistry
from pypr3.renderer import Renderer, TextureRegistry
from pypr3.audio import DirectSound


NOTE_TEXTURE_WIDTH = 0.123


class NoteRenderable(ABC):
    _HITSOUND_MAP: dict[Any, str]
    _NORMAL_TEXTURE_MAP: dict[Any, tuple[str, str, str]]
    _HIGHLIGHT_TEXTURE_MAP: dict[Any, tuple[str, str, str]]

    def __init__(self) -> None:
        self.type: Any = None
        self.hitsound: DirectSound | None = None
        self.textures: list[mgl.Texture | None] = []
        self._texture_sizes: list[tuple[float, float]] = []
        self.is_highlight: bool = False

    def init_assets(self) -> None:
        self.hitsound = SoundRegistry.get(
            self._HITSOUND_MAP.get(self.type, "none"))

        self._init_textures()

    def _init_textures(self) -> None:
        normal_keys = self._NORMAL_TEXTURE_MAP.get(
            self.type, ("none",) * 3)
        highlight_keys = self._HIGHLIGHT_TEXTURE_MAP.get(
            self.type, ("none",) * 3)

        textures: list[mgl.Texture | None] = []
        texture_sizes: list[tuple[float, float]] = []

        for normal_key, highlight_key in zip(normal_keys, highlight_keys):
            normal_tex = TextureRegistry.get(normal_key)
            highlight_tex = TextureRegistry.get(highlight_key)

            if self.is_highlight and highlight_tex:
                tex = highlight_tex
                w_scale = highlight_tex.width / normal_tex.width if normal_tex else 1.0
                tex_w = NOTE_TEXTURE_WIDTH * w_scale
            else:
                tex = normal_tex
                tex_w = NOTE_TEXTURE_WIDTH

            textures.append(tex)
            texture_sizes.append(self._calc_texture_size(tex, tex_w))

        self.textures = textures
        self._texture_sizes = texture_sizes

    def _calc_texture_size(self, tex: mgl.Texture | None, width: float) -> tuple[float, float]:
        if tex is None:
            return (1, 1)
        return (width, width / (tex.width / tex.height))

    @abstractmethod
    def render(self, renderer: Renderer, screen_size: tuple[int, int]) -> None:
        pass

    def _render_texture(self, renderer: Renderer, screen_size: tuple[int, int], index: int,
                        x: float, y: float, w_scale: float = 1.0, h_scale: float = 1.0,
                        rotation: float = 0.0, anchor: tuple[float, float] = (0.5, 0.5), size_override: tuple[int, int] | None = None) -> bool:
        texture = self.textures[index]
        if texture is None:
            return False

        if size_override is None:
            tex_w, tex_h = self._texture_sizes[index]
            w, _ = screen_size
            texture_size = (round(tex_w * w), round(tex_h * w))
        else:
            texture_size = size_override

        renderer.render_texture(
            screen_size,
            texture=texture,
            x=x,
            y=y,
            w_scale=w_scale,
            h_scale=h_scale,
            rotation=rotation,
            anchor=anchor,
            texture_size=texture_size
        )
        return True
