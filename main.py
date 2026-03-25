from core.android_microphone_recorder import AndroidMicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from controller.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from core.fps_timer import FPSTimer
from core.fps_loop import FPSLoop
from core.fps_sound_loopstation_engine import FPSSoundLoopstationEngine

# Rutas
from config.paths import SAMPLE_FILES, TEMP_DIR, ICON, ANDROID_CONFIG_ENGINE_FILE, ANDROID_CONFIG_GUI_FILE, ANDROID_THEMES_FILE, ANDROID_PATH

# Window
from views.fps_sound_loopstation_window import FPSSoundLoopstationWindow

# Android
ANDROID_MUSIC_PATH = ANDROID_PATH

# Config
from controllers.fps_sound_loopstation.config_gui_controller import ConfigGUIController
from controllers.fps_sound_loopstation.config_engine_controller import ConfigEngineController
from entities.fps_sound_loopstation.config_engine import ConfigEngine
from entities.fps_sound_loopstation.config_gui import ConfigGUI
config_engine = ConfigEngine()
config_engine_controller = ConfigEngineController(
    config_engine, ANDROID_CONFIG_ENGINE_FILE
)
config_gui = ConfigGUI()
config_gui_controller = ConfigGUIController(
    config_gui, ANDROID_CONFIG_GUI_FILE, ANDROID_THEMES_FILE
)



# Constantes necesarias
VOLUME = config_engine.volume
FPS_ENGINE = config_engine.fps
FPS_GUI = float(60)


## Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]

# FPSLoopstation Engine
loopstation = FPSSoundLoopstation(
    fps=FPS_ENGINE, volume=config_engine.volume, play_beat=config_engine.play_beat, beat_play_mode='emphasis_on_first',
    beats_per_bar=config_engine.beats, beats_limit_per_bar=config_engine.beats_limit,
    bpm=config_engine.bpm, bpm_limit=config_engine.bpm_limit
)
metronome = loopstation.fps_metronome
microphone_recorder = AndroidMicrophoneRecorder()
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=ANDROID_MUSIC_PATH, fileformat="wav"
)
recorder_controller.limit_record = config_engine.limit_record
recorder_controller.record_bars = config_engine.record_bars
timer = FPSTimer( fps=FPS_ENGINE, seconds=config_engine.seconds, activate=False )
engine = FPSSoundLoopstationEngine(
    sound_loopstation=loopstation, recorder_controller=recorder_controller, timer=timer
)

# App
## Forzar FPS
from kivy.config import Config
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'maxfps', str(FPS_GUI))

# Inicializar
from kivy.core.window import Window
from android import api_version
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

# Color
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba,
    is_the_rgba_color_bright
)


'''
Constructor de aplicación
'''
class FPSSoundLoopstationApp(App):
    def build(self):
        # Permisos
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        # Ventana
        vertical_padding_offsets = [0,0,0,0]
        horizontal_padding_offsets = [0,0,0,0]
        if api_version > 35:
            # Android 15 (API 35) y 16 son los que fuerzan el Edge-to-Edge
            # Standard de celus: `16:9`, `20:9`, `19:9`.
            vertical_padding_offsets=[0,0.05, 0,0.08]
            horizontal_padding_offsets=[0,0.05, 0.08,0]

        window = FPSSoundLoopstationWindow(
            engine, vertical_padding_offsets, horizontal_padding_offsets,
            config_controller=config_gui_controller
        )
        window.build()

        # Delta Time
        Clock.schedule_interval(window.update, 1.0/FPS_GUI)

        return window

    # Pause y resume an android
    def on_pause(self):
        return self.window.on_pause()

    def on_resume(self):
        self.window.on_resume()

    def on_stop(self):
        # A guardar al cerrar
        config_engine_controller.update_beats( metronome.beats_per_bar )
        config_engine_controller.update_bpm( metronome.bpm )
        config_engine_controller.update_play_beat( metronome.play_beat )

        config_engine_controller.update_limit_record( recorder_controller.limit_record )
        config_engine_controller.update_record_bars( recorder_controller.record_bars )

        config_engine_controller.update_seconds( timer.seconds )

if __name__ == '__main__':
    FPSSoundLoopstationApp().run()
