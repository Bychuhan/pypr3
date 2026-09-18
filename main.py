import time
import sys
import os
import mimetypes
from pathlib import Path
from tkinter.filedialog import askopenfilename


import pygame


from pypr3.core import Window, ResourceManager
from pypr3.player import Player
from pypr3.renderer import Renderer


pygame.init()
mimetypes.init()


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main() -> None:
    resource_manager = ResourceManager(resource_path("resources"))

    window = Window(970, 600, "pypr3", resizable=True)
    window.create()

    renderer = Renderer(resource_manager)
    renderer.set_blend(True)

    player = Player(resource_manager, renderer)
    player.init_assets()

    audio_types = " ".join(
        [f"*{k}" for k, v in mimetypes.types_map.items() if v.startswith("audio/")])
    image_types = " ".join(
        [f"*{k}" for k, v in mimetypes.types_map.items() if v.startswith("image/")])

    chart_path = Path(askopenfilename(
        filetypes=(("Chart", "*.json *.zip *.pez"),)))

    if chart_path.suffix in (".zip", ".pez"):
        player.load_pez(chart_path)
    else:
        player.load_chart(chart_path)
        player.load_music(askopenfilename(filetypes=(("Audio", audio_types),)))
        player.load_illustration(askopenfilename(
            filetypes=(("Image", image_types),)))

    frame_count = 0
    fps_timer = time.time()

    st = time.time()
    player.play_music()

    running = True
    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        window.handle_events(events)

        screen_size = window.size

        renderer.clear()

        nowt = time.time() - st
        player.update(nowt, screen_size)
        player.render(screen_size)

        pygame.display.flip()

        frame_count += 1
        if time.time() - fps_timer >= 1.0:
            print(f"FPS: {frame_count}")
            frame_count = 0
            fps_timer = time.time()

    pygame.quit()


if __name__ == "__main__":
    main()
