from dataclasses import dataclass, field
from typing import Any, Callable
from collections import deque


from pypr3.player.chart import Chart
from pypr3.player.chart.hit import Hit, HIT_GRID_SIZE, HIT_SIZE
from pypr3.player.chart.rpe.model import *
from pypr3.player.chart.rpe.easing import EASE_FUNCTIONS
from pypr3.player.chart.easing import clamp_ease
from pypr3.player.chart.note import NoteRenderable
from pypr3.utils import rotate_translate
from pypr3.renderer import Renderer, TextureRegistry


RPE_SCREEN_WIDTH = 1350
RPE_SCREEN_HEIGHT = 900
SPEED_HEIGHT = 120 / RPE_SCREEN_HEIGHT

LINE_WIDTH = 4000 / RPE_SCREEN_WIDTH
LINE_HEIGHT = 5 / RPE_SCREEN_HEIGHT
LINE_DEFAULT_COLOR = (1, 1, 1)

NOTE_Z_ORDER = 1000
NOTE_COVER_FP = -1e-3


def init_bpm_list(bpm_list: list[BpmModel]) -> deque["BpmEvent"]:
    result: list[BpmEvent] = []

    sorted_list = sorted(bpm_list, key=lambda x: x.startTime.value)

    for index, model in enumerate(sorted_list):
        start_beat = (model.startTime if index > 0
                      else Beat(0, 0, 1))
        end_beat = (sorted_list[index + 1].startTime if index < len(sorted_list) - 1
                    else Beat(999999, 0, 1))

        result.append(BpmEvent(
            start_beat=start_beat,
            end_beat=end_beat,
            bpm=model.bpm
        ))

    return deque(result)


def convert_time(time: Beat, bpm_list: deque["BpmEvent"]) -> float:
    result = 0

    for bpm_event in bpm_list:
        if time.value >= bpm_event.end_beat.value:
            result += bpm_event.get_duration()
        else:
            result += bpm_event.get_time_at_beat(time)

            break

    return result


def convert_normal_event_value(value: float, event_type: "EventType") -> float:
    match event_type:
        case EventType.MOVEX:
            return value / RPE_SCREEN_WIDTH
        case EventType.MOVEY:
            return value / RPE_SCREEN_HEIGHT
        case EventType.ROTATE:
            return -value
        case EventType.ALPHA:
            return value / 255
        case EventType.SPEED:
            return value * SPEED_HEIGHT
        case EventType.PAINT:
            return value / RPE_SCREEN_HEIGHT
        case _:
            return value


def convert_event_value(value: Any, event_type: "EventType") -> Any:
    if event_type == EventType.COLOR:
        return tuple([i / 255 for i in value])
    elif event_type == EventType.TEXT:
        return value  # TODO
    else:
        return convert_normal_event_value(value, event_type)


def init_events(events: list[NormalEventModel] | list[ColorEventModel] | list[TextEventModel], bpm_list: deque["BpmEvent"], event_type: "EventType"):
    match event_type:
        case EventType.COLOR:
            event_object = ColorEvent
        case _:
            event_object = Event

    return deque([event_object(
        start_time=convert_time(event.startTime, bpm_list),
        end_time=convert_time(event.endTime, bpm_list),
        start=convert_event_value(event.start, event_type),
        end=convert_event_value(event.end, event_type),
        ease_func=clamp_ease(
            EASE_FUNCTIONS[event.easingType], event.easingLeft, event.easingRight)
    ) for event in sorted(events, key=lambda x: x.startTime.value)])


def init_speed_events(events: list[NormalEventModel], bpm_list: deque["BpmEvent"]) -> deque["SpeedEvent"]:
    result: list[SpeedEvent] = []

    fp: float = 0  # Floor position

    for index, data in enumerate(sorted(events, key=lambda x: x.startTime.value)):
        if index == 0:
            event = SpeedEvent(
                start_time=convert_time(Beat(-999999, 0, 1), bpm_list),
                end_time=convert_time(data.startTime, bpm_list),
                start=convert_event_value(data.start, EventType.SPEED),
                end=convert_event_value(data.start, EventType.SPEED),
                ease_func=EASE_FUNCTIONS[EaseType.LINEAR],
                fp_offset=fp
            )

            result.append(event)

            fp += event.get_event_fp()

        event = SpeedEvent(
            start_time=convert_time(data.startTime, bpm_list),
            end_time=convert_time(data.endTime, bpm_list),
            start=convert_event_value(data.start, EventType.SPEED),
            end=convert_event_value(data.end, EventType.SPEED),
            ease_func=clamp_ease(
                EASE_FUNCTIONS[data.easingType], data.easingLeft, data.easingRight),
            fp_offset=fp
        )

        result.append(event)

        fp += event.get_event_fp()

        next_beat = (Beat(999999, 0, 1) if index == len(
            events) - 1 else events[index + 1].startTime)

        if next_beat.value > data.endTime.value:
            event = SpeedEvent(
                start_time=convert_time(data.endTime, bpm_list),
                end_time=convert_time(next_beat, bpm_list),
                start=convert_event_value(data.end, EventType.SPEED),
                end=convert_event_value(data.end, EventType.SPEED),
                ease_func=EASE_FUNCTIONS[EaseType.LINEAR],
                fp_offset=fp
            )

            result.append(event)

            fp += event.get_event_fp()

    return deque(result)


