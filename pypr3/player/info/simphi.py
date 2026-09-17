import csv
from typing import IO
from io import StringIO


from pydantic import BaseModel, Field, AliasChoices


from pypr3.player.info.base import InfoParser


class SimPhiChartInfo(BaseModel):
    """
    Reference: https://docs.lchzh.net/project/sim-phi-core/resource#info-csv
    """

    Chart: str | None = None
    Music: str | None = None
    Image: str | None = None
    Name: str = "Unknown"
    Artist: str = Field(
        "Unknown", validation_alias=AliasChoices("Artist", "Composer", "Musician"))
    Level: str = "Unknown"
    Illustrator: str = "Unknown"
    Charter: str = Field("Unknown", validation_alias=AliasChoices(
        "Charter", "Designer"))
    AspectRatio: float = 16 / 9
    NoteScale: float = Field(1, validation_alias=AliasChoices(
        "NoteScale", "ScaleRatio"))
    BackgroundDim: float = Field(0.6, validation_alias=AliasChoices(
        "BackgroundDim", "GlobalAlpha"))


class SimPhiChartInfoParser(InfoParser):
    @staticmethod
    def load(fp: IO[str]) -> SimPhiChartInfo:
        reader = csv.DictReader(fp)

        data = {}
        for row in reader:
            data = row  # Keep the last row

        data = {k: v for k, v in data.items() if not v is None}

        info = SimPhiChartInfo.model_validate(data)

        return info

    @staticmethod
    def loads(data: str) -> SimPhiChartInfo:
        return SimPhiChartInfoParser.load(StringIO(data))
