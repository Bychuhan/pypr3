import moderngl as mgl


from pypr3.core import ResourceManager
from pypr3.renderer import Shader


class HitRenderer:
    def __init__(self, ctx: mgl.Context, resource_manager: ResourceManager) -> None:
        self._ctx = ctx
        self._resource_manager = resource_manager

        self._hit_verticles: list[float] = []
        self._hit_indices: list[int] = []
        self._particle_verticles: list[float] = []
        self._particle_indices: list[int] = []

        self._init_shaders()

    def _init_shaders(self):
        vs, fs, _ = self._resource_manager.get_shader("hit")

        self._hit_shader: None | Shader = None

        if vs and fs:
            self._hit_shader = Shader(
                ctx=self._ctx,
                vertex_shader=vs,
                fragment_shader=fs,
                vertices=None,
                vertex_format="2f 2f 2f 4f 1f",
                attributes=["in_pos", "in_texCoord",
                            "position", "in_color", "in_frame"],
                indices=None,
                vbo_reserve=4096 * (2 + 2 + 2 + 4 + 1) * 4,
                vbo_dynamic=True,
                ibo_reserve=4096 * 6,
                ibo_dynamic=True
            )

        vs, fs, _ = self._resource_manager.get_shader("particle")

        self._particle_shader: None | Shader = None

        if vs and fs:
            self._particle_shader = Shader(
                ctx=self._ctx,
                vertex_shader=vs,
                fragment_shader=fs,
                vertices=None,
                vertex_format="2f 2f 1f 4f",
                attributes=["in_pos", "position", "size", "in_color"],
                indices=None,
                vbo_reserve=4096 * (2 + 2 + 1 + 4) * 4,
                vbo_dynamic=True,
                ibo_reserve=4096 * 6,
                ibo_dynamic=True
            )

    def clear(self):
        self._hit_verticles.clear()
        self._hit_indices.clear()
        self._particle_verticles.clear()
        self._particle_indices.clear()

    def add_hit(self, x: float, y: float, color: tuple[float, float, float, float], frame: int):
        start = len(self._hit_verticles) // 44 * 4

        vertices: list[float] = [
            -1.0, -1.0, 0.0, 0.0, x, y, *color, frame,
            1.0, -1.0, 1.0, 0.0, x, y, *color, frame,
            1.0, 1.0, 1.0, 1.0, x, y, *color, frame,
            -1.0, 1.0, 0.0, 1.0, x, y, *color, frame,
        ]

        self._hit_verticles.extend(vertices)
        self._hit_indices.extend(
            [start, start + 1, start + 2, start, start + 3, start + 2])

    def add_particle(self, x: float, y: float, color: tuple[float, float, float, float], size: float):
        start = len(self._particle_verticles) // 36 * 4

        vertices: list[float] = [
            -1.0, -1.0, x, y, size, *color,
            1.0, -1.0, x, y, size, *color,
            1.0, 1.0, x, y, size, *color,
            -1.0, 1.0, x, y, size, *color,
        ]

        self._particle_verticles.extend(vertices)
        self._particle_indices.extend(
            [start, start + 1, start + 2, start, start + 3, start + 2])

    def render_hits(self, screen_size: tuple[int, int], texture: mgl.Texture, grid_size: tuple[int, int] = (1, 1),
                    texture_size: tuple[int, int] | None = None):
        if not self._hit_verticles:
            return

        if not self._hit_shader:
            return

        self._hit_shader.write_vbo(self._hit_verticles)
        self._hit_shader.write_ibo(self._hit_indices)

        self._hit_shader.set_uniform("screenSize", screen_size)
        self._hit_shader.set_uniform(
            "textureSize", texture_size or (texture.width, texture.height))
        self._hit_shader.set_uniform("gridSize", grid_size)

        self._hit_shader.set_uniform("texture", 0)
        texture.use(0)

        self._hit_shader.render(mgl.TRIANGLES)

    def render_particles(self, screen_size: tuple[int, int]):
        if not self._particle_verticles:
            return

        if not self._particle_shader:
            return

        self._particle_shader.write_vbo(self._particle_verticles)
        self._particle_shader.write_ibo(self._particle_indices)

        self._particle_shader.set_uniform("screenSize", screen_size)

        self._particle_shader.render(mgl.TRIANGLES)