def init_notes(line: "Line", notes: list[NoteModel]) -> list[list["Note"]]:
    all_notes = ([Note(line, note) for note in notes])

    speed_groups: dict[float, list[Note]] = {}
    for note in all_notes:
        speed_groups.setdefault(note.speed, []).append(note)

    return [sorted(group, key=lambda x: x.fp) for group in (speed_groups.values())]


@dataclass
class BpmEvent:
    start_beat: Beat
    end_beat: Beat
    bpm: float

    def get_duration(self):
        return 60 / self.bpm * (self.end_beat.value - self.start_beat.value)

    def get_time_at_beat(self, beat: Beat):
        return 60 / self.bpm * (beat.value - self.start_beat.value)


@dataclass
class Event:
    start_time: float
    end_time: float
    start: Any
    end: Any
    ease_func: Callable[[float], float]

    def get_value(self, time: float) -> Any:
        if self.start_time == self.end_time:
            progress = 1.0
        else:
            progress = ((time - self.start_time) /
                        (self.end_time - self.start_time))
            progress = min(progress, 1.0)

        try:
            ease_progress = self.ease_func(progress)
        except OverflowError:
            ease_progress = 0
        return (self.start + (self.end - self.start) * ease_progress).real

    def get_is_start(self, time: float) -> bool:
        return time >= self.start_time

    def get_is_end(self, time: float) -> bool:
        return time >= self.end_time


@dataclass
class ColorEvent(Event):
    start: tuple[float, float, float]
    end: tuple[float, float, float]

    def get_value(self, time: float) -> tuple[float, float, float]:
        if self.start_time == self.end_time:
            progress = 1.0
        else:
            progress = ((time - self.start_time) /
                        (self.end_time - self.start_time))
            progress = min(progress, 1.0)

        r = self.start[0] + (self.end[0] - self.start[0]
                             ) * self.ease_func(progress)
        g = self.start[1] + (self.end[1] - self.start[1]
                             ) * self.ease_func(progress)
        b = self.start[2] + (self.end[2] - self.start[2]
                             ) * self.ease_func(progress)

        return (r.real, g.real, b.real)


@dataclass
class SpeedEvent(Event):
    start: float
    end: float
    fp_offset: float

    _samples: int = 64
    _times: list[float] = field(default_factory=lambda: [])
    _fps: list[float] = field(default_factory=lambda: [])
    _is_linear: bool = True

    def __post_init__(self):
        self._is_linear = (self.ease_func == EASE_FUNCTIONS[EaseType.LINEAR])

        if self._is_linear:
            return

        dt = (self.end_time - self.start_time) / self._samples

        cumulative = 0.0
        prev_v = self.get_value(self.start_time)

        for i in range(self._samples + 1):
            t = self.start_time + i * dt
            v = self.get_value(t)

            if i > 0:
                cumulative += (prev_v + v) * dt / 2

            self._times.append(t)
            self._fps.append(cumulative)

            prev_v = v

    def get_fp(self, time: float) -> Any:
        if time <= self.start_time:
            return self.fp_offset
        if time >= self.end_time:
            return self.fp_offset + self.get_event_fp()

        if self._is_linear:
            if self.start_time == self.end_time:
                return self.fp_offset
            else:
                progress = ((time - self.start_time) /
                            (self.end_time - self.start_time))
                progress = min(progress, 1.0)

            top = self.start + (self.end - self.start) * progress

            return self.fp_offset + (self.start + top) * (time - self.start_time) / 2
        else:
            dt = (self.end_time - self.start_time) / self._samples
            idx = int((time - self.start_time) / dt)
            idx = min(idx, self._samples - 1)

            t0 = self._times[idx]
            t1 = self._times[idx + 1]
            fp0 = self._fps[idx]
            fp1 = self._fps[idx + 1]

            if t1 == t0:
                return self.fp_offset + fp0

            ratio = (time - t0) / (t1 - t0)

            return self.fp_offset + fp0 + (fp1 - fp0) * ratio

    def get_event_fp(self) -> float:
        if self._is_linear:
            return (self.start + self.end) * (self.end_time - self.start_time) / 2
        else:
            return self._fps[-1]

    def get_is_start(self, time: float) -> bool:
        return time >= self.start_time

    def get_is_end(self, time: float) -> bool:
        return time >= self.end_time


