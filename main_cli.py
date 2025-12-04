import time


from utils import ResourceLoader

resource_loader = ResourceLoader()
TEMP_DIR = resource_loader.base_dir.joinpath('tmp')
AUDIO_DIR = resource_loader.resources_dir.joinpath( 'audio' )
TEMPO_DIR = AUDIO_DIR.joinpath( 'tempo' )
SAMPLE_DIR = AUDIO_DIR.joinpath( 'sample' )

DICT_SAMPLE_DIR = resource_loader.get_recursive_tree( SAMPLE_DIR )
SAMPLE_FILES = DICT_SAMPLE_DIR['file']

DICT_TEMPO_DIR = resource_loader.get_recursive_tree( TEMPO_DIR )
TEMPO_FILES = DICT_TEMPO_DIR["file"]


from core.fps_loopstation import FPSLoopstation


FPS = 20
FRAME_TIME = 1.0 / FPS

loopstation = FPSLoopstation()
loopstation.fps = FPS
loopstation.update_metronome_settings()
loopstation.save_track( 0, path=str(SAMPLE_FILES[0]), sample=True )
loopstation.save_track( 1, path=str(SAMPLE_FILES[3]), sample=True )

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
