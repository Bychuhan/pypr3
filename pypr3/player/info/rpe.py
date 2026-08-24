from typing import IO, Any
from io import StringIO


from pydantic import BaseModel


from pypr3.player.info.base import InfoParser


class RPEChartInfo(BaseModel):
    Name: str = "Unknown"
    Path: str = "Unknown"
    Song: str | None = None
    Picture: str | None = None
    Chart: str | None = None
    Level: str = "Unknown"
    Composer: str = "Unknown"
    Charter: str = "Unknown"
    LastEditTime: str = "Unknown"
    Length: float = 0
    EditTime: float = 0
    Group: str = "Unknown"


class RPEChartInfoParser(InfoParser):
    @staticmethod
    def load(fp: IO[str]) -> RPEChartInfo:
        lines = fp.readlines()

        dict_data: dict[str, Any] = {}

        for line in lines:
            if ":" in line:
                line_data = line.strip()
                key, _, value = line_data.partition(":")

                key = key.strip()
                value = value.strip()

                dict_data[key] = value

        info = RPEChartInfo.model_validate(dict_data)

        return info

    @staticmethod
    def loads(data: str) -> RPEChartInfo:
        return RPEChartInfoParser.load(StringIO(data))