class Line:
    def __init__(self, data: JudgeLineModel, bpm_list: deque[BpmEvent]) -> None:
        self.bpm_factor = data.bpmfactor
        self.bpm_list = deque([BpmEvent(
            start_beat=event.start_beat,
            end_beat=event.end_beat,
            bpm=event.bpm / self.bpm_factor if self.bpm_factor else 0,
        ) for event in bpm_list])

        self.x_events = [init_events(layer.moveXEvents, self.bpm_list, EventType.MOVEX)
                         for layer in data.eventLayers if layer and layer.moveXEvents]
        self.y_events = [init_events(layer.moveYEvents, self.bpm_list, EventType.MOVEY)
                         for layer in data.eventLayers if layer and layer.moveYEvents]
        self.rotate_events = [init_events(layer.rotateEvents, self.bpm_list, EventType.ROTATE)
                              for layer in data.eventLayers if layer and layer.rotateEvents]
        self.alpha_events = [init_events(layer.alphaEvents, self.bpm_list, EventType.ALPHA)
                             for layer in data.eventLayers if layer and layer.alphaEvents]
        self.speed_events = [init_speed_events(layer.speedEvents, self.bpm_list)
                             for layer in data.eventLayers if layer and layer.speedEvents]

        self.x_scale_events = [init_events(layer, self.bpm_list, EventType.SCALEX)
                               for layer in [data.extended.scaleXEvents] if layer]
        self.y_scale_events = [init_events(layer, self.bpm_list, EventType.SCALEY)
                               for layer in [data.extended.scaleYEvents] if layer]
        self.color_events = [init_events(layer, self.bpm_list, EventType.COLOR)
                             for layer in [data.extended.colorEvents] if layer]

        self.notes = init_notes(
            self, [note for note in data.notes if note.type != NoteType.HOLD])
        self.holds = init_notes(
            self, [note for note in data.notes if note.type == NoteType.HOLD])
        self.is_cover = data.isCover == 1

        self.x: float = 0
        self.y: float = 0
        self.rotation: float = 0
        self.alpha: float = 0
        self.current_fp: float = 0

        self.x_scale: float = 1
        self.y_scale: float = 1
        self.color: tuple[float, float, float] = LINE_DEFAULT_COLOR

        self.father_index: int = data.father
        self.father_line: Line | None = None
        self.rotate_with_father: bool = data.rotateWithFather

        self.texture_file = data.Texture
        self.has_texture = self.texture_file != "line.png"
        self.texture_name = f"line.custom.{self.texture_file}" if self.has_texture else "none"

        self.anchor = data.anchor
        self.z_order = data.zOrder

        self.attach_ui_id = data.attachUI

        self.is_updated: bool = False

        self.hits: list[Hit] = []

    def post_init(self, lines: list["Line"]):
        if self.father_index != -1:
            self.father_line = lines[self.father_index]

    def _update_events(self, time: float, event_layers: list[deque[Event]] | list[deque[ColorEvent]] | list[deque[SpeedEvent]], default_value: Any = 0) -> Any:
        value = default_value

        for events in event_layers:
            while len(events) >= 2 and time >= events[1].start_time and (time >= events[0].end_time or not isinstance(events[0], SpeedEvent)):
                events.popleft()

            if events:
                if isinstance(events[0], SpeedEvent):
                    value += events[0].get_fp(time)
                elif isinstance(events[0], ColorEvent):
                    event_value = events[0].get_value(time)
                    value = (
                        value[0] + event_value[0],
                        value[1] + event_value[1],
                        value[2] + event_value[2],
                    )
                else:
                    value += events[0].get_value(time)

        return value

    def _update_notes(self, time: float):
        for group in self.holds.copy():
            for note in group.copy():
                if note.update(time):
                    group.remove(note)

                if note.should_spawn_hit:
                    self.hits.append(Hit(
                        x=note.x_pos, y=note.hit_y, start_time=note.hit_time,
                        line_x=self.x, line_y=self.y, line_r=self.rotation
                    ))

                if note.base_fp * note.base_speed > 2:  # TODO
                    break

            if not group:
                self.holds.remove(group)

        for group in self.notes.copy():
            for note in group.copy():
                if note.update(time):
                    group.remove(note)

                if note.should_spawn_hit:
                    self.hits.append(Hit(
                        x=note.x_pos, y=note.hit_y, start_time=note.hit_time,
                        line_x=self.x, line_y=self.y, line_r=self.rotation
                    ))

                if note.base_fp * note.base_speed > 2:  # TODO
                    break

            if not group:
                self.notes.remove(group)

    def _update_hits(self, time: float):
        for hit in self.hits.copy():
            if hit.update(time):
                self.hits.remove(hit)

    def render_holds(self, renderer: Renderer, screen_size: tuple[int, int]):
        if self.alpha < 0:
            return

        for group in self.holds:
            for note in group:
                if note.base_fp * note.base_speed > 2:  # TODO
                    break

                note.render(renderer, screen_size)

    def render_notes(self, renderer: Renderer, screen_size: tuple[int, int]):
        if self.alpha < 0:
            return

        for group in self.notes:
            for note in group:
                if note.base_fp * note.base_speed > 2:  # TODO
                    break

                note.render(renderer, screen_size)

    def render_hits(self, renderer: Renderer, screen_size: tuple[int, int]):
        for hit in self.hits.copy():
            hit.render(renderer, screen_size)

    def get_fp(self, time: float):  # Get floor position
        result: float = 0

        for layer in self.speed_events:
            first, last = 0, len(layer) - 1

            mid = 0
            while first <= last:
                mid = (first + last) // 2
                event = layer[mid]

                if event.start_time <= time < event.end_time:
                    result += event.get_fp(time)

                    break
                elif event.start_time > time:
                    last = mid - 1
                else:  # time >= event.end_time
                    first = mid + 1
            else:
                result += layer[-1].get_fp(time)

        return result

    def update(self, time: float, screen_size: tuple[int, int]):
        if self.is_updated:
            return

        if self.x_events:
            self.x = self._update_events(time, self.x_events)
        if self.y_events:
            self.y = self._update_events(time, self.y_events)
        if self.rotate_events:
            self.rotation = self._update_events(time, self.rotate_events)

        if self.father_line:
            self.father_line.update(time, screen_size)

            w, h = screen_size

            self.x, self.y = rotate_translate(
                self.father_line.x * w, self.father_line.y * h, self.father_line.rotation,
                self.x * w, self.y * h
            )
            self.x /= w
            self.y /= h

            if self.rotate_with_father:
                self.rotation += self.father_line.rotation

        if self.alpha_events:
            self.alpha = self._update_events(time, self.alpha_events)
        if self.speed_events:
            self.current_fp = self._update_events(time, self.speed_events)

        if self.x_scale_events:
            self.x_scale = self._update_events(time, self.x_scale_events)
        if self.y_scale_events:
            self.y_scale = self._update_events(time, self.y_scale_events)
        if self.color_events:
            self.color = self._update_events(
                time, self.color_events, (0, 0, 0))

        self._update_notes(time)

        self._update_hits(time)

        self.is_updated = True

    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        if self.alpha <= 0:
            return

        w, h = screen_size

        if self.attach_ui_id != AttachUIId.NONE:
            return

        if self.has_texture:
            texture = TextureRegistry.get(self.texture_name)
            texture_scale = h / RPE_SCREEN_HEIGHT

            if texture:
                renderer.render_texture(
                    screen_size=screen_size,
                    texture=texture,
                    x=self.x * w,
                    y=self.y * h,
                    w_scale=texture_scale * self.x_scale,
                    h_scale=texture_scale * self.y_scale,
                    rotation=self.rotation,
                    anchor=self.anchor,
                    color=(*self.color, self.alpha)
                )

        else:
            renderer.render_rect(
                screen_size=screen_size,
                x=self.x * w,
                y=self.y * h,
                width=LINE_WIDTH * w * self.x_scale,
                height=LINE_HEIGHT * h * self.y_scale,
                rotation=self.rotation,
                anchor=self.anchor,
                color=(*self.color, self.alpha)
            )


