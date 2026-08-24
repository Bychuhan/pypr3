import csv
from typing import IO
from io import StringIO


from pydantic import BaseModel, Field, AliasChoices


class SimPhiChartInfo(BaseModel):
    """
    Reference: https://docs.lchzh.net/project/sim-phi-core/resource#info-csv
    """

    Chart: str | None = None
    Music: str | None = None
    Image: str | None = None
    Name: str = "Unknown"
    Artist: str = Field(
        "Unknown", validation_alias=AliasChoices("Composer", "Musician"))
    Level: str = "Unknown"
    Illustrator: str = "Unknown"
    Charter: str = Field("Unknown", validation_alias="Designer")  # Legacy
    AspectRatio: float = 16 / 9
    NoteScale: float = Field(1, validation_alias="ScaleRatio")  # Legacy
    BackgroundDim: float = Field(0.6, validation_alias="GlobalAlpha")  # Legacy


class SimPhiChartInfoParser:
    @staticmethod
    def load(fp: IO[str]) -> SimPhiChartInfo:
        reader = csv.DictReader(fp)

        data = {}
        for row in reader:
            data = row  # Keep the last row

        info = SimPhiChartInfo.model_validate(data)

        return info

    @staticmethod
    def loads(data: str) -> SimPhiChartInfo:
        return SimPhiChartInfoParser.load(StringIO(data))
