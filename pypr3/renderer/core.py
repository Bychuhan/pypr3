import moderngl as mgl


from pypr3.core import ResourceManager
from pypr3.renderer import Shader


class Renderer:
    def __init__(self, resource_manager: ResourceManager, gl_version: int = 330, standalone: bool = False) -> None:
        self._resource_manager = resource_manager

        self.ctx = mgl.create_context(
            require=gl_version, standalone=standalone)

        self.ctx.blend_func = (  # type: ignore
            mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA,
            mgl.ONE, mgl.ONE
        )

        self._init_shaders()

    def _init_shaders(self):
        vs, fs, _ = self._resource_manager.get_shader("rect")

        self._rect_shader = Shader(
            ctx=self.ctx,
            vertex_shader=vs,
            fragment_shader=fs,
            vertices=[
                -1.0, -1.0,
                1.0, -1.0,
                1.0,  1.0,
                -1.0,  1.0
            ],
            vertex_format="2f",
            attributes=["in_pos"],
            indices=[
                0, 1, 2,
                0, 3, 2
            ]
        )

    def set_blend(self, enable: bool):
        if enable:
            self.ctx.enable(mgl.BLEND)
        else:
            self.ctx.disable(mgl.BLEND)

    def clear(self, r: float = 0, g: float = 0, b: float = 0, a: float = 0, depth: float = 1):
        self.ctx.clear(r, g, b, a, depth)

    def render_rect(self, screen_size: tuple[int, int], x: float, y: float, width: float, height: float,
                    rotation: float, anchor: tuple[float, float] = (0.5, 0.5),
                    color: tuple[float, float, float, float] = (1, 1, 1, 1)):
        self._rect_shader.set_uniform("screenSize", screen_size)
        self._rect_shader.set_uniform("position", (x, y))
        self._rect_shader.set_uniform("size", (width, height))
        self._rect_shader.set_uniform("rotation", rotation)
        self._rect_shader.set_uniform("anchor", anchor)
        self._rect_shader.set_uniform("color", color)

        self._rect_shader.render(mgl.TRIANGLES)

    @property
    def viewport(self):
        return self.ctx.viewport

    @viewport.setter
    def viewport(self, value: tuple[int, int, int, int]):
        if len(value) != 4:
            raise ValueError("Viewport must be (x, y, width, height)")

        _, _, w, h = value

        if w < 0 or h < 0:
            raise ValueError("Width and height must be positive")

        self.ctx.viewport = value
