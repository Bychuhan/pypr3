from typing import Sequence, Any


import moderngl as mgl
import numpy as np


class Shader:
    def __init__(self, ctx: mgl.Context, vertex_shader: str, fragment_shader: str, vertices: Sequence[float],
                 vertex_format: str, attributes: Sequence[str], geometry_shader: str | None = None,
                 indices: Sequence[int] | None = None) -> None:
        self._program = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
            geometry_shader=geometry_shader
        )

        self._vertices = vertices
        self._vbo = ctx.buffer(np.array(self._vertices, dtype=np.float32))

        self._indices = indices
        self._ibo = None
        if not self._indices is None:
            self._ibo = ctx.buffer(np.array(self._indices, dtype=np.int32))

        self._vao = ctx.vertex_array(  # type: ignore
            self._program,
            [(self._vbo, vertex_format, *attributes)],
            index_buffer=self._ibo
        )

    def set_uniform(self, key: str, value: Any):
        if not key in self._program:
            raise KeyError(f"Uniform '{key}' not found in shader program")

        self._program[key] = value

    def render(self, mode: int):
        self._vao.render(mode)

    def release(self):
        self._vao.release()
        self._vbo.release()
        if not self._ibo is None:
            self._ibo.release()
        self._program.release()
