from pathlib import Path
from io import BytesIO


import moderngl as mgl
from PIL import Image


class TextureConverter:
    @staticmethod
    def from_file(ctx: mgl.Context, path: str | Path) -> mgl.Texture:
        with Image.open(path) as image:
            return TextureConverter.from_image(ctx, image)

    @staticmethod
    def from_bytes(ctx: mgl.Context, data: bytes) -> mgl.Texture:
        with Image.open(BytesIO(data)) as image:
            return TextureConverter.from_image(ctx, image)

    @staticmethod
    def from_image(ctx: mgl.Context, image: Image.Image) -> mgl.Texture:
        image = image.convert("RGBA")
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        texture = ctx.texture(
            size=image.size,
            components=4,
            data=image.tobytes()
        )

        texture.repeat_x = False
        texture.repeat_y = False

        texture.filter = (mgl.LINEAR, mgl.LINEAR)

        return texture
