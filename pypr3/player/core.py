import json
from pathlib import Path
from io import TextIOWrapper
from typing import IO
from zipfile import ZipFile


import moderngl as mgl
from PIL import Image, ImageFilter


from pypr3.core import ResourceManager
from pypr3.player.info import ChartInfo
from pypr3.player.chart import Chart, ChartParser
from pypr3.audio import DirectSound, MusicCls, SoundRegistry
from pypr3.renderer import Renderer, TextureConverter, TextureRegistry


BG_DIM_COLOR = (0, 0, 0, 0.55)


class Player:
    def __init__(self, resource_manager: ResourceManager, renderer: Renderer) -> None:
        self.info: ChartInfo | None = None
        self.chart: Chart | None = None
        self.music: MusicCls = MusicCls()
        self.illustration: mgl.Texture | None = None

        self._resource_manager = resource_manager
        self._renderer = renderer

    def init_assets(self):
        self._init_hitsounds()
        self._init_textures()

    def _init_hitsounds(self):
        for name in ("tap", "drag", "hold", "flick"):
            sound = (self._resource_manager.get_sound(f"{name}.ogg"))

            if sound:
                SoundRegistry.register(f"hitsound.{name}", DirectSound(sound))

    def _init_textures(self):
        for texture_name, file_name in (
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
        ):
            texture = self._resource_manager.get_texture(file_name)

            if texture:
                TextureRegistry.register(texture_name, TextureConverter.from_bytes(
                    self._renderer.ctx, texture))

    def _load_chart_assets(self, chart: str | Path | ZipFile, textures: list[tuple[str, str]]):
        if isinstance(chart, (str, Path)):
            chart_dir = Path(chart).parent

            chart_resource_manager = ResourceManager(chart_dir)

            for texture_name, file_name in textures:
                texture = chart_resource_manager.get_file(file_name)

                if texture:
                    TextureRegistry.register(texture_name, TextureConverter.from_bytes(
                        self._renderer.ctx, texture))

        else:
            for texture_name, file_name in textures:
                with chart.open(file_name) as f:
                    texture = f.read()

                    if texture:
                        TextureRegistry.register(texture_name, TextureConverter.from_bytes(
                            self._renderer.ctx, texture))

    def load_info(self, fp: str | Path):
        self.info = ChartInfo.from_file(fp)

    def load_chart(self, fp: str | Path):
        with open(fp, "r", encoding="utf-8") as f:
            self.chart = ChartParser.from_dict(json.load(f))

        self._load_chart_assets(fp, self.chart.get_texture_assets())

    def load_music(self, fp: str | Path | bytes):
        if isinstance(fp, (str, Path)):
            self.music.load(str(fp))
        else:
            self.music.load(fp)

    def load_illustration(self, fp: str | Path | IO[bytes]):
        if self.illustration:
            self.illustration.release()

        with Image.open(fp) as img:
            img = img.convert("RGB")
            img = img.filter(ImageFilter.GaussianBlur(80))

            self.illustration = TextureConverter.from_image(
                self._renderer.ctx, img)

    def load_pez(self, fp: str | Path):
        with ZipFile(fp) as pez:
            file_names = [i.filename for i in pez.filelist]
            for file_name in file_names:
                path = Path(file_name)

                if path.stem == "info":
                    parser = ChartInfo.get_parser(path)

                    with pez.open(file_name) as f:
                        self.info = ChartInfo.from_any(
                            parser.load(TextIOWrapper(f, encoding="utf-8")))

                    break
            else:
                raise FileNotFoundError(
                    f"No 'info' file found in archive: {fp}")

            if self.info.chart:
                with pez.open(self.info.chart) as f:
                    self.chart = ChartParser.from_dict(json.load(f))

                self._load_chart_assets(pez, self.chart.get_texture_assets())
            else:
                raise ValueError(
                    f"Chart file not specified in info: {self.info}")

            if self.info.music:
                with pez.open(self.info.music) as f:
                    self.load_music(f.read())
            else:
                raise ValueError(
                    f"Music file not specified in info: {self.info}")

            if self.info.illustration:
                with pez.open(self.info.illustration) as f:
                    self.load_illustration(f)
            else:
                raise ValueError(
                    f"Illustration file not specified in info: {self.info}")

    def play_music(self):
        self.music.play()

    def update(self, time: float, screen_size: tuple[int, int]):
        if self.chart:
            self.chart.update(time, screen_size)

    def render(self, screen_size: tuple[int, int]):
        w, h = screen_size

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

        if self.chart:
            self.chart.render(self._renderer, screen_size)
