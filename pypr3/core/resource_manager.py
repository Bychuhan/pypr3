from pathlib import Path


class ResourceManager:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def get_shader(self, name: str) -> tuple[str, str]:
        vs_path = self.root / "shaders" / name / "vert.glsl"
        fs_path = self.root / "shaders" / name / "frag.glsl"

        with open(vs_path, "r", encoding="utf-8") as f:
            vs = f.read()

        with open(fs_path, "r", encoding="utf-8") as f:
            fs = f.read()

        return vs, fs
