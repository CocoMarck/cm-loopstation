import time

from core.fps_loopstation import FPSLoopstation


FPS = 60
FRAME_TIME = 1.0 / FPS

loopstation = FPSLoopstation()
loopstation.fps = FPS
loopstation.update_metronome_settings()

def update(dt):
    # Logica
    loopstation.looping()

def main():
    last_time = time.perf_counter()

    while True:
        start = time.perf_counter()

        # calcular delta time real
        now = time.perf_counter()
        dt = now - last_time
        last_time = now

        # actualizar lógica
        update(dt)

        # limitar a FPS fijos:
        elapsed = time.perf_counter() - start
        if elapsed < FRAME_TIME:
            time.sleep(FRAME_TIME - elapsed)

if __name__ == "__main__":
    main()
