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


class EaseType(IntEnum):
    LINEAR = 0
    IN_QUAD = 1
    OUT_QUAD = 2
    IN_OUT_QUAD = 3
    IN_CUBIC = 4
    OUT_CUBIC = 5
    IN_OUT_CUBIC = 6
    IN_QUART = 7
    OUT_QUART = 8
    IN_OUT_QUART = 9
    IN_QUINT = 10
    OUT_QUINT = 11
    IN_OUT_QUINT = 12
    ZERO = 13
    ONE = 14

    @classmethod
    def _missing_(cls, value: object) -> "EaseType":
        return cls.LINEAR


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


class BlockEventPosition(BaseModel):
    x: float = 0.5
    y: float = 0.5


class BlockRotateEventModel(BaseModel):
    anchor: BlockEventPosition = BlockEventPosition()
    time: float = 0
    easeType: EaseType = EaseType.LINEAR
    rotation: float = 0


class BlockMoveEventModel(BaseModel):
    endPosition: BlockEventPosition = BlockEventPosition()
    time: float = 0
    easeTypeX: EaseType = EaseType.LINEAR
    easeTypeY: EaseType = EaseType.LINEAR


class BlockScaleEventModel(BaseModel):
    anchor: BlockEventPosition = BlockEventPosition()
    time: float = 0
    easeTypeX: EaseType = EaseType.LINEAR
    easeTypeY: EaseType = EaseType.LINEAR
    scale: BlockEventPosition = BlockEventPosition()


class BlockAreaModel(BaseModel):
    topRightPercentage: BlockEventPosition = BlockEventPosition()
    bottomLeftPercentage: BlockEventPosition = BlockEventPosition()
    appearTime: float = 0
    enableTime: float = 0
    disableTime: float = 0
    disappearTime: float = 0
    isSubtract: bool = False
    rotateEvents: list[BlockRotateEventModel] = []
    moveEvents: list[BlockMoveEventModel] = []
    scaleEvents: list[BlockMoveEventModel] = []


class PhiChartModel(BaseModel):
    formatVersion: PhiFormatVersion = PhiFormatVersion.FV3
    offset: float = 0
    judgeLineList: list[JudgeLineModel] = []
    blockAreaList: list[BlockAreaModel] = []
