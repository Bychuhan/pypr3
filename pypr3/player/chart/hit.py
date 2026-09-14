import random
import math

from pypr3.renderer import Renderer
from pypr3.utils import rotate_translate


HIT_SIZE = 0.193848
HIT_COLOR = (255/255, 236/255, 160/255)
HIT_ALPHA = 225/255
HIT_DURATION = 0.5

HIT_GRID_SIZE = (6, 5)  # w, h
HIT_FRAME_COUNT = HIT_GRID_SIZE[0] * HIT_GRID_SIZE[1]

PARTICLE_SIZE = 0.024
PARTICLE_NUM = 4
PARTICLE_DISTANCE = (0.142578125, 0.190625)
PARTICLE_TIME_OFFSET = 0.015


def particle_easing(t: float): return ((850.3997391752 * t + 6236.3848902154) *
                                       t + 80.3542231806) * t / ((6570.5817658876 * t + 495.7977913926) * t + 1.0)


def particle_size_easing(t: float): return (
    (0.20783014 * t - 1.65243926) * t + 1.6398785) * t + 0.49884492


def particle_alpha(t: float): return 1 - t


class HitParticle:
    def __init__(self, pos_rotation: float, distance: float, start_time: float) -> None:
        self.max_distance = distance
        self.x_distance = math.cos(pos_rotation)
        self.y_distance = math.sin(pos_rotation)

        self.start_time = start_time
        self.now_time = 0

    def update(self, time: float):
        self.now_time = time - self.start_time

    def render(self, base_x: float, base_y: float, renderer: Renderer, screen_size: tuple[int, int]):
        w = screen_size[0]

        if (0 <= self.now_time < 0.5):
            progress = self.now_time / 0.5

            now_distance = particle_easing(progress) * self.max_distance

            x = base_x + now_distance * self.x_distance * w
            y = base_y + now_distance * self.y_distance * w

            alpha = particle_alpha(progress)
            size = particle_size_easing(progress) * PARTICLE_SIZE * w

            renderer.hit_renderer.add_particle(
                x=x, y=y,
                color=(*HIT_COLOR, alpha), size=size
            )


class Hit:
    _counter = 0

    def __init__(self, x: float, start_time: float, line_x: float, line_y: float, line_r: float,):
        self.x = x
        self.start_time = start_time

        self.line_x = line_x
        self.line_y = line_y
        self.line_r = line_r

        self.now_time: float = 0
        self.frame: int = 0

        seed = hash((self.start_time, self.x, Hit._counter))
        rng = random.Random(seed)
        Hit._counter += 1

        self.particles = [
            HitParticle(
                pos_rotation=rng.random() * (math.pi * 2),
                distance=rng.uniform(
                    PARTICLE_DISTANCE[0], PARTICLE_DISTANCE[1]),
                start_time=self.start_time + i * PARTICLE_TIME_OFFSET
            ) for i in range(PARTICLE_NUM)
        ]

        self.duration = (HIT_DURATION +
                         (len(self.particles) - 1) * PARTICLE_TIME_OFFSET)

    def update(self, time: float) -> bool:
        self.now_time = (time - self.start_time)

        if self.now_time < 0:
            return True

        if (self.now_time >= self.duration):
            return True

        self.frame = int(self.now_time / HIT_DURATION * HIT_FRAME_COUNT)
        self.frame = min(self.frame, HIT_FRAME_COUNT - 1)

        for particle in self.particles:
            particle.update(time)

        return False

    def render(self,  renderer: Renderer, screen_size: tuple[int, int]):
        w, h = screen_size

        x, y = rotate_translate(
            self.line_x * w, self.line_y * h, self.line_r,
            self.x * w, 0
        )

        for particle in self.particles:
            particle.render(x, y, renderer, screen_size)

        if 0 <= self.frame <= HIT_FRAME_COUNT - 1:
            progress = self.now_time / HIT_DURATION
            alpha = 1 - (progress * (1 - HIT_ALPHA))
            color = (*HIT_COLOR, alpha)

            renderer.hit_renderer.add_hit(
                x=x, y=y,
                color=color,
                frame=self.frame
            )
