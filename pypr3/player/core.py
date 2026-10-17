import json
from pathlib import Path
from io import TextIOWrapper
from typing import IO, Callable
lazy from zipfile import ZipFile


import moderngl as mgl
lazy from PIL import Image, ImageFilter
from loguru import logger


from pypr3.core import ResourceManager, AssetCategory
from pypr3.player.info import ChartInfo
from pypr3.player.chart import Chart, ChartParser
from pypr3.audio import DirectSound, MusicCls, SoundRegistry
from pypr3.renderer import Renderer, TextureConverter, TextureRegistry


BG_DIM_COLOR = (0, 0, 0, 0.5)
CHART_DIM_COLOR = (0, 0, 0, 0.1)
SIDE_DIM_COLOR = (0.1, 0.1, 0.1, 0.7)
FONT_SIZE = 75
MAX_ASPECT_RATIO = 16 / 9


class Player:
    def __init__(self, resource_manager: ResourceManager, renderer: Renderer) -> None:
        self.info: ChartInfo | None = None
        self.chart: Chart | None = None
        self.music: MusicCls = MusicCls()
        self.illustration: mgl.Texture | None = None

        self._resource_manager = resource_manager
        self._renderer = renderer

    def _load_textures(self, func: Callable[[str], IO[bytes]], data: list[tuple[str, str]]):
        for texture_name, file_name in data:
            try:
                with func(file_name) as f:
                    TextureRegistry.register(texture_name, TextureConverter.from_bytes(
                        self._renderer.ctx, f.read()))

                    logger.opt(colors=True).info(
                        "Loaded texture: '<green>{}</green>', file: '<light-black>{}</light-black>'",
                        texture_name,
                        file_name
                    )
            except Exception:
                logger.opt(colors=True).exception(
                    "Failed to load texture '<yellow>{}</yellow>' from '<yellow>{}</yellow>'",
                    texture_name,
                    file_name
                )

    def _load_sounds(self, func: Callable[[str], IO[bytes]], data: list[tuple[str, str]]):
        for sound_name, file_name in data:
            try:
                with func(file_name) as f:
                    SoundRegistry.register(sound_name, DirectSound(f.read()))

                    logger.opt(colors=True).info(
                        "Loaded sound: '<green>{}</green>', file: '<light-black>{}</light-black>'",
                        sound_name,
                        file_name
                    )
            except Exception:
                logger.opt(colors=True).exception(
                    "Failed to load sound '<yellow>{}</yellow>' from '<yellow>{}</yellow>'",
                    sound_name,
                    file_name
                )

    def _load_fonts(self, func: Callable[[str], IO[bytes]], data: list[tuple[str, str]]):
        for font_name, file_name in data:
            try:
                try:
                    # Font uses lazy loading; do NOT close the file object
                    f = func(file_name)

                    self._renderer.text_renderer.load_font(
                        name=font_name,
                        path=f,
                        size=FONT_SIZE
                    )

                    logger.opt(colors=True).info(
                        "Loaded font: '<green>{}</green>', file: '<light-black>{}</light-black>'",
                        font_name,
                        file_name
                    )
                except (FileNotFoundError, KeyError):
                    logger.opt(colors=True).warning(
                        "Font file '<light-black>{}</light-black>' not found, "
                        "trying system font for '<green>{}</green>'",
                        file_name,
                        font_name
                    )

                    self._renderer.text_renderer.load_system_font(
                        name=font_name,
                        path=file_name,
                        size=FONT_SIZE
                    )

                    logger.opt(colors=True).info(
                        "Loaded font '<green>{}</green>' from system font",
                        font_name,
                        file_name
                    )
            except Exception:
                logger.opt(colors=True).exception(
                    "Failed to load font '<yellow>{}</yellow>' from '<yellow>{}</yellow>'",
                    font_name,
                    file_name
                )

    def init_assets(self):
        logger.info("Initializing player assets")

        self._load_textures(lambda file: self._resource_manager.open(self._resource_manager.get_path(AssetCategory.TEXTURE, file)), [
            ("note.tap", "tap.png"),
            ("note.tap.hl", "tap_hl.png"),
            ("note.drag", "drag.png"),
            ("note.drag.hl", "drag_hl.png"),
            ("note.flick", "flick.png"),
            ("note.flick.hl", "flick_hl.png"),
            ("note.hold.head", "hold_head.png"),
            ("note.hold.head.hl", "hold_head_hl.png"),
            ("note.hold.body", "hold_body.png"),
            ("note.hold.body.hl", "hold_body_hl.png"),
            ("note.hold.tail", "hold_tail.png"),
            ("note.hold.tail.hl", "hold_tail_hl.png"),
            ("hit_fx", "hit_fx.png"),
        ])

        self._load_sounds(lambda file: self._resource_manager.open(self._resource_manager.get_path(AssetCategory.SOUND, file)), [
            ("hitsound.tap", "tap.ogg"),
            ("hitsound.drag", "drag.ogg"),
            ("hitsound.hold", "hold.ogg"),
            ("hitsound.flick", "flick.ogg"),
        ])

        self._load_fonts(lambda file: self._resource_manager.open(self._resource_manager.get_path(AssetCategory.FONT, file)), [
            ("default", "font.ttf"),
        ])

        logger.info("Player assets initialized")

    def _load_chart_assets(
        self,
        chart: str | Path | ZipFile,
        textures: list[tuple[str, str]],
        sounds: list[tuple[str, str]],
        fonts: list[tuple[str, str]]
    ):
        if isinstance(chart, (str, Path)):
            chart_dir = Path(chart).parent

            chart_resource_manager = ResourceManager(chart_dir)

            self._load_textures(chart_resource_manager.open, textures)

            self._load_sounds(chart_resource_manager.open, sounds)

            self._load_fonts(chart_resource_manager.open, fonts)
        else:
            self._load_textures(chart.open, textures)

            self._load_sounds(chart.open, sounds)

            self._load_fonts(chart.open, fonts)

    def load_info(self, fp: str | Path):
        logger.info(f"Loading info: {fp}")

        self.info = ChartInfo.from_file(fp)

        logger.debug(f"Info loaded: {self.info}")

    def load_chart(self, fp: str | Path):
        logger.info(f"Loading chart: {fp}")

        with open(fp, "r", encoding="utf-8") as f:
            self.chart = ChartParser.from_dict(json.load(f))

        logger.debug("Chart parsed")

        self._load_chart_assets(
            fp,
            self.chart.get_texture_assets(),
            self.chart.get_sound_assets(),
            self.chart.get_font_assets()
        )

        logger.info("Chart assets loaded")

    def load_music(self, fp: str | Path | bytes):
        if isinstance(fp, (str, Path)):
            logger.info(f"Loading music: {fp}")

            self.music.load(str(fp))
        else:
            logger.info(f"Loading music from bytes")

            self.music.load(fp)

    def load_illustration(self, fp: str | Path | IO[bytes]):
        logger.info("Loading illustration")

        if self.illustration:
            self.illustration.release()

            logger.debug("Released previous illustration")

        with Image.open(fp) as img:
            img = img.convert("RGB")
            img = img.filter(ImageFilter.GaussianBlur(80))

            self.illustration = TextureConverter.from_image(
                self._renderer.ctx, img)

        logger.debug(
            f"Illustration loaded, size: {self.illustration.width}x{self.illustration.height}")

    def load_pez(self, fp: str | Path):
        logger.info(f"Loading PEZ: {fp}")

        with ZipFile(fp) as pez:
            file_names = [i.filename for i in pez.filelist]
            for file_name in file_names:
                path = Path(file_name)

                if path.stem == "info":
                    logger.debug(f"Found info file: {file_name}")

                    parser = ChartInfo.get_parser(path)

                    with pez.open(file_name) as f:
                        self.info = ChartInfo.from_any(
                            parser.load(TextIOWrapper(f, encoding="utf-8")))

                    logger.debug(f"Info loaded: {self.info}")

                    break
            else:
                raise FileNotFoundError(
                    f"No 'info' file found in archive: {fp}")

            if self.info.chart:
                logger.debug(f"Loading chart: {self.info.chart}")

                with pez.open(self.info.chart) as f:
                    self.chart = ChartParser.from_dict(json.load(f))

                self._load_chart_assets(
                    pez,
                    self.chart.get_texture_assets(),
                    self.chart.get_sound_assets(),
                    self.chart.get_font_assets()
                )
            else:
                raise ValueError(
                    f"Chart file not specified in info: {self.info}")

            if self.info.music:
                logger.debug(f"Loading music: {self.info.music}")

                with pez.open(self.info.music) as f:
                    self.load_music(f.read())
            else:
                raise ValueError(
                    f"Music file not specified in info: {self.info}")

            if self.info.illustration:
                logger.debug(f"Loading illustration: {self.info.illustration}")

                with pez.open(self.info.illustration) as f:
                    self.load_illustration(f)
            else:
                raise ValueError(
                    f"Illustration file not specified in info: {self.info}")

    def play_music(self):
        self.music.play()

    def _get_chart_size(self, screen_size: tuple[int, int]) -> tuple[tuple[float, float], tuple[int, int, int, int] | None]:
        result = screen_size
        aspect_ratio = result[0] / result[1]

        scissor = None

        if aspect_ratio > MAX_ASPECT_RATIO:
            chart_width = result[1] * MAX_ASPECT_RATIO
            result = (chart_width, result[1])

            scissor_left = (screen_size[0] - chart_width) / 2
            scissor = (round(scissor_left), 0, round(chart_width), result[1])

        return result, scissor

    def update(self, time: float, screen_size: tuple[int, int]):
        if self.chart:
            chart_size, _ = self._get_chart_size(screen_size)

            self.chart.update(time, chart_size, screen_size)

    def render(self, screen_size: tuple[int, int]):
        w, h = screen_size

        chart_size, scissor = self._get_chart_size(screen_size)

        if self.illustration:
            scale = max(w / self.illustration.width,
                        h / self.illustration.height)

            self._renderer.render_texture(
                screen_size,
                texture=self.illustration,
                x=0, y=0, w_scale=scale, h_scale=scale,
                rotation=0
            )

            self._renderer.render_rect(
                screen_size,
                x=0, y=0,
                width=w, height=h,
                rotation=0,
                color=BG_DIM_COLOR
            )

            self._renderer.render_rect(
                screen_size,
                x=0, y=0,
                width=chart_size[0], height=chart_size[1],
                rotation=0,
                color=CHART_DIM_COLOR
            )

            if scissor:
                side_width = scissor[0]

                self._renderer.render_rect(
                    screen_size,
                    x=-w / 2, y=0, width=side_width, height=h,
                    rotation=0, anchor=(0, 0.5), color=SIDE_DIM_COLOR
                )

                self._renderer.render_rect(
                    screen_size,
                    x=w / 2, y=0, width=side_width, height=h,
                    rotation=0, anchor=(1, 0.5), color=SIDE_DIM_COLOR
                )

        if self.chart:
            self._renderer.ctx.scissor = scissor
            self.chart.render(self._renderer, chart_size, screen_size)
            self._renderer.ctx.scissor = None
