import math


def rotate_translate(x: float, y: float, rotation: float, dx: float, dy: float) -> tuple[float, float]:
    result_x, result_y = x, y

    if dx:
        r = math.radians(rotation)
        result_x += math.cos(r) * dx
        result_y += math.sin(r) * dx

    if dy:
        r = math.radians(rotation + 90)
        result_x += math.cos(r) * dy
        result_y += math.sin(r) * dy

    return result_x, result_y
