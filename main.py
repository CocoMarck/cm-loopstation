from core.microphone_recorder import MicrophoneRecorder
from core.dt_metronome import DTMetronome
from core.dt_sound_loopstation import DTSoundLoopstation
from controllers.dt_sound_loopstation_recorder_controller import DTSoundLoopstationRecorderController
from core.dt_timer import DTTimer
from core.dt_sound_loopstation_engine import DTSoundLoopstationEngine
from controllers.beat_controller import BeatController

# Sound Manager
from core.sound_manager_kivy import SoundManagerKivy
from core.sound_manager_ffplay import SoundManagerFFPlay

# Paths
from config.paths import SAMPLE_FILES, TEMP_DIR, ICON, CONFIG_ENGINE_FILE, CONFIG_GUI_FILE, THEMES_FILE

# Window
from views.dt_sound_loopstation_screen import DTSoundLoopstationScreen


# Config
from controllers.fps_sound_loopstation.config_gui_controller import ConfigGUIController
from controllers.fps_sound_loopstation.config_engine_controller import ConfigEngineController
from entities.fps_sound_loopstation.config_engine import ConfigEngine
from entities.fps_sound_loopstation.config_gui import ConfigGUI
config_engine = ConfigEngine()
config_engine_controller = ConfigEngineController(
    config_engine, CONFIG_ENGINE_FILE
)
config_gui = ConfigGUI()
config_gui_controller = ConfigGUIController(
    config_gui, CONFIG_GUI_FILE, THEMES_FILE
)
print(
    config_gui_controller.get_theme_names(), config_gui.theme,
    config_gui_controller.get_current_rgba_theme()
)


# Constantes necesarias
FPS_GUI = float(config_engine.fps)

sound_manager_kivy = SoundManagerKivy(volume=config_engine.volume)
sound_manager_ffplay = SoundManagerFFPlay(volume=config_engine.volume)

# Beat controller
beat_controller = BeatController( sound_manager_ffplay )

# FPSLoopstation Engine
metronome = DTMetronome(
    beats_per_bar=config_engine.beats, beats_limit_per_bar=config_engine.beats_limit,
    bpm=config_engine.bpm, bpm_limit=config_engine.bpm_limit
)
loopstation = DTSoundLoopstation(
    dt_metronome=metronome, sound_manager=sound_manager_ffplay, volume=config_engine.volume

)
microphone_recorder = MicrophoneRecorder()
recorder_controller = DTSoundLoopstationRecorderController(
    dt_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=TEMP_DIR, fileformat="wav"
)
recorder_controller.limit_record = config_engine.limit_record
recorder_controller.record_bars = config_engine.record_bars
timer = DTTimer( seconds=config_engine.seconds, activate=False )
engine = DTSoundLoopstationEngine(
    sound_loopstation=loopstation, recorder_controller=recorder_controller, timer=timer
)

# App
## Forzar FPS
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
## Forzar FPS
Config.set('graphics', 'vsync', '0')
#Config.set('graphics', 'maxfps', str(FPS_GUI))

## Resolution
#Window.size = (9*50, 20*50) # Res 9:20 Celular
#Window.size = (16*70, 9*70) # Res 16:9 PC
#Window.size = (1024, 500) # Res grafico de funciones
#loopstation.save_track(path=SAMPLE_FILES[0], loop=True, sample=True)
#loopstation.save_track(path=SAMPLE_FILES[1], loop=True, sample=True)
#loopstation.save_track(path=SAMPLE_FILES[3], loop=True, sample=True)
#loopstation.save_track(path=SAMPLE_FILES[2], loop=True, sample=True)
screen = DTSoundLoopstationScreen(
    engine=engine,
    #vertical_padding_offsets=[0,0.05, 0,0.08], # Margen pa celu
    #horizontal_padding_offsets=[0,0.05, 0.08,0], # Margen pa celu
    config_engine_controller=config_engine_controller,
    config_controller=config_gui_controller,
    beat_controller=beat_controller,
    play_metronome_beat=config_engine.play_beat
)
class FPSSoundLoopstationApp(App):
    def build(self):
        # Inicializar
        _screen = screen

        # Construir
        _screen.build()

        # Delta Time, GUI loop
        Clock.schedule_interval(_screen.update, 1/config_engine.fps if config_engine.fps > 0 else 0)

        return screen

    # Pause y resume an android
    def on_pause(self):
        return True

    def on_resume(self):
        return True

if __name__ == '__main__':
    FPSSoundLoopstationApp().run()

    # Guardar al cerrar
    try:
        config_engine_controller.update_beats( metronome.get_beats_per_bar() )
        config_engine_controller.update_bpm( metronome.get_bpm() )
        config_engine_controller.update_play_beat( screen.play_metronome_beat )

        config_engine_controller.update_limit_record( recorder_controller.limit_record )
        config_engine_controller.update_record_bars( recorder_controller.record_bars )

        config_engine_controller.update_seconds( timer.get_seconds() )
    except Exception as e:
        print(f"ERROR {e}.")
