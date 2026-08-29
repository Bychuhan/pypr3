from collections import deque
from dataclasses import dataclass


import moderngl as mgl


from pypr3.audio.registry import SoundRegistry
from pypr3.player.chart import Chart, Hit
from pypr3.player.chart.phi.model import *
from pypr3.renderer import Renderer, TextureRegistry
from pypr3.audio import DirectSound
from pypr3.utils import rotate_translate


LINE_WIDTH = 5.76
LINE_HEIGHT = 0.0075

SPEED_HEIGHT = 0.6

NOTE_X = 0.05625
NOTE_COVER_FP = -1e-3
NOTE_MAX_VISIBLE_FP = 2
NOTE_TEXTURE_WIDTH = 0.123


def convert_time(time: float, bpm: float) -> float:
    return 1.875 / bpm * time


def convert_event_value(value: float, event_type: "EventType") -> float:
    if event_type == EventType.MOVE:
        return value - 0.5
    if event_type == EventType.SPEED:
        return value * SPEED_HEIGHT
    return value


def init_events(events: list[EventModel], bpm: float, event_type: "EventType") -> deque["Event"]:
    return deque([Event(
        start_time=convert_time(event.startTime, bpm),
        end_time=convert_time(event.endTime, bpm),
        start=convert_event_value(event.start, event_type),
        end=convert_event_value(event.end, event_type),
        start2=convert_event_value(event.start2, event_type),
        end2=convert_event_value(event.end2, event_type),
    ) for event in sorted(events, key=lambda x: x.startTime)])


def init_speed_events(events: list[SpeedEventModel], bpm: float) -> deque["Event"]:
    result: list[Event] = []

    fp = 0  # Floor position
    for event in sorted(events, key=lambda x: x.startTime):
        start_time = convert_time(event.startTime, bpm)
        end_time = convert_time(event.endTime, bpm)
        value = convert_event_value(event.value, EventType.SPEED)

        event_fp = value * (end_time - start_time)

        result.append(
            Event(
                start_time=start_time,
                end_time=end_time,
                start=fp,
                end=fp + event_fp
            )
        )

        fp += event_fp

    return deque(result)


def init_notes(line: "Line", above_notes: list[NoteModel], below_notes: list[NoteModel]) -> tuple[list[list["Note"]], list["Note"]]:
    all_notes = ([Note(line, note, True) for note in above_notes] +
                 [Note(line, note, False) for note in below_notes])

    holds: list[Note] = []

    speed_groups: dict[float, list[Note]] = {}
    for note in all_notes:
        if note.type == NoteType.OTHER:
            continue
        elif note.type == NoteType.HOLD:
            holds.append(note)
        else:
            speed_groups.setdefault(note.speed, []).append(note)

    holds.sort(key=lambda x: x.fp)

    return [sorted(group, key=lambda x: x.fp) for group in (speed_groups.values())], holds


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
        self.speed_events = init_speed_events(data.speedEvents, self.bpm)

        self.notes, self.holds = init_notes(
            self, data.notesAbove, data.notesBelow)

        self.x: float = 0
        self.y: float = 0
        self.rotation: float = 0
        self.alpha: float = 0
        self.current_fp: float = 0

        self.hits: list[Hit] = []

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
                case EventType.SPEED:
                    self.current_fp = events[0].get_single_value(time)
                case _:
                    pass

    def _update_notes(self, time: float):
        for note in self.holds.copy():
            if note.update(time):
                self.holds.remove(note)

            if note.should_spawn_hit:
                self.hits.append(Hit(
                    x=note.x_pos, start_time=note.hit_time,
                    line_x=self.x, line_y=self.y, line_r=self.rotation
                ))

            if note.base_fp > NOTE_MAX_VISIBLE_FP:
                break

        for group in self.notes.copy():
            for note in group.copy():
                if note.update(time):
                    group.remove(note)

                if note.should_spawn_hit:
                    self.hits.append(Hit(
                        x=note.x_pos, start_time=note.hit_time,
                        line_x=self.x, line_y=self.y, line_r=self.rotation
                    ))

                if note.base_fp * note.base_speed > NOTE_MAX_VISIBLE_FP:
                    break

            if not group:
                self.notes.remove(group)

    def _update_hits(self, time: float):
        for hit in self.hits.copy():
            if hit.update(time):
                self.hits.remove(hit)

    def render_holds(self, renderer: Renderer, screen_size: tuple[int, int]):
        for note in self.holds:
            if note.base_fp > NOTE_MAX_VISIBLE_FP:
                break

            note.render(renderer, screen_size)

    def render_notes(self, renderer: Renderer, screen_size: tuple[int, int]):
        for group in self.notes:
            for note in group:
                if note.base_fp * note.base_speed > NOTE_MAX_VISIBLE_FP:
                    break

                note.render(renderer, screen_size)

    def render_hits(self, renderer: Renderer, screen_size: tuple[int, int]):
        for hit in self.hits.copy():
            hit.render(renderer, screen_size)

    def get_fp(self, time: float):  # Get floor position
        first, last = 0, len(self.speed_events) - 1

        mid = 0
        while first <= last:
            mid = (first + last) // 2
            event = self.speed_events[mid]

            if event.start_time <= time < event.end_time:
                return event.get_single_value(time)
            elif event.start_time > time:
                last = mid - 1
            else:  # time >= event.end_time
                first = mid + 1

        return self.speed_events[-1].get_single_value(time)

    def update(self, time: float):
        self._update_events(time, self.move_events, EventType.MOVE)
        self._update_events(time, self.rotate_events, EventType.ROTATE)
        self._update_events(time, self.disappear_events, EventType.DISAPPEAR)
        self._update_events(time, self.speed_events, EventType.SPEED)

        self._update_notes(time)

        self._update_hits(time)

    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        if self.alpha <= 0:
            return

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


