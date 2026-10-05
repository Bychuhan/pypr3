from typing import Callable


from pypr3.player.chart.easing import *
from pypr3.player.chart.phi.model import EaseType


EASE_FUNCTIONS: dict[EaseType, Callable[[float], float]] = {
    EaseType.LINEAR: linear,
    EaseType.IN_QUAD: in_quad,
    EaseType.OUT_QUAD: out_quad,
    EaseType.IN_OUT_QUAD: in_out_quad,
    EaseType.IN_CUBIC: in_cubic,
    EaseType.OUT_CUBIC: out_cubic,
    EaseType.IN_OUT_CUBIC: in_out_cubic,
    EaseType.IN_QUART: in_quart,
    EaseType.OUT_QUART: out_quart,
    EaseType.IN_OUT_QUART: in_out_quart,
    EaseType.IN_QUINT: in_quint,
    EaseType.OUT_QUINT: out_quint,
    EaseType.IN_OUT_QUINT: in_out_quint,
    EaseType.ZERO: zero,
    EaseType.ONE: one,
}
