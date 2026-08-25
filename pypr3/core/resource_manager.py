from pathlib import Path


class ResourceManager:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def get_shader(self, name: str) -> tuple[str, str, str | None]:
        vs_path = self.root / "shaders" / name / "vert.glsl"
        fs_path = self.root / "shaders" / name / "frag.glsl"
        gs_path = self.root / "shaders" / name / "geom.glsl"

        with open(vs_path, "r", encoding="utf-8") as f:
            vs = f.read()

        with open(fs_path, "r", encoding="utf-8") as f:
            fs = f.read()

        gs = None
        if gs_path.exists():
            with open(gs_path, "r", encoding="utf-8") as f:
                gs = f.read()

        return vs, fs, gs