class Note(NoteRenderable):
    _HITSOUND_MAP: dict[NoteType, str] = {
        NoteType.TAP: "hitsound.tap",
        NoteType.DRAG: "hitsound.drag",
        NoteType.HOLD: "hitsound.hold",
        NoteType.FLICK: "hitsound.flick"
    }

    _NORMAL_TEXTURE_MAP: dict[NoteType, tuple[str, str, str]] = {
        NoteType.TAP: ("note.tap", "none", "none"),
        NoteType.DRAG: ("note.drag", "none", "none"),
        NoteType.HOLD: ("note.hold.head", "note.hold.body", "note.hold.tail"),
        NoteType.FLICK: ("note.flick", "none", "none")
    }

    _HIGHLIGHT_TEXTURE_MAP: dict[NoteType, tuple[str, str, str]] = {
        NoteType.TAP: ("note.tap.hl", "none", "none"),
        NoteType.DRAG: ("note.drag.hl", "none", "none"),
        NoteType.HOLD: ("note.hold.head.hl", "note.hold.body.hl", "note.hold.tail.hl"),
        NoteType.FLICK: ("note.flick.hl", "none", "none")
    }

    def __init__(self, line: Line, data: NoteModel) -> None:
        super().__init__()

        self.line = line

        self.type: NoteType = data.type
        self.time = convert_time(data.startTime, self.line.bpm_list)
        self.end_time = convert_time(data.endTime, self.line.bpm_list)
        self.x_pos = data.positionX / RPE_SCREEN_WIDTH
        self.is_above = data.above == 1
        self.y_offset = data.yOffset / RPE_SCREEN_HEIGHT

        self.direction = 1 if self.is_above else -1

        self.base_speed = data.speed
        self.speed: float = self.base_speed * self.direction

        self.fp = self.line.get_fp(self.time) + self.y_offset
        self.base_fp = self.fp
        self.current_fp = self.base_fp * self.speed
        if self.type == NoteType.HOLD:
            self.end_fp = self.line.get_fp(self.end_time) + self.y_offset
            self.length = (self.end_fp - self.fp) * self.speed
            self.base_end_fp = self.end_fp
            self.current_end_fp = self.base_end_fp * self.speed
        else:
            self.end_fp = 0
            self.length = 0
            self.base_end_fp = 0
            self.current_end_fp = 0

        self.is_hited: bool = False
        self.is_real = not data.isFake

        self.width = data.size
        self.visible_time = self.time - data.visibleTime
        self.is_visible = False
        self.color: tuple[float, float, float, float] = (
            data.tint[0] / 255,
            data.tint[1] / 255,
            data.tint[2] / 255,
            data.alpha / 255,
        )
        self.hit_color: tuple[float, float, float, float] = (
            data.tintHitEffects[0] / 255,
            data.tintHitEffects[1] / 255,
            data.tintHitEffects[2] / 255,
            1,
        )

        self.should_spawn_hit: bool = False
        self.hit_time: float = 0
        self.hold_next_spawn_hit_time = self.time + 0.15  # TODO
        self.hit_y = self.y_offset * self.speed

    def update(self, time: float) -> bool:
        self.should_spawn_hit = False

        if time >= self.visible_time:
            self.is_visible = True

        if self.type == NoteType.HOLD:
            self.base_end_fp = self.end_fp - self.line.current_fp
            self.current_end_fp = self.base_end_fp * self.speed

        if time >= self.time:
            self.base_fp = self.y_offset
            self.current_fp = self.y_offset * self.speed

            if not self.is_hited:
                self.is_hited = True

                if self.is_real:
                    if self.hitsound:
                        self.hitsound.play()

                    self.should_spawn_hit = True
                    self.hit_time = self.time

            if self.type == NoteType.HOLD and time < self.end_time:
                self.length = self.current_end_fp - self.current_fp

                if self.is_real and time >= self.hold_next_spawn_hit_time:
                    self.should_spawn_hit = True
                    self.hit_time = self.hold_next_spawn_hit_time

                    self.hold_next_spawn_hit_time += 0.15  # TODO

                return False
            else:
                return True
        else:
            self.base_fp = self.fp - self.line.current_fp
            self.current_fp = self.base_fp * self.speed

        return False

    def render(self, renderer: Renderer, screen_size: tuple[int, int]) -> None:
        cover_fp = (self.base_end_fp if self.type == NoteType.HOLD
                    else self.base_fp)
        if (self.line.is_cover and cover_fp < NOTE_COVER_FP and not self.is_hited):
            return
        if self.base_fp * self.base_speed > 2:  # TODO
            return
        if not self.is_visible:
            return

        if not self.textures:
            return

        w, h = screen_size
        x, y = rotate_translate(
            self.line.x * w, self.line.y * h, self.line.rotation,
            self.x_pos * w, self.current_fp * h
        )

        if self.type == NoteType.HOLD:
            self._render_hold(renderer, screen_size, x, y)
        else:
            self._render_texture(renderer, screen_size, 0, x, y,
                                 w_scale=self.width, color=self.color, rotation=self.line.rotation)

    def _render_hold(self, renderer: Renderer, screen_size: tuple[int, int], x: float, y: float) -> None:
        w, h = screen_size

        hold_direction = 1 if self.length >= 0 else -1

        # Head
        if not self.is_hited:
            if not self._render_texture(renderer, screen_size, 0, x, y, w_scale=self.width,
                                        h_scale=hold_direction, rotation=self.line.rotation,
                                        color=self.color, anchor=(0.5, 1)):
                return

        # Body
        tex_w, _ = self._texture_sizes[1]
        if not self._render_texture(renderer, screen_size, 1, x, y,
                                    w_scale=self.width, h_scale=self.length * h, rotation=self.line.rotation,
                                    color=self.color, anchor=(0.5, 0), size_override=(round(tex_w * w), 1)):
            return

        # Tail
        end_x, end_y = rotate_translate(
            x, y, self.line.rotation, 0, self.length * h)
        self._render_texture(renderer, screen_size, 2, end_x, end_y, w_scale=self.width,
                             color=self.color, h_scale=hold_direction, rotation=self.line.rotation, anchor=(0.5, 0))


