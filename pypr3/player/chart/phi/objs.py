from enum import IntEnum
from collections import deque
from dataclasses import dataclass


from pypr3.player.chart import Chart
from pypr3.player.chart.phi.model import PhiChartModel, JudgeLineModel, EventModel
from pypr3.renderer import Renderer


LINE_WIDTH = 5.76
LINE_HEIGHT = 0.0075


def convert_time(time: int, bpm: float) -> float:
    return 1.875 / bpm * time


def convert_event_value(value: float, event_type: "EventType") -> float:
    if event_type == EventType.MOVE:
        return value - 0.5
    return value


def init_events(events: list[EventModel], bpm: float, event_type: "EventType") -> deque["Event"]:
    return deque([Event(
        start_time=convert_time(event.startTime, bpm),
        end_time=convert_time(event.endTime, bpm),
        start=convert_event_value(event.start, event_type),
        end=convert_event_value(event.end, event_type),
        start2=convert_event_value(event.start2, event_type),
        end2=convert_event_value(event.end2, event_type),
    ) for event in events])


class EventType(IntEnum):
    MOVE = 0
    ROTATE = 1
    DISAPPEAR = 2


@dataclass
class Event:
    start_time: float
    end_time: float
    start: float
    end: float
    start2: float = 0
    end2: float = 0

    def get_single_value(self, time: float) -> float:
        return self.start + (self.end - self.start) * self.get_progress(time)

    def get_move_value(self, time: float) -> tuple[float, float]:
        progress = self.get_progress(time)

        return (
            self.start + (self.end - self.start) * progress,
            self.start2 + (self.end2 - self.start2) * progress,
        )

    def get_progress(self, time: float) -> float:
        if self.start_time == self.end_time:
            return 1
        return (time - self.start_time) / (self.end_time - self.start_time)

    def get_is_end(self, time: float) -> bool:
        return time >= self.end_time


class Line:
    def __init__(self, data: JudgeLineModel) -> None:
        self.bpm = data.bpm
        self.move_events = init_events(
            data.judgeLineMoveEvents, self.bpm, EventType.MOVE)
        self.rotate_events = init_events(
            data.judgeLineRotateEvents, self.bpm, EventType.ROTATE)
        self.disappear_events = init_events(
            data.judgeLineDisappearEvents, self.bpm, EventType.DISAPPEAR)

        self.x: float = 0
        self.y: float = 0
        self.rotation: float = 0
        self.alpha: float = 0

    def _update_events(self, time: float, events: deque[Event], event_type: EventType) -> None:
        while events and events[0].get_is_end(time):
            events.popleft()

        if events:
            match event_type:
                case EventType.MOVE:
                    self.x, self.y = events[0].get_move_value(time)
                case EventType.ROTATE:
                    self.rotation = events[0].get_single_value(time)
                case EventType.DISAPPEAR:
                    self.alpha = events[0].get_single_value(time)
                case _:
                    pass

    def update(self, time: float):
        self._update_events(time, self.move_events, EventType.MOVE)
        self._update_events(time, self.rotate_events, EventType.ROTATE)
        self._update_events(time, self.disappear_events, EventType.DISAPPEAR)

    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        w, h = screen_size

        renderer.render_rect(
            screen_size=screen_size,
            x=self.x * w,
            y=self.y * h,
            width=LINE_WIDTH * h,
            height=LINE_HEIGHT * h,
            rotation=self.rotation,
            color=(1, 1, 1, self.alpha)
        )


class PhiChart(Chart):
    def __init__(self, data: PhiChartModel) -> None:
        self.lines = [Line(line_model) for line_model in data.judgeLineList]

    def update(self, time: float):
        for line in self.lines:
            line.update(time)

    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        for line in self.lines:
            line.render(renderer, screen_size)
