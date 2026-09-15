from enum import IntEnum, StrEnum
from typing import Any


from pydantic import BaseModel, ValidationInfo, GetCoreSchemaHandler, Field
from pydantic_core.core_schema import with_info_plain_validator_function


class NoteType(IntEnum):
    TAP = 1
    HOLD = 2
    FLICK = 3
    DRAG = 4

    @classmethod
    def _missing_(cls, value: object) -> "NoteType":
        return cls.TAP


class EventType(IntEnum):
    MOVEX = 0
    MOVEY = 1
    ROTATE = 2
    ALPHA = 3
    SPEED = 4
    SCALEX = 5
    SCALEY = 6
    COLOR = 7
    TEXT = 8
    PAINT = 9
    GIF = 10
    INCLINE = 11


class EaseType(IntEnum):
    LINEAR = 1
    OUT_SINE = 2
    IN_SINE = 3
    OUT_QUAD = 4
    IN_QUAD = 5
    IN_OUT_SINE = 6
    IN_OUT_QUAD = 7
    OUT_CUBIC = 8
    IN_CUBIC = 9
    OUT_QUART = 10
    IN_QUART = 11
    IN_OUT_CUBIC = 12
    IN_OUT_QUART = 13
    OUT_QUINT = 14
    IN_QUINT = 15
    OUT_EXPO = 16
    IN_EXPO = 17
    OUT_CIRC = 18
    IN_CIRC = 19
    OUT_BACK = 20
    IN_BACK = 21
    IN_OUT_CIRC = 22
    IN_OUT_BACK = 23
    OUT_ELASTIC = 24
    IN_ELASTIC = 25
    OUT_BOUNCE = 26
    IN_BOUNCE = 27
    IN_OUT_BOUNCE = 28
    IN_OUT_ELASTIC = 29

    @classmethod
    def _missing_(cls, value: object) -> "EaseType":
        return cls.LINEAR


class AttachUIId(StrEnum):
    NONE = "none"
    PAUSE = "pause"
    COMBONUMBER = "combonumber"
    COMBO = "combo"
    SCORE = "score"
    BAR = "bar"
    NAME = "name"
    LEVEL = "level"

    @classmethod
    def _missing_(cls, value: object) -> "AttachUIId":
        return cls.NONE


class Beat(tuple[int, int, int]):
    def __new__(cls, measure: int, beat: int, tick: int):
        return super().__new__(cls, (measure, beat, tick))

    @property
    def value(self):
        return self[0] + self[1] / self[2]

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        def create_beat(value: tuple[int, int, int] | Beat, info: ValidationInfo) -> "Beat":
            if isinstance(value, Beat):
                return value
            else:
                return Beat(value[0], value[1], value[2])

            raise ValueError(f"Cannot create Beat from {value}")

        return with_info_plain_validator_function(
            create_beat
        )

    def __repr__(self) -> str:
        return f"Beat({self[0]}, {self[1]}, {self[2]})"


class BpmModel(BaseModel):
    bpm: float = 60
    startTime: Beat = Beat(0, 0, 1)


class MetaModel(BaseModel):
    RPEVersion: int = 160
    background: str = "Unknown"
    charter: str = "Unknown"
    composer: str = "Unknown"
    id: str = "0"
    illustration: str = "Unknown"
    level: str = "Unknown"
    name: str = "Unknown"
    offset: float = 0
    song: str = "Unknown"


class EventModel(BaseModel):
    bezier: int = 0
    bezierPoints: tuple[float, float, float, float] = (0, 0, 0, 0)
    easingLeft: float = 0
    easingRight: float = 1
    easingType: EaseType = EaseType.LINEAR
    linkgroup: int = 0
    startTime: Beat = Beat(0, 0, 1)
    endTime: Beat = Beat(1, 0, 1)


class NormalEventModel(EventModel):
    start: float = 0
    end: float = 0


class ColorEventModel(EventModel):
    start: tuple[int, int, int] = (0, 0, 0)
    end: tuple[int, int, int] = (0, 0, 0)


class TextEventModel(EventModel):
    start: str = ""
    end: str = ""
    font: str = "cmdysj"


class EventLayerModel(BaseModel):
    moveXEvents: list[NormalEventModel] = []
    moveYEvents: list[NormalEventModel] = []
    rotateEvents: list[NormalEventModel] = []
    alphaEvents: list[NormalEventModel] = []
    speedEvents: list[NormalEventModel] = []


class ExtendedModel(BaseModel):
    colorEvents: list[ColorEventModel] = []
    scaleXEvents: list[NormalEventModel] = []
    scaleYEvents: list[NormalEventModel] = []
    textEvents: list[TextEventModel] = []
    paintEvents: list[NormalEventModel] = []
    gifEvents: list[NormalEventModel] = []
    inclineEvents: list[NormalEventModel] = []


class NoteModel(BaseModel):
    above: int = 1
    alpha: int = 255
    startTime: Beat = Beat(0, 0, 1)
    endTime: Beat = Beat(1, 0, 1)
    isFake: int = 0
    positionX: float = 0
    size: float = 1
    speed: float = 1
    type: NoteType = NoteType.TAP
    visibleTime: float = 999999
    yOffset: float = 0
    hitsound: str | None = None
    judgeArea: float = 1
    tint: tuple[int, int, int] = Field((255, 255, 255), alias="color")
    tintHitEffects: tuple[int, int, int] = (255, 255, 255)


class ControlModel(BaseModel):
    easing: EaseType = EaseType.LINEAR
    x: float = 0


class PosControlModel(ControlModel):
    pos: float = 1


class SizeControlModel(ControlModel):
    size: float = 1


class SkewControlModel(ControlModel):
    skew: float = 1


class YControlModel(ControlModel):
    y: float = 1


class AlphaControlModel(ControlModel):
    alpha: float = 1


class JudgeLineModel(BaseModel):
    Group: int = 0
    Name: str = "Untitled"
    Texture: str = "line.png"
    anchor: tuple[float, float] = (0.5, 0.5)
    eventLayers: list[EventLayerModel | None] = []
    extended: ExtendedModel = ExtendedModel()
    father: int = -1
    isCover: int = 1
    notes: list[NoteModel] = []
    numOfNotes: int = 0
    zOrder: int = 0
    attachUI: AttachUIId = AttachUIId.NONE
    isGif: bool = False
    posControl: list[PosControlModel] = []
    sizeControl: list[SizeControlModel] = []
    skewControl: list[SkewControlModel] = []
    yControl: list[YControlModel] = []
    alphaControl: list[AlphaControlModel] = []
    bpmfactor: float = 1
    rotateWithFather: bool = False


class TimeTagModel(BaseModel):
    name: str = "Unknown"
    time: Beat = Beat(0, 0, 1)


class RpeChartModel(BaseModel):
    BPMList: list[BpmModel] = []
    META: MetaModel = MetaModel()
    chartTime: float = 0
    judgeLineGroup: list[str] = []
    judgeLineList: list[JudgeLineModel] = []
    multiLineString: str = "0"
    multiScale: float = 1
    timeTags: list[TimeTagModel] = []
    xybind: bool = False
