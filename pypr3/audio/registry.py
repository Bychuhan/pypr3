from pypr3.audio import DirectSound


class SoundRegistry:
    _sounds: dict[str, DirectSound] = {}

    @classmethod
    def register(cls, key: str, sound: DirectSound) -> None:
        cls._sounds[key] = sound

    @classmethod
    def get(cls, key: str) -> DirectSound | None:
        return cls._sounds.get(key)