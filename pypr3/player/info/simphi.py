import csv
from typing import IO
from io import StringIO


from pydantic import BaseModel


class SimPhiChartInfo(BaseModel):
    Chart: str | None = None
    Music: str | None = None
    Image: str | None = None
    Name: str = "Unknown"
    Artist: str = "Unknown"
    Level: str = "Unknown"
    Illustrator: str = "Unknown"
    Charter: str = "Unknown"
    AspectRatio: float = 16 / 9
    NoteScale: float = 1
    BackgroundDim: float = 0.6


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
