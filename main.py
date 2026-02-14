from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from controller.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from core.fps_timer import FPSTimer
from core.fps_loop import FPSLoop
from core.fps_sound_loopstation_engine import FPSSoundLoopstationEngine

from config.paths import SAMPLE_FILES, TEMP_DIR, ICON

# Window
from views.fps_sound_loopstation_window import FPSSoundLoopstationWindow


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
microphone_recorder = MicrophoneRecorder()
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=TEMP_DIR, fileformat="wav"
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
#Window.size = (960, 540)
#Window.resizable = True
class FPSSoundLoopstationApp(App):
    def build(self):
        window = FPSSoundLoopstationWindow( engine )
        window.build()

        Clock.schedule_interval(window.update, 1.0/FPS_GUI)

        return window

if __name__ == '__main__':
    FPSSoundLoopstationApp().run()
