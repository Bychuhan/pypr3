from typing import Sequence, Any


import moderngl as mgl
import numpy as np


class Shader:
    def __init__(self, ctx: mgl.Context, vertex_shader: str, fragment_shader: str, vertices: Sequence[Any] | None,
                 vertex_format: str, attributes: Sequence[str], geometry_shader: str | None = None,
                 indices: Sequence[int] | None = None, vbo_reserve: int = 0, vbo_dynamic: bool = False,
                 ibo_reserve: int = 0, ibo_dynamic: bool = False) -> None:
        self._ctx = ctx

        self._program = self._ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
            geometry_shader=geometry_shader
        )

        self._vbo: mgl.Buffer = self._ctx.buffer(np.array(
            vertices, dtype=np.float32) if vertices else None, reserve=vbo_reserve, dynamic=vbo_dynamic)

        self._indices = indices
        self._ibo = self._ctx.buffer(
            np.array(self._indices, dtype=np.int32) if indices else None, reserve=ibo_reserve, dynamic=ibo_dynamic)

        self._vertex_format = vertex_format
        self._attributes = attributes
        self._vao = self._ctx.vertex_array(  # type: ignore
            self._program,
            [(self._vbo, self._vertex_format, *self._attributes)],
            index_buffer=self._ibo
        )

    def set_uniform(self, key: str, value: Any):
        if not key in self._program:
            raise KeyError(f"Uniform '{key}' not found in shader program")

        self._program[key] = value

    def write_vbo(self, data: Sequence[Any]):
        arr = np.array(data, dtype=np.float32)

        size = arr.nbytes
        vbo_size = self._vbo.size

        if size > vbo_size:
            self._vbo.release()
            self._vao.release()

            self._vbo = self._ctx.buffer(
                reserve=max(size, vbo_size * 2)
            )

            self._vao = self._ctx.vertex_array(  # type: ignore
                self._program,
                [(self._vbo, self._vertex_format, *self._attributes)],
                index_buffer=self._ibo
            )

        self._vbo.clear()
        self._vbo.write(arr)

    def write_ibo(self, data: Sequence[Any]):
        arr = np.array(data, dtype=np.int32)

        size = arr.nbytes
        ibo_size = self._ibo.size

        if size > ibo_size:
            self._ibo.release()
            self._vao.release()

            self._ibo = self._ctx.buffer(
                reserve=max(size, ibo_size * 2)
            )

            self._vao = self._ctx.vertex_array(  # type: ignore
                self._program,
                [(self._vbo, self._vertex_format, *self._attributes)],
                index_buffer=self._ibo
            )

        self._ibo.clear()
        self._ibo.write(arr)

    def render(self, mode: int):
        self._vao.render(mode)

    def release(self):
        self._vao.release()
        self._vbo.release()
        self._ibo.release()
        self._program.release()
