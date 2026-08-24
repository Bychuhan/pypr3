from typing import IO
from io import StringIO
from enum import IntEnum, auto
from datetime import datetime


import yaml
from pydantic import BaseModel, model_validator


class ChartFormat(IntEnum):
    Rpe = 0
    Pec = auto()
    Pgr = auto()
    Pbc = auto()


class PhiraChartInfo(BaseModel):
    """
    Reference: https://teamflos.github.io/phira-docs/chart-standard/chartinfo.html
    """

    id: int | None = None
    uploader: int | None = None
    name: str = "UK"
    difficulty: float = 10
    level: str = "UK Lv.10"
    charter: str = "UK"
    composer: str = "UK"
    illustrator: str = "UK"
    chart: str = "chart.json"
    format: ChartFormat | None = None
    music: str = "song.mp3"
    illustration: str = "background.png"
    unlockVideo: str | None = None
    previewStart: float = 0
    previewEnd: float | None = None
    aspectRatio: float = 16 / 9
    backgroundDim: float = 0.6
    lineLength: float = 6
    offset: float = 0
    tip: str | None = None
    tags: list[str] = []
    intro: str = ""
    holdPartialCover: bool = False
    created: datetime | None = None
    updated: datetime | None = None
    chartUpdated: datetime | None = None

    @model_validator(mode="after")
    def set_default_preview_end(self) -> "PhiraChartInfo":
        if self.previewEnd is None:
            self.previewEnd = self.previewStart + 15
        return self


class PhiraChartInfoParser:
    @staticmethod
    def load(fp: IO[str]) -> PhiraChartInfo:
        dict_data = yaml.load(fp, Loader=yaml.SafeLoader)

        info = PhiraChartInfo.model_validate(dict_data)

        return info

    @staticmethod
    def loads(data: str) -> PhiraChartInfo:
        return PhiraChartInfoParser.load(StringIO(data))
