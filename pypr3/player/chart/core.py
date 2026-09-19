from abc import ABC, abstractmethod
from typing import Any


from pypr3.renderer import Renderer


class Chart(ABC):
    @abstractmethod
    def update(self, time: float, screen_size: tuple[int, int]):
        pass

    @abstractmethod
    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        pass

    @classmethod
    @abstractmethod
    def from_any(cls, data: Any) -> "Chart":
        pass

    def get_texture_assets(self) -> list[tuple[str, str]]:
        return []

    def get_sound_assets(self) -> list[tuple[str, str]]:
        return []

    def get_font_assets(self) -> list[tuple[str, str]]:
        return []