class Note:
    _HITSOUND_MAP = {
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

    def __init__(self, line: Line, data: NoteModel, is_above: bool) -> None:
        self.line = line

        self.type = data.type
        self.time = convert_time(data.time, self.line.bpm)
        self.x_pos = data.positionX * NOTE_X
        self.hold_time = convert_time(data.holdTime, self.line.bpm)
        self.fp = self.line.get_fp(self.time)

        self.direction = 1 if is_above else -1

        if self.type == NoteType.HOLD:
            self.base_speed = 1
            self.hold_speed = data.speed * SPEED_HEIGHT * self.direction
            self.hold_direction = 1 if self.hold_speed >= 0 else -1
        else:
            self.base_speed = data.speed
            self.hold_speed = 0
            self.hold_direction = 0

        self.speed: float = self.base_speed * self.direction

        self.base_fp = self.fp
        self.current_fp = self.base_fp * self.speed

        self.is_visible = self._get_is_visible()
        self.is_hited: bool = False

        if self.type == NoteType.HOLD:
            self.length = self.hold_speed * self.hold_time
            self.end_time = self.time + self.hold_time
        else:
            self.length = 0
            self.end_time = 0

        # Set by Chart after multihit detection
        self.hitsound: DirectSound | None = None
        self.textures: list[mgl.Texture | None] = []
        self._texture_sizes: list[tuple[float, float]] = []
        self.is_highlight: bool = False

        self.should_spawn_hit: bool = False
        self.hit_time: float = 0

    def init_assets(self) -> None:
        self.hitsound = SoundRegistry.get(
            self._HITSOUND_MAP.get(self.type, "none"))

        self._init_textures()

    def _init_textures(self) -> None:
        normal_keys = self._NORMAL_TEXTURE_MAP.get(
            self.type, ("none",) * 3)
        highlight_keys = self._HIGHLIGHT_TEXTURE_MAP.get(
            self.type, ("none",) * 3)

        textures: list[mgl.Texture | None] = []
        texture_sizes: list[tuple[float, float]] = []

        for normal_key, highlight_key in zip(normal_keys, highlight_keys):
            normal_tex = TextureRegistry.get(normal_key)
            highlight_tex = TextureRegistry.get(highlight_key)

            if self.is_highlight and highlight_tex:
                tex = highlight_tex
                w_scale = highlight_tex.width / normal_tex.width if normal_tex else 1.0
                tex_w = NOTE_TEXTURE_WIDTH * w_scale
            else:
                tex = normal_tex
                tex_w = NOTE_TEXTURE_WIDTH

            textures.append(tex)
            texture_sizes.append(self._calc_texture_size(tex, tex_w))

        self.textures = textures
        self._texture_sizes = texture_sizes

    def _calc_texture_size(self, tex: mgl.Texture | None, width: float) -> tuple[float, float]:
        if tex is None:
            return (1, 1)
        return (width, width / (tex.width / tex.height))

    def _get_is_visible(self):
        if self.type == NoteType.HOLD:
            return self.hold_time != 0 and self.hold_speed != 0

        return True

    def update(self, time: float) -> bool:
        self.should_spawn_hit = False

        if time >= self.time:
            self.base_fp = 0
            self.current_fp = 0

            self.should_spawn_hit = True
            self.hit_time = time

            if not self.is_hited:
                self.is_hited = True
                if self.hitsound:
                    self.hitsound.play()

            if self.type == NoteType.HOLD and time < self.end_time:
                self.length = (self.end_time - time) * self.hold_speed
                return False
            else:
                return True
        else:
            self.base_fp = self.fp - self.line.current_fp
            self.current_fp = self.base_fp * self.speed

        return False

    def render(self, renderer: Renderer, screen_size: tuple[int, int]) -> None:
        if (self.base_fp * self.base_speed < NOTE_COVER_FP and not self.is_hited):
            return
        if not self.is_visible:
            return
        if self.base_fp * self.base_speed > NOTE_MAX_VISIBLE_FP:
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
            self._render_texture(renderer, screen_size, 0, x, y)

    def _render_hold(self, renderer: Renderer, screen_size: tuple[int, int], x: float, y: float) -> None:
        w, h = screen_size

        # Head
        if not self.is_hited:
            if not self._render_texture(renderer, screen_size, 0, x, y, h_scale=self.hold_direction, anchor=(0.5, 1)):
                return

        # Body
        tex_w, _ = self._texture_sizes[1]
        if not self._render_texture(renderer, screen_size, 1, x, y,
                                    w_scale=1, h_scale=self.length * h, anchor=(0.5, 0),
                                    size_override=(round(tex_w * w), 1)):
            return

        # Tail
        end_x, end_y = rotate_translate(
            x, y, self.line.rotation, 0, self.length * h)
        self._render_texture(renderer, screen_size, 2,
                             end_x, end_y, h_scale=self.hold_direction, anchor=(0.5, 0))

    def _render_texture(self, renderer: Renderer, screen_size: tuple[int, int], index: int,
                        x: float, y: float, w_scale: float = 1.0, h_scale: float = 1.0,
                        anchor: tuple[float, float] = (0.5, 0.5), size_override: tuple[int, int] | None = None) -> bool:
        texture = self.textures[index]
        if texture is None:
            return False

        if size_override is None:
            tex_w, tex_h = self._texture_sizes[index]
            w, _ = screen_size
            texture_size = (round(tex_w * w), round(tex_h * w))
        else:
            texture_size = size_override

        renderer.render_texture(
            screen_size,
            texture=texture,
            x=x,
            y=y,
            w_scale=w_scale,
            h_scale=h_scale,
            rotation=self.line.rotation,
            anchor=anchor,
            texture_size=texture_size
        )
        return True


class PhiChart(Chart):
    def __init__(self, data: PhiChartModel) -> None:
        self.lines = [Line(line_model) for line_model in data.judgeLineList]

        self._init_note_assets()

    def _init_note_assets(self) -> None:
        time_groups: dict[float, list[Note]] = {}

        for line in self.lines:
            for group in line.notes:
                for note in group:
                    time_groups.setdefault(note.time, []).append(note)

            for note in line.holds:
                time_groups.setdefault(note.time, []).append(note)

        for notes in time_groups.values():
            for note in notes:
                note.is_highlight = len(notes) > 1

                note.init_assets()

    def update(self, time: float):
        for line in self.lines:
            line.update(time)

    def render(self, renderer: Renderer, screen_size: tuple[int, int]):
        for line in self.lines:
            line.render(renderer, screen_size)

        for line in self.lines:
            line.render_holds(renderer, screen_size)

        for line in self.lines:
            line.render_notes(renderer, screen_size)

        for line in self.lines:
            line.render_hits(renderer, screen_size)