class RpeChart(Chart):
    def __init__(self, data: RpeChartModel) -> None:
        self.meta = data.META

        self.offset = self.meta.offset / 1000
        self.bpm_list = init_bpm_list(data.BPMList)

        self.lines = [Line(line_model, self.bpm_list)
                      for line_model in data.judgeLineList]

        self.back_lines: list[Line] = [
            line for line in self.lines if line.z_order < NOTE_Z_ORDER]
        self.front_lines: list[Line] = [
            line for line in self.lines if line.z_order >= NOTE_Z_ORDER]

        self.back_lines.sort(key=lambda x: x.z_order)
        self.front_lines.sort(key=lambda x: x.z_order)

        for line in self.lines:
            line.post_init(self.lines)

        self._init_note_assets()

    def _init_note_assets(self) -> None:
        time_groups: dict[float, list[Note]] = {}

        for line in self.lines:
            for group in line.notes:
                for note in group:
                    time_groups.setdefault(note.time, []).append(note)

            for group in line.holds:
                for hold in group:
                    time_groups.setdefault(hold.time, []).append(hold)

        for notes in time_groups.values():
            for note in notes:
                note.is_highlight = len(notes) > 1

                note.init_assets()

    def update(self, time: float, screen_size: tuple[int, int]):
        chart_time = time - self.offset

        for line in self.lines:
            line.is_updated = False

        for line in self.lines:
            line.update(chart_time, screen_size)

    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        w = screen_size[0]

        for line in self.back_lines:
            line.render(renderer, screen_size)

        for line in self.lines:
            line.render_holds(renderer, screen_size)

        for line in self.lines:
            line.render_notes(renderer, screen_size)

        hit_renderer = renderer.hit_renderer
        hit_renderer.clear()

        for line in self.lines:
            line.render_hits(renderer, screen_size)

        hit_renderer.render_particles(
            screen_size=screen_size
        )

        texture = TextureRegistry.get("hit_fx")

        if texture:
            hit_renderer.render_hits(
                screen_size=screen_size,
                texture=texture,
                grid_size=HIT_GRID_SIZE,
                texture_size=(round(HIT_SIZE * w), round(HIT_SIZE * w))
            )

        for line in self.front_lines:
            line.render(renderer, screen_size)

    @classmethod
    def from_any(cls, data: Any) -> "RpeChart":
        if isinstance(data, dict):
            return cls(data=RpeChartModel.model_validate(data))
        else:
            raise TypeError(f"Expected dict, got {type(data).__name__}")

    def get_texture_assets(self) -> list[tuple[str, str]]:
        textures: list[tuple[str, str]] = []
        for line in self.lines:
            if line.has_texture:
                textures.append(
                    (line.texture_name, line.texture_file)
                )

        return list(dict.fromkeys(textures))
