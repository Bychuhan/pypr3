from pathlib import Path


class ResourceManager:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def get_file(self, file: str) -> bytes | None:
        path = self.root / file

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None\

    def get_texture(self, file: str) -> bytes | None:
        path = self.root / "textures" / file

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_sound(self, file: str) -> bytes | None:
        path = self.root / "sounds" / file

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_shader(self, name: str) -> tuple[str | None, str | None, str | None]:
        vs_path = self.root / "shaders" / name / "vert.glsl"
        fs_path = self.root / "shaders" / name / "frag.glsl"
        gs_path = self.root / "shaders" / name / "geom.glsl"

        vs = None
        if vs_path.exists():
            with open(vs_path, "r", encoding="utf-8") as f:
                vs = f.read()

        fs = None
        if fs_path.exists():
            with open(fs_path, "r", encoding="utf-8") as f:
                fs = f.read()

        gs = None
        if gs_path.exists():
            with open(gs_path, "r", encoding="utf-8") as f:
                gs = f.read()

        return vs, fs, gs
