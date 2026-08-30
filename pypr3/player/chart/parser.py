from typing import Any


from pypr3.player.chart import Chart
from pypr3.player.chart.phi.objs import PhiChart
from pypr3.player.chart.rpe.objs import RpeChart


class ChartParser:
    @staticmethod
    def from_dict(data: dict[Any, Any]) -> Chart:
        chart_type: type[Chart]
        if "META" in data:
            chart_type = RpeChart
        elif "formatVersion" in data:
            chart_type = PhiChart
        else:
            raise ValueError(f"Unknown chart format: {list(data.keys())}")

        return chart_type.from_any(data)
