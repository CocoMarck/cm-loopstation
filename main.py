from core.android_microphone_recorder import AndroidMicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from controller.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from core.fps_timer import FPSTimer
from core.fps_loop import FPSLoop
from core.fps_sound_loopstation_engine import FPSSoundLoopstationEngine

from config.paths import SAMPLE_FILES, ICON

# Window
from views.fps_sound_loopstation_window import FPSSoundLoopstationWindow

# Android
import pathlib
from android.storage import app_storage_path
ANDROID_MUSIC_PATH = pathlib.Path(app_storage_path())


# Constantes necesarias
VOLUME = float(1)
FPS_ENGINE = float(20)
FPS_GUI = float(60)

## Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]

# FPSLoopstation Engine
loopstation = FPSSoundLoopstation(
    fps=FPS_ENGINE, volume=VOLUME, play_beat=True, beat_play_mode='emphasis_on_first',
    beats_per_bar=3, beats_limit_per_bar=9, bpm_limit=200
)
metronome = loopstation.fps_metronome
microphone_recorder = AndroidMicrophoneRecorder()
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=ANDROID_MUSIC_PATH, fileformat="wav"
)
recorder_controller.limit_record = True
recorder_controller.record_bars = 1
timer = FPSTimer( fps=FPS_ENGINE, seconds=10, activate=False )
engine = FPSSoundLoopstationEngine(
    sound_loopstation=loopstation, recorder_controller=recorder_controller, timer=timer
)

# App
## Forzar FPS
from kivy.config import Config
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'maxfps', str(FPS_GUI))

# Inicializar
from kivy.app import App
from kivy.clock import Clock

'''
Constructor de aplicación
'''
class FPSSoundLoopstationApp(App):
    def build(self):
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        window = FPSSoundLoopstationWindow( engine )
        window.build()

        Clock.schedule_interval(window.update, 1.0/FPS_GUI)

        return window

    # Pause y resume an android
    def on_puase(self):
        return self.window.on_pause()

    def on_resume(self):
        self.window.on_resume()

if __name__ == '__main__':
    FPSSoundLoopstationApp().run()
