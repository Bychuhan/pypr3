from typing import Any


from pydantic import BaseModel


from pypr3.player.info.rpe import RPEChartInfo
from pypr3.player.info.phira import PhiraChartInfo
from pypr3.player.info.simphi import SimPhiChartInfo


class ChartInfo(BaseModel):
    chart: str | None = None
    music: str | None = None
    illustration: str | None = None

    name: str = "Unknown"
    level: str = "Unknown"
    composer: str = "Unknown"
    illustrator: str = "Unknown"
    charter: str = "Unknown"

    @classmethod
    def from_rpe_info(cls, info: RPEChartInfo) -> "ChartInfo":
        return cls(
            chart=info.Chart,
            music=info.Song,
            illustration=info.Picture,
            name=info.Name,
            level=info.Level,
            composer=info.Composer,
            charter=info.Charter
        )

    @classmethod
    def from_phira_info(cls, info: PhiraChartInfo) -> "ChartInfo":
        return cls(
            chart=info.chart,
            music=info.music,
            illustration=info.illustration,
            name=info.name,
            level=info.level,
            composer=info.composer,
            illustrator=info.illustrator,
            charter=info.charter
        )

    @classmethod
    def from_simphi_info(cls, info: SimPhiChartInfo) -> "ChartInfo":
        return cls(
            chart=info.Chart,
            music=info.Music,
            illustration=info.Image,
            name=info.Name,
            level=info.Level,
            composer=info.Artist,
            illustrator=info.Illustrator,
            charter=info.Charter
        )

    @classmethod
    def from_any(cls, info: Any):
        if isinstance(info, RPEChartInfo):
            return cls.from_rpe_info(info)
        elif isinstance(info, PhiraChartInfo):
            return cls.from_phira_info(info)
        elif isinstance(info, SimPhiChartInfo):
            return cls.from_simphi_info(info)
        else:
            raise TypeError(f"Unsupported info type: {type(info).__name__}")
