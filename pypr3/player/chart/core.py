from abc import ABC, abstractmethod


from pypr3.renderer import Renderer


class Chart(ABC):
    @abstractmethod
    def update(self, time: float):
        pass

    @abstractmethod
    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        pass
