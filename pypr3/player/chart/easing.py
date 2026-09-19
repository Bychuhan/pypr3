import math
from typing import Callable


def linear(t: float) -> float:
    return t


def in_sine(t: float) -> float:
    return 1 - math.cos((t * math.pi) / 2)


def out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2)


def in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def in_quad(t: float) -> float:
    return t ** 2


def out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


def in_out_quad(t: float) -> float:
    return 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def in_cubic(t: float) -> float:
    return t ** 3


def out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def in_out_cubic(t: float) -> float:
    return 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def in_quart(t: float) -> float:
    return t ** 4


def out_quart(t: float) -> float:
    return 1 - (1 - t) ** 4


def in_out_quart(t: float) -> float:
    return 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2


def in_quint(t: float) -> float:
    return t ** 5


def out_quint(t: float) -> float:
    return 1 - (1 - t) ** 5


def in_out_quint(t: float) -> float:
    return 16 * (t ** 5) if t < 0.5 else 1 - (-2 * t + 2) ** 5 / 2


def in_expo(t: float) -> float:
    return 0 if t == 0 else 2 ** (10 * t - 10)


def out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def in_out_expo(t: float) -> float:
    return 0 if t == 0 else 1 if t == 1 else 2 ** (20 * t - 10) / 2 if t < 0.5 else (2 - 2 ** (-20 * t + 10)) / 2


def in_circ(t: float) -> float:
    return 1 - (1 - t ** 2) ** 0.5


def out_circ(t: float) -> float:
    return (1 - (t - 1) ** 2) ** 0.5


def in_out_circ(t: float) -> float:
    return (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2


def in_back(t: float) -> float:
    return 2.70158 * (t ** 3) - 1.70158 * (t ** 2)


def out_back(t: float) -> float:
    return 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2)


def in_out_back(t: float) -> float:
    return ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2


def in_elastic(t: float) -> float:
    return 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3)))


def out_elastic(t: float) -> float:
    return 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1)


def in_out_elastic(t: float) -> float:
    return 0 if t == 0 else (1 if t == 1 else (-2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 + 1)


def in_bounce(t: float) -> float:
    return 1 - (7.5625 * ((1 - t) ** 2) if ((1 - t) < 1 / 2.75) else (7.5625 * ((1 - t) - (1.5 / 2.75)) * ((1 - t) - (1.5 / 2.75)) + 0.75 if ((1 - t) < 2 / 2.75) else (7.5625 * ((1 - t) - (2.25 / 2.75)) * ((1 - t) - (2.25 / 2.75)) + 0.9375 if ((1 - t) < 2.5 / 2.75) else (7.5625 * ((1 - t) - (2.625 / 2.75)) * ((1 - t) - (2.625 / 2.75)) + 0.984375))))


def out_bounce(t: float) -> float:
    return 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375)))


def in_out_bounce(t: float) -> float:
    return (1 - (7.5625 * ((1 - 2 * t) ** 2) if ((1 - 2 * t) < 1 / 2.75) else (7.5625 * ((1 - 2 * t) - (1.5 / 2.75)) * ((1 - 2 * t) - (1.5 / 2.75)) + 0.75 if ((1 - 2 * t) < 2 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.25 / 2.75)) * ((1 - 2 * t) - (2.25 / 2.75)) + 0.9375 if ((1 - 2 * t) < 2.5 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.625 / 2.75)) * ((1 - 2 * t) - (2.625 / 2.75)) + 0.984375))))) / 2 if t < 0.5 else (1 + (7.5625 * ((2 * t - 1) ** 2) if ((2 * t - 1) < 1 / 2.75) else (7.5625 * ((2 * t - 1) - (1.5 / 2.75)) * ((2 * t - 1) - (1.5 / 2.75)) + 0.75 if ((2 * t - 1) < 2 / 2.75) else (7.5625 * ((2 * t - 1) - (2.25 / 2.75)) * ((2 * t - 1) - (2.25 / 2.75)) + 0.9375 if ((2 * t - 1) < 2.5 / 2.75) else (7.5625 * ((2 * t - 1) - (2.625 / 2.75)) * ((2 * t - 1) - (2.625 / 2.75)) + 0.984375))))) / 2


def clamp_ease(ease_func: Callable[[float], float], left: float, right: float) -> Callable[[float], float]:
    if left == 0 and right == 1:
        return ease_func

    a = ease_func(left)
    b = ease_func(right)
    return lambda t: (ease_func(left + (right - left) * t) - a) / (b - a)


class CubicBezier:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, resolution: int = 64):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.resolution = resolution
        self._build_table()

    def _build_table(self):
        self._xs: list[float] = []
        self._ys: list[float] = []
        for i in range(self.resolution + 1):
            t = i / self.resolution
            self._xs.append(self._bezier_x(t))
            self._ys.append(self._bezier_y(t))

    def _bezier_x(self, t: float) -> float:
        return 3 * (1 - t) ** 2 * t * self.x1 + 3 * (1 - t) * t ** 2 * self.x2 + t ** 3

    def _bezier_y(self, t: float) -> float:
        return 3 * (1 - t) ** 2 * t * self.y1 + 3 * (1 - t) * t ** 2 * self.y2 + t ** 3

    def __call__(self, x: float) -> float:
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0

        lo, hi = 0, self.resolution
        while lo < hi:
            mid = (lo + hi) // 2
            if self._xs[mid] < x:
                lo = mid + 1
            else:
                hi = mid

        i = max(0, lo - 1)
        x0, x1 = self._xs[i], self._xs[i + 1]
        y0, y1 = self._ys[i], self._ys[i + 1]

        if x1 == x0:
            return y0

        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
