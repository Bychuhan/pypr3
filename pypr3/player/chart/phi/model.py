from enum import IntEnum


from pydantic import BaseModel


class PhiFormatVersion(IntEnum):
    FV1 = 1
    FV3 = 3


class NoteType(IntEnum):
    OTHER = 0
    TAP = 1
    DRAG = 2
    HOLD = 3
    FLICK = 4

    @classmethod
    def _missing_(cls, value: object) -> "NoteType":
        return cls.OTHER


class EventType(IntEnum):
    MOVE = 0
    ROTATE = 1
    DISAPPEAR = 2
    SPEED = 3


class NoteModel(BaseModel):
    type: NoteType = NoteType.OTHER
    time: float = 0
    positionX: float = 0
    holdTime: float = 0
    speed: float = 1
    floorPosition: float = 0


class SpeedEventModel(BaseModel):
    startTime: float = 0
    endTime: float = 0
    value: float = 0


class EventModel(BaseModel):
    startTime: float = 0
    endTime: float = 0
    start: float = 0
    end: float = 0
    start2: float = 0
    end2: float = 0


class JudgeLineModel(BaseModel):
    bpm: float = 60
    notesAbove: list[NoteModel] = []
    notesBelow: list[NoteModel] = []
    speedEvents: list[SpeedEventModel] = []
    judgeLineDisappearEvents: list[EventModel] = []
    judgeLineMoveEvents: list[EventModel] = []
    judgeLineRotateEvents: list[EventModel] = []


class PhiChartModel(BaseModel):
    formatVersion: PhiFormatVersion = PhiFormatVersion.FV3
    offset: float = 0
    judgeLineList: list[JudgeLineModel] = []
