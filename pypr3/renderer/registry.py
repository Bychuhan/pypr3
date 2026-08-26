import moderngl as mgl


class TextureRegistry:
    _textures: dict[str, mgl.Texture] = {}

    @classmethod
    def register(cls, key: str, texture: mgl.Texture) -> None:
        cls._textures[key] = texture

    @classmethod
    def get(cls, texture: str) -> mgl.Texture | None:
        return cls._textures.get(texture)

    @classmethod
    def unregister(cls, key: str) -> mgl.Texture | None:
        return cls._textures.pop(key, None)
