from typing import Callable


from pypr3.player.chart.easing import *
from pypr3.player.chart.phi.model import EaseType


EASE_FUNCTIONS: dict[EaseType, Callable[[float], float]] = {
    EaseType.LINEAR: linear,
    EaseType.IN_SINE: in_sine,
    EaseType.OUT_SINE: out_sine,
    EaseType.IN_OUT_SINE: in_out_sine,
    EaseType.IN_CUBIC: in_cubic,
    EaseType.OUT_CUBIC: out_cubic,
    EaseType.IN_OUT_CUBIC: in_out_cubic,
    EaseType.IN_QUINT: in_quint,
    EaseType.OUT_QUINT: out_quint,
    EaseType.IN_OUT_QUINT: in_out_quint,
    EaseType.IN_CIRC: in_circ,
    EaseType.OUT_CIRC: out_circ,
    EaseType.IN_OUT_CIRC: in_out_circ,
    EaseType.ZERO: zero,
    EaseType.ONE: one,
}
