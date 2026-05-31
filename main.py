# Engine
from core.android_microphone_recorder import AndroidMicrophoneRecorder
from core.dt_metronome import DTMetronome
from core.dt_sound_loopstation import DTSoundLoopstation
from controllers.dt_sound_loopstation_recorder_controller import DTSoundLoopstationRecorderController
from core.dt_timer import DTTimer
from core.dt_sound_loopstation_engine import DTSoundLoopstationEngine
from controllers.beat_controller import BeatController

# Sound Manager
from core.sound_manager_kivy import SoundManagerKivy

# Paths
from config.paths import (
    # Normal
    SAMPLE_FILES, TEMP_DIR, ICON, CONFIG_ENGINE_FILE, CONFIG_GUI_FILE, THEMES_FILE,

    # Android
    ANDROID_CONFIG_ENGINE_FILE, ANDROID_CONFIG_GUI_FILE, ANDROID_THEMES_FILE, ANDROID_PATH
)

# Window
from views.dt_sound_loopstation_screen import DTSoundLoopstationScreen


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
FPS_GUI = float(config_engine.fps)

sound_manager_kivy = SoundManagerKivy(volume=config_engine.volume)

# Beat controller
beat_controller = BeatController( sound_manager_kivy )

# FPSLoopstation Engine
metronome = DTMetronome(
    beats_per_bar=config_engine.beats, beats_limit_per_bar=config_engine.beats_limit,
    bpm=config_engine.bpm, bpm_limit=config_engine.bpm_limit
)
loopstation = DTSoundLoopstation(
    dt_metronome=metronome, sound_manager=sound_manager_kivy, volume=config_engine.volume

)
microphone_recorder = AndroidMicrophoneRecorder()
recorder_controller = DTSoundLoopstationRecorderController(
    dt_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=ANDROID_PATH, fileformat="wav"
)
recorder_controller.limit_record = config_engine.limit_record
recorder_controller.record_bars = config_engine.record_bars
timer = DTTimer( seconds=config_engine.seconds, activate=False )
engine = DTSoundLoopstationEngine(
    sound_loopstation=loopstation, recorder_controller=recorder_controller, timer=timer
)

# App
from kivy.config import Config
Config.set('kivy', 'window_icon', str(ICON))

# Inicializar
from kivy.core.window import Window
from kivy.properties import ListProperty
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
from android import api_version

## Forzar FPS
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'maxfps', str(FPS_GUI))

## Screen
vertical_padding_offsets = [0,0,0,0]
horizontal_padding_offsets = [0,0,0,0]
if api_version > 35:
    # Android 15 (API 35) y 16 son los que fuerzan el Edge-to-Edge
    # Standard de celus: `16:9`, `20:9`, `19:9`.
    vertical_padding_offsets=[0,0.05, 0,0.08]
    horizontal_padding_offsets=[0,0.05, 0.08,0]

screen = DTSoundLoopstationScreen(
    engine=engine,
    vertical_padding_offsets=vertical_padding_offsets,
    horizontal_padding_offsets=horizontal_padding_offsets,
    config_controller=config_gui_controller, beat_controller=beat_controller,
    play_metronome_beat=config_engine.play_beat
)
class FPSSoundLoopstationApp(App):
    def build(self):
        # Permisos
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        # Inicializar
        _screen = screen

        # Construir
        _screen.build()

        # Delta Time, GUI loop
        Clock.schedule_interval(_screen.update, 1.0/FPS_GUI)

        return _screen

    # Pause y resume an android
    def on_pause(self):
        # Guardar al pausar
        try:
            config_engine_controller.update_beats( metronome.get_beats_per_bar() )
            config_engine_controller.update_bpm( metronome.get_bpm() )
            config_engine_controller.update_play_beat( screen.play_metronome_beat )

            config_engine_controller.update_limit_record( recorder_controller.limit_record )
            config_engine_controller.update_record_bars( recorder_controller.record_bars )

            config_engine_controller.update_seconds( timer.get_seconds() )
        except Exception as e:
            print(f"ERROR: {e}.")
        return True

    def on_resume(self):
        return True

if __name__ == '__main__':
    FPSSoundLoopstationApp().run()
