from enum import IntEnum


import pygame
from loguru import logger


class VSyncType(IntEnum):
    AUTO = -1
    DISABLE = 0
    ENABLE = 1


class Window:
    def __init__(self, width: int, height: int, title: str, resizable: bool = False, vsync: VSyncType = VSyncType.DISABLE, multisample: int = 4):
        self._width = width
        self._height = height
        self._title = title

        self._vsync = vsync
        self._resizable = resizable

        self._multisample = multisample

        self._is_created = False

    def _get_flags(self) -> int:
        flags = pygame.DOUBLEBUF | pygame.OPENGL  # enable OpenGL rendering by default

        if self._resizable:
            flags |= pygame.RESIZABLE

        return flags

    def _set_mode(self):
        logger.debug(
            f"Setting display mode: {self._width}x{self._height}, flags={self._get_flags()}, vsync={self._vsync.name}")

        pygame.display.set_mode(
            size=(self._width, self._height),
            flags=self._get_flags(),
            vsync=self._vsync
        )

    def _set_caption(self):
        pygame.display.set_caption(self._title)

    def create(self):
        if self._is_created:
            raise RuntimeError("Window has already been created")

        if self._multisample > 0:
            logger.debug(f"Enabling MSAA {self._multisample}x")

            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
            pygame.display.gl_set_attribute(
                pygame.GL_MULTISAMPLESAMPLES, self._multisample)

        self._set_mode()
        self._set_caption()

        self._is_created = True

        logger.info(
            f"Window created: size={self.size}, title='{self._title}', resizable={self._resizable}, vsync={self._vsync.name}")

    def handle_events(self, events: list[pygame.Event]):
        for event in events:
            if event.type == pygame.WINDOWRESIZED:
                logger.debug(
                    f"Window resized: {self._width}x{self._height} -> {event.x}x{event.y}")

                self._width = event.x
                self._height = event.y

    def _on_size_changed(self):
        if self._is_created:
            self._set_mode()

    def _on_title_changed(self):
        if self._is_created:
            self._set_caption()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: int):
        if value <= 0:
            raise ValueError("Width must be positive")

        self._width = value
        self._on_size_changed()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: int):
        if value <= 0:
            raise ValueError("Height must be positive")

        self._height = value
        self._on_size_changed()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        self._on_title_changed()

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self, value: bool):
        self._resizable = value

        if self._is_created:
            self._set_mode()

    @property
    def vsync(self):
        return self._vsync

    @vsync.setter
    def vsync(self, value: VSyncType):
        self._vsync = value

        if self._is_created:
            self._set_mode()

    @property
    def size(self):
        return (self._width, self._height)

    @size.setter
    def size(self, value: tuple[int, int]):
        if len(value) != 2:
            raise ValueError("Size must be a tuple of (width, height)")

        width, height = value

        if width <= 0:
            raise ValueError("Width must be positive")
        if height <= 0:
            raise ValueError("Height must be positive")

        self._width, self._height = width, height

        self._on_size_changed()

    @property
    def multisample(self):
        return self._multisample
