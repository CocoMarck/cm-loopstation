import time


from config.paths import SAMPLE_FILES


from core.fps_metronome import FPSMetronome


FPS = 20
FRAME_TIME = 1.0 / FPS

metronome = FPSMetronome()

def update(dt):
    # Logica
    metronome.update()

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
    #from multiprocessing import Process
    #p = Process(target=main, args=())
    #p.start()
    #p.join()
