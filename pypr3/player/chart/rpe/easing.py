from typing import Callable


from pypr3.player.chart.easing import *
from pypr3.player.chart.rpe.model import EaseType


EASE_FUNCTIONS: dict[EaseType, Callable[[float], float]] = {
    EaseType.LINEAR: linear,
    EaseType.OUT_SINE: out_sine,
    EaseType.IN_SINE: in_sine,
    EaseType.OUT_QUAD: out_quad,
    EaseType.IN_QUAD: in_quad,
    EaseType.IN_OUT_SINE: in_out_sine,
    EaseType.IN_OUT_QUAD: in_out_quad,
    EaseType.OUT_CUBIC: out_cubic,
    EaseType.IN_CUBIC: in_cubic,
    EaseType.OUT_QUART: out_quart,
    EaseType.IN_QUART: in_quart,
    EaseType.IN_OUT_CUBIC: in_out_cubic,
    EaseType.IN_OUT_QUART: in_out_quart,
    EaseType.OUT_QUINT: out_quint,
    EaseType.IN_QUINT: in_quint,
    EaseType.OUT_EXPO: out_expo,
    EaseType.IN_EXPO: in_expo,
    EaseType.OUT_CIRC: out_circ,
    EaseType.IN_CIRC: in_circ,
    EaseType.OUT_BACK: out_back,
    EaseType.IN_BACK: in_back,
    EaseType.IN_OUT_CIRC: in_out_circ,
    EaseType.IN_OUT_BACK: in_out_back,
    EaseType.OUT_ELASTIC: out_elastic,
    EaseType.IN_ELASTIC: in_elastic,
    EaseType.OUT_BOUNCE: out_bounce,
    EaseType.IN_BOUNCE: in_bounce,
    EaseType.IN_OUT_BOUNCE: in_out_bounce,
    EaseType.IN_OUT_ELASTIC: in_out_elastic,
}
