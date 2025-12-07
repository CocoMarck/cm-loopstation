import time


from config.paths import SAMPLE_FILES


from core.fps_loopstation import FPSLoopstation


FPS = 60
FRAME_TIME = 1.0 / FPS

loopstation = FPSLoopstation()
loopstation.fps = FPS
loopstation.volume = 0.1
loopstation.update_metronome_settings()
loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
loopstation.save_track( path=SAMPLE_FILES[1], sample=True )
#loopstation.save_track( path=SAMPLE_FILES[2], sample=True )
#loopstation.save_track( path=SAMPLE_FILES[3], sample=True )
#loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
loopstation.recording = True
loopstation.recorder_limit_in_bars = 1

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
